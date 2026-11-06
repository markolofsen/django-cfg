"""The chunk table of the optional vectorisation (decision D6). A host with its own chat tables subclasses it:

    class ThreadChunk(AbstractChatChunk):
        thread = models.ForeignKey(Thread, on_delete=models.CASCADE, related_name="chunks")

        class Meta(AbstractChatChunk.Meta):
            db_table = "assistant_thread_chunk"

One row per run of consecutive messages (see `chunking`), never per message, and no column on the message table. The row keeps the
span, a hash of the text it embedded and the vector; the text is read back from the messages.
"""

from __future__ import annotations

import uuid

from django.db import models


class AbstractChatChunk(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_seq = models.PositiveIntegerField()
    last_seq = models.PositiveIntegerField()
    message_count = models.PositiveSmallIntegerField()
    closed = models.BooleanField(default=False, help_text="Full: its text never changes. The open tail is re-embedded when it grows.")
    text_hash = models.CharField(max_length=64, help_text="sha256 of the embedded text: equal hash, no re-embedding.")
    model = models.CharField(max_length=80, blank=True, default="", help_text="The embedding model that made the vector.")
    embedding = models.JSONField(default=list, help_text="list[float]. A host on pgvector replaces this column with a VectorField.")
    embedded_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["first_seq"]
        constraints = [models.UniqueConstraint(fields=["thread", "first_seq"], name="%(app_label)s_%(class)s_thread_first_uniq")]

    def __str__(self) -> str:
        return f"{self.first_seq}-{self.last_seq}"
