"""Two-factor verification session model."""

import uuid
from datetime import timedelta

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from .choices import SessionStatus

User = get_user_model()

class TwoFactorSession(models.Model):
    """
    Tracks pending 2FA verification for a login session.

    Created after successful primary auth (OTP or password).
    User must verify 2FA before session becomes fully authenticated.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="two_factor_sessions",
    )

    status = models.CharField(
        max_length=20,
        choices=SessionStatus.choices,
        default=SessionStatus.PENDING,
        db_index=True,
    )

    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
    )

    user_agent = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    expires_at = models.DateTimeField(
        db_index=True,
        help_text="Session validity window",
    )

    verified_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    attempts = models.PositiveIntegerField(
        default=0,
        help_text="Failed verification attempts",
    )

    max_attempts = models.PositiveIntegerField(
        default=5,
        help_text="Lock session after N failures",
    )

    class Meta:
        app_label = "django_cfg_totp"
        verbose_name = "Two-Factor Session"
        verbose_name_plural = "Two-Factor Sessions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self) -> str:
        return f"2FA Session {self.id} for {self.user.email} ({self.status})"

    def save(self, *args, **kwargs):
        if not self.expires_at:
            # Default: 5 minutes to complete 2FA
            self.expires_at = timezone.now() + timedelta(minutes=5)
        super().save(*args, **kwargs)

    @property
    def is_pending(self) -> bool:
        """Check if session is pending verification."""
        return self.status == SessionStatus.PENDING

    @property
    def is_verified(self) -> bool:
        """Check if session has been verified."""
        return self.status == SessionStatus.VERIFIED

    @property
    def is_expired(self) -> bool:
        """Check if session has expired."""
        if self.status == SessionStatus.EXPIRED:
            return True
        return timezone.now() > self.expires_at

    @property
    def is_locked(self) -> bool:
        """Check if session is locked due to max attempts."""
        return self.attempts >= self.max_attempts

    @property
    def attempts_remaining(self) -> int:
        """Get remaining verification attempts."""
        return max(0, self.max_attempts - self.attempts)

    def mark_verified(self) -> None:
        """Mark session as verified."""
        self.status = SessionStatus.VERIFIED
        self.verified_at = timezone.now()
        self.save(update_fields=["status", "verified_at"])

    def mark_expired(self) -> None:
        """Mark session as expired."""
        self.status = SessionStatus.EXPIRED
        self.save(update_fields=["status"])

    def mark_failed(self) -> None:
        """Mark session as failed (max attempts exceeded)."""
        self.status = SessionStatus.FAILED
        self.save(update_fields=["status"])

    def record_attempt(self) -> None:
        """Record a failed verification attempt."""
        self.attempts += 1
        if self.attempts >= self.max_attempts:
            self.status = SessionStatus.FAILED
            self.save(update_fields=["attempts", "status"])
        else:
            self.save(update_fields=["attempts"])

    @classmethod
    def create_for_user(
        cls,
        user,
        request=None,
        lifetime_minutes: int = 5,
    ) -> "TwoFactorSession":
        """Create a new 2FA session for user."""
        ip_address = None
        user_agent = ""

        if request:
            ip_address = cls._get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]

        return cls.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=timezone.now() + timedelta(minutes=lifetime_minutes),
        )

    @staticmethod
    def _get_client_ip(request) -> str:
        """Extract client IP from request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "")
