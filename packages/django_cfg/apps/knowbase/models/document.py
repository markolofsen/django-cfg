"""
Document models with pgvector support.
"""

from django.db import models
from pgvector.django import VectorField
from typing import Optional, List
from .base import UserScopedModel, ProcessingStatus, TimestampedModel


class DocumentCategory(TimestampedModel):
    """Document category for organization and access control."""
    
    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="Category name"
    )
    description = models.TextField(
        blank=True,
        help_text="Category description"
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Whether documents in this category are publicly accessible"
    )
    
    class Meta:
        db_table = 'django_cfg_knowbase_document_categories'
        verbose_name = 'Document Category'
        verbose_name_plural = 'Document Categories'
        ordering = ['name']
    
    def __str__(self) -> str:
        return f"{self.name} ({'Public' if self.is_public else 'Private'})"


class Document(UserScopedModel):
    """Knowledge document with processing status tracking."""
    
    # Custom managers
    from ..managers.document import DocumentManager
    objects = DocumentManager()
    
    title = models.CharField(
        max_length=512,
        help_text="Document title"
    )
    content = models.TextField(
        help_text="Full document content"
    )
    # Multiple categories field
    categories = models.ManyToManyField(
        DocumentCategory,
        blank=True,
        related_name='documents',
        help_text="Document categories (supports multiple)"
    )
    is_public = models.BooleanField(
        default=True,
        help_text="Whether this document is publicly accessible"
    )
    content_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text="SHA-256 hash for duplicate detection"
    )
    file_type = models.CharField(
        max_length=100,
        default="text/plain",
        help_text="MIME type of original file"
    )
    file_size = models.PositiveIntegerField(
        default=0,
        help_text="Original file size in bytes"
    )
    
    # Processing status
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
        db_index=True
    )
    processing_started_at = models.DateTimeField(null=True, blank=True)
    processing_completed_at = models.DateTimeField(null=True, blank=True)
    processing_error = models.TextField(blank=True, default="")
    
    # Chunk statistics
    chunks_count = models.PositiveIntegerField(default=0)
    total_tokens = models.PositiveIntegerField(default=0)
    
    # Cost tracking for monitoring
    total_cost_usd = models.FloatField(
        default=0.0,
        help_text="Total processing cost in USD"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Additional document metadata"
    )
    
    class Meta:
        db_table = 'django_cfg_knowbase_documents'
        indexes = [
            models.Index(fields=['user', 'processing_status']),
            models.Index(fields=['content_hash']),
            models.Index(fields=['-processing_completed_at']),
            models.Index(fields=['is_public', '-created_at']),  # For multiple categories queries
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'content_hash'],
                name='unique_user_document'
            )
        ]
    
    def save(self, *args, **kwargs):
        """Override save to generate content_hash if not provided."""
        if not self.content_hash and self.content:
            import hashlib
            self.content_hash = hashlib.sha256(self.content.encode()).hexdigest()
        
        # Set file_size if not provided
        if not self.file_size and self.content:
            self.file_size = len(self.content.encode('utf-8'))
        
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.title} ({self.user.username})"
    
    @property
    def is_processed(self) -> bool:
        """Check if document processing is completed."""
        return self.processing_status == ProcessingStatus.COMPLETED
    
    @property
    def processing_duration(self) -> Optional[float]:
        """Calculate processing duration in seconds."""
        if self.processing_started_at and self.processing_completed_at:
            delta = self.processing_completed_at - self.processing_started_at
            return delta.total_seconds()
        return None
    
    @property
    def is_publicly_accessible(self) -> bool:
        """Check if document is publicly accessible (document and at least one category must be public)."""
        if not self.is_public:
            return False
        
        # If document has categories, at least one must be public
        if self.categories.exists():
            return self.categories.filter(is_public=True).exists()
        
        # If no categories assigned, document is public by default
        return True
    
    def get_all_categories(self):
        """Get all categories for this document."""
        return list(self.categories.all())
    
    def add_category(self, category):
        """Add a category to this document."""
        self.categories.add(category)
    
    def remove_category(self, category):
        """Remove a category from this document."""
        self.categories.remove(category)
    
    def set_categories(self, categories_list):
        """Set multiple categories for this document."""
        self.categories.set(categories_list)


class DocumentChunk(UserScopedModel):
    """Text chunk with vector embedding for semantic search."""
    
    # Custom managers
    from ..managers.document import DocumentChunkManager
    objects = DocumentChunkManager()
    
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='chunks',
        help_text="Parent document"
    )
    content = models.TextField(
        help_text="Chunk text content"
    )
    chunk_index = models.PositiveIntegerField(
        help_text="Sequential chunk number within document"
    )
    
    # Vector embedding (1536 dimensions for OpenAI text-embedding-ada-002)
    embedding = VectorField(
        dimensions=1536,
        help_text="Vector embedding for semantic search"
    )
    
    # Chunk statistics
    token_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of tokens in chunk"
    )
    character_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of characters in chunk"
    )
    
    # Processing metadata
    embedding_model = models.CharField(
        max_length=100,
        default="text-embedding-ada-002",
        help_text="Model used for embedding generation"
    )
    embedding_cost = models.FloatField(
        default=0.0,
        help_text="Cost in USD for embedding generation"
    )
    
    # Additional metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Chunk-specific metadata"
    )
    
    class Meta:
        db_table = 'django_cfg_knowbase_document_chunks'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['document', 'chunk_index']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['document', 'chunk_index'],
                name='unique_document_chunk'
            )
        ]
        ordering = ['document', 'chunk_index']
    
    def __str__(self) -> str:
        return f"Chunk {self.chunk_index} of {self.document.title}"
    
    @classmethod
    def semantic_search(
        cls,
        user,
        query_embedding: List[float],
        limit: int = 5,
        similarity_threshold: float = 0.7
    ):
        """Perform semantic search using pgvector."""
        from pgvector.django import CosineDistance
        
        return cls.objects.filter(user=user).annotate(
            similarity=1 - CosineDistance('embedding', query_embedding)
        ).filter(
            similarity__gte=similarity_threshold
        ).order_by('-similarity')[:limit]
