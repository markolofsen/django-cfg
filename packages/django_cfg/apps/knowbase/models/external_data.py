"""
External Data models for integrating external Django models into django_cfg.apps.knowbase.

Provides a unified way to vectorize and search any external data source.
"""

from django.db import models
from django.conf import settings
from pgvector.django import VectorField
from typing import Optional, List, Dict, Any
import json
from enum import Enum

from .base import UserScopedModel, ProcessingStatus, TimestampedModel
from .document import DocumentCategory


class ExternalDataType(models.TextChoices):
    """Types of external data sources."""
    MODEL = "model", "Django Model"
    API = "api", "API Endpoint"
    DATABASE = "database", "Database Query"
    FILE = "file", "File System"
    CUSTOM = "custom", "Custom Source"


class ExternalDataStatus(models.TextChoices):
    """Processing status for external data."""
    PENDING = "pending", "Pending"
    PROCESSING = "processing", "Processing"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    OUTDATED = "outdated", "Outdated"


class ExternalData(UserScopedModel):
    """
    External data source integrated into knowbase for AI search.
    
    This model represents any external data source (Django models, APIs, etc.)
    that has been integrated into the knowledge base for semantic search.
    """
    
    # Manager will be set after class definition
    from ..managers.external_data import ExternalDataManager
    objects = ExternalDataManager()
    
    # Basic information
    title = models.CharField(
        max_length=512,
        help_text="Human-readable title for this external data source"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this external data contains"
    )
    
    # Source configuration
    source_type = models.CharField(
        max_length=20,
        choices=ExternalDataType.choices,
        default=ExternalDataType.MODEL,
        help_text="Type of external data source"
    )
    source_identifier = models.CharField(
        max_length=255,
        blank=True,
        help_text="Unique identifier for the data source (e.g., 'vehicles_data.Vehicle')"
    )
    source_config = models.JSONField(
        default=dict,
        blank=True,
        help_text="Configuration for data extraction (fields, filters, etc.)"
    )
    
    # Content and metadata
    content = models.TextField(
        blank=True,
        help_text="Extracted text content for vectorization"
    )
    content_hash = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="SHA256 hash of content for change detection"
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata from the source"
    )
    
    # Processing status
    status = models.CharField(
        max_length=20,
        choices=ExternalDataStatus.choices,
        default=ExternalDataStatus.PENDING,
        help_text="Current processing status"
    )
    processing_error = models.TextField(
        blank=True,
        help_text="Error message if processing failed"
    )
    
    # Vectorization settings
    chunk_size = models.PositiveIntegerField(
        default=1000,
        help_text="Size of text chunks for vectorization"
    )
    overlap_size = models.PositiveIntegerField(
        default=200,
        help_text="Overlap between chunks"
    )
    embedding_model = models.CharField(
        max_length=100,
        default="text-embedding-ada-002",
        help_text="Embedding model used for vectorization"
    )
    
    # Search settings
    similarity_threshold = models.FloatField(
        default=0.5,
        help_text="Similarity threshold for this external data (0.0-1.0). Lower = more results, higher = more precise"
    )
    
    # Processing timestamps
    processed_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When the data was last processed"
    )
    source_updated_at = models.DateTimeField(
        null=True, blank=True,
        help_text="When the source data was last updated"
    )
    
    # Statistics
    total_chunks = models.PositiveIntegerField(
        default=0,
        help_text="Total number of chunks created"
    )
    total_tokens = models.PositiveIntegerField(
        default=0,
        help_text="Total tokens processed"
    )
    processing_cost = models.FloatField(
        default=0.0,
        help_text="Total cost for processing this data (USD)"
    )
    
    # Organization
    category = models.ForeignKey(
        DocumentCategory,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        help_text="Category for organization"
    )
    tags = models.JSONField(
        default=list,
        blank=True,
        help_text="Tags for categorization and filtering"
    )
    
    # Access control
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this data source is active for search"
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this data is publicly searchable"
    )
    
    class Meta:
        db_table = 'django_cfg_knowbase_external_data'
        verbose_name = 'External Data'
        verbose_name_plural = 'External Data'
        unique_together = [['user', 'source_identifier']]
        indexes = [
            models.Index(fields=['user', 'source_type']),
            models.Index(fields=['status']),
            models.Index(fields=['is_active']),
            models.Index(fields=['processed_at']),
            models.Index(fields=['source_identifier']),
            models.Index(fields=['content_hash']),
        ]
        ordering = ['-processed_at', '-created_at']
    
    def save(self, *args, **kwargs):
        """Override save to generate content_hash if not provided."""
        # Store original hash for comparison in signals
        if self.pk:
            try:
                original = ExternalData.objects.get(pk=self.pk)
                self._original_content_hash = original.content_hash
            except ExternalData.DoesNotExist:
                self._original_content_hash = None
        else:
            self._original_content_hash = None
            
        # Generate hash if not provided
        if not self.content_hash and self.content:
            import hashlib
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()
        elif self.content:
            # Regenerate hash if content exists (to catch manual content changes)
            import hashlib
            new_hash = hashlib.sha256(self.content.encode()).hexdigest()
            if self.content_hash != new_hash:
                self.content_hash = new_hash
                
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.title} ({self.source_type})"
    
    @property
    def full_name(self) -> str:
        """Full name including source type."""
        return f"{self.title} ({self.get_source_type_display()})"
    
    @property
    def is_processed(self) -> bool:
        """Check if data has been successfully processed."""
        return self.status == ExternalDataStatus.COMPLETED
    
    @property
    def is_outdated(self) -> bool:
        """Check if data needs reprocessing."""
        return (
            self.status == ExternalDataStatus.OUTDATED or
            (self.source_updated_at and self.processed_at and 
             self.source_updated_at > self.processed_at)
        )
    
    @property
    def chunks_count(self) -> int:
        """Get the number of chunks for this external data."""
        return self.chunks.count()
    
    def get_config_value(self, key: str, default=None):
        """Get a configuration value."""
        return self.source_config.get(key, default)
    
    def set_config_value(self, key: str, value):
        """Set a configuration value."""
        self.source_config[key] = value
        self.save(update_fields=['source_config'])
    
    def add_tag(self, tag: str):
        """Add a tag if it doesn't exist."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.save(update_fields=['tags'])
    
    def remove_tag(self, tag: str):
        """Remove a tag if it exists."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.save(update_fields=['tags'])


