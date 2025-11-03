"""
Authentication models (OTP, etc.).
"""

import random
import string
from datetime import timedelta

from django.db import models
from django.utils import timezone


class OTPSecret(models.Model):
    """Stores One-Time Passwords for authentication."""

    email = models.EmailField(db_index=True)
    secret = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)

    @staticmethod
    def generate_otp(length=6):
        """Generate random numeric OTP."""
        return "".join(random.choices(string.digits, k=length))

    @property
    def is_valid(self):
        """Check if OTP is still valid."""
        return not self.is_used and timezone.now() < self.expires_at

    def mark_used(self):
        """Mark OTP as used."""
        self.is_used = True
        self.save(update_fields=["is_used"])

    def __str__(self):
        return f"OTP for {self.email}"

    class Meta:
        app_label = 'django_cfg_accounts'
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["email", "is_used", "expires_at"]),
        ]
