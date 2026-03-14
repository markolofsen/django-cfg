"""
Anonymous session tracking for frontend monitor.

Assigned by the browser client on first visit (UUID stored in localStorage/cookie).
Linked to a User when the visitor authenticates.
"""

import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class AnonymousSession(models.Model):
    """
    Represents a browser session for an anonymous (or later authenticated) visitor.

    The session_id UUID is generated on the client side and sent with every event.
    When the user logs in, the signal handler links this session to the User.
    """

    session_id = models.UUIDField(
        primary_key=True,
        help_text="UUID assigned by the browser client (stored in localStorage/cookie)",
    )

    ip_address = models.GenericIPAddressField(
        help_text="Client IP address at the time of first event",
    )

    user_agent = models.TextField(
        blank=True,
        default="",
        help_text="Browser User-Agent string",
    )

    fingerprint = models.CharField(
        max_length=64,
        blank=True,
        default="",
        db_index=True,
        help_text="Optional browser fingerprint hash (computed client-side)",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="anonymous_sessions",
        help_text="Authenticated user this session was matched to",
    )

    first_seen = models.DateTimeField(auto_now_add=True)

    last_seen = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="Last time an event was received from this session",
    )

    matched_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this anonymous session was linked to a user",
    )

    class Meta:
        app_label = "django_cfg_monitor"
        verbose_name = "Anonymous Session"
        verbose_name_plural = "Anonymous Sessions"
        ordering = ["-last_seen"]
        indexes = [
            models.Index(fields=["ip_address", "last_seen"]),
        ]

    def __str__(self) -> str:
        if self.user:
            return f"Session {str(self.session_id)[:8]}… → {self.user}"
        return f"Session {str(self.session_id)[:8]}… (anonymous)"

    @property
    def is_matched(self) -> bool:
        return self.user_id is not None