class ExternalDataChunk(TimestampedModel):
    """
    Vectorized chunk of external data content.
    
    Similar to DocumentChunk but for external data sources.
    """
    
    # Manager will be set after class definition
    objects = models.Manager()  # Temporary default manager
    
    # Relationships
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        db_index=True,
        help_text="Owner of this chunk"
    )
    external_data = models.ForeignKey(
        ExternalData,
        on_delete=models.CASCADE,
        related_name='chunks',
        help_text="External data this chunk belongs to"
    )
    
    # Content
    content = models.TextField(
        blank=True,
        help_text="Text content of the chunk"
    )
    chunk_index = models.PositiveIntegerField(
        default=0,
        help_text="Sequential index of this chunk within the external data"
    )
    
    # Vector embedding
    embedding = VectorField(
        dimensions=1536,  # OpenAI ada-002 default
        null=True, blank=True,
        help_text="Vector embedding for semantic search"
    )
    embedding_model = models.CharField(
        max_length=100,
        default="text-embedding-ada-002",
        help_text="Model used for embedding generation"
    )
    
    # Metrics
    token_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of tokens in this chunk"
    )
    character_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of characters in this chunk"
    )
    embedding_cost = models.FloatField(
        default=0.0,
        help_text="Cost for generating this embedding (USD)"
    )
    
    # Context information
    chunk_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional metadata for this specific chunk"
    )
    
    class Meta:
        db_table = 'django_cfg_knowbase_external_data_chunk'
        verbose_name = 'External Data Chunk'
        verbose_name_plural = 'External Data Chunks'
        unique_together = [['external_data', 'chunk_index']]
        indexes = [
            models.Index(fields=['user', 'external_data']),
            models.Index(fields=['embedding_model']),
            models.Index(fields=['token_count']),
            models.Index(fields=['chunk_index']),
        ]
        ordering = ['external_data', 'chunk_index']
    
    def __str__(self) -> str:
        return f"{self.external_data.title} - Chunk {self.chunk_index}"
    
    @property
    def content_preview(self) -> str:
        """Get a preview of the chunk content."""
        if not self.content:
            return "No content"
        if len(self.content) <= 100:
            return self.content
        return self.content[:100] + "..."
    
    @property
    def embedding_info(self) -> str:
        """Get embedding information."""
        if not self.embedding:
            return "No embedding"
        return f"{len(self.embedding)} dimensions"
    
    @property
    def similarity_search_ready(self) -> bool:
        """Check if chunk is ready for similarity search."""
        return self.embedding is not None
    
    @property
    def source_info(self) -> Dict[str, Any]:
        """Get source information for this chunk."""
        return {
            'source_type': self.external_data.source_type,
            'source_identifier': self.external_data.source_identifier,
            'title': self.external_data.title,
            'chunk_index': self.chunk_index,
            'total_chunks': self.external_data.total_chunks,
        }

