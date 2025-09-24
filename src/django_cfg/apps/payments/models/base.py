"""
Base model classes for the universal payments system.
"""

import uuid
from django.db import models


class TimestampedModel(models.Model):
    """Base model with automatic timestamps."""
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class UUIDTimestampedModel(models.Model):
    """Base model with UUID primary key and automatic timestamps."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier"
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True