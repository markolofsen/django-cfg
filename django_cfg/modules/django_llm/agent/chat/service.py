"""`ChatService`: sessions, the daily cap, a turn's history and its stream, over the host's concrete models.

    service = ChatService(Thread, ChatPolicy(messages_per_day=200))
    opened = service.begin(user, thread, text, client_id, turn_context)      # may refuse; nothing streamed yet
    return StreamingHttpResponse(service.frames(opened), content_type="text/event-stream", headers=SSE_HEADERS)

`begin` is sync (ORM) and raises `ServiceUnavailable`, `RateLimited`, `InvalidContext`, `InvalidTurn`, `Busy`, `NotFound`. `frames` is an async
iterator of SSE strings: `run` first, the answer stored (flushed while streaming, closed once, shielded) before the
`done`/`error` frame leaves. A resend of a `client_id` whose answer is still running (`TurnKind.LIVE`) is streamed from storage instead
(`attach`), as is a second reader of any answer. `cancel` asks a running answer to stop, from any worker. A kind that sets `detach`
keeps its run going when the reader leaves; otherwise a disconnect cancels it, and either way the tokens spent are booked.
Tests replace `model_factory` (a scripted model; test-only, a production set logs a warning) and `pricer`.
"""

from __future__ import annotations

import functools
import logging
import math
import sys
import uuid
from collections.abc import AsyncIterator, Callable, Mapping
from dataclasses import dataclass
from datetime import datetime, time, timedelta, timezone as dt_timezone
from typing import Any

from django.db import transaction
from django.utils import timezone
from pydantic import BaseModel, ValidationError
from pydantic_ai.models import Model

from django_cfg.modules.django_llm.agent.bus.events import RunEvent, encode_sse
from django_cfg.modules.django_llm.agent.chat import contract, kind as kinds
from django_cfg.modules.django_llm.agent.chat.cancel import CacheCancelSignal, CancelSignal
from django_cfg.modules.django_llm.agent.chat import turn as rules
from django_cfg.modules.django_llm.agent.chat.errors import InvalidContext, InvalidKind, InvalidTurn, NotFound, QuotaExceeded, RateLimited, ServiceUnavailable
from django_cfg.modules.django_llm.agent.chat.kind import ChatKind, KindScope
from django_cfg.modules.django_llm.agent.chat.runner import build_model, kind_source, replay_events
from django_cfg.modules.django_llm.agent.chat.store import DjangoTurnStore
from django_cfg.modules.django_llm.agent.chat.tail import Cursor, Tailer, follow
from django_cfg.modules.django_llm.agent.runtime.cost import Pricer, PriceRow, price_run
from django_cfg.modules.django_llm.agent.runtime.driver import DriverConfig, RunDriver, RunHooks, RunLock, RunOutcome, RunState
from django_cfg.modules.django_llm.agent.runtime.detach import detached
from django_cfg.modules.django_llm.agent.runtime.streaming import StreamRunResult
from django_cfg.modules.django_llm.agent.runtime.tally import UsageTally
from django_cfg.modules.django_llm.agent.trace import MessageJsonSink, Recorder, TraceSink


log = logging.getLogger(__name__)

#: Appended to an answer that did not finish when it is replayed to the model, so a cut-off text is not read as a complete one.
INTERRUPTED_NOTE = "[interrupted: this answer was cut off before it was finished]"

#: The window of `ChatPolicy.send_rate`.
SEND_RATE_WINDOW_S = 60

#: `(actor, thread, now) -> None`; raises `RateLimited` / `QuotaExceeded` to refuse. `thread` is None only for a check made without one.
QuotaCheck = Callable[[Any, Any, datetime], None]
#: `(service, actor, thread_id) -> thread | None`: the tenancy rule. None reads as "no such chat" (404), for a stranger and a missing one alike.
ResolveThread = Callable[["ChatService", Any, uuid.UUID], Any]
#: `(stored answer row, RunOutcome) -> None`, after the answer is stored; an exception is logged and swallowed.
OnAnswer = Callable[[Any, RunOutcome], None]
#: `(answer row, part index, part dict incl. its `ack`) -> None`, after a browser reported a `ui_payload`; an exception is logged and swallowed.
OnUiPayloadAccepted = Callable[[Any, int, dict], None]


