"""Test helpers: capture publishes like `mail.outbox`, drive a socket through the raw ASGI callable.

    from django_cfg.modules.django_realtime.testing import realtime_outbox

    def test_paid_order_notifies():
        with realtime_outbox() as outbox:
            pay(order)                                  # calls publish(...)
        assert outbox == [("orders:42", OrderEvent(kind="paid"))]

Inside a `TestCase` (or `django_db`) test the publish waits for a commit that never comes; wrap the code in
`self.captureOnCommitCallbacks(execute=True)` (pytest-django: `django_capture_on_commit_callbacks`).

`WebSocketDriver` speaks ASGI directly (no server, no Channels) against the memory backend:

    async with WebSocketDriver(headers={"origin": "http://testserver"}) as ws:
        await ws.send({"op": "sub", "id": 1, "topic": "demo.ping"})
        assert (await ws.receive())["op"] == "hello"

The driver's own handler runs hooks (`authenticate`, `allow`) with `InlineHookRunner`: driven from a sync test
through `async_to_sync`, they run on the test's own thread and see its `TestCase` data. Pass `inline=False` to
exercise the real thread pool. A driver given an `app` uses that app's hooks.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any, Dict, Iterable, List, Mapping, NamedTuple, Optional, Tuple, Union

from pydantic import BaseModel

from .backends import Backend, MemoryBackend, pop_backend, push_backend
from .publishing import _listeners


class Published(NamedTuple):
    topic: str
    event: BaseModel


class realtime_outbox:  # noqa: N801 - reads like Django's mail.outbox / override_settings
    """Context manager: a fresh memory backend for the block, and every committed publish recorded in order."""

    def __init__(self, backend: Optional[Backend] = None) -> None:
        self.backend = backend or MemoryBackend()
        self.messages: List[Published] = []

    def _record(self, topic: str, event: BaseModel, offset: str) -> None:
        self.messages.append(Published(topic, event))

    def __enter__(self) -> "realtime_outbox":
        push_backend(self.backend)
        _listeners.append(self._record)
        return self

    def __exit__(self, *exc) -> None:
        if self._record in _listeners:
            _listeners.remove(self._record)
        pop_backend(self.backend)

    def clear(self) -> None:
        self.messages.clear()

    def topics(self) -> List[str]:
        return [m.topic for m in self.messages]

    def __iter__(self):
        return iter(self.messages)

    def __len__(self) -> int:
        return len(self.messages)

    def __getitem__(self, index):
        return self.messages[index]

    def __eq__(self, other: object) -> bool:
        if isinstance(other, (list, tuple)):
            return self.messages == list(other)
        return NotImplemented

    def __repr__(self) -> str:
        return f"realtime_outbox({self.messages!r})"


class Closed(Exception):
    """The server closed the socket; `code` is the close code (or None when it never accepted)."""

    def __init__(self, code: Optional[int]) -> None:
        super().__init__(f"closed with {code}")
        self.code = code


HeaderInput = Union[Mapping[str, str], Iterable[Tuple[str, str]]]


class WebSocketDriver:
    """One client socket against an ASGI app. Without `app`, a bare realtime handler with the given parts."""

    def __init__(
        self,
        app=None,
        *,
        path: str = "/ws",
        headers: HeaderInput = (),
        client: Tuple[str, int] = ("127.0.0.1", 50000),
        config=None,
        registry=None,
        hub=None,
        inline: bool = True,
    ) -> None:
        self.app = app or self._handler(config=config, registry=registry, hub=hub, inline=inline)
        items = headers.items() if isinstance(headers, Mapping) else headers
        self.scope: Dict[str, Any] = {
            "type": "websocket",
            "asgi": {"version": "3.0"},
            "scheme": "ws",
            "path": path,
            "raw_path": path.encode(),
            "query_string": b"",
            "root_path": "",
            "headers": [(k.lower().encode("latin-1"), v.encode("latin-1")) for k, v in items],
            "client": client,
            "server": ("testserver", 80),
            "subprotocols": [],
        }
        self._inbox: asyncio.Queue = asyncio.Queue()
        self._outbox: asyncio.Queue = asyncio.Queue()
        self._task: Optional[asyncio.Task] = None
        self.accepted = False
        self.close_code: Optional[int] = None

    @staticmethod
    def _handler(*, config, registry, hub, inline):
        async def app(scope, receive, send):
            from .backends import get_realtime_config
            from .connection import Connection, InlineHookRunner
            from .hub import get_hub

            await Connection(scope, receive, send, hub=hub or get_hub(), config=config or get_realtime_config(),
                             registry=registry, hooks=InlineHookRunner() if inline else None).run()

        return app

    # -- ASGI side --------------------------------------------------------------------------------

    async def _receive(self):
        return await self._inbox.get()

    async def _send(self, message):
        await self._outbox.put(message)

    # -- client side ------------------------------------------------------------------------------

    async def connect(self, timeout: float = 2.0) -> "WebSocketDriver":
        self._task = asyncio.ensure_future(self.app(self.scope, self._receive, self._send))
        await self._inbox.put({"type": "websocket.connect"})
        message = await self._next(timeout)
        if message["type"] == "websocket.accept":
            self.accepted = True
            return self
        self.close_code = message.get("code")
        raise Closed(None)

    async def _next(self, timeout: float):
        getter = asyncio.ensure_future(self._outbox.get())
        done, _ = await asyncio.wait({getter, self._task}, timeout=timeout, return_when=asyncio.FIRST_COMPLETED)
        if getter in done:
            return getter.result()
        getter.cancel()
        if self._task in done:
            exc = self._task.exception()
            if exc is not None:
                raise exc
            raise Closed(self.close_code)
        raise asyncio.TimeoutError(f"no frame within {timeout} s")

    async def send(self, frame: Union[Mapping[str, Any], str]) -> None:
        text = frame if isinstance(frame, str) else json.dumps(frame)
        await self._inbox.put({"type": "websocket.receive", "text": text})

    async def send_bytes(self, data: bytes) -> None:
        await self._inbox.put({"type": "websocket.receive", "bytes": data})

    async def receive(self, timeout: float = 2.0) -> Dict[str, Any]:
        """The next server frame; Closed when the server closes instead."""
        message = await self._next(timeout)
        if message["type"] == "websocket.close":
            self.close_code = message.get("code", 1000)
            raise Closed(self.close_code)
        return json.loads(message["text"])

    async def receive_until(self, op: str, timeout: float = 2.0) -> Dict[str, Any]:
        """Skip frames until one with `op` (server pings, for instance)."""
        while True:
            frame = await self.receive(timeout)
            if frame.get("op") == op:
                return frame

    async def expect_close(self, timeout: float = 2.0) -> int:
        """Read until the server closes; returns the close code."""
        while True:
            try:
                await self.receive(timeout)
            except Closed as closed:
                return closed.code

    async def assert_silent(self, timeout: float = 0.2) -> None:
        try:
            frame = await self.receive(timeout)
        except asyncio.TimeoutError:
            return
        raise AssertionError(f"expected no frame, got {frame}")

    async def disconnect(self, code: int = 1000) -> None:
        """Send `websocket.disconnect` and wait for the handler to return (it must, within a second)."""
        if self._task is None:
            return
        await self._inbox.put({"type": "websocket.disconnect", "code": code})
        try:
            await asyncio.wait_for(asyncio.shield(self._task), 2.0)
        except asyncio.TimeoutError:
            self._task.cancel()
            raise

    @property
    def finished(self) -> bool:
        return self._task is not None and self._task.done()

    async def __aenter__(self) -> "WebSocketDriver":
        return await self.connect()

    async def __aexit__(self, *exc) -> None:
        await self.disconnect()


__all__ = ["Closed", "Published", "WebSocketDriver", "realtime_outbox"]
