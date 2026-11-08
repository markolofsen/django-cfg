"""`ChatService`: sessions, the daily cap, a turn's history and its stream, over the host's concrete models.

    service = ChatService(Thread, ChatPolicy(messages_per_day=200))
    opened = service.begin(user, thread, text, client_id, turn_context)      # may refuse; nothing streamed yet
    if opened.turn.kind is TurnKind.BUSY: ...                                # answer 409
    return StreamingHttpResponse(service.frames(opened), content_type="text/event-stream", headers=SSE_HEADERS)

`begin` is sync (ORM) and raises `ServiceUnavailable`, `RateLimited`, `InvalidContext`, `InvalidTurn`, `Busy`, `NotFound`. `frames` is an async
iterator of SSE strings: `run` first, the answer stored (flushed while streaming, closed once, shielded) before the
`done`/`error` frame leaves. Tests replace `model_factory` (a scripted model) and `pricer`.
"""

from __future__ import annotations

import functools
import logging
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
from django_cfg.modules.django_llm.agent.chat import kind as kinds
from django_cfg.modules.django_llm.agent.chat import turn as rules
from django_cfg.modules.django_llm.agent.chat.errors import InvalidContext, InvalidKind, NotFound, RateLimited, ServiceUnavailable
from django_cfg.modules.django_llm.agent.chat.kind import ChatKind, KindScope
from django_cfg.modules.django_llm.agent.chat.runner import build_model, kind_source, replay_events
from django_cfg.modules.django_llm.agent.chat.store import DjangoTurnStore
from django_cfg.modules.django_llm.agent.runtime.cost import Pricer, PriceRow, price_run
from django_cfg.modules.django_llm.agent.runtime.driver import DriverConfig, RunDriver, RunHooks, RunLock, RunOutcome, RunState
from django_cfg.modules.django_llm.agent.runtime.streaming import StreamRunResult


