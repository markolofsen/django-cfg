"""The cancel request of a running answer: a flag the run's driver polls, so the request works from any worker or connection.

`POST .../cancel` does not reach the process that streams the answer (it may be another worker; the reader may be gone). It sets
the flag; the driver asks for it every `DriverConfig.cancel_poll_s`, ends the run as `cancelled` and stores what was said. The
default flag lives on Django's cache: a host with more than one worker needs a cache they share (Redis, Memcached), exactly as the
run lock does.
"""

from __future__ import annotations

import uuid
from typing import Any, Protocol

TTL_S = 300  # outlives any run (a kind's timeout_s is under the stale window); a flag set after a run ended just expires


class CancelSignal(Protocol):
    """Sync: the service calls it from a request thread, and the driver through `sync_to_async`."""

    def request(self, message_id: uuid.UUID) -> None: ...
    def requested(self, message_id: uuid.UUID) -> bool: ...
    def clear(self, message_id: uuid.UUID) -> None: ...


class CacheCancelSignal:
    """`CancelSignal` on a Django cache (default: `django.core.cache.cache`)."""

    def __init__(self, cache: Any = None, prefix: str = "chat-cancel:") -> None:
        self._cache = cache
        self._prefix = prefix

    def _backend(self) -> Any:
        if self._cache is not None:
            return self._cache
        from django.core.cache import cache

        return cache

    def request(self, message_id: uuid.UUID) -> None:
        self._backend().set(self._prefix + str(message_id), 1, TTL_S)

    def requested(self, message_id: uuid.UUID) -> bool:
        return self._backend().get(self._prefix + str(message_id)) is not None

    def clear(self, message_id: uuid.UUID) -> None:
        self._backend().delete(self._prefix + str(message_id))
