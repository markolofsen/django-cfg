"""
The storage outbox: one row per key (or prefix) whose file must disappear.

Rows are written inside the transaction that deletes the owning object, so a
rollback discards them and a commit makes them durable. A worker
(`sync.worker.drain`) deletes the files later, with retries.
"""

from django.db import models


class StorageDeletion(models.Model):
    """A key or prefix queued for deletion from a storage, and for a CDN purge."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PURGE = "purge", "Deleted, CDN purge pending"
        DONE = "done", "Done"
        FAILED = "failed", "Failed (attempts exhausted)"
        REFUSED = "refused", "Refused by the guard"

    storage_alias = models.CharField(max_length=64, default="default")
    key = models.CharField(max_length=1024, help_text="Object key, or a prefix ending in '/'")
    is_prefix = models.BooleanField(default=False)
    model_label = models.CharField(max_length=128, blank=True)
    object_pk = models.CharField(max_length=64, blank=True)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING)
    attempts = models.PositiveIntegerField(default=0)
    next_attempt_at = models.DateTimeField(db_index=True)
    last_error = models.TextField(blank=True)
    purge_urls = models.JSONField(default=list, blank=True, help_text="URLs still to purge from the CDN")
    claimed_by = models.CharField(max_length=64, blank=True, help_text="Set by an external consumer in queue_only mode")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "storage deletion"
        verbose_name_plural = "storage deletions"
        indexes = [models.Index(fields=["status", "next_attempt_at"], name="cleanup_outbox_due_idx")]
        ordering = ["id"]

    def __str__(self) -> str:
        return f"{self.status} {self.storage_alias}:{self.key}"
