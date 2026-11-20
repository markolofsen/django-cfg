"""Redis backend: per-topic epoch metadata and history, one delivery bus.

Keys:
    rt:m:<topic>   hash {e: epoch, s: top seq}            EXPIRE meta_ttl on every publish (history_ttl when a read
                                                          created it)
    rt:h:<topic>   stream, entry ids "<seq>-0", MAXLEN    EXPIRE history_ttl on every publish
    rt:bus         stream of every publication and kick   MAXLEN ~ bus_maxlen

One Lua script assigns epoch and seq and writes history and bus atomically, so a Redis restart that lost the
metadata starts a new epoch and old offsets read as `recovered:false`; creating metadata (on publish or on a read)
deletes history left from the lost epoch. The bus reader uses its own connection (a blocked XREAD holds it, with a
socket timeout above the block and TCP keepalive); subscribes and replays share a blocking pool per event loop
(`redis_pool_size`), so a burst waits for a connection instead of failing.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
import weakref
from typing import Any, Dict, List, Optional, Tuple

from .base import READ_BLOCK, Backend, BusItem, Entry, format_offset, new_epoch, parse_offset

logger = logging.getLogger(__name__)

META_PREFIX = "rt:m:"
HISTORY_PREFIX = "rt:h:"
BUS_KEY = "rt:bus"
ZERO = "0-0"
#: Records one bus read returns at most; a full batch triggers a trim-gap check.
BUS_COUNT = 500

_PUBLISH = """
local e = redis.call('hget', KEYS[1], 'e')
if not e then
  e = ARGV[6]
  redis.call('del', KEYS[2])
  redis.call('hset', KEYS[1], 'e', e)
end
local s = redis.call('hincrby', KEYS[1], 's', 1)
redis.call('xadd', KEYS[2], 'MAXLEN', ARGV[3], s .. '-0', 'd', ARGV[2], 'c', ARGV[8])
redis.call('expire', KEYS[2], ARGV[4])
redis.call('expire', KEYS[1], ARGV[5])
local off = e .. ':' .. s
redis.call('xadd', KEYS[3], 'MAXLEN', '~', ARGV[7], '*', 'k', 'm', 't', ARGV[1], 'o', off, 'd', ARGV[2], 'c', ARGV[8])
return off
"""

_HEAD = """
local e = redis.call('hget', KEYS[1], 'e')
if not e then
  e = ARGV[1]
  redis.call('del', KEYS[2])
  redis.call('hset', KEYS[1], 'e', e, 's', 0)
  redis.call('expire', KEYS[1], ARGV[2])
