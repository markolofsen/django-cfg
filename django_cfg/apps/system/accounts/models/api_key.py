"""
User API key model for service-to-service authentication.

Each user has exactly one API key that acts as a long-lived alternative
to JWT tokens. Keys are auto-generated on user creation and can be
regenerated on demand.
"""

import uuid

from django.db import models


class UserAPIKey(models.Model):
    """Per-user API key for automated/service access."""

    user = models.OneToOneField(
        "django_cfg_accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="api_key",
    )
    key = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        help_text="API key in plain text (UUIDv4).",
    )
    reissued_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the key was last regenerated.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "django_cfg_accounts"
        verbose_name = "User API Key"
        verbose_name_plural = "User API Keys"

    def __str__(self) -> str:
        return f"API key for {self.user.email}"

    def regenerate(self) -> "UserAPIKey":
        """Generate a new key and update reissued_at."""
        from django.utils import timezone

        self.key = uuid.uuid4()
        self.reissued_at = timezone.now()
        self.save(update_fields=["key", "reissued_at"])
        return self

    @property
    def masked_key(self) -> str:
        """Return a masked representation of the key for display."""
        key_str = str(self.key)
        if len(key_str) < 12:
            return key_str
        return f"{key_str[:6]}{'•' * (len(key_str) - 12)}{key_str[-6:]}"