def parse_chain(raw: str | tuple[str, ...] | list[str] | None) -> tuple[str, ...] | None:
    """A model chain from an env string (`"a/b, c/d"`) or a sequence; empty means "not set"."""
    if raw is None:
        return None
    items = raw.split(",") if isinstance(raw, str) else raw
    chain = tuple(i.strip() for i in items if i and i.strip())
    return chain or None


@dataclass(frozen=True)
class ChatPolicy:
    """The host's numbers. Everything has a default; none is product-specific."""

    messages_per_day: int | None = 200  # user messages per user per UTC day over all threads; None = no cap
    max_text_chars: int = 4000
    stale_run_seconds: float = 150.0  # a `running` row older than this is dead (keep above every kind's timeout_s)
    ping_s: float = 15.0
    tail_poll_s: float = 0.5  # how often a stream that follows a running answer from storage (`attach`) looks at its row
    models: str | tuple[str, ...] | None = None  # overrides every kind's chain (ops switch; an env string "a/b, c/d" is parsed); None = each kind's own
    price_timeout_s: float = 3.0
    check_quota: QuotaCheck | None = None  # replaces the built-in daily message cap (`messages_per_day` is then ignored)
    available: Callable[[], bool] | None = None  # THE kill switch: False = a spent budget or an ops switch; a send is refused with `ServiceUnavailable` (503) before anything is read or stored. A host has no second gate beside it
    send_rate: int | None = None  # THE burst cap: user messages per user per rolling minute over all threads; over it a send is refused 429 `rate_limited` with `Retry-After`; None = no cap. Checked after `available`, before the daily cap / `check_quota`; a host needs no DRF throttle beside it
    fallback_prices: Mapping[str, PriceRow] | None = None  # {slug: {input, output}} USD per Mtok for a run the registry cannot price
    default_price: PriceRow | None = None  # the row for a slug in no table: set it to the dearest you know so a run is never free
    title_models: str | tuple[str, ...] | None = None  # cheap model chain that writes the title after the first answer; None = no LLM titles


@dataclass(frozen=True)
class Opened:
    thread: Any
    kind: ChatKind
    turn: rules.Turn
    deps: Any
    history: list[dict]
    store: DjangoTurnStore
    attachments: tuple = ()  # the rows bound to this turn's user message (empty without files)


def day_start(now: datetime) -> datetime:
    return datetime.combine(now.astimezone(dt_timezone.utc).date(), time.min, tzinfo=dt_timezone.utc)


def stored_context(chat_kind: ChatKind, context: BaseModel) -> dict:
    """What a thread keeps of a validated context: all of it but the kind's transient keys."""
    dumped = context.model_dump(mode="json")
    return {k: v for k, v in dumped.items() if k not in chat_kind.transient_context}


def parse_context(chat_kind: ChatKind, raw: dict) -> BaseModel:
    """The kind's context schema applied to a client-sent dict."""
    try:
        return chat_kind.context_schema.model_validate(raw)
    except ValidationError as err:
        raise InvalidContext([{"field": ".".join(str(p) for p in e["loc"]), "code": e["type"]} for e in err.errors()]) from err


def owners_thread(service: "ChatService", actor, thread_id: uuid.UUID):
    """Default `resolve_thread`: the thread of this owner, or None."""
    return service.thread_model.objects.for_owner(actor).filter(pk=thread_id).first()


