"""The backend contract: per-topic replay history with epoch offsets, plus one delivery bus for every process.

Offsets are `"<epoch>:<seq>"`. Per topic, `seq` grows by one per publish; the epoch is set when a topic's metadata
is created and changes only when that metadata was lost (expired after `meta_ttl`, or Redis lost data). A new epoch
means history is gone, never "nothing new".

A topic's metadata created by a read (`ahead`, a subscribe before any publish) lives `history_ttl`; a publish extends
it to `meta_ttl`. Creating metadata discards any history left from a lost epoch.

Recovery rule, the same in every backend: `aread_since(topic, since)` is `recovered=True` iff the metadata exists,
its epoch equals since's, `since_seq <= top`, and (`since_seq == top`, or the history still holds the entry right
after `since`: `since_seq >= first_retained - 1`). Otherwise it returns no entries and `recovered=False`.

Delivery: every publish also goes on the bus (`rt:bus`), which each process reads once and filters locally. The bus
also carries kicks (close a user's or a session's sockets).
"""

from __future__ import annotations

import abc
import secrets
from typing import Any, Dict, List, NamedTuple, Optional, Tuple

BUS_MAXLEN = 10_000
HISTORY_TTL = 300
META_TTL = 86_400
#: Seconds one bus read blocks at most; the Redis reader's socket timeout is set above it.
READ_BLOCK = 5.0


class Entry(NamedTuple):
    topic: str
    offset: str
    data: Dict[str, Any]
    origin_cid: Optional[str] = None


class BusItem(NamedTuple):
    """One bus record: a publication (`entry`) or a kick (`kick`: {"user": id} | {"session": hash} | {"all": true})."""

    id: str
    entry: Optional[Entry] = None
    kick: Optional[Dict[str, Any]] = None


def new_epoch() -> str:
    return secrets.token_hex(4)


def parse_offset(offset: str) -> Optional[Tuple[str, int]]:
    """`"<epoch>:<seq>"` -> (epoch, seq), or None for anything else."""
    if not isinstance(offset, str) or ":" not in offset:
        return None
    epoch, _, seq = offset.rpartition(":")
    if not epoch or not seq.isdigit():
        return None
    return epoch, int(seq)


def format_offset(epoch: str, seq: int) -> str:
    return f"{epoch}:{seq}"


class Backend(abc.ABC):
    """Writes are sync (`publish()` runs in views and jobs); reads are async (the socket handler)."""

    name: str = "base"

    def __init__(self, *, history_ttl: int = HISTORY_TTL, meta_ttl: int = META_TTL, bus_maxlen: int = BUS_MAXLEN):
        self.history_ttl = history_ttl
        self.meta_ttl = meta_ttl
        self.bus_maxlen = bus_maxlen

    # -- writes -----------------------------------------------------------------------------------

    @abc.abstractmethod
    def append(self, topic: str, data: Dict[str, Any], *, history: int, origin_cid: Optional[str] = None) -> str:
        """Add one entry to the topic's history (trimmed to `history`) and to the bus; return its offset."""

    @abc.abstractmethod
    def kick(self, kick: Dict[str, Any]) -> None:
        """Put a kick on the bus; every process closes its matching sockets."""

    # -- topic reads ------------------------------------------------------------------------------

    @abc.abstractmethod
    async def ahead(self, topic: str) -> str:
        """The topic's current offset; creates the metadata (a fresh epoch, seq 0) when there is none."""

    @abc.abstractmethod
    async def aread_since(self, topic: str, since: str) -> Tuple[List[Entry], bool]:
        """Entries after `since` and whether that is everything; see the module docstring."""

    # -- the bus ----------------------------------------------------------------------------------

    @abc.abstractmethod
    async def bus_head(self) -> str:
        """The id of the newest bus record; a reader starting now reads after it."""

    @abc.abstractmethod
    async def read_bus(self, after: str, timeout: float) -> Tuple[List[BusItem], bool]:
        """Bus records after `after`, oldest first, waiting up to `timeout` s; and whether records after `after`
        were trimmed before they could be read (then every local subscription must recover)."""

    async def aclose(self) -> None:
        """Release connections bound to the running event loop."""

    def close(self) -> None:
        """Release sync connections."""

    @staticmethod
    def recovered(meta: Optional[Tuple[str, int]], first_retained: Optional[int], since: str) -> bool:
        """The recovery rule on (epoch, top seq), the first retained seq (None: history empty) and `since`."""
        parsed = parse_offset(since)
        if parsed is None or meta is None:
            return False
        epoch, top = meta
        since_epoch, since_seq = parsed
        if since_epoch != epoch or since_seq > top:
            return False
        if since_seq == top:
            return True
        return first_retained is not None and since_seq >= first_retained - 1


__all__ = [
    "BUS_MAXLEN", "Backend", "BusItem", "Entry", "HISTORY_TTL", "META_TTL", "READ_BLOCK", "format_offset", "new_epoch",
    "parse_offset",
]
