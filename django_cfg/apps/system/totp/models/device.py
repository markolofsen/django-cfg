"""TOTP Device model for storing authenticator configuration."""

import uuid

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

from .choices import DeviceStatus

User = get_user_model()


class TOTPDevice(models.Model):
    """
    TOTP authenticator device linked to a user.

    A user can have multiple devices (e.g., phone, backup device).
    Only one device can be primary at a time.
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="totp_devices",
    )

    name = models.CharField(
        max_length=100,
        default="Authenticator",
        help_text="Device name for identification",
    )

    secret = models.CharField(
        max_length=32,
        help_text="Base32-encoded TOTP secret",
    )

    status = models.CharField(
        max_length=20,
        choices=DeviceStatus.choices,
        default=DeviceStatus.PENDING,
        db_index=True,
    )

    is_primary = models.BooleanField(
        default=False,
        help_text="Primary device used for verification",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    confirmed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When device setup was confirmed",
    )

    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Last successful verification",
    )

    last_verified_code = models.CharField(
        max_length=10,
        null=True,
        blank=True,
        help_text="Last verified code to prevent reuse",
    )

    failed_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Consecutive failed verification attempts",
    )

    class Meta:
        app_label = "django_cfg_totp"
        verbose_name = "TOTP Device"
        verbose_name_plural = "TOTP Devices"
        ordering = ["-is_primary", "-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "is_primary"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["user"],
                condition=models.Q(is_primary=True, status=DeviceStatus.ACTIVE),
                name="unique_primary_active_device",
            )
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.user.email})"

    @property
    def is_active(self) -> bool:
        """Check if device is active."""
        return self.status == DeviceStatus.ACTIVE

    @property
    def is_pending(self) -> bool:
        """Check if device is pending confirmation."""
        return self.status == DeviceStatus.PENDING

    def confirm(self) -> None:
        """Confirm device after first successful verification."""
        self.status = DeviceStatus.ACTIVE
        self.confirmed_at = timezone.now()
        self.save(update_fields=["status", "confirmed_at"])

    def disable(self) -> None:
        """Disable the device."""
        self.status = DeviceStatus.DISABLED
        self.is_primary = False
        self.save(update_fields=["status", "is_primary"])

    def record_success(self, code: str) -> None:
        """Record successful verification."""
        self.last_used_at = timezone.now()
        self.last_verified_code = code
        self.failed_attempts = 0
        self.save(update_fields=["last_used_at", "last_verified_code", "failed_attempts"])

    def record_failure(self) -> None:
        """Record failed verification attempt."""
        self.failed_attempts += 1
        self.save(update_fields=["failed_attempts"])

    def make_primary(self) -> None:
        """Make this device the primary one."""
        # Remove primary from other devices
        TOTPDevice.objects.filter(
            user=self.user,
            is_primary=True,
        ).exclude(pk=self.pk).update(is_primary=False)

        self.is_primary = True
        self.save(update_fields=["is_primary"])
