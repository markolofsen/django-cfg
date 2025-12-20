"""Backup recovery codes for 2FA bypass."""

import hashlib
import secrets

from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class BackupCode(models.Model):
    """
    Backup recovery codes for 2FA bypass.

    Generated when 2FA is enabled. Each code can only be used once.
    Codes are stored as SHA256 hashes for security.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="backup_codes",
    )

    code_hash = models.CharField(
        max_length=64,
        help_text="SHA256 hash of the backup code",
    )

    is_used = models.BooleanField(
        default=False,
        db_index=True,
    )

    used_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "django_cfg_totp"
        verbose_name = "Backup Code"
        verbose_name_plural = "Backup Codes"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "is_used"]),
        ]

    def __str__(self) -> str:
        status = "used" if self.is_used else "available"
        return f"Backup code for {self.user.email} ({status})"

    @staticmethod
    def hash_code(code: str) -> str:
        """Generate SHA256 hash of a code."""
        return hashlib.sha256(code.encode()).hexdigest()

    @staticmethod
    def generate_code(length: int = 8) -> str:
        """Generate a random backup code."""
        alphabet = "abcdefghijklmnopqrstuvwxyz0123456789"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def verify(self, code: str) -> bool:
        """
        Verify a code against this backup code.

        Returns True if valid and not already used.
        Does NOT consume the code - call consume() separately.
        """
        if self.is_used:
            return False
        return self.code_hash == self.hash_code(code.lower().strip())

    def consume(self) -> None:
        """Mark the code as used."""
        self.is_used = True
        self.used_at = timezone.now()
        self.save(update_fields=["is_used", "used_at"])
