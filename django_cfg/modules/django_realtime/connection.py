"""One socket's lifecycle: origin, auth window, `hello`, sub/unsub, ping, limits, kicks, close codes.

The event loop never touches the ORM. `authenticate` and each topic's `allow` run through the connection's hook
runner: by default `HookRunner`, a process-wide pool of `RealtimeConfig.db_threads` threads
(`sync_to_async(thread_sensitive=False, executor=...)`; the default thread-sensitive path would funnel every socket
of the process through one thread), each call between two `close_old_connections()`. Tests inject
`InlineHookRunner`. A hook slower than `hook_timeout` answers `sub_err timeout` (allow) or closes 4500 (auth).

Auth window: the socket attaches to the hub first (a kick during the handshake is kept and applied), then waits up
to `auth_timeout` for the first frame. `auth` with a token authenticates with it; `auth` without one, or any other
first frame (a `sub`), settles on the handshake's own credentials (cookies, headers), and a `sub` is processed right
after `hello`. With no first frame, `hello` follows when the handshake identified a user or some topic admits
visitors, else 4408. A credential that was presented and refused closes 4419; no credential and no topic for
visitors closes 4401. `hello.cid` is bound to the identity (`auth.issue_cid`), so a request cannot borrow it.

Per subscription the client gets `sub_ok`, then the replay, then live `msg`s. A replay that would not fit the send
queue (less `REPLAY_MARGIN`) is not sent: `sub_ok recovered:false`. Every `reauth_interval` the credential is
re-checked and every subscription's `allow` re-run; a refused one is dropped with `sub_err forbidden`.

Receiving and sending are separate tasks; the send queue is bounded and a client that falls behind is closed with
1013 (it reconnects and replays). Liveness is uvicorn's protocol ping; the client's `ping` frames get `pong`.
"""

from __future__ import annotations

import asyncio
import logging
import secrets
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, Any, Callable, Dict, List, Optional

from django_cfg.models.django.realtime import REPLAY_MARGIN

from .auth import AuthFailed, Identity, authenticate, issue_cid, origin_allowed
from .backends import Entry, format_offset, parse_offset
from .protocol import (
    TOPIC_RE,
    AuthFrame,
    Close,
    Error,
    Hello,
    Msg,
    PingFrame,
    Pong,
    ProtocolError,
    SubErr,
    SubFrame,
    SubOk,
    UnsubFrame,
    encode,
    parse_client_frame,
)
from .registry import Registry, UnknownTopic
from .registry import registry as default_registry

if TYPE_CHECKING:
    from django_cfg.models.django.realtime import RealtimeConfig

    from .hub import Hub

logger = logging.getLogger(__name__)

_CLOSE_FLUSH = 1.0

# ---------------------------------------------------------------- hooks

_pool_lock = threading.Lock()
_pool: Optional[ThreadPoolExecutor] = None


def hook_pool(size: int) -> ThreadPoolExecutor:
    """The process's hook threads, created on first use with `size` workers."""
    global _pool
    if _pool is None:
        with _pool_lock:
            if _pool is None:
                _pool = ThreadPoolExecutor(max_workers=size, thread_name_prefix="realtime-db")
    return _pool


def _guarded(fn: Callable[..., Any], *args: Any) -> Any:
    from django.db import close_old_connections

    close_old_connections()
    try:
        return fn(*args)
    finally:
        close_old_connections()


class HookRunner:
    """Runs a sync hook in the pool; asyncio.TimeoutError after `timeout` (the thread then finishes alone)."""

    def __init__(self, threads: int) -> None:
        self.threads = threads

    async def __call__(self, fn: Callable[..., Any], *args: Any, timeout: float) -> Any:
        from asgiref.sync import sync_to_async

        call = sync_to_async(_guarded, thread_sensitive=False, executor=hook_pool(self.threads))
        return await asyncio.wait_for(call(fn, *args), timeout)


class InlineHookRunner:
    """Tests: hooks run thread-sensitively with no connection handling. Driven from a sync test through
    `async_to_sync`, that is the test's own thread, inside its transaction, so TestCase data is visible."""

    async def __call__(self, fn: Callable[..., Any], *args: Any, timeout: float) -> Any:
        from asgiref.sync import sync_to_async

        return await asyncio.wait_for(sync_to_async(fn, thread_sensitive=True)(*args), timeout)


