"""Where a finished trace goes. A sink is told, it never reads: `write` while the answer runs, `flush` once at the end."""

from __future__ import annotations

import logging
from typing import Any, Protocol

log = logging.getLogger(__name__)


class TraceSink(Protocol):
    def write(self, doc: dict) -> None:
        """An incremental save (the answer is still running). Best effort."""

    def flush(self, doc: dict) -> None:
        """The final document. Called once, after the answer is stored."""


class MessageJsonSink:
    """The default: one JSON column, `trace`, on the answer's message row. A host whose message model has no `trace` column
    (its migration is not applied yet) gets a no-op and one warning: the answer is never lost for the trace."""

    def __init__(self, store: Any, message_id: Any) -> None:
        self._store = store
        self._message_id = message_id

    def write(self, doc: dict) -> None:
        self._save(doc)

    def flush(self, doc: dict) -> None:
        self._save(doc)

    def _save(self, doc: dict) -> None:
        try:
            if not self._store.set_trace(self._message_id, doc):
                log.debug("trace: nothing stored for message %s", self._message_id)
        except Exception:  # noqa: BLE001 - the trace must not lose an answer
            log.exception("trace: could not store the trace of message %s", self._message_id)
