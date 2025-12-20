"""Enum choices for TOTP models."""

from django.db import models


class DeviceStatus(models.TextChoices):
    """TOTP device status."""

    PENDING = "pending", "Pending Confirmation"
    ACTIVE = "active", "Active"
    DISABLED = "disabled", "Disabled"


class SessionStatus(models.TextChoices):
    """Two-factor session verification status."""

    PENDING = "pending", "Pending Verification"
    VERIFIED = "verified", "Verified"
    EXPIRED = "expired", "Expired"
    FAILED = "failed", "Failed (Max Attempts)"
