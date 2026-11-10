"""A product-free run driver: one assistant turn as a widget SSE stream.

Everything every host of `@djangocfg/widget-assistant` had to write around the agent
loop, with no model, table or product in it:

* **ping**: an SSE comment every ``ping_s`` of silence (the client treats 45 s of
  silence as a lost stream);
* **wall-clock cap**: ``max_run_s`` ends the run with ``error{code: "timeout"}``;
* **shielded finalize**: whatever ends the run (done, error, timeout, the browser
  closing the connection, an abort) the host's ``on_finish`` runs exactly once, in a
  task the cancellation cannot reach, so a dropped client still saves the answer;
* **run lock per key**: ``acquire(key)`` before anything is stored or streamed, one run
  in flight per thread; a held lock raises ``RunBusy`` (the view answers ``409 busy``);
  the lock is released after ``on_finish``;
* **abort**: ``DrivenRun.abort()`` ends the run as ``cancelled`` (no terminal frame: the
  widget reconciles from storage and reads ``cancelled``).

What it does not do: store anything (hooks do), replay a stored answer by ``client_id``
(needs storage: the host's), pick a model or tools (the host builds the agent), know a
thread or a user (the lock ``key`` is an opaque string).

Use::

    driver = RunDriver(DriverConfig(max_run_s=60), lock=CacheRunLock(), hooks=RunHooks(
        on_flush=save_partial,        # about once a second and after each payload
        on_finish=save_final,         # exactly once, with the RunOutcome
    ))
    try:
        run = await driver.open(
            agent_source(agent=agent, deps=deps, user_message=text, message_history=history),
            run=RunEvent(thread_id=str(thread.pk), message_id=str(answer.pk), client_id=cid, seq=answer.seq),
            key=f"chat:{thread.pk}",
        )
    except RunBusy:
        return problem("busy", ..., 409)
    return StreamingHttpResponse(run.frames(), content_type="text/event-stream", headers=SSE_HEADERS)

The source is any async iterator of bus events (``bus/events.py``), so a host that
drives ``agent.run_stream_events`` itself can feed the driver too. ``RunEvent`` from the
source is ignored (the driver sends its own ``run`` first); tool events reach
``on_event`` (to store them for replay) and are never put on the wire.
"""

from __future__ import annotations

import asyncio
import inspect
import logging
import time
import uuid
from collections.abc import AsyncIterator, Callable, Mapping
from dataclasses import dataclass, field
from typing import Any, Literal, Protocol

from django_cfg.modules.django_llm.agent.bus.events import (
    PING,
    SSE_HEADERS,
    DoneEvent,
    ErrorEvent,
    ReasoningDeltaEvent,
    ReasoningEndEvent,
    RunEvent,
    StatusEvent,
    TextDeltaEvent,
    TraceStepEvent,
    UIPayloadEvent,
    encode_sse,
)
from django_cfg.modules.django_llm.agent.runtime.errors import (
    DEFAULT_ERROR_MESSAGES,
    describe,
    error_code_for,
    is_provider_failure,
)

logger = logging.getLogger(__name__)

__all__ = [
    "CacheRunLock",
    "DriverConfig",
    "DrivenRun",
    "InMemoryRunLock",
    "PING",
    "RunBusy",
    "RunFeed",
    "RunDriver",
    "RunHooks",
    "RunLock",
    "RunOutcome",
    "RunState",
    "SSE_HEADERS",
    "agent_source",
]

Status = Literal["done", "error", "cancelled"]


class RunFeed(Protocol):
    """Frames that do not come from the source: a side channel the run fills while the source is busy (the answer's trace).

    The driver wakes on ``wake``, sends what ``drain()`` returns, and calls ``finish`` once when the run ends (before the
    last ``drain``), so a feed can add its closing frames. ``Recorder`` (``agent/trace``) is one.
    """

    wake: asyncio.Event

    def drain(self) -> list[Any]: ...

    def finish(self, status: str, error_code: str = "", *, tokens_in: int | None = None, tokens_out: int | None = None, cost_usd: float | None = None, model: str | None = None) -> None: ...


