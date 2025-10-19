"""
Base models for Payments v2.0.

Provides common functionality for all payment-related models.
"""

import uuid

from django.db import models
from django.utils import timezone


class UUIDTimestampedModel(models.Model):
    """
    Abstract base model with UUID primary key and timestamps.

    Provides:
    - UUID primary key for security and scalability
    - Created/updated timestamps with timezone awareness
    - Common functionality for all payment models
    """

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When this record was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        """String representation showing ID and creation time."""
        return f"{self.__class__.__name__}({str(self.id)[:8]}...)"

    def __repr__(self):
        """Developer-friendly representation."""
        return f"<{self.__class__.__name__}: {str(self.id)}>"

    @property
    def age_in_seconds(self) -> int:
        """Get age of this record in seconds."""
        return int((timezone.now() - self.created_at).total_seconds())

    @property
    def is_recent(self) -> bool:
        """Check if record was created in the last hour."""
        return self.age_in_seconds < 3600


class TimestampedModel(models.Model):
    """
    Abstract base model with auto-incrementing ID and timestamps.

    Use this for models that don't need UUID (like configuration models).
    """

    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        help_text="When this record was created"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this record was last updated"
    )

    class Meta:
        abstract = True
        ordering = ['-created_at']
