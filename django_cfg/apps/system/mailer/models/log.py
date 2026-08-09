"""A record of what was actually sent.

Sending is threaded and the transport is an HTTP gateway, so a failure surfaces
nowhere a human looks — this is the trail that answers "did that user get their
letter, in which language, and if not, why".

It records the **attempt**, not delivery. The gateway accepting a message is not
proof it reached an inbox; bounces and spam placement happen later and are the
provider's story to tell. Treating "queued" as "delivered" is the error this
model must not encourage, which is why the status vocabulary stops at `sent`.
"""

from __future__ import annotations

from django.db import models


class EmailLog(models.Model):
    """One send attempt of one letter to one address."""

    class Status(models.TextChoices):
        QUEUED = "queued", "Queued"
        SENT = "sent", "Handed to the transport"
        FAILED = "failed", "Failed"

    key = models.CharField(
        max_length=64,
        db_index=True,
        blank=True,
        help_text="Which letter this was, e.g. 'welcome'. Blank for ad-hoc mail.",
    )
    recipient = models.EmailField(db_index=True)
    subject = models.CharField(max_length=255, blank=True)
    locale = models.CharField(
        max_length=16,
        blank=True,
        help_text="The locale it rendered in — the field that answers 'why was it in English'.",
    )

    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.QUEUED, db_index=True
    )
    error = models.TextField(
        blank=True,
        help_text="Transport error, when the attempt failed. Kept verbatim: a "
                  "paraphrased provider message is not diagnosable.",
    )

    # Not a FK to the user: mail is also sent to addresses with no account, and a
    # letter's record should outlive the account being deleted.
    user_id = models.IntegerField(
        null=True, blank=True, db_index=True, help_text="The recipient's user id, if any."
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        app_label = "django_cfg_mailer"
        verbose_name = "Email log"
        verbose_name_plural = "Email log"
        ordering = ("-created_at",)
        indexes = [models.Index(fields=["key", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.key or 'email'} -> {self.recipient} ({self.status})"