class RunBusy(Exception):
    """The run lock for this key is held: another run is in flight. Answer ``409 busy``."""


# ── lock ─────────────────────────────────────────────────────────────────────────────


class RunLock(Protocol):
    """One run in flight per key. ``release`` frees the lock only for the token that took it."""

    async def acquire(self, key: str, token: str, ttl_s: float) -> bool: ...

    async def release(self, key: str, token: str) -> None: ...


class CacheRunLock:
    """A lock on Django's cache (``cache.add`` is atomic on Redis and Memcached).

    Shared between workers when the cache is. The TTL is the safety net for a killed
    worker; the owner token stops a slow run from freeing a lock that has since been
    taken by another. ``release`` is get-then-delete, not atomic: after a TTL expiry the
    window is a few microseconds, and the cost is one extra run, not corruption.

    Pass ``cache=`` (any object with ``add``/``get``/``delete``) or leave it for
    ``django.core.cache.cache``. Calls go through ``sync_to_async`` so a database or
    file cache backend is safe on an ASGI loop.
    """

    def __init__(self, cache: Any = None, prefix: str = "agent-run-lock:") -> None:
        self._cache = cache
        self._prefix = prefix

    def _backend(self) -> Any:
        if self._cache is not None:
            return self._cache
        from django.core.cache import cache  # lazy: the plane never imports Django at load

        return cache

    async def acquire(self, key: str, token: str, ttl_s: float) -> bool:
        from asgiref.sync import sync_to_async

        return bool(await sync_to_async(self._backend().add)(self._prefix + key, token, int(max(1, ttl_s))))

    async def release(self, key: str, token: str) -> None:
        from asgiref.sync import sync_to_async

        def _release() -> None:
            backend = self._backend()
            if backend.get(self._prefix + key) == token:
                backend.delete(self._prefix + key)

        await sync_to_async(_release)()


class InMemoryRunLock:
    """A process-local lock (tests, single-process dev). Does not span workers."""

    def __init__(self) -> None:
        self._held: dict[str, tuple[str, float]] = {}

    async def acquire(self, key: str, token: str, ttl_s: float) -> bool:
        now = time.monotonic()
        held = self._held.get(key)
        if held is not None and held[1] > now:
            return False
        self._held[key] = (token, now + ttl_s)
        return True

    async def release(self, key: str, token: str) -> None:
        held = self._held.get(key)
        if held is not None and held[0] == token:
            del self._held[key]


# ── configuration, state, hooks ──────────────────────────────────────────────────────


@dataclass(frozen=True)
class DriverConfig:
    ping_s: float = 15.0
    """Seconds of silence before an SSE ``: ping`` comment. Keep it under the client's idle limit (45 s)."""

    max_run_s: float | None = 60.0
    """Wall-clock cap of one run; ``None`` disables it. Past it: ``error{code: "timeout"}``."""

    flush_s: float = 1.0
    """Minimum seconds between ``on_flush`` calls while text streams (a payload flushes at once)."""

    lock_ttl_s: float | None = None
    """Run lock lifetime. Default: ``max_run_s`` + 30 s (or 300 s without a cap)."""

    error_messages: Mapping[str, str] = field(default_factory=lambda: dict(DEFAULT_ERROR_MESSAGES))
    """The ``error.message`` per code, for errors the driver raises itself (timeout, a crashed source)."""

    @property
    def effective_lock_ttl_s(self) -> float:
        if self.lock_ttl_s is not None:
            return self.lock_ttl_s
        return (self.max_run_s + 30.0) if self.max_run_s else 300.0


@dataclass
class RunState:
    """What the run has produced so far; passed to ``on_event`` and ``on_flush``."""

    texts: list[str] = field(default_factory=list)
    payloads: list[UIPayloadEvent] = field(default_factory=list)
    tokens_in: int | None = None
    tokens_out: int | None = None
    cost_usd: float | None = None
    finish_reason: str | None = None
    model: str | None = None  # the slug that served the run, when the source reports it
    started_at: float = field(default_factory=time.monotonic)

    @property
    def text(self) -> str:
        return "".join(self.texts)


