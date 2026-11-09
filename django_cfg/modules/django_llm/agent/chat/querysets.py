"""Reads of the chat tables, once. A view, a service or a tool calls these and never spells a second copy of a filter.

`for_owner` is the only tenancy filter on threads: a thread outside it reads as missing. Time is passed in, never read here.
The thread must reach its messages as `messages` (the host's FK `related_name`).
"""

from __future__ import annotations

from datetime import datetime

from django.db import models

from django_cfg.modules.django_llm.agent.chat.turn import Role, Status


class ThreadQuerySet(models.QuerySet):
    def for_owner(self, user) -> "ThreadQuerySet":
        """Tenancy: the signed-in user's own threads. Anyone else's, and a missing one, are the same nothing."""
        return self.filter(owner_id=user.pk)

    def with_activity(self) -> "ThreadQuerySet":
        """Adds `message_count` and `last_message_at` for the sessions list (one query)."""
        return self.annotate(message_count=models.Count("messages"), last_message_at=models.Max("messages__created_at"))

    def nonempty(self) -> "ThreadQuerySet":
        """Threads that hold at least one message, with `message_count` and `last_message_at` read from the thread row itself
        (`last_seq` counts every message, none is deleted singly; `updated_at` moves with each write): no join, no group by."""
        return (
            self.filter(last_seq__gt=0)
            .annotate(message_count=models.F("last_seq"), last_message_at=models.F("updated_at"))
        )

    def of_kind(self, kind: str) -> "ThreadQuerySet":
        return self.filter(kind=kind)

    def newest_first(self) -> "ThreadQuerySet":
        return self.order_by("-updated_at", "-created_at")


class MessageQuerySet(models.QuerySet):
    def in_thread(self, thread) -> "MessageQuerySet":
        return self.filter(thread=thread)

    def running(self) -> "MessageQuerySet":
        return self.filter(role=Role.ASSISTANT, status=Status.RUNNING)

    def finished(self) -> "MessageQuerySet":
        return self.exclude(status=Status.RUNNING)

    def sent_by(self, user, since: datetime) -> "MessageQuerySet":
        """The user's own messages since `since`, over all their threads (starting a new session never resets a cap)."""
        return self.filter(thread__owner_id=user.pk, role=Role.USER, created_at__gte=since)

    def window(self, thread, n: int, *, before_seq: int | None = None) -> list:
        """The last `n` messages the model may see, oldest first; `before_seq` leaves out that message and everything after.

        User messages, and answers that said something. A `running` placeholder never. The cut is made in the database,
        so empty rows cannot shrink the window.
        """
        qs = self.in_thread(thread).finished().filter(models.Q(role=Role.USER) | ~models.Q(text=""))
        if before_seq is not None:
            qs = qs.filter(seq__lt=before_seq)
        return list(qs.order_by("-seq")[:n])[::-1]


class AttachmentQuerySet(models.QuerySet):
    """Reads of the attachment table. Tenancy is `for_owner`: someone else's file reads as missing."""

    def for_owner(self, user) -> "AttachmentQuerySet":
        return self.filter(owner_id=user.pk)

    def staged(self) -> "AttachmentQuerySet":
        return self.filter(status="staged")

    def expired(self, cutoff: datetime) -> "AttachmentQuerySet":
        """Staged uploads older than `cutoff`: never sent, safe to delete."""
        return self.filter(status="staged", created_at__lt=cutoff)

    def stored_since(self, user, since: datetime) -> "AttachmentQuerySet":
        return self.filter(owner_id=user.pk, created_at__gte=since)
