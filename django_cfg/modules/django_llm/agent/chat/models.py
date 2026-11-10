"""Abstract tables of the persisted-turn contract. The host subclasses them in its own app; a library, not a forced app.

    class Thread(AbstractThread):
        class Meta(AbstractThread.Meta):
            db_table = "assistant_thread"
            indexes = [models.Index(fields=["owner", "-updated_at"], name="assistant_thread_owner_idx")]

    class Message(AbstractMessage):
        thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="messages")  # the name is the contract
        class Meta(AbstractMessage.Meta):
            db_table = "assistant_message"
            indexes = [models.Index(fields=["thread", "-seq"], name="assistant_msg_thread_seq_idx")]

Attachments (optional): `class Attachment(AbstractAttachment)` with `message = ForeignKey(Message, null=True, on_delete=CASCADE, related_name="attachments")`
(the name is the contract). The message table is untouched; a host that sets no policy never needs the table.

What the schema enforces, whatever a writer forgets: `seq` unique per thread; `client_id` unique per thread when set
(a resend is idempotent); at most one `running` assistant row per thread. There is no delete path in the services.
Constraint names are `<app>_<model>_...`; indexes are the host's (their names are the host's to choose).
"""

from __future__ import annotations

import uuid
from enum import StrEnum

from django.conf import settings
from django.db import models
from django.db.models import Q
from django.utils import timezone

from django_cfg.modules.django_llm.agent.chat.querysets import AttachmentQuerySet, MessageQuerySet, ThreadQuerySet
from django_cfg.modules.django_llm.agent.chat.turn import ErrorCode, Role, Status


def choices(enum: type[StrEnum]) -> list[tuple[str, str]]:
    """The harness owns the vocabulary; the columns only pin it."""
    return [(m.value, m.value.capitalize()) for m in enum]


class AbstractThread(models.Model):
    """One session: a conversation of one chat kind, owned by one user. 'New chat' makes another row; old ones stay listed."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    kind = models.CharField(max_length=40, help_text="A registered chat kind. Plain text: kinds are code, not rows.")
    # A thread is its owner's data: it dies with the account.
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="%(app_label)s_threads")
    title = models.CharField(max_length=200, blank=True, default="", help_text="Set from the first message.")
    context = models.JSONField(default=dict, blank=True, help_text="The kind's context at creation; each turn's own context is laid over it.")
    last_seq = models.PositiveIntegerField(default=0, help_text="The seq of the newest message; the row lock on this counter orders writers.")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ThreadQuerySet.as_manager()

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return f"{self.kind} {self.pk}"


class AbstractMessage(models.Model):
    """A user message or the assistant's answer. `seq` orders them; `client_id` makes a resend idempotent.

    The subclass declares `thread = ForeignKey(<its Thread>, related_name="messages")`.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    seq = models.PositiveIntegerField()
    role = models.CharField(max_length=10, choices=choices(Role))
    text = models.TextField(blank=True, default="")
    parts = models.JSONField(default=list, blank=True, help_text="[{kind, data}] ui payloads the answer carried.")
    tool_calls = models.JSONField(default=list, blank=True, help_text="[{id, name, input, output}] compact; replayed into the model context.")
    trace = models.JSONField(null=True, blank=True, default=None, help_text="TraceDoc v1: how the answer was reached, at the kind's `trace_level` (see `agent/trace`); null when the kind records none. At most 24 KB.")
    status = models.CharField(max_length=10, choices=choices(Status), default=Status.DONE.value)
    error_code = models.CharField(max_length=12, choices=choices(ErrorCode), blank=True, default="")
    model = models.CharField(max_length=80, blank=True, default="", help_text="The slug that served the answer.")
    prompt_version = models.CharField(max_length=40, blank=True, default="", help_text="The chat kind's prompt_version at the time.")
    tokens_in = models.PositiveIntegerField(default=0)
    tokens_out = models.PositiveIntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True, help_text="Empty: the run was cut before it could be priced.")
    latency_ms = models.PositiveIntegerField(default=0)
    client_id = models.UUIDField(null=True, blank=True, help_text="Client-made id of a user message: a resend is not stored twice.")
    created_at = models.DateTimeField(default=timezone.now, help_text="Stamped by the writer from its own clock.")

    objects = MessageQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ["seq"]
        constraints = [
            models.UniqueConstraint(fields=["thread", "seq"], name="%(app_label)s_%(class)s_thread_seq_uniq"),
            models.UniqueConstraint(
                fields=["thread", "client_id"], condition=Q(client_id__isnull=False), name="%(app_label)s_%(class)s_thread_client_uniq"
            ),
            # One run in flight per thread, whatever the writer forgot to check.
            models.UniqueConstraint(
                fields=["thread"], condition=Q(role=Role.ASSISTANT.value, status=Status.RUNNING.value), name="%(app_label)s_%(class)s_one_running"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.role}#{self.seq} ({self.status})"


class AbstractAttachment(models.Model):
    """A file a user attached to a chat message: its own row, so the message table stays as it is.

    `staged` until the message that carries it is stored (then `attached`, and `expired` once its bytes were deleted: `file` is then empty); a staged file nobody sent is reaped after the policy's TTL.
    The subclass declares `message = ForeignKey(<its Message>, null=True, blank=True, on_delete=CASCADE, related_name="attachments")`.
    `mime`, `size` and `sha256` come from the bytes the server read, never from the client's claims.
    """

    STAGED = "staged"
    ATTACHED = "attached"
    EXPIRED = "expired"  # the bytes are deleted (`AttachmentPolicy.keep_days`); the row, the name and the text read from it stay

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="+")
    chat_kind = models.CharField(max_length=40, help_text="The chat kind whose policy accepted the file.")
    media_kind = models.CharField(max_length=12, help_text="image | audio | video | text | document, sniffed from the bytes.")
    name = models.CharField(max_length=200, help_text="The file name the user gave; a label, never a path.")
    mime = models.CharField(max_length=100)
    size = models.PositiveBigIntegerField()
    sha256 = models.CharField(max_length=64)
    storage = models.CharField(max_length=40, default="default", help_text="Django STORAGES alias holding the bytes.")
    file = models.FileField(max_length=255, help_text="The storage key, `chat/<kind>/<uuid>`: never a client name.")
    derived = models.JSONField(default=dict, blank=True, help_text="What was read from the file once (OCR text, transcript); the model-facing cache.")
    status = models.CharField(max_length=10, default="staged")
    created_at = models.DateTimeField(default=timezone.now)

    objects = AttachmentQuerySet.as_manager()

    class Meta:
        abstract = True
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["owner", "status", "created_at"], name="%(app_label)s_%(class)s_own_idx"),
            models.Index(fields=["message"], name="%(app_label)s_%(class)s_msg_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.media_kind} {self.pk} ({self.status})"