class ChatService:
    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        contract.check_subclass(cls, ChatService)  # an override that drops a parameter of the base fails here, not on the first send

    def __init__(
        self,
        thread_model: Any,
        policy: ChatPolicy | None = None,
        *,
        model_factory: Callable[[ChatKind], Model] | None = None,
        pricer: Pricer | None = None,
        lock: RunLock | None = None,
        resolve_thread: ResolveThread | None = None,
        on_answer: OnAnswer | None = None,
        title_job: Callable[..., None] | None = None,
        on_ui_payload_accepted: OnUiPayloadAccepted | None = None,
        trace_sink: Callable[[Any, Any], TraceSink] | None = None,
        cancel_signal: CancelSignal | None = None,
    ):
        """`policy` may be a `ChatPolicy` or a zero-argument callable returning one, read on every use (rates from settings,
        swapped in tests). `resolve_thread(service, actor, id)` is the tenancy rule (default: the owner's thread); `on_answer`
        runs after each stored answer; `title_job(thread_model, thread_id, models)` runs the LLM title off the request (default:
        a daemon thread; a host may enqueue a job instead). `on_ui_payload_accepted(answer, index, part)` runs after `ack_part`
        stored a browser's verdict on a part (`{"applied": bool, "reason": str}` under `part["ack"]`). `trace_sink(store, message_id)`
        returns where a kind's trace goes (default: `MessageJsonSink`, the message row's `trace` column). `cancel_signal` carries a cancel
        request to the worker that streams the answer (default: a flag on Django's cache, so workers must share one)."""
        self.thread_model = thread_model
        self.message_model = thread_model.messages.rel.related_model
        self._policy = policy or ChatPolicy()
        self._model_factory: Callable[[ChatKind], Model] | None = None
        self.model_factory = model_factory  # through the setter: a warning outside tests
        self.pricer = pricer
        self.lock = lock
        self.resolve_thread = resolve_thread or owners_thread
        self.on_answer = on_answer
        self.title_job = title_job
        self.on_ui_payload_accepted = on_ui_payload_accepted
        self.trace_sink = trace_sink
        self.cancel_signal: CancelSignal = cancel_signal or CacheCancelSignal()
        self._attachment_store: Any = False

    @property
    def model_factory(self) -> Callable[[ChatKind], Model] | None:
        """A TEST hook: it replaces the kind's model chain, so the fallbacks and the error classification never run. Production sets
        `ChatKind.models` or `ChatPolicy.models`; a factory set outside a test run is logged as a warning."""
        return self._model_factory

    @model_factory.setter
    def model_factory(self, value: Callable[[ChatKind], Model] | None) -> None:
        if value is not None and "pytest" not in sys.modules:
            log.warning("chat: ChatService.model_factory is a test hook and bypasses the kind's model chain (no fallback, no error classification); set ChatKind.models or ChatPolicy.models instead")
        self._model_factory = value

    @property
    def attachment_model(self) -> Any:
        """The host's concrete attachment table (`Message.attachments`), or None when the host declared none."""
        descriptor = getattr(self.message_model, "attachments", None)
        return descriptor.rel.related_model if descriptor is not None and hasattr(descriptor, "rel") else None

    @property
    def attachment_store(self) -> Any:
        """`AttachmentStore` over `attachment_model`, or None."""
        if self._attachment_store is False:
            model = self.attachment_model
            if model is None:
                self._attachment_store = None
            else:
                from django_cfg.modules.django_llm.agent.chat.attachments.store import AttachmentStore

                self._attachment_store = AttachmentStore(model)
        return self._attachment_store

    @property
    def policy(self) -> ChatPolicy:
        return self._policy() if callable(self._policy) else self._policy

    @policy.setter
    def policy(self, value: ChatPolicy | Callable[[], ChatPolicy]) -> None:
        self._policy = value

    # ── sessions ────────────────────────────────────────────────────────────────

    def create(self, owner, kind_name: str, *, title: str = "", context: dict | None = None, fields: dict | None = None):
        """A new empty thread. `fields` are extra columns of the host's model (project, link ...), set as given."""
        try:
            chat_kind = kinds.get(kind_name)
        except kinds.UnknownKind as err:
            raise InvalidKind(kind_name) from err
        return self.thread_model.objects.create(
            **{**(fields or {}), "owner": owner, "kind": chat_kind.name, "title": title[:200], "context": stored_context(chat_kind, parse_context(chat_kind, context or {}))}
        )

    def get(self, owner, thread_id: uuid.UUID):
        """The actor's thread (`resolve_thread`; by default the owner's). A stranger's thread and a missing one raise the same `NotFound`."""
        found = self.resolve_thread(self, owner, thread_id)
        if found is None:
            raise NotFound(str(thread_id))
        return found

    def list_for(self, owner, *, kind: str | None = None, limit: int = 50, nonempty: bool = False, only_with_messages: bool = False) -> list:
        """The owner's threads, newest first. `nonempty` (alias `only_with_messages`) leaves out empty "new chat" rows and
        orders by last activity; it reads `message_count` / `last_message_at` from the thread row, with no join over messages."""
        threads = self.thread_model.objects.for_owner(owner)
        if nonempty or only_with_messages:
            qs = threads.nonempty()
            if kind:
                qs = qs.of_kind(kind)
            return list(qs.order_by("-updated_at", "-created_at")[:limit])
        qs = threads.with_activity()
        if kind:
            qs = qs.of_kind(kind)
        return list(qs.newest_first()[:limit])

    def remember(self, thread, context: BaseModel) -> None:
        """Keep the validated context on the thread: the latest of what every turn said. Only a changed one is written."""
        stored = stored_context(kinds.get(thread.kind), context)
        if stored != thread.context:
            self.thread_model.objects.filter(pk=thread.pk).update(context=stored)
            thread.context = stored

    # ── reads ───────────────────────────────────────────────────────────────────

    def history_for_model(self, thread, chat_kind: ChatKind, *, before_seq: int) -> list[dict]:
        """The window as `[{role, content, tool_calls?}]`, oldest first: the shape `convert_history` takes.

        Tool calls are replayed only for the latest `limits.replay_tool_calls_of` answers; older ones are text. An answer that did not
        finish (`cancelled`, `error`) keeps what it said, marked with `INTERRUPTED_NOTE`, and replays no tool calls.
        """
        rows = self.message_model.objects.window(thread, chat_kind.history_window, before_seq=before_seq)
        keep = chat_kind.limits.replay_tool_calls_of
        answers = [m for m in rows if m.role == rules.Role.ASSISTANT]
        replay = {m.pk for m in (answers[-keep:] if keep else [])}
        out: list[dict] = []
        files = self._attachments_of([m.pk for m in rows if m.role == rules.Role.USER]) if chat_kind.attachments is not None else {}
        for m in rows:
            if m.role == rules.Role.USER and not m.text and m.pk not in files:
                continue  # a hidden feedback turn has no words: nothing to replay (providers refuse an empty user message)
            interrupted = m.role == rules.Role.ASSISTANT and m.status != rules.Status.DONE
            item: dict = {"role": m.role, "content": f"{m.text}\n\n{INTERRUPTED_NOTE}" if interrupted else m.text}
            if m.pk in files:
                item["attachments"] = files[m.pk]
            if m.pk in replay and not interrupted:
                calls = [c for c in (m.tool_calls or []) if isinstance(c, dict) and c.get("output") is not None]
                if calls:
                    item["tool_calls"] = calls
            out.append(item)
        return out

    def _attachments_of(self, message_ids: list) -> dict:
        """`{message id: [attachment rows]}` for the given user messages: one query."""
        model = self.attachment_model
        if model is None or not message_ids:
            return {}
        grouped: dict = {}
        for row in model.objects.filter(message_id__in=message_ids).exclude(status="staged").order_by("created_at"):
            grouped.setdefault(row.message_id, []).append(row)
        return grouped

    def page(self, thread, *, limit: int = 50, before_seq: int | None = None) -> list:
        """The transcript for a surface: the newest `limit` messages (older than `before_seq` when paging back), oldest first."""
        qs = self.message_model.objects.in_thread(thread)
        if before_seq is not None:
            qs = qs.filter(seq__lt=before_seq)
        found = list(qs.order_by("-seq")[:limit])[::-1]
        if self.attachment_model is not None:
            grouped = self._attachments_of([m.pk for m in found if m.role == rules.Role.USER])
            for m in found:
                m.attached = grouped.get(m.pk, [])  # read by `MessageSerializer.attachments`; no query per message
        return found

    def ack_part(self, thread, message_id: uuid.UUID, index: int, *, applied: bool, reason: str = "") -> dict:
        """Store the browser's verdict on part `index` of an answer of `thread` as `part["ack"]` (the latest report wins), then run the
        host's `on_ui_payload_accepted`. Raises `NotFound` for no such answer of this thread or no such part."""
        with transaction.atomic():
            row = self.message_model.objects.in_thread(thread).select_for_update().filter(pk=message_id, role=rules.Role.ASSISTANT).first()
            parts = list(row.parts or []) if row is not None else []
            if row is None or not 0 <= index < len(parts) or not isinstance(parts[index], dict):
                raise NotFound(f"{message_id}/parts/{index}")
            parts[index] = {**parts[index], "ack": {"applied": bool(applied), "reason": reason[:200]}}
            self.message_model.objects.filter(pk=row.pk).update(parts=parts)
            row.parts = parts
        if self.on_ui_payload_accepted is not None:
            try:
                self.on_ui_payload_accepted(row, index, parts[index])
            except Exception:  # noqa: BLE001 - a hook must not lose the stored verdict
                log.exception("chat: on_ui_payload_accepted failed for message %s", message_id)
        return parts[index]

    # ── cap and reaper ──────────────────────────────────────────────────────────

    def sent_today(self, user, now: datetime) -> int:
        return self.message_model.objects.sent_by(user, day_start(now)).count()

    def check_quota(self, user, now: datetime, thread=None) -> None:
        """THE quota: the per-minute `send_rate`, then the daily cap or the host's `check_quota` (which replaces the daily cap only)."""
        policy = self.policy
        if policy.send_rate is not None:
            recent = self.message_model.objects.sent_by(user, now - timedelta(seconds=SEND_RATE_WINDOW_S))
            if recent.count() >= policy.send_rate:
                oldest = recent.order_by("created_at").values_list("created_at", flat=True).first()
                wait = SEND_RATE_WINDOW_S - (now - oldest).total_seconds() if oldest is not None else SEND_RATE_WINDOW_S
                raise QuotaExceeded("send_rate", retry_after=max(1, math.ceil(wait)))
        if policy.check_quota is not None:
            policy.check_quota(user, thread, now)
            return
        cap = policy.messages_per_day
        if cap is not None and self.sent_today(user, now) >= cap:
            raise RateLimited(str(user.pk))

    def ensure_available(self) -> None:
        """Raise `ServiceUnavailable` while the policy's `available` says no. Cheap; call it before reading or storing anything."""
        gate = self.policy.available
        if gate is not None and not gate():
            raise ServiceUnavailable()

    def reap_stale(self, now: datetime | None = None) -> int:
        """Close every answer left `running` past the window, in all threads (a periodic job; `begin` also reaps its own thread)."""
        cutoff = (now or timezone.now()) - timedelta(seconds=self.policy.stale_run_seconds)
        return (
            self.message_model.objects.running()
            .filter(created_at__lt=cutoff)
            .update(status=rules.Status.ERROR, error_code=rules.ErrorCode.FAILED)
        )

    # ── a turn ──────────────────────────────────────────────────────────────────

    def model_for(self, chat_kind: ChatKind) -> Model:
        if self.model_factory is not None:
            return self.model_factory(chat_kind)
        return build_model(parse_chain(self.policy.models) or chat_kind.models)

    def begin(
        self, owner, thread, text: str, client_id: uuid.UUID | None, turn_context: dict | None = None, *, now: datetime | None = None,
        attachments: list[uuid.UUID] | None = None,
    ) -> Opened:
        """Store the message and begin the answer. Raises `ServiceUnavailable`, `RateLimited` (or the host's `QuotaExceeded`), `InvalidContext`, `InvalidTurn`, `Busy`, `NotFound`."""
        self.ensure_available()
        now = now or timezone.now()
        try:
            chat_kind = kinds.get(thread.kind)
        except kinds.UnknownKind as err:
            raise NotFound(str(thread.pk)) from err
        constraints = chat_kind.message_constraints
        if constraints is not None:
            constraints.validate(text, turn_context)  # before the quota and before anything is stored
        context = parse_context(chat_kind, chat_kind.merge_context(thread.context, turn_context or {}))
        resend = client_id is not None and self.message_model.objects.in_thread(thread).filter(role=rules.Role.USER, client_id=client_id).exists()
        files: list = []
        if attachments and not resend:  # a resend is served from storage: its files are already bound
            if chat_kind.attachments is None or self.attachment_store is None:
                raise InvalidTurn("attachments", "not_enabled")
            files = self.attachment_store.lock_staged(owner, chat_kind.name, list(attachments), chat_kind.attachments)
            from django_cfg.modules.django_llm.agent.chat.attachments.delivery import can_read_everything

            if not can_read_everything(chat_kind.attachments, parse_chain(self.policy.models) or chat_kind.models, files):
                raise InvalidTurn("attachments", "model_cannot_read")  # `on_unreadable="refuse"`: before anything is stored
        if not resend:
            self.check_quota(owner, now, thread)  # a resend is served from storage and costs nothing
        deps = chat_kind.make_deps(KindScope(user=owner, thread_id=thread.pk, kind=chat_kind.name, context=context, thread_context=thread.context, thread=thread))
        store = DjangoTurnStore(thread)
        with transaction.atomic():  # the message and its files bind together or not at all
            started = rules.start(store, text, client_id, now=now, max_chars=(constraints.max_text_chars if constraints is not None and constraints.max_text_chars is not None else self.policy.max_text_chars), stale_after_s=self.policy.stale_run_seconds, allow_empty=chat_kind.allows_empty_text(turn_context) or bool(files))
            if files and started.kind is rules.TurnKind.STARTED and self.attachment_store.bind(owner, [f.pk for f in files], started.user.id, chat_kind.name) != len(files):
                raise InvalidTurn("attachments", "unavailable")  # another request took one first: roll the message back
        bound = tuple(self.attachment_model.objects.filter(message_id=started.user.id, status="attached").order_by("created_at")) if started.runs_model and chat_kind.attachments is not None and self.attachment_model is not None else ()
        if started.runs_model:
            self.remember(thread, context)  # the next turn may omit what this one said (e.g. a document sent once per hash)
        if started.kind is not rules.TurnKind.LIVE and not thread.title and started.user.text:
            self.thread_model.objects.filter(pk=thread.pk, title="").update(title=chat_kind.title_of(started.user.text)[:200])
        prior = self.history_for_model(thread, chat_kind, before_seq=started.user.seq) if started.runs_model else []
        if started.runs_model and chat_kind.on_turn is not None:
            info = kinds.TurnInfo(text=started.user.text, history=tuple(prior), window=chat_kind.history_window, user_seq=started.user.seq, context=context)
            try:
                replaced = chat_kind.on_turn(deps, info)
            except BaseException:
                rules.finish(store, started.assistant.id, status=rules.Status.ERROR, text="", error_code=rules.ErrorCode.FAILED)  # the answer row was begun: close it, do not leave it `running` until the reaper
                raise
            deps = deps if replaced is None else replaced
        return Opened(thread, chat_kind, started, deps, prior, store, bound)

    def fallback_pricer(self) -> Pricer | None:
        """The registry pricer with the policy's tables behind it, so an unknown slug is estimated, not free. None without tables."""
        policy = self.policy
        if policy.fallback_prices is None and policy.default_price is None:
            return None
        return functools.partial(price_run, fallback_prices=policy.fallback_prices, default_price=policy.default_price)

    def after_answer(self, opened: Opened, outcome: RunOutcome, status: rules.Status) -> None:
        """Runs after the answer is stored (sync, in the finalize): the host's `on_answer`, then the LLM title. Neither can lose the answer."""
        answer_id = opened.turn.assistant.id
        if self.on_answer is not None:
            try:
                self.on_answer(self.message_model.objects.get(pk=answer_id), outcome)
            except Exception:  # noqa: BLE001 - a hook must not lose a stored answer
                log.exception("chat: on_answer failed for %s", opened.kind.name)
        models = parse_chain(self.policy.title_models)
        if models and status is rules.Status.DONE and not self.message_model.objects.in_thread(opened.thread).filter(
            role=rules.Role.ASSISTANT, status=rules.Status.DONE
        ).exclude(pk=answer_id).exists():
            try:
                from django_cfg.modules.django_llm.agent.chat import titles

                (self.title_job or titles.spawn)(self.thread_model, opened.thread.pk, models)
            except Exception:  # noqa: BLE001 - the fallback title stays
                log.exception("chat: could not start the title job")

    def cancel(self, thread, message_id: uuid.UUID, *, now: datetime | None = None) -> str:
        """Ask a running answer of `thread` to stop; returns its status: `cancelling` (asked; the run ends within a poll and is stored
        `cancelled` with what it said) or the status it already has (`done`, `error`, `cancelled`). A `running` row past the stale window is
        dead: it is closed as `error` here. Raises `NotFound` for no such answer of this thread."""
        store = DjangoTurnStore(thread)
        row = store.progress(message_id)
        if row is None or row.role is not rules.Role.ASSISTANT:
            raise NotFound(str(message_id))
        if row.status is not rules.Status.RUNNING:
            return row.status.value
        if self._stale(row, now or timezone.now()):
            store.reap((now or timezone.now()) - timedelta(seconds=self.policy.stale_run_seconds))
            refreshed = store.progress(message_id)
            return refreshed.status.value if refreshed is not None else rules.Status.ERROR.value
        self.cancel_signal.request(message_id)
        return "cancelling"

    def _stale(self, row: rules.Progress, now: datetime) -> bool:
        return row.created_at is not None and row.created_at < now - timedelta(seconds=self.policy.stale_run_seconds)

    def attach(self, thread, message_id: uuid.UUID, cursor: Cursor | None = None) -> AsyncIterator[str]:
        """The frames of an answer written by someone else (another tab, a reconnect), read from storage: `run` with `resume`, the
        text past `cursor.text_offset`, the steps and parts past `cursor.after`, then the closing frame once the answer is closed.
        Raises `NotFound` (sync, before anything streams) for no such answer of this thread."""
        try:
            chat_kind = kinds.get(thread.kind)
        except kinds.UnknownKind as err:
            raise NotFound(str(thread.pk)) from err
        store = DjangoTurnStore(thread)
        row = store.progress(message_id)
        if row is None or row.role is not rules.Role.ASSISTANT:
            raise NotFound(str(message_id))
        asked = self.message_model.objects.in_thread(thread).filter(role=rules.Role.USER, seq__lt=row.seq).order_by("-seq").values_list("client_id", flat=True).first()
        run = RunEvent(thread_id=str(thread.pk), message_id=str(message_id), client_id=str(asked) if asked else None, seq=row.seq, resume=True)
        return self._follow(thread, store, chat_kind, run, message_id, cursor or Cursor())

    def _follow(self, thread, store: DjangoTurnStore, chat_kind: ChatKind, run: RunEvent, message_id: uuid.UUID, cursor: Cursor) -> AsyncIterator[str]:
        policy = self.policy

        def reap() -> None:
            store.reap(timezone.now() - timedelta(seconds=policy.stale_run_seconds))

        return follow(
            lambda: store.progress(message_id), Tailer(run, cursor, chat_kind.trace_level),
            poll_s=policy.tail_poll_s, ping_s=policy.ping_s, is_stale=lambda row: self._stale(row, timezone.now()), reap=reap,
        )

    def _price_tally(self, tally: UsageTally) -> float | None:
        """The cost of a run that ended without the source's usage. Offline: this runs while the run is closing and must not wait on a catalogue fetch."""
        policy = self.policy
        pricer = self.pricer or functools.partial(price_run, offline=True, fallback_prices=policy.fallback_prices, default_price=policy.default_price)
        return pricer(tally, tally.model).cost_usd

    async def frames(self, opened: Opened, *, driver_config: DriverConfig | None = None) -> AsyncIterator[str]:
        """SSE strings of an opened turn. A `LIVE` turn (a resend of a running answer) is followed from storage, from the start."""
        turn = opened.turn
        answer = turn.assistant
        client_id = turn.user.client_id
        run = RunEvent(thread_id=str(opened.thread.pk), message_id=str(answer.id), client_id=str(client_id) if client_id else None, seq=answer.seq)
        if turn.kind is rules.TurnKind.LIVE:
            async for chunk in self._follow(opened.thread, opened.store, opened.kind, RunEvent(thread_id=run.thread_id, message_id=run.message_id, client_id=run.client_id, seq=run.seq, resume=True), answer.id, Cursor()):
                yield chunk
            return
        if turn.kind is rules.TurnKind.REPLAY:
            yield encode_sse(run, "widget", seq=1)
            for position, event in enumerate(replay_events(answer), start=2):
                yield encode_sse(event, "widget", seq=position)
            return

        store, chat_kind = opened.store, opened.kind
        out = StreamRunResult()
        recorder = Recorder(chat_kind.trace_level, guided_by=chat_kind.prompt_version) if chat_kind.trace_level > 0 else None
        sink = (self.trace_sink or MessageJsonSink)(store, answer.id) if recorder is not None else None

        def parts_of(state: RunState) -> list[dict]:
            return [{"kind": p.kind, "data": p.data, "event_seq": p.event_seq} for p in state.payloads]

        def on_flush(state: RunState) -> None:
            rules.flush(store, answer.id, text=state.text, parts=parts_of(state), tool_calls=list(out.tool_calls))
            if sink is not None and recorder is not None:
                sink.write(recorder.doc())

        def on_finish(outcome: RunOutcome) -> None:
            state = outcome.state
            status = {"done": rules.Status.DONE, "error": rules.Status.ERROR}.get(outcome.status, rules.Status.CANCELLED)
            code = (outcome.error_code if outcome.error_code in rules.ErrorCode._value2member_map_ else "failed") if status is rules.Status.ERROR else ""
            if sink is not None and recorder is not None:
                sink.flush(recorder.doc())  # before the row closes: a follower that sees the closed row finds the whole trace
            rules.finish(
                store, answer.id, status=status, text=state.text, error_code=code,
                parts=parts_of(state), tool_calls=list(out.tool_calls),
                tokens_in=state.tokens_in or 0, tokens_out=state.tokens_out or 0, cost_usd=state.cost_usd,
                latency_ms=outcome.latency_ms, model=state.model or "", prompt_version=chat_kind.prompt_version,
            )
            try:
                self.cancel_signal.clear(answer.id)
            except Exception:  # noqa: BLE001 - the flag expires on its own
                log.warning("chat: could not clear the cancel flag of %s", answer.id, exc_info=True)
            log_run(chat_kind, answer.id, opened.thread.pk, status, state, outcome, len(out.tool_calls), len(opened.attachments))
            policy = chat_kind.attachments
            if status is rules.Status.DONE and opened.attachments and policy is not None and policy.keep_days == 0 and self.attachment_store is not None:
                try:
                    self.attachment_store.expire(list(opened.attachments))  # keep_days=0: the model has seen it, nothing is kept
                except Exception:  # noqa: BLE001 - a deletion that fails is retried by `chat_reap`; the answer is already stored
                    log.warning("chat attachments: could not delete the files of a finished turn", exc_info=True)
            self.after_answer(opened, outcome, status)

        cfg = driver_config or DriverConfig(ping_s=self.policy.ping_s, max_run_s=chat_kind.limits.timeout_s)
        driver = RunDriver(cfg, lock=self.lock, hooks=RunHooks(on_flush=on_flush, on_finish=on_finish))
        model = self.model_for(chat_kind)
        prompt, history = turn.user.text, opened.history
        if chat_kind.attachments is not None and self.attachment_store is not None and (opened.attachments or any(h.get("attachments") for h in history)):
            from django_cfg.modules.django_llm.agent.chat.attachments.delivery import resolve

            prompt, history = await resolve(opened, self.attachment_store, parse_chain(self.policy.models) or chat_kind.models)
        source = kind_source(
            chat_kind, opened.deps, history, prompt, model=model, out=out,
            pricer=self.pricer or self.fallback_pricer(), price_timeout_s=self.policy.price_timeout_s,
            trace=recorder,
        )
        try:
            driven = await driver.open(
                source, run=run, key=f"chat:{opened.thread.pk}" if self.lock else None, feed=recorder,
                tally=out.usage, price_tally=self._price_tally, cancel=self._cancel_probe(answer.id),
            )
        except BaseException:
            await source.aclose()
            await _close_unrun(store, answer.id, chat_kind)
            raise
        stream = driven.frames()
        if chat_kind.detach:
            stream = detached(stream)  # the run goes on when this reader leaves; see `runtime.detach`
        try:
            async for chunk in stream:
                yield chunk
        finally:
            await stream.aclose()  # a reader that left ends the run now (stored `cancelled`), not when the collector gets to it

    def _cancel_probe(self, message_id: uuid.UUID) -> Callable[[], Any]:
        from asgiref.sync import sync_to_async

        requested = sync_to_async(self.cancel_signal.requested)

        async def probe() -> bool:
            return bool(await requested(message_id))

        return probe


def log_run(chat_kind: ChatKind, message_id: Any, thread_id: Any, status: rules.Status, state: RunState, outcome: RunOutcome, tools: int, files: int = 0) -> None:
    """One INFO line per run: ids, kind, model, tokens, cost, latency, tool count. Never the user's text, the answer or tool arguments."""
    try:
        log.info(
            "chat run kind=%s status=%s model=%s tokens_in=%d tokens_out=%d cost_usd=%s latency_ms=%d tools=%d files=%d thread=%s message=%s",
            chat_kind.name, status.value, state.model or "-", state.tokens_in or 0, state.tokens_out or 0,
            "-" if state.cost_usd is None else f"{state.cost_usd:.6f}", outcome.latency_ms or 0, tools, files, thread_id, message_id,
        )
    except Exception:  # noqa: BLE001 - a log line must not lose a stored answer
        log.exception("chat: could not write the run log line")


async def _close_unrun(store: DjangoTurnStore, message_id: Any, chat_kind: ChatKind) -> None:
    from asgiref.sync import sync_to_async

    await sync_to_async(rules.finish)(store, message_id, status=rules.Status.ERROR, text="", error_code="failed", prompt_version=chat_kind.prompt_version)