# ---------------------------------------------------------------- one subscription

class Subscription:
    """A topic on one socket. Pending until its replay is queued; live entries are held back until then."""

    def __init__(self, conn: "Connection", topic: str, sub_id: int) -> None:
        self.conn = conn
        self.topic = topic
        self.id = sub_id
        self.pending = True
        self.closed = False
        self.offset: Optional[str] = None  # the last offset this client has (head or last sent)
        self._held: List[Entry] = []

    def deliver(self, entry: Entry) -> None:
        if self.closed:
            return
        if entry.origin_cid is not None and entry.origin_cid == self.conn.cid:
            self._advance(entry.offset)  # the sender already knows; the next replay must not resend it
            return
        if self.pending:
            self._held.append(entry)
            if len(self._held) > self.conn.config.send_queue:
                self.conn.close(Close.TRY_AGAIN)
            return
        self.emit(entry)

    def _advance(self, offset: str) -> bool:
        """Move to `offset`; False when it is not newer. A new epoch means history was lost: tell the client."""
        new, old = parse_offset(offset), parse_offset(self.offset) if self.offset else None
        if new is None:
            return False
        if old is not None and new[0] == old[0] and new[1] <= old[1]:
            return False
        self.offset = offset
        if old is not None and new[0] != old[0]:
            # History was lost: refetch, then this entry follows as the first of the new epoch.
            before = format_offset(new[0], max(new[1] - 1, 0))
            self.conn.enqueue(SubOk(id=self.id, topic=self.topic, offset=before, recovered=False))
        return True

    def emit(self, entry: Entry) -> None:
        if self._advance(entry.offset):
            self.conn.enqueue(Msg(topic=entry.topic, offset=entry.offset, data=entry.data, origin_cid=entry.origin_cid))

    def go_live(self) -> None:
        self.pending = False
        held, self._held = self._held, []
        for entry in held:
            self.deliver(entry)


class _CloseSignal:
    __slots__ = ("code",)

    def __init__(self, code: int) -> None:
        self.code = code


class _Disconnected(Exception):
    pass


def _consume(future: asyncio.Future) -> None:
    """Retrieve an abandoned future's exception so asyncio does not report it as never retrieved."""
    if not future.cancelled():
        future.exception()


# ---------------------------------------------------------------- the socket