@dataclass(frozen=True)
class RunOutcome:
    """How the run ended, handed to ``on_finish`` once."""

    status: Status
    state: RunState
    error_code: str = ""
    error_message: str = ""
    retryable: bool = True
    latency_ms: int = 0

    @property
    def text(self) -> str:
        return self.state.text


Hook = Callable[..., Any]  # sync or async; a sync hook runs in a thread (ORM calls are safe)


@dataclass
class RunHooks:
    """Optional callbacks. A hook is a plain function or a coroutine function."""

    on_event: Hook | None = None
    """``(event, state)`` for every event the source yields, before it is forwarded (collect tool calls here)."""

    on_flush: Hook | None = None
    """``(state)`` about every ``flush_s`` while text streams, and after each ``ui_payload``: save the partial answer."""

    on_finish: Hook | None = None
    """``(outcome)`` exactly once per run, shielded from cancellation: store the final answer, count tokens."""


async def _call(hook: Hook | None, *args: Any) -> None:
    if hook is None:
        return
    if inspect.iscoroutinefunction(hook):
        await hook(*args)
        return
    from asgiref.sync import sync_to_async

    result = await sync_to_async(hook)(*args)
    if inspect.isawaitable(result):
        await result


# ── driver ───────────────────────────────────────────────────────────────────────────


class RunDriver:
    def __init__(
        self,
        config: DriverConfig | None = None,
        *,
        lock: RunLock | None = None,
        hooks: RunHooks | None = None,
    ) -> None:
        self.config = config or DriverConfig()
        self.lock = lock
        self.hooks = hooks or RunHooks()

    async def open(
        self,
        source: AsyncIterator[Any] | Callable[[], AsyncIterator[Any]],
        *,
        run: RunEvent,
        key: str | None = None,
        feed: RunFeed | None = None,
    ) -> DrivenRun:
        """Take the run lock for ``key`` (if the driver has a lock and a key) and return the run.

        Raises ``RunBusy`` when the lock is held. ``source`` may be a factory, called only
        once the lock is taken, so a refused run builds no agent. ``feed`` adds frames from a side channel (see ``RunFeed``).
        """
        token = uuid.uuid4().hex
        if self.lock is not None and key is not None:
            if not await self.lock.acquire(key, token, self.config.effective_lock_ttl_s):
                raise RunBusy(key)
        iterator = source() if callable(source) and not hasattr(source, "__aiter__") else source
        return DrivenRun(self, iterator, run, key if self.lock is not None else None, token, feed)


