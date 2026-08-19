"""A record of what was actually sent.

Sending is threaded and the transport is an HTTP gateway, so a failure surfaces
nowhere a human looks — this is the trail that answers "did that user get their
letter, in which language, and if not, why".

It records the **attempt**, not delivery. The gateway accepting a message is not
proof it reached an inbox; bounces and spam placement happen later and are the
provider's story to tell. Treating "queued" as "delivered" is the error this
model must not encourage, which is why the status vocabulary stops at `sent`.

**The row is now written before the attempt, not after it.** For the life of this
model `queued` was declared, made the field default, and written by nothing:
measured on cmdop production, 112 rows, `queued` = 0. Every row was created after
the transport had already returned, so a process that died mid-send left no trace
of the letter at all — the failure with no evidence. `dedup_key` is what makes
that pre-write safe to retry: it identifies the letter rather than the row, so a
reconciler can tell "this was never attempted" from "this was attempted twice".
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

    dedup_key = models.CharField(
        max_length=200,
        blank=True,
        db_index=True,
        help_text="Identifies the letter, not the row: event + channel + recipient. "
                  "Two rows sharing one is a double send, which is the thing a "
                  "retry must be able to check for before sending again.",
    )

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the transport accepted it. NULL on a `queued` row that "
                  "was never resolved — the signature of a process that died "
                  "mid-send, and the only way to find one.",
    )

    class Meta:
        app_label = "django_cfg_mailer"
        verbose_name = "Email log"
        verbose_name_plural = "Email log"
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=["key", "-created_at"]),
            # Finds abandoned intents. Partial, because the rows worth scanning
            # for are the rare ones: `queued` is a transient state that a healthy
            # send leaves within seconds.
            models.Index(
                fields=["created_at"],
                condition=models.Q(status="queued"),
                name="mailer_log_stuck_queued_idx",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.key or 'email'} -> {self.recipient} ({self.status})"

    @property
    def is_abandoned(self) -> bool:
        """Still `queued` with nothing recorded against it.

        Not "is it old": age is the caller's policy, and a send in flight is
        legitimately queued for a moment. This answers only the structural half —
        the row was opened and never closed.
        """
        return self.status == self.Status.QUEUED and self.sent_at is None
