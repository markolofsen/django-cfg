"""In-process backend for tests and single-process development: the Redis rules, without Redis.

Epochs, sequential offsets, exact history trim, `history_ttl` / `meta_ttl` expiry (checked lazily against `clock`)
and a bus with trim-gap detection behave as in `redis_streams.py`. Appends may come from any thread; readers on
event loops are woken with `call_soon_threadsafe`.
"""

from __future__ import annotations

import asyncio
import json
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Callable, Deque, Dict, List, Optional, Set, Tuple

from .base import Backend, BusItem, Entry, format_offset, new_epoch


@dataclass
class _Topic:
    epoch: str
    seq: int = 0
    history: Deque[Tuple[int, Dict[str, Any], Optional[str]]] = field(default_factory=deque)
    history_until: float = 0.0
    meta_until: float = 0.0


class MemoryBackend(Backend):
    name = "memory"

    def __init__(self, *, clock: Callable[[], float] = time.monotonic, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.clock = clock
        self._lock = threading.Lock()
        self._topics: Dict[str, _Topic] = {}
        self._bus: Deque[Tuple[int, BusItem]] = deque()
        self._bus_last = 0
        self._bus_trimmed = 0  # highest bus id removed by the trim
        self._waiters: Set[Tuple[asyncio.AbstractEventLoop, asyncio.Event]] = set()

    # -- state ------------------------------------------------------------------------------------

    def _topic(self, name: str, *, create: bool) -> Optional[_Topic]:
        now = self.clock()
        topic = self._topics.get(name)
        if topic is not None and topic.meta_until <= now:
            del self._topics[name]
            topic = None
        if topic is not None and topic.history_until <= now:
            topic.history.clear()
        if topic is None and create:  # a publish extends both to their full TTLs
            topic = _Topic(epoch=new_epoch(), meta_until=now + self.history_ttl, history_until=now + self.history_ttl)
            self._topics[name] = topic
        return topic

    def drop_meta(self, name: str) -> None:
        """Forget a topic's metadata, as a Redis restart without persistence would (tests)."""
        with self._lock:
            self._topics.pop(name, None)

    def _bus_add(self, item_fn: Callable[[str], BusItem]) -> None:
        self._bus_last += 1
        self._bus.append((self._bus_last, item_fn(str(self._bus_last))))
        while len(self._bus) > self.bus_maxlen:
            self._bus_trimmed = self._bus.popleft()[0]
        waiters = list(self._waiters)
        for loop, event in waiters:
            try:
                loop.call_soon_threadsafe(event.set)
            except RuntimeError:  # the loop is closed; its waiter is gone
                pass

    # -- writes -----------------------------------------------------------------------------------

    def append(self, topic: str, data: Dict[str, Any], *, history: int, origin_cid: Optional[str] = None) -> str:
        data = json.loads(json.dumps(data))  # the wire copy, as Redis would store it
        with self._lock:
            state = self._topic(topic, create=True)
            state.seq += 1
            state.history.append((state.seq, data, origin_cid))
            while len(state.history) > history:
                state.history.popleft()
            now = self.clock()
            state.history_until = now + self.history_ttl
            state.meta_until = now + self.meta_ttl
            offset = format_offset(state.epoch, state.seq)
            entry = Entry(topic, offset, data, origin_cid)
            self._bus_add(lambda bus_id: BusItem(bus_id, entry=entry))
        return offset

    def kick(self, kick: Dict[str, Any]) -> None:
        payload = json.loads(json.dumps(kick))
        with self._lock:
            self._bus_add(lambda bus_id: BusItem(bus_id, kick=payload))

    # -- topic reads ------------------------------------------------------------------------------

    async def ahead(self, topic: str) -> str:
        with self._lock:
            state = self._topic(topic, create=True)
            return format_offset(state.epoch, state.seq)

    async def aread_since(self, topic: str, since: str) -> Tuple[List[Entry], bool]:
        with self._lock:
            state = self._topic(topic, create=False)
            meta = (state.epoch, state.seq) if state else None
            first = state.history[0][0] if state and state.history else None
            if not self.recovered(meta, first, since):
                return [], False
            after = int(since.rpartition(":")[2])
            return [
                Entry(topic, format_offset(state.epoch, seq), data, cid)
                for seq, data, cid in state.history if seq > after
            ], True

    # -- the bus ----------------------------------------------------------------------------------

    async def bus_head(self) -> str:
        with self._lock:
            return str(self._bus_last)

    def _collect(self, after: int) -> Tuple[List[BusItem], bool]:
        with self._lock:
            gap = self._bus_trimmed > after
            return [item for bus_id, item in self._bus if bus_id > after], gap

    async def read_bus(self, after: str, timeout: float) -> Tuple[List[BusItem], bool]:
        start = int(after or 0)
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while True:
            event = asyncio.Event()
            waiter = (loop, event)
            with self._lock:
                self._waiters.add(waiter)
            try:
                items, gap = self._collect(start)
                if items or gap:
                    return items, gap
                remaining = deadline - loop.time()
                if remaining <= 0:
                    return [], False
                try:
                    await asyncio.wait_for(event.wait(), remaining)
                except asyncio.TimeoutError:
                    return self._collect(start)
            finally:
                with self._lock:
                    self._waiters.discard(waiter)


__all__ = ["MemoryBackend"]
