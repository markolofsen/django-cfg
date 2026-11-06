"""The turn state machine: pure rules over a store. The store owns atomicity and persistence; this owns the rules.

A turn is a user message plus the answer begun for it, taken under one lock on the thread (`store.atomic`).
**seq**: the store hands out the next one under that lock. **Idempotent resend**: a user message is keyed by the client's
`client_id`; sending it again never stores it twice: a stored answer is replayed, a running one reported busy, a failed or
never-begun one begun again. **One running answer per thread**; a run that died is closed by the reaper.
"""

from __future__ import annotations

import time
import uuid
from contextlib import AbstractContextManager
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Any, Protocol

FLUSH_EVERY_S = 1.0  # incremental save of a streaming answer


class Role(StrEnum):
    USER = "user"
    ASSISTANT = "assistant"


class Status(StrEnum):
    DONE = "done"
    RUNNING = "running"
    ERROR = "error"
    CANCELLED = "cancelled"


class ErrorCode(StrEnum):
    UNAVAILABLE = "unavailable"
    TIMEOUT = "timeout"
    FAILED = "failed"


class TurnKind(StrEnum):
    STARTED = "started"  # new message, answer begun
    REPLAY = "replay"  # resent; the stored answer is served
    RETRY = "retry"  # resent; the earlier answer failed or never began, a new one begun
    BUSY = "busy"  # resent; the answer is still running


class TurnError(Exception):
    pass


class Busy(TurnError):
    """The thread already has an answer running."""


class InvalidTurn(TurnError):
    def __init__(self, field: str, code: str):
        super().__init__(f"{field}: {code}")
        self.field = field
        self.code = code  # empty | too_long | too_short | not_allowed | moved_on, or a code a kind's check raises


@dataclass(frozen=True)
class StoredMessage:
    """A snapshot of a stored row, all the rules and a replay need."""

    id: uuid.UUID
    seq: int
    role: Role
    status: Status
    text: str = ""
    client_id: uuid.UUID | None = None
    parts: tuple = ()
    error_code: str = ""
    tokens_in: int = 0
    tokens_out: int = 0
    cost_usd: float | None = None


@dataclass(frozen=True)
class Turn:
    kind: TurnKind
    user: StoredMessage
    assistant: StoredMessage

    @property
    def runs_model(self) -> bool:
        return self.kind in (TurnKind.STARTED, TurnKind.RETRY)


class TurnStore(Protocol):
    """One thread's rows. The adapter makes `atomic` a transaction holding an exclusive lock on the thread, and maps a
    violated one-running constraint to `Busy`. `update_running` never touches a finished row; `close` never touches a `done` one."""

    def atomic(self) -> AbstractContextManager[Any]: ...
    def reap(self, cutoff: datetime) -> int: ...
    def user_by_client_id(self, client_id: uuid.UUID) -> StoredMessage | None: ...
    def answers_to(self, user: StoredMessage) -> list[StoredMessage]: ...
    def latest_user(self) -> StoredMessage | None: ...
    def has_running(self) -> bool: ...
    def append(self, role: Role, now: datetime, *, text: str = "", status: Status = Status.DONE, client_id: uuid.UUID | None = None) -> StoredMessage: ...
    def update_running(self, message_id: uuid.UUID, **fields: Any) -> bool: ...
    def close(self, message_id: uuid.UUID, **fields: Any) -> bool: ...


def clean_text(text: str, max_chars: int) -> str:
    text = (text or "").strip()
    if not text:
        raise InvalidTurn("text", "empty")
    if len(text) > max_chars:
        raise InvalidTurn("text", "too_long")
    return text


def reap(store: TurnStore, now: datetime, stale_after_s: float) -> int:
    """Close answers stuck `running` past the window (a crash, a restart): they would read as running for ever."""
    return store.reap(now - timedelta(seconds=stale_after_s))


def start(
    store: TurnStore, text: str, client_id: uuid.UUID | None, *, now: datetime, max_chars: int, stale_after_s: float
) -> Turn:
    """Store the user message and begin the answer for it, or settle a resend of `client_id`. Raises `Busy`, `InvalidTurn`."""
    text = clean_text(text, max_chars)
    with store.atomic():
        reap(store, now, stale_after_s)
        if client_id is not None:
            known = store.user_by_client_id(client_id)
            if known is not None:
                return _resend(store, known, now)
        _require_idle(store)
        user = store.append(Role.USER, now, text=text, client_id=client_id)
        answer = store.append(Role.ASSISTANT, now, status=Status.RUNNING)
        return Turn(TurnKind.STARTED, user, answer)


def _resend(store: TurnStore, user: StoredMessage, now: datetime) -> Turn:
    answers = store.answers_to(user)
    last = answers[-1] if answers else None
    if last is not None and last.status == Status.DONE:
        return Turn(TurnKind.REPLAY, user, last)
    if last is not None and last.status == Status.RUNNING:
        return Turn(TurnKind.BUSY, user, last)
    latest = store.latest_user()
    if latest is None or latest.id != user.id:
        raise InvalidTurn("client_id", "moved_on")
    _require_idle(store)
    return Turn(TurnKind.RETRY, user, store.append(Role.ASSISTANT, now, status=Status.RUNNING))


def _require_idle(store: TurnStore) -> None:
    if store.has_running():
        raise Busy("an answer is still running")


def flush(store: TurnStore, message_id: uuid.UUID, *, text: str, parts: list | None = None, tool_calls: list | None = None) -> bool:
    """Save a running answer as it stands, so a dropped stream keeps what was said."""
    fields: dict[str, Any] = {"text": text}
    if parts is not None:
        fields["parts"] = parts
    if tool_calls is not None:
        fields["tool_calls"] = tool_calls
    return store.update_running(message_id, **fields)


def finish(store: TurnStore, message_id: uuid.UUID, *, status: Status, text: str, error_code: str = "", **fields: Any) -> bool:
    """Close an answer. A `done` row is final; an `error` row the reaper closed may still take the real result."""
    if status == Status.RUNNING:
        raise ValueError("cannot finish an answer as running")
    if error_code and error_code not in ErrorCode:
        raise ValueError(f"unknown error code {error_code!r}")
    return store.close(message_id, status=status, text=text.strip(), error_code=error_code, **fields)


class Flusher:
    """Says when a streaming answer is due for its next incremental save."""

    def __init__(self, every: float = FLUSH_EVERY_S, clock=time.monotonic):
        self._every, self._clock, self._last = every, clock, clock()

    def due(self) -> bool:
        now = self._clock()
        if now - self._last < self._every:
            return False
        self._last = now
        return True
