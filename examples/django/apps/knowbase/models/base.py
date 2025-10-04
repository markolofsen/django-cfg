"""
Base models for knowledge base application.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.conf import settings
from enum import Enum
import uuid


class ProcessingStatus(models.TextChoices):
    """Document processing status enumeration."""
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    CANCELLED = "cancelled", "Cancelled"


class TimestampedModel(models.Model):
    """Base model with automatic timestamps."""
    
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['-created_at']),
        ]
    
    @property
    def short_uuid(self) -> str:
        """Return first 6 characters of UUID for display."""
        return str(self.id)[:6]


class UserScopedModel(TimestampedModel):
    """Base model with user isolation."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        db_index=True,
        help_text="Owner of this record"
    )
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['user', '-created_at']),
        ]
