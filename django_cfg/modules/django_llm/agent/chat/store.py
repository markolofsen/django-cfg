"""The Django side of the `TurnStore`: one thread's rows. The only writer of the message table."""

from __future__ import annotations

import uuid
from collections.abc import Iterator
from contextlib import contextmanager
from datetime import datetime
from decimal import Decimal
from typing import Any

from django.db import IntegrityError, transaction
from django.utils import timezone

from django_cfg.modules.django_llm.agent.chat.turn import Busy, ErrorCode, Role, Status, StoredMessage


def snapshot(m: Any) -> StoredMessage:
    return StoredMessage(
        id=m.pk, seq=m.seq, role=Role(m.role), status=Status(m.status), text=m.text, client_id=m.client_id,
        parts=tuple(m.parts or ()), error_code=m.error_code, tokens_in=m.tokens_in, tokens_out=m.tokens_out,
        cost_usd=float(m.cost_usd) if m.cost_usd is not None else None,
    )


def _money(value: float | None) -> Decimal | None:
    return None if value is None else Decimal(str(round(value, 6)))


class DjangoTurnStore:
    """`thread` is an instance of the host's Thread model (a subclass of `AbstractThread`); messages are `thread.messages`."""

    def __init__(self, thread: Any):
        self.thread = thread
        self._thread_model = type(thread)
        self._message_model = thread.messages.model
        self._locked: Any = None

    @contextmanager
    def atomic(self) -> Iterator[None]:
        """A transaction holding the thread row: writers of one thread take `seq` one after the other."""
        try:
            with transaction.atomic():
                self._locked = self._thread_model.objects.select_for_update().get(pk=self.thread.pk)
                yield
        except IntegrityError as err:  # the one-running constraint decided a race the row lock did not cover
            raise Busy(str(self.thread.pk)) from err
        finally:
            self._locked = None

    def _messages(self):
        return self._message_model.objects.in_thread(self.thread)

    def reap(self, cutoff: datetime) -> int:
        return self._messages().running().filter(created_at__lt=cutoff).update(status=Status.ERROR, error_code=ErrorCode.FAILED)

    def user_by_client_id(self, client_id: uuid.UUID) -> StoredMessage | None:
        found = self._messages().filter(role=Role.USER, client_id=client_id).first()
        return snapshot(found) if found else None

    def answers_to(self, user: StoredMessage) -> list[StoredMessage]:
        """The assistant rows written for one user message, oldest first: more than one only after a retry."""
        qs = self._messages().filter(role=Role.ASSISTANT, seq__gt=user.seq)
        next_user = self._messages().filter(role=Role.USER, seq__gt=user.seq).order_by("seq").values_list("seq", flat=True).first()
        if next_user is not None:
            qs = qs.filter(seq__lt=next_user)
        return [snapshot(m) for m in qs.order_by("seq")]

    def latest_user(self) -> StoredMessage | None:
        found = self._messages().filter(role=Role.USER).order_by("-seq").first()
        return snapshot(found) if found else None

    def has_running(self) -> bool:
        return self._messages().running().exists()

    def append(self, role: Role, now: datetime, *, text: str = "", status: Status = Status.DONE, client_id: uuid.UUID | None = None) -> StoredMessage:
        if self._locked is None:
            raise RuntimeError("append outside store.atomic()")
        self._locked.last_seq += 1
        self._thread_model.objects.filter(pk=self._locked.pk).update(last_seq=self._locked.last_seq, updated_at=now)
        row = self._message_model.objects.create(
            thread=self._locked, seq=self._locked.last_seq, role=role, text=text, status=status, client_id=client_id, created_at=now
        )
        return snapshot(row)

    def update_running(self, message_id: uuid.UUID, **fields: Any) -> bool:
        return self._message_model.objects.filter(pk=message_id, status=Status.RUNNING).update(**fields) > 0

    def close(self, message_id: uuid.UUID, **fields: Any) -> bool:
        """Close an answer unless it is `done`: a late truth may replace a reaper's guess, never a stored answer."""
        if "cost_usd" in fields:
            fields["cost_usd"] = _money(fields["cost_usd"])
        changed = self._message_model.objects.filter(pk=message_id).exclude(status=Status.DONE).update(**fields) > 0
        if changed:
            self._thread_model.objects.filter(pk=self.thread.pk).update(updated_at=timezone.now())
        return changed