class Connection:
    def __init__(self, scope, receive, send, *, hub: "Hub", config: "RealtimeConfig",
                 registry: Optional[Registry] = None, hooks: Optional[Callable[..., Any]] = None) -> None:
        self.scope = scope
        self._receive = receive
        self._send = send
        self.hub = hub
        self.backend = hub.backend
        self.config = config
        self.registry = registry or default_registry
        self.hooks = hooks or HookRunner(config.db_threads)
        self.cid = secrets.token_hex(8)  # provisional, for log lines; `hello` carries the identity-bound one
        self.identity: Optional[Identity] = None
        self._early_kicks: Optional[List[Dict[str, Any]]] = []
        self.subs: Dict[str, Subscription] = {}
        self._tasks: Dict[str, asyncio.Task] = {}
        self._background: set = set()
        self._out: asyncio.Queue = asyncio.Queue()
        self._closing = False
        self._close_code: Optional[int] = None
        self._limit_key: Optional[str] = None
        self._window_start = 0.0
        self._window_frames = 0
        self._stats = {"in": 0, "out": 0, "peak_subs": 0}

    # -- outbound ---------------------------------------------------------------------------------

    def enqueue(self, frame) -> None:
        if self._closing:
            return
        if self._out.qsize() >= self.config.send_queue:
            self.close(Close.TRY_AGAIN)
            return
        self._out.put_nowait(encode(frame))

    def close(self, code: int) -> None:
        """Close with `code` as soon as possible: queued frames are dropped, the close frame goes next."""
        if self._closing:
            return
        self._closing = True
        self._close_code = int(code)
        while not self._out.empty():
            self._out.get_nowait()
        self._out.put_nowait(_CloseSignal(int(code)))

    async def _writer(self) -> None:
        try:
            while True:
                item = await self._out.get()
                if isinstance(item, _CloseSignal):
                    await self._send({"type": "websocket.close", "code": item.code})
                    return
                await self._send({"type": "websocket.send", "text": item})
                self._stats["out"] += 1
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001 - the peer is gone; nothing left to write to
            return

    # -- inbound ----------------------------------------------------------------------------------

    def _flooding(self) -> bool:
        now = time.monotonic()
        if now - self._window_start >= 1.0:
            self._window_start, self._window_frames = now, 0
        self._window_frames += 1
        return self._window_frames > self.config.max_frames_per_second

    async def _receive_text(self) -> str:
        while True:
            message = await self._receive()
            kind = message.get("type")
            if kind == "websocket.disconnect":
                if self._close_code is None:
                    self._close_code = message.get("code", 1005)
                raise _Disconnected()
            if kind != "websocket.receive":
                continue
            self._stats["in"] += 1
            if self._flooding():
                self.close(Close.LIMIT)
                raise _Disconnected()
            text = message.get("text")
            if text is None:
                self.enqueue(Error(code="bad_frame", detail="binary frames are not supported"))
                continue
            if len(text) > self.config.max_frame_bytes or len(text.encode("utf-8")) > self.config.max_frame_bytes:
                self.enqueue(Error(code="too_large", detail=f"limit {self.config.max_frame_bytes} bytes"))
                continue
            return text

    async def _next_frame(self):
        text = await self._receive_text()
        try:
            return parse_client_frame(text)
        except ProtocolError as exc:
            self.enqueue(Error(code=exc.code, detail=exc.detail or None))
            return None

    # -- lifecycle --------------------------------------------------------------------------------

    async def run(self) -> None:
        message = await self._receive()
        if message.get("type") != "websocket.connect":
            return
        from django_cfg.core.edge import meta_from_scope

        await self._send({"type": "websocket.accept"})
        if not origin_allowed(meta_from_scope(self.scope), self.config):
            await self._send({"type": "websocket.close", "code": int(Close.ORIGIN)})
            logger.info("realtime: origin refused cid=%s", self.cid)
            return
        opened = time.monotonic()
        writer = asyncio.ensure_future(self._writer())
        session = asyncio.ensure_future(self._session())
        try:
            await asyncio.wait({writer, session}, return_when=asyncio.FIRST_COMPLETED)
            if session.done() and not session.cancelled() and session.exception() is not None:
                exc = session.exception()
                if not isinstance(exc, _Disconnected):
                    logger.error("realtime: connection failed cid=%s", self.cid, exc_info=exc)
                    self.close(Close.SERVER_ERROR)
            if not writer.done():
                if self._closing:
                    await asyncio.wait({writer}, timeout=_CLOSE_FLUSH)
                writer.cancel()
        finally:
            for task in (session, writer, *self._tasks.values(), *self._background):
                if not task.done():
                    task.cancel()
            for name, sub in list(self.subs.items()):
                sub.closed = True
                self.hub.remove(name, sub)
            self.subs.clear()
            if self._limit_key is not None:
                self.hub.release(self._limit_key)
            self.hub.detach(self)
            identity = self.identity
            logger.info(
                "realtime: closed cid=%s user=%s code=%s duration=%.1fs in=%d out=%d peak_subs=%d",
                self.cid, identity.user_id if identity else None, self._close_code,
                time.monotonic() - opened, self._stats["in"], self._stats["out"], self._stats["peak_subs"],
            )

    def _spawn(self, coro) -> asyncio.Task:
        task = asyncio.ensure_future(coro)
        self._background.add(task)
        task.add_done_callback(self._background.discard)
        task.add_done_callback(_consume)
        return task

    async def _auth_hook(self, token: Optional[str]) -> Identity:
        return await self.hooks(authenticate, self.scope, token, timeout=self.config.hook_timeout)

    async def _allow(self, bound) -> bool:
        return bool(await self.hooks(bound.topic.is_allowed, self.identity.user, bound.params,
                                     timeout=self.config.hook_timeout))

    def _room(self) -> int:
        """Frames a replay may queue now and still leave REPLAY_MARGIN free."""
        return self.config.send_queue - self._out.qsize() - REPLAY_MARGIN

    async def _first_frame(self):
        loop = asyncio.get_running_loop()
        deadline = loop.time() + self.config.auth_timeout
        while True:
            remaining = deadline - loop.time()
            if remaining <= 0:
                return None
            try:
                frame = await asyncio.wait_for(self._next_frame(), remaining)
            except asyncio.TimeoutError:
                return None
            if frame is not None:
                return frame

    async def _session(self) -> None:
        await self.hub.attach(self)  # before auth: a kick during the handshake lands in _early_kicks
        first = await self._first_frame()
        token = first.token if isinstance(first, AuthFrame) else None
        try:
            identity = await self._auth_hook(token)
        except AuthFailed:  # presented and refused: the client refreshes its credential and reconnects
            self.close(Close.REVOKED)
            return
        except asyncio.TimeoutError:
            logger.warning("realtime: auth hook exceeded %s s", self.config.hook_timeout)
            self.close(Close.SERVER_ERROR)
            return

        if not identity.is_authenticated and not self.registry.has_anonymous():
            self.close(Close.AUTH_TIMEOUT if first is None else Close.AUTH)
            return
        early, self._early_kicks = self._early_kicks or [], None
        if any(identity.matches_kick(kick) for kick in early):
            self.close(Close.REVOKED)
            return
        if not self.hub.acquire(identity.limit_key, self.config.max_connections_per_user):
            self.close(Close.LIMIT)
            return
        self._limit_key = identity.limit_key
        self.identity = identity
        self.cid = issue_cid(identity)
        self.enqueue(Hello(user=identity.user_id, ping=self.config.ping_interval, cid=self.cid))
        logger.info("realtime: opened cid=%s user=%s ip=%s", self.cid, identity.user_id, identity.client_ip)
        if identity.is_authenticated and self.config.reauth_interval:
            self._spawn(self._reauth())

        if first is not None and not isinstance(first, AuthFrame):
            self._dispatch(first)
        while not self._closing:
            frame = await self._next_frame()
            if frame is not None:
                self._dispatch(frame)
        await asyncio.Event().wait()  # closing: the writer ends the connection

    async def _reauth(self) -> None:
        """Re-run the authenticator on the socket's credential (a refusal or another user closes 4419), then
        every live subscription's `allow` with the fresh user (a refused one gets `sub_err forbidden`)."""
        while not self._closing:
            await asyncio.sleep(self.config.reauth_interval)
            try:
                fresh = await self._auth_hook(self.identity.token)
            except AuthFailed:
                self.close(Close.REVOKED)
                return
            except asyncio.TimeoutError:
                logger.warning("realtime: credential re-check timed out cid=%s; retrying later", self.cid)
                continue
            if not fresh.is_authenticated or str(fresh.user_id) != str(self.identity.user_id):
                self.close(Close.REVOKED)
                return
            self.identity = fresh  # same user, so the cid stays valid
            await self._recheck_subscriptions()

    async def _recheck_subscriptions(self) -> None:
        for name, sub in list(self.subs.items()):
            if sub.pending or sub.closed or self._closing:
                continue
            try:
                allowed = await self._allow(self.registry.resolve(name))
            except asyncio.TimeoutError:
                logger.warning("realtime: allow re-check of %s timed out; kept until the next one", name)
                continue
            except asyncio.CancelledError:
                raise
            except Exception:  # noqa: BLE001 - a broken hook denies, as on subscribe
                logger.exception("realtime: allow re-check of %s raised", name)
                allowed = False
            if not allowed and self.subs.get(name) is sub:
                self._drop(name)
                self.enqueue(SubErr(id=sub.id, topic=name, code="forbidden"))

    def on_kick(self, kick: Dict[str, Any]) -> None:
        if self.identity is None:
            if self._early_kicks is not None:
                self._early_kicks.append(kick)
            return
        if self.identity.matches_kick(kick):
            self.close(Close.REVOKED)

    # -- frames -----------------------------------------------------------------------------------

    def _dispatch(self, frame) -> None:
        if isinstance(frame, SubFrame):
            previous = self._tasks.pop(frame.topic, None)
            if previous is not None:
                previous.cancel()
            task = asyncio.ensure_future(self._subscribe(frame))
            self._tasks[frame.topic] = task
            task.add_done_callback(lambda t, name=frame.topic: self._sub_done(name, t))
        elif isinstance(frame, UnsubFrame):
            self._unsubscribe(frame.topic)
        elif isinstance(frame, PingFrame):
            self.enqueue(Pong())
        elif isinstance(frame, AuthFrame):
            self.enqueue(Error(code="auth_late", detail="auth is accepted as the first frame only"))

    def _sub_done(self, name: str, task: asyncio.Task) -> None:
        if self._tasks.get(name) is task:
            del self._tasks[name]
        if task.cancelled():
            return
        exc = task.exception()
        if exc is not None:
            logger.error("realtime: subscribe to %s failed", name, exc_info=exc)
            self.close(Close.SERVER_ERROR)

    def _drop(self, name: str) -> None:
        sub = self.subs.pop(name, None)
        if sub is not None:
            sub.closed = True
            self.hub.remove(name, sub)

    def _unsubscribe(self, name: str) -> None:
        task = self._tasks.pop(name, None)
        if task is not None:
            task.cancel()
        self._drop(name)

    def _refuse(self, frame: SubFrame, code: str, sub: Optional[Subscription] = None) -> None:
        if sub is not None and self.subs.get(frame.topic) is sub:
            del self.subs[frame.topic]
        self.enqueue(SubErr(id=frame.id, topic=frame.topic, code=code))

    async def _subscribe(self, frame: SubFrame) -> None:
        name = frame.topic
        if not TOPIC_RE.match(name):
            self._refuse(frame, "invalid")
            return
        try:
            bound = self.registry.resolve(name)
        except UnknownTopic:
            self._refuse(frame, "unknown_topic")
            return
        self._drop(name)  # a repeated `sub` replaces the earlier one
        if len(self.subs) >= self.config.max_subscriptions:
            self._refuse(frame, "limit")
            return
        sub = Subscription(self, name, frame.id)
        self.subs[name] = sub  # reserved while `allow` runs, so concurrent subs respect the limit
        try:
            allowed = await self._allow(bound)
        except asyncio.TimeoutError:
            logger.warning("realtime: allow hook of %s exceeded %s s", bound.topic.pattern, self.config.hook_timeout)
            self._refuse(frame, "timeout", sub)
            return
        except asyncio.CancelledError:
            raise
        except Exception:  # noqa: BLE001 - a broken hook denies, and is logged once here
            logger.exception("realtime: allow hook of %s raised", bound.topic.pattern)
            self._refuse(frame, "forbidden", sub)
            return
        if not allowed:
            self._refuse(frame, "forbidden", sub)
            return
        if self.subs.get(name) is not sub:
            return

        self.hub.add(name, sub)  # first: anything published from here on reaches the held queue
        head = await self.backend.ahead(name)
        recovered: Optional[bool] = None
        replay: List[Entry] = []
        if frame.since is not None:
            try:
                replay, recovered = await self.backend.aread_since(name, frame.since)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 - the replay failed; the client refetches instead
                logger.warning("realtime: replay of %s failed (%s); answering recovered:false", name, exc)
                replay, recovered = [], False
            if recovered and len(replay) > self._room() - 1:  # sub_ok takes a slot too
                logger.info("realtime: replay of %s (%d) does not fit the send queue; recovered:false",
                            name, len(replay))
                replay, recovered = [], False
        if self.subs.get(name) is not sub:
            self.hub.remove(name, sub)
            return
        self.enqueue(SubOk(id=frame.id, topic=name, offset=head, recovered=recovered))
        self._stats["peak_subs"] = max(self._stats["peak_subs"], len(self.subs))
        if recovered:
            sub.offset = frame.since
            for entry in replay:
                sub.emit(entry)
        else:
            sub.offset = head
        sub.go_live()

    async def recover(self, sub: Subscription) -> None:
        """The bus lost records: replay the subscription from its offset, or tell the client to refetch.

        A replay that fails or would not fit the send queue answers `sub_ok recovered:false` too; never silence.
        """
        if sub.closed or sub.pending or sub.offset is None:
            return
        try:
            replay, recovered = await self.backend.aread_since(sub.topic, sub.offset)
            if recovered and len(replay) > self._room():
                recovered = False
            if not recovered:
                sub.offset = await self.backend.ahead(sub.topic)
        except asyncio.CancelledError:
            raise
        except Exception as exc:  # noqa: BLE001 - Redis away: the client refetches; live delivery continues
            logger.warning("realtime: recovery of %s failed (%s); answering recovered:false", sub.topic, exc)
            replay, recovered = [], False
        if sub.closed:
            return
        if recovered:
            for entry in replay:
                sub.emit(entry)
        else:
            self.enqueue(SubOk(id=sub.id, topic=sub.topic, offset=sub.offset, recovered=False))


__all__ = ["Connection", "HookRunner", "InlineHookRunner", "Subscription", "hook_pool"]