log = logging.getLogger(__name__)

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
    models: str | tuple[str, ...] | None = None  # overrides every kind's chain (ops switch; an env string "a/b, c/d" is parsed); None = each kind's own
    price_timeout_s: float = 3.0
    check_quota: QuotaCheck | None = None  # replaces the built-in daily message cap (`messages_per_day` is then ignored)
    available: Callable[[], bool] | None = None  # False = a kill switch or a spent budget: a send is refused with `ServiceUnavailable` before anything is stored
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
    ):
        """`policy` may be a `ChatPolicy` or a zero-argument callable returning one, read on every use (rates from settings,
        swapped in tests). `resolve_thread(service, actor, id)` is the tenancy rule (default: the owner's thread); `on_answer`
        runs after each stored answer; `title_job(thread_model, thread_id, models)` runs the LLM title off the request (default:
        a daemon thread; a host may enqueue a job instead). `on_ui_payload_accepted(answer, index, part)` runs after `ack_part`
        stored a browser's verdict on a part (`{"applied": bool, "reason": str}` under `part["ack"]`)."""
        self.thread_model = thread_model
        self.message_model = thread_model.messages.rel.related_model
        self._policy = policy or ChatPolicy()
        self.model_factory = model_factory
        self.pricer = pricer
        self.lock = lock
        self.resolve_thread = resolve_thread or owners_thread
        self.on_answer = on_answer
        self.title_job = title_job
        self.on_ui_payload_accepted = on_ui_payload_accepted

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

        Tool calls are replayed only for the latest `limits.replay_tool_calls_of` answers; older ones are text.
        """
        rows = self.message_model.objects.window(thread, chat_kind.history_window, before_seq=before_seq)
        keep = chat_kind.limits.replay_tool_calls_of
        answers = [m for m in rows if m.role == rules.Role.ASSISTANT]
        replay = {m.pk for m in (answers[-keep:] if keep else [])}
        out: list[dict] = []
        for m in rows:
            if m.role == rules.Role.USER and not m.text:
                continue  # a hidden feedback turn has no words: nothing to replay (providers refuse an empty user message)
            item: dict = {"role": m.role, "content": m.text}
            if m.pk in replay:
                calls = [c for c in (m.tool_calls or []) if isinstance(c, dict) and c.get("output") is not None]
                if calls:
                    item["tool_calls"] = calls
            out.append(item)
        return out

    def page(self, thread, *, limit: int = 50, before_seq: int | None = None) -> list:
        """The transcript for a surface: the newest `limit` messages (older than `before_seq` when paging back), oldest first."""
        qs = self.message_model.objects.in_thread(thread)
        if before_seq is not None:
            qs = qs.filter(seq__lt=before_seq)
        return list(qs.order_by("-seq")[:limit])[::-1]

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
        policy = self.policy
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

    def begin(self, owner, thread, text: str, client_id: uuid.UUID | None, turn_context: dict | None = None, *, now: datetime | None = None) -> Opened:
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
        if not resend:
            self.check_quota(owner, now, thread)  # a resend is served from storage and costs nothing
        deps = chat_kind.make_deps(KindScope(user=owner, thread_id=thread.pk, kind=chat_kind.name, context=context, thread_context=thread.context, thread=thread))
        store = DjangoTurnStore(thread)
        started = rules.start(store, text, client_id, now=now, max_chars=(constraints.max_text_chars if constraints is not None and constraints.max_text_chars is not None else self.policy.max_text_chars), stale_after_s=self.policy.stale_run_seconds, allow_empty=chat_kind.allows_empty_text(turn_context))
        if started.runs_model:
            self.remember(thread, context)  # the next turn may omit what this one said (e.g. a document sent once per hash)
        if started.kind is not rules.TurnKind.BUSY and not thread.title and started.user.text:
            self.thread_model.objects.filter(pk=thread.pk, title="").update(title=chat_kind.title_of(started.user.text)[:200])
        prior = self.history_for_model(thread, chat_kind, before_seq=started.user.seq) if started.runs_model else []
        return Opened(thread, chat_kind, started, deps, prior, store)

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

    async def frames(self, opened: Opened, *, driver_config: DriverConfig | None = None) -> AsyncIterator[str]:
        """SSE strings of an opened turn (not `BUSY`: the caller answers that with a conflict)."""
        turn = opened.turn
        answer = turn.assistant
        client_id = turn.user.client_id
        run = RunEvent(thread_id=str(opened.thread.pk), message_id=str(answer.id), client_id=str(client_id) if client_id else None, seq=answer.seq)
        if turn.kind is rules.TurnKind.REPLAY:
            yield encode_sse(run, "widget")
            for event in replay_events(answer):
                yield encode_sse(event, "widget")
            return

        store, chat_kind = opened.store, opened.kind
        out = StreamRunResult()

        def parts_of(state: RunState) -> list[dict]:
            return [{"kind": p.kind, "data": p.data} for p in state.payloads]

        def on_flush(state: RunState) -> None:
            rules.flush(store, answer.id, text=state.text, parts=parts_of(state), tool_calls=list(out.tool_calls))

        def on_finish(outcome: RunOutcome) -> None:
            state = outcome.state
            status = {"done": rules.Status.DONE, "error": rules.Status.ERROR}.get(outcome.status, rules.Status.CANCELLED)
            code = (outcome.error_code if outcome.error_code in rules.ErrorCode._value2member_map_ else "failed") if status is rules.Status.ERROR else ""
            rules.finish(
                store, answer.id, status=status, text=state.text, error_code=code,
                parts=parts_of(state), tool_calls=list(out.tool_calls),
                tokens_in=state.tokens_in or 0, tokens_out=state.tokens_out or 0, cost_usd=state.cost_usd,
                latency_ms=outcome.latency_ms, model=state.model or "", prompt_version=chat_kind.prompt_version,
            )
            log_run(chat_kind, answer.id, opened.thread.pk, status, state, outcome, len(out.tool_calls))
            self.after_answer(opened, outcome, status)

        cfg = driver_config or DriverConfig(ping_s=self.policy.ping_s, max_run_s=chat_kind.limits.timeout_s)
        driver = RunDriver(cfg, lock=self.lock, hooks=RunHooks(on_flush=on_flush, on_finish=on_finish))
        model = self.model_for(chat_kind)
        source = kind_source(
            chat_kind, opened.deps, opened.history, turn.user.text, model=model, out=out,
            pricer=self.pricer or self.fallback_pricer(), price_timeout_s=self.policy.price_timeout_s,
        )
        try:
            driven = await driver.open(source, run=run, key=f"chat:{opened.thread.pk}" if self.lock else None)
        except BaseException:
            await source.aclose()
            await _close_unrun(store, answer.id, chat_kind)
            raise
        async for chunk in driven.frames():
            yield chunk


def log_run(chat_kind: ChatKind, message_id: Any, thread_id: Any, status: rules.Status, state: RunState, outcome: RunOutcome, tools: int) -> None:
    """One INFO line per run: ids, kind, model, tokens, cost, latency, tool count. Never the user's text, the answer or tool arguments."""
    try:
        log.info(
            "chat run kind=%s status=%s model=%s tokens_in=%d tokens_out=%d cost_usd=%s latency_ms=%d tools=%d thread=%s message=%s",
            chat_kind.name, status.value, state.model or "-", state.tokens_in or 0, state.tokens_out or 0,
            "-" if state.cost_usd is None else f"{state.cost_usd:.6f}", outcome.latency_ms or 0, tools, thread_id, message_id,
        )
    except Exception:  # noqa: BLE001 - a log line must not lose a stored answer
        log.exception("chat: could not write the run log line")


async def _close_unrun(store: DjangoTurnStore, message_id: Any, chat_kind: ChatKind) -> None:
    from asgiref.sync import sync_to_async

    await sync_to_async(rules.finish)(store, message_id, status=rules.Status.ERROR, text="", error_code="failed", prompt_version=chat_kind.prompt_version)