end
local s = redis.call('hget', KEYS[1], 's') or '0'
return e .. ':' .. s
"""


def _meta_key(topic: str) -> str:
    return META_PREFIX + topic


def _history_key(topic: str) -> str:
    return HISTORY_PREFIX + topic


def _seq_of(stream_id: str) -> int:
    return int(stream_id.split("-", 1)[0])


def _bus_id(value: str) -> Tuple[int, int]:
    ms, _, seq = (value or ZERO).partition("-")
    return int(ms or 0), int(seq or 0)


def _bus_item(stream_id: str, fields: Dict[str, str]) -> BusItem:
    """One bus record; a malformed one becomes an empty item, so the reader skips it and still moves past it."""
    try:
        if fields.get("k") == "k":
            return BusItem(stream_id, kick=dict(json.loads(fields.get("d") or "{}")))
        entry = Entry(fields["t"], fields["o"], dict(json.loads(fields.get("d") or "{}")), fields.get("c") or None)
        return BusItem(stream_id, entry=entry)
    except (KeyError, TypeError, ValueError) as exc:
        logger.warning("realtime: skipping malformed bus record %s (%s)", stream_id, exc)
        return BusItem(stream_id)


class RedisStreamsBackend(Backend):
    name = "redis"

    def __init__(self, url: str, *, pool_size: int = 20, pool_timeout: float = 5.0, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.url = url
        self.pool_size = pool_size
        self.pool_timeout = pool_timeout
        self._sync = None
        self._sync_lock = threading.Lock()
        self._scripts: Dict[str, Any] = {}
        self._pools: "weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, Any]" = weakref.WeakKeyDictionary()
        self._readers: "weakref.WeakKeyDictionary[asyncio.AbstractEventLoop, Any]" = weakref.WeakKeyDictionary()

    # -- clients ----------------------------------------------------------------------------------

    def _client(self):
        if self._sync is None:
            with self._sync_lock:
                if self._sync is None:
                    import redis

                    client = redis.Redis.from_url(self.url, decode_responses=True)
                    self._scripts = {"publish": client.register_script(_PUBLISH)}
                    self._sync = client
        return self._sync

    def _pool(self):
        loop = asyncio.get_running_loop()
        client = self._pools.get(loop)
        if client is None:
            import redis.asyncio as aredis

            pool = aredis.BlockingConnectionPool.from_url(
                self.url, max_connections=self.pool_size, timeout=self.pool_timeout, decode_responses=True,
                health_check_interval=30,
            )
            client = aredis.Redis(connection_pool=pool)
            client._rt_head = client.register_script(_HEAD)
            self._pools[loop] = client
        return client

    def _reader(self):
        """A dedicated connection for the blocking bus read: no socket timeout shorter than the block."""
        loop = asyncio.get_running_loop()
        client = self._readers.get(loop)
        if client is None:
            import redis.asyncio as aredis

            client = aredis.Redis.from_url(self.url, decode_responses=True, max_connections=1,
                                           socket_timeout=READ_BLOCK + 5, socket_keepalive=True,
                                           health_check_interval=30)
            self._readers[loop] = client
        return client

    # -- writes -----------------------------------------------------------------------------------

    def append(self, topic: str, data: Dict[str, Any], *, history: int, origin_cid: Optional[str] = None) -> str:
        self._client()  # registers the scripts
        payload = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
        return self._scripts["publish"](
            keys=[_meta_key(topic), _history_key(topic), BUS_KEY],
            args=[topic, payload, history, self.history_ttl, self.meta_ttl, new_epoch(), self.bus_maxlen,
                  origin_cid or ""],
        )

    def kick(self, kick: Dict[str, Any]) -> None:
        payload = json.dumps(kick, separators=(",", ":"))
        self._client().xadd(BUS_KEY, {"k": "k", "d": payload}, maxlen=self.bus_maxlen, approximate=True)

    # -- topic reads ------------------------------------------------------------------------------

    def drop_meta(self, topic: str) -> None:
        """Delete a topic's metadata and history, as a Redis restart without persistence would (tests)."""
        self._client().delete(_meta_key(topic), _history_key(topic))

    async def ahead(self, topic: str) -> str:
        client = self._pool()
        return await client._rt_head(keys=[_meta_key(topic), _history_key(topic)], args=[new_epoch(), self.history_ttl])

    async def aread_since(self, topic: str, since: str) -> Tuple[List[Entry], bool]:
        parsed = parse_offset(since)
        if parsed is None:
            return [], False
        since_seq = parsed[1]
        client = self._pool()
        # One MULTI/EXEC: the metadata, the oldest retained entry and the rows are read at the same instant.
        async with client.pipeline(transaction=True) as pipe:
            pipe.hmget(_meta_key(topic), "e", "s")
            pipe.xrange(_history_key(topic), "-", "+", count=1)
            pipe.xrange(_history_key(topic), f"({since_seq}-0", "+")
            (epoch, top), first_rows, rows = await pipe.execute()
        meta = (epoch, int(top or 0)) if epoch else None
        first = _seq_of(first_rows[0][0]) if first_rows else None
        if not Backend.recovered(meta, first, since):
            return [], False
        if since_seq < meta[1] and (not rows or _seq_of(rows[0][0]) != since_seq + 1):
            return [], False
        return [Entry(topic, format_offset(epoch, _seq_of(i)), json.loads(f["d"]), f.get("c") or None)
                for i, f in rows], True

    # -- the bus ----------------------------------------------------------------------------------

    async def _bus_info(self):
        try:
            return await self._pool().xinfo_stream(BUS_KEY)
        except Exception as exc:  # redis.ResponseError, imported lazily
            if "no such key" in str(exc).lower():
                return None
            raise

    async def bus_head(self) -> str:
        info = await self._bus_info()
        return info["last-generated-id"] if info else ZERO

    async def bus_gap(self, after: str) -> bool:
        """Were bus records after `after` trimmed? Conservative: also true when `after` itself was the last trimmed."""
        info = await self._bus_info()
        if info is None or int(info.get("entries-added", 0) or 0) <= int(info.get("length", 0)):
            return False
        first = info.get("first-entry")
        return bool(first) and _bus_id(after) < _bus_id(first[0])

    async def read_bus(self, after: str, timeout: float) -> Tuple[List[BusItem], bool]:
        block = min(timeout, READ_BLOCK)  # the reader's socket timeout is READ_BLOCK + 5
        reply = await self._reader().xread({BUS_KEY: after or ZERO}, block=max(1, int(block * 1000)),
                                           count=BUS_COUNT)
        # RESP2 (the redis-py default): [[key, [(id, fields), ...]]]; RESP3: {key: [[(id, fields), ...]]}.
        rows = []
        if isinstance(reply, dict):
            for value in reply.values():
                rows.extend(value[0])
        else:
            for _key, items in reply or []:
                rows.extend(items)
        gap = len(rows) >= BUS_COUNT and await self.bus_gap(after)
        return [_bus_item(i, f) for i, f in rows], gap

    async def aclose(self) -> None:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            return
        for registry in (self._pools, self._readers):
            client = registry.pop(loop, None)
            if client is not None:
                await client.aclose()

    def close(self) -> None:
        if self._sync is not None:
            self._sync.close()
            self._sync = None


__all__ = ["BUS_KEY", "HISTORY_PREFIX", "META_PREFIX", "RedisStreamsBackend"]