class DrivenRun:
    """One opened run. ``frames()`` is the response body; call it once."""

    def __init__(self, driver: RunDriver, source: AsyncIterator[Any], run: RunEvent, key: str | None, token: str, feed: RunFeed | None = None) -> None:
        self._driver = driver
        self._source = source
        self._run = run
        self._key = key
        self._token = token
        self._feed = feed
        self._started = False
        self._abort = asyncio.Event()
        self.finished = asyncio.Event()
        self.outcome: RunOutcome | None = None

    def abort(self) -> None:
        """End the run as ``cancelled``. No terminal frame is sent: the client reconciles from storage."""
        self._abort.set()

    async def release(self) -> None:
        """Free the lock of a run whose ``frames()`` will never be iterated (the response was not built)."""
        if self._started:
            return
        self._started = True
        await self._release_lock()
        close = getattr(self._source, "aclose", None)
        if close is not None:
            await close()
        self.finished.set()

    async def _release_lock(self) -> None:
        lock = self._driver.lock
        if lock is not None and self._key is not None:
            try:
                await lock.release(self._key, self._token)
            except Exception:  # noqa: BLE001 - the TTL frees it
                logger.exception("run driver: could not release the run lock %s", self._key)

    async def frames(self) -> AsyncIterator[str]:
        if self._started:
            raise RuntimeError("DrivenRun.frames() can be iterated once")
        self._started = True
        cfg = self._driver.config
        hooks = self._driver.hooks
        state = RunState()
        started = time.monotonic()
        deadline = started + cfg.max_run_s if cfg.max_run_s else None
        iterator = self._source.__aiter__()
        pending: asyncio.Future | None = None
        abort_wait = asyncio.ensure_future(self._abort.wait())
        status: Status | None = None
        code = ""
        message = ""
        retryable = True
        last_sent = started
        last_flush = started

        feed = self._feed
        wake: asyncio.Future | None = None
        position = 0  # the SSE `id:` of the next frame: the place a client resumes from

        def frame(event: Any) -> str | None:
            nonlocal position
            position += 1
            if isinstance(event, TraceStepEvent):
                event.event_seq = position
            return encode_sse(event, "widget", seq=position)

        def feed_frames() -> list[str]:
            if feed is None:
                return []
            try:
                return [frame(ev) or "" for ev in feed.drain()]
            except Exception:  # noqa: BLE001 - a side channel must not kill the run
                logger.exception("run driver: the feed failed")
                return []

        try:
            yield frame(self._run) or ""
            last_sent = time.monotonic()
            while True:
                if self._abort.is_set():
                    status = "cancelled"
                    break
                now = time.monotonic()
                if deadline is not None and now >= deadline:
                    raise TimeoutError("run exceeded its wall-clock cap")
                for chunk in feed_frames():
                    last_sent = time.monotonic()
                    yield chunk
                if pending is None:
                    pending = asyncio.ensure_future(iterator.__anext__())
                if feed is not None and wake is None:
                    wake = asyncio.ensure_future(feed.wake.wait())
                wait_for = cfg.ping_s - (now - last_sent)
                if deadline is not None:
                    wait_for = min(wait_for, deadline - now)
                waiting = {pending, abort_wait} | ({wake} if wake is not None else set())
                done, _ = await asyncio.wait(waiting, timeout=max(0.001, wait_for), return_when=asyncio.FIRST_COMPLETED)
                if wake is not None and wake in done:
                    wake = None
                if pending not in done:
                    if self._abort.is_set():
                        continue
                    if time.monotonic() - last_sent >= cfg.ping_s:
                        last_sent = time.monotonic()
                        yield PING
                    continue
                try:
                    event = pending.result()
                except StopAsyncIteration:
                    pending = None
                    break
                pending = None

                if isinstance(event, RunEvent):
                    continue  # the driver owns the first frame
                try:
                    await _call(hooks.on_event, event, state)
                except Exception:  # noqa: BLE001 - a host hook must not kill the run
                    logger.exception("run driver: on_event failed")

                if isinstance(event, TextDeltaEvent):
                    state.texts.append(event.delta)
                    last_sent = time.monotonic()
                    yield frame(event) or ""
                    if last_sent - last_flush >= cfg.flush_s:
                        last_flush = last_sent
                        await self._flush(state)
                elif isinstance(event, UIPayloadEvent):
                    state.payloads.append(event)
                    last_sent = time.monotonic()
                    yield frame(event) or ""
                    last_flush = last_sent
                    await self._flush(state)
                elif isinstance(event, (StatusEvent, ReasoningDeltaEvent, ReasoningEndEvent)):
                    last_sent = time.monotonic()
                    yield frame(event) or ""
                elif isinstance(event, DoneEvent):
                    state.tokens_in = event.tokens_input
                    state.tokens_out = event.tokens_output
                    state.cost_usd = event.cost_usd
                    state.finish_reason = event.finish_reason
                    state.model = event.model
                elif isinstance(event, ErrorEvent):
                    status = "error"
                    code = event.code if event.code in cfg.error_messages else "failed"
                    message = event.error or cfg.error_messages.get(code, "")
                    retryable = event.retryable
                    break
                # anything else (tool_call, tool_result, directive, ...) has no wire frame: dropped
            if status is None:
                status = "done"
        except (asyncio.CancelledError, GeneratorExit):
            status = "cancelled"
            raise
        except Exception as exc:  # noqa: BLE001 - the stream ends with one `error` frame, the cause goes to the log
            if isinstance(exc, TimeoutError):
                logger.warning("run driver: %s", exc)
            elif is_provider_failure(exc):
                logger.warning("run driver: the run failed: %s", describe(exc))
            else:
                logger.exception("run driver: the run failed")
            status = "error"
            code = error_code_for(exc)
            message = cfg.error_messages.get(code, "")
            retryable = True
        finally:
            if wake is not None:
                wake.cancel()
            if feed is not None:
                try:
                    feed.finish(status or "cancelled", code, tokens_in=state.tokens_in, tokens_out=state.tokens_out, cost_usd=state.cost_usd, model=state.model)
                except Exception:  # noqa: BLE001
                    logger.exception("run driver: the feed could not close")
            outcome = RunOutcome(
                status=status or "cancelled",
                state=state,
                error_code=code,
                error_message=message,
                retryable=retryable,
                latency_ms=int((time.monotonic() - started) * 1000),
            )
            # Shielded: cancellation of this generator cannot interrupt the cleanup or the host's
            # on_finish, which therefore runs exactly once whatever ended the run.
            await asyncio.shield(asyncio.ensure_future(self._finalize(outcome, pending, abort_wait, iterator)))

        outcome = self.outcome
        assert outcome is not None
        if outcome.status != "cancelled":
            for chunk in feed_frames():
                yield chunk
        if outcome.status == "done":
            yield frame(
                DoneEvent(
                    tokens_input=state.tokens_in,
                    tokens_output=state.tokens_out,
                    cost_usd=state.cost_usd,
                    finish_reason=state.finish_reason or "stop",
                )
            ) or ""
        elif outcome.status == "error":
            yield frame(ErrorEvent(error=outcome.error_message, code=outcome.error_code, retryable=outcome.retryable)) or ""
        # cancelled (abort): no terminal frame

    async def _flush(self, state: RunState) -> None:
        try:
            await _call(self._driver.hooks.on_flush, state)
        except Exception:  # noqa: BLE001 - mid-run saves are best effort; finalize is the authority
            logger.exception("run driver: on_flush failed")

    async def _finalize(
        self,
        outcome: RunOutcome,
        pending: asyncio.Future | None,
        abort_wait: asyncio.Future,
        iterator: Any,
    ) -> None:
        try:
            abort_wait.cancel()
            if pending is not None and not pending.done():
                pending.cancel()
            if pending is not None:
                await asyncio.wait({pending})  # the iterator must be idle before it is closed
                if not pending.cancelled():
                    pending.exception()  # mark a late source error as retrieved
            close = getattr(iterator, "aclose", None)
            if close is not None:
                try:
                    await close()
                except Exception:  # noqa: BLE001
                    logger.exception("run driver: closing the source failed")
            self.outcome = outcome
            try:
                await _call(self._driver.hooks.on_finish, outcome)
            except Exception:  # noqa: BLE001 - the host's reaper closes a row left `running`
                logger.exception("run driver: on_finish failed")
        finally:
            await self._release_lock()
            self.finished.set()


def agent_source(
    *,
    agent: Any,
    deps: Any,
    user_message: str | None,
    message_history: list | None = None,
    log_prefix: str = "Agent",
    **options: Any,
) -> AsyncIterator[Any]:
    """The widget-dialect event stream of a pydantic-ai agent: ``stream_agent_run(wire="widget")``.

    ``options`` are ``stream_agent_run``'s: ``limits``, ``payload_types``, ``phase_for_tool``.
    Imported lazily: pydantic-ai loads only when a run starts.
    """
    from django_cfg.modules.django_llm.agent.runtime.streaming import StreamRunResult, stream_agent_run

    return stream_agent_run(
        agent=agent,
        deps=deps,
        user_message=user_message,
        message_history=message_history or [],
        deferred_tool_results=None,
        is_admin_chat=False,
        out=StreamRunResult(),
        log_prefix=log_prefix,
        wire="widget",
        **options,
    )
