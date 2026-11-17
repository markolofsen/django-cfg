from django.db import models
from django.utils import timezone


class NotionOutbox(models.Model):
    """One lead waiting to be (or already) mirrored into Notion. The row is written in the lead's own transaction."""

    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        SENDING = "sending", "Sending"
        SENT = "sent", "Sent"
        FAILED = "failed", "Failed, will retry"
        DEAD = "dead", "Dead (needs a person)"

    key = models.CharField(max_length=255, unique=True, help_text="<project>:<app.Model>:<pk>, also written to Hub run id")
    target = models.CharField(max_length=64, db_index=True)
    payload = models.JSONField(default=dict, help_text="The NotionLead as it was when the lead was saved (holds PII)")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PENDING, db_index=True)
    attempts = models.PositiveIntegerField(default=0)
    last_error = models.TextField(blank=True)
    notion_page_id = models.CharField(max_length=64, blank=True)
    maybe_created = models.BooleanField(default=False, help_text="The last attempt ended unclear: Notion may have created the page")
    next_attempt_at = models.DateTimeField(default=timezone.now, db_index=True)
    locked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    # Telegram / admin-email fan-out (notify.py). Independent of ``status``. A timestamp means the channel is settled:
    # sent, or skipped on purpose (not configured / no recipients). Never cleared, so a lead is announced once.
    telegram_notified_at = models.DateTimeField(null=True, blank=True)
    email_notified_at = models.DateTimeField(null=True, blank=True)
    ack_notified_at = models.DateTimeField(null=True, blank=True, help_text="Acknowledgement letter to the lead's author: sent, or skipped on purpose")
    ack_email = models.CharField(max_length=254, blank=True, db_index=True, help_text="Address an acknowledgement was actually sent to (24 h per-address limit)")
    notify_attempts = models.PositiveIntegerField(default=0)
    notify_next_at = models.DateTimeField(default=timezone.now, db_index=True)
    notify_error = models.TextField(blank=True)

    class Meta:
        app_label = "django_cfg_notion"
        ordering = ("-created_at",)
        verbose_name = "Notion outbox row"
        verbose_name_plural = "Notion outbox"
        indexes = [models.Index(fields=["status", "next_attempt_at"])]

    def __str__(self) -> str:
        return f"{self.key} [{self.status}]"
