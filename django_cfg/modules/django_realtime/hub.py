"""Per-process fan-out: one reader over the bus, local filtering by topic, kicks.

The reader runs while the process has open sockets. It starts at the bus head, so a subscription registered
before it reads its topic's head misses nothing (`connection.py` registers first, then reads the head). A bus trim
past the reader's cursor (Redis was away longer than the bus holds) makes every local subscription recover through
the replay rule, at most `RECOVER_CONCURRENCY` at a time so the recovery cannot drain the Redis pool. A record
that cannot be parsed or delivered is logged and skipped; the cursor still moves past it. Sockets attach before
they authenticate, so a kick that lands during the handshake is not missed.
"""

from __future__ import annotations

import asyncio
import logging
import weakref
from collections import Counter
from typing import TYPE_CHECKING, Dict, Optional, Set

from .backends import Backend, get_backend
from .backends.base import READ_BLOCK

if TYPE_CHECKING:
    from .connection import Connection, Subscription

logger = logging.getLogger(__name__)

_RETRY_DELAY = 1.0
#: Subscriptions replayed at once after a bus gap.
RECOVER_CONCURRENCY = 8


class Hub:
    def __init__(self, backend: Backend, *, block: float = READ_BLOCK) -> None:
        self.backend = backend
        self.block = block
        self._subs: Dict[str, Set["Subscription"]] = {}
        self._task: Optional[asyncio.Task] = None
        self._after: str = ""
        self._per_key: Counter = Counter()
        self.connections: "weakref.WeakSet[Connection]" = weakref.WeakSet()

    # -- connections ------------------------------------------------------------------------------

    def acquire(self, key: str, limit: int) -> bool:
        if self._per_key[key] >= limit:
            return False
        self._per_key[key] += 1
        return True

    def release(self, key: str) -> None:
        self._per_key[key] -= 1
        if self._per_key[key] <= 0:
            del self._per_key[key]

    async def attach(self, conn: "Connection") -> None:
        """Register a live socket (it then receives kicks) and make sure the reader runs."""
        self.connections.add(conn)
        if self._task is None or self._task.done():
            head = await self.backend.bus_head()
            if self._task is None or self._task.done():  # another attach may have started it meanwhile
                self._after = head
                self._task = asyncio.get_running_loop().create_task(self._run(), name="realtime-bus")

    def detach(self, conn: "Connection") -> None:
        self.connections.discard(conn)

    # -- subscriptions ----------------------------------------------------------------------------

    def add(self, topic: str, sub: "Subscription") -> None:
        self._subs.setdefault(topic, set()).add(sub)

    def remove(self, topic: str, sub: "Subscription") -> None:
        subs = self._subs.get(topic)
        if subs is None:
            return
        subs.discard(sub)
        if not subs:
            del self._subs[topic]

    def topics(self) -> Dict[str, int]:
        return {t: len(s) for t, s in self._subs.items()}

    # -- the reader -------------------------------------------------------------------------------

    async def _run(self) -> None:
        while len(self.connections):
            try:
                items, gap = await self.backend.read_bus(self._after, self.block)
            except asyncio.CancelledError:
                raise
            except Exception as exc:  # noqa: BLE001 - backend outage: keep the sockets, resume from the cursor
                logger.warning("realtime: bus read failed (%s), retrying in %.0f s", exc, _RETRY_DELAY)
                await asyncio.sleep(_RETRY_DELAY)
                continue
            if gap:
                # Replay first, so the live records below are recognised as already sent.
                logger.warning("realtime: bus trimmed past the reader; recovering %d topics", len(self._subs))
                subs = [sub for group in self._subs.values() for sub in group]
                gate = asyncio.Semaphore(RECOVER_CONCURRENCY)

                async def recover(sub: "Subscription") -> None:
                    async with gate:
                        await sub.conn.recover(sub)

                await asyncio.gather(*(recover(sub) for sub in subs), return_exceptions=True)
            for item in items:
                self._after = item.id
                try:
                    self._dispatch(item)
                except Exception:  # noqa: BLE001 - one bad record must not stop delivery for the process
                    logger.exception("realtime: bus record %s could not be delivered; skipped", item.id)

    def _dispatch(self, item) -> None:
        if item.kick is not None:
            for conn in list(self.connections):
                conn.on_kick(item.kick)
        elif item.entry is not None:
            for sub in list(self._subs.get(item.entry.topic, ())):
                sub.deliver(item.entry)

    async def shutdown(self, code: int, *, wait: float = 1.0) -> None:
        """Close every socket of this hub with `code`, then stop the reader."""
        for conn in list(self.connections):
            conn.close(code)
        loop = asyncio.get_running_loop()
        deadline = loop.time() + wait
        while len(self.connections) and loop.time() < deadline:
            await asyncio.sleep(0.01)
        if self._task is not None:
            self._task.cancel()
            try:
                await self._task
            except (asyncio.CancelledError, Exception):  # noqa: BLE001 - shutting down
                pass
        await self.backend.aclose()


_hubs: "weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, Hub]" = weakref.WeakKeyDictionary()


def get_hub() -> Hub:
    """The hub of the running event loop, bound to the current backend."""
    loop = asyncio.get_running_loop()
    backend = get_backend()
    hub = _hubs.get(loop)
    if hub is None or hub.backend is not backend:
        hub = Hub(backend)
        _hubs[loop] = hub
    return hub


async def shutdown_hubs(code: int) -> None:
    hub = _hubs.pop(asyncio.get_running_loop(), None)
    if hub is not None:
        await hub.shutdown(code)


__all__ = ["Hub", "READ_BLOCK", "RECOVER_CONCURRENCY", "get_hub", "shutdown_hubs"]
