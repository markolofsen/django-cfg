"""Per-user access tables for the ``manage`` backend (keys and OAuth grants)."""

from django.conf import settings
from django.db import models
from django.utils import timezone


class McpKey(models.Model):
    """A per-user MCP key. Only the sha256 of the secret is stored; the secret is shown once, at creation."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mcp_keys")
    name = models.CharField(max_length=40)
    prefix = models.CharField(max_length=12, help_text="First characters of the key, for the user's list")
    key_hash = models.CharField(max_length=64, unique=True, editable=False)
    scopes = models.JSONField(default=list, blank=True)
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)
    last_used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["user", "revoked_at"], name="mcp_key_user_revoked_idx")]

    def __str__(self) -> str:
        return f"{self.prefix}... ({self.name})"

    @property
    def status(self) -> str:
        if self.revoked_at is not None:
            return "revoked"
        return "expired" if self.expires_at <= timezone.now() else "active"


class McpGrant(models.Model):
    """One OAuth client a user allowed (Claude, ChatGPT, ...).

    Nothing in django-cfg creates these yet: its OAuth is stateless. The table
    is here for a project that issues grants itself (``stateful_oauth=True``).
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mcp_grants")
    client_name = models.CharField(max_length=80)
    scopes = models.JSONField(default=list, blank=True)
    refresh_gen = models.PositiveIntegerField(default=0, help_text="Generation of the one refresh token that is valid")
    last_used_at = models.DateTimeField(null=True, blank=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        indexes = [models.Index(fields=["user", "revoked_at"], name="mcp_grant_user_revoked_idx")]

    def __str__(self) -> str:
        return f"{self.client_name} (user {self.user_id})"
