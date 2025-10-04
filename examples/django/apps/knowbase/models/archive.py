"""
Archive models for universal document processing.

Supports any type of compressed document collections with context-aware chunking.
"""

from django.db import models
from pgvector.django import VectorField
from typing import Optional, List, Dict, Any
import hashlib
import mimetypes
from pathlib import Path
from enum import Enum

from .base import UserScopedModel, ProcessingStatus, TimestampedModel
from .document import DocumentCategory


class ArchiveType(models.TextChoices):
    """Supported archive formats."""
    ZIP = "zip", "ZIP"
    TAR = "tar", "TAR"
    TAR_GZ = "tar.gz", "TAR.GZ"
    TAR_BZ2 = "tar.bz2", "TAR.BZ2"


class ContentType(models.TextChoices):
    """Content type classification for items."""
    DOCUMENT = "document", "Document"      # PDF, DOCX, TXT, MD
    CODE = "code", "Code"                 # Programming files
    IMAGE = "image", "Image"              # Images (for OCR)
    DATA = "data", "Data"                 # JSON, CSV, XML
    ARCHIVE = "archive", "Archive"        # Nested archives
    UNKNOWN = "unknown", "Unknown"        # Unprocessable


class ChunkType(models.TextChoices):
    """Chunk type classification."""
    TEXT = "text", "Text"                 # Regular text content
    CODE = "code", "Code"                 # Code blocks
    HEADING = "heading", "Heading"        # Document headings
    METADATA = "metadata", "Metadata"     # File metadata
    TABLE = "table", "Table"              # Tabular data
    LIST = "list", "List"                 # Lists and enumerations


class DocumentArchive(UserScopedModel):
    """Universal archive entity for any document collection."""
    
    # Custom managers
    from ..managers.archive import DocumentArchiveManager
    objects = DocumentArchiveManager()
    
    title = models.CharField(
        max_length=512,
        help_text="Archive title"
    )
    description = models.TextField(
        blank=True,
        help_text="Archive description"
    )
    
    # Categories relationship (reuse existing DocumentCategory)
    categories = models.ManyToManyField(
        DocumentCategory,
        blank=True,
        related_name='archives',
        help_text="Archive categories (supports multiple)"
    )
    
    is_public = models.BooleanField(
        default=True,
        help_text="Whether this archive is publicly accessible"
    )
    
    # Archive file storage
    archive_file = models.FileField(
        upload_to='archives/%Y/%m/%d/',
        help_text="Uploaded archive file"
    )
    
    # Archive metadata
    original_filename = models.CharField(
        max_length=255,
        help_text="Original uploaded filename"
    )
    file_size = models.PositiveIntegerField(
        default=0,
        help_text="Archive size in bytes"
    )
    archive_type = models.CharField(
        max_length=20,
        choices=ArchiveType.choices,
        help_text="Archive format"
    )
    content_hash = models.CharField(
        max_length=64,
        db_index=True,
        help_text="SHA-256 hash for duplicate detection"
    )
    
    # Processing status (synchronous processing)
    processing_status = models.CharField(
        max_length=20,
        choices=ProcessingStatus.choices,
        default=ProcessingStatus.PENDING,
        db_index=True
    )
    processed_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text="When processing completed"
    )
    processing_error = models.TextField(
        blank=True, 
        default="",
        help_text="Error message if processing failed"
    )
    processing_duration_ms = models.PositiveIntegerField(
        default=0,
        help_text="Processing time in milliseconds"
    )
    
    # Statistics
    total_items = models.PositiveIntegerField(
        default=0,
        help_text="Total items in archive"
    )
    processed_items = models.PositiveIntegerField(
        default=0,
        help_text="Successfully processed items"
    )
    total_chunks = models.PositiveIntegerField(
        default=0,
        help_text="Total chunks created"
    )
    vectorized_chunks = models.PositiveIntegerField(
        default=0,
        help_text="Chunks with embeddings"
    )
    total_tokens = models.PositiveIntegerField(
        default=0,
        help_text="Total tokens across all chunks"
    )
    total_cost_usd = models.FloatField(
        default=0.0,
        help_text="Total processing cost in USD"
    )
    
    # Metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Additional archive metadata"
    )
    
    class Meta:
        db_table = 'django_cfg_knowbase_document_archives'
        indexes = [
            models.Index(fields=['user', 'processing_status']),
            models.Index(fields=['content_hash']),
            models.Index(fields=['-processed_at']),
            models.Index(fields=['is_public', '-created_at']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'content_hash'],
                name='unique_user_archive'
            )
        ]
        verbose_name = 'Document Archive'
        verbose_name_plural = 'Document Archives'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """Override save to generate content_hash if not provided."""
        # content_hash will be set by the service when processing file
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.title} ({self.user.username})"
    
    @property
    def is_processed(self) -> bool:
        """Check if archive processing is completed."""
        return self.processing_status == ProcessingStatus.COMPLETED
    
    @property
    def processing_progress(self) -> float:
        """Calculate processing progress as percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.processed_items / self.total_items) * 100
    
    @property
    def vectorization_progress(self) -> float:
        """Calculate vectorization progress as percentage."""
        if self.total_chunks == 0:
            return 0.0
        return (self.vectorized_chunks / self.total_chunks) * 100
    
    def get_file_tree(self) -> Dict[str, Any]:
        """Build hierarchical file tree structure."""
        items = self.items.all().order_by('relative_path')
        tree: Dict[str, Any] = {}
        
        for item in items:
            parts = item.relative_path.split('/')
            current = tree
            
            for part in parts[:-1]:  # All except filename
                if part not in current:
                    current[part] = {'type': 'directory', 'children': {}}
                current = current[part]['children']
            
            # Add file
            filename = parts[-1]
            current[filename] = {
                'type': 'file',
                'id': str(item.id),
                'size': item.file_size,
                'content_type': item.content_type,
                'language': item.language,
                'is_processable': item.is_processable,
                'chunks_count': item.chunks_count
            }
        
        return tree


class ArchiveItem(UserScopedModel):
    """Individual file/document within archive."""
    
    # Custom managers
    from ..managers.archive import ArchiveItemManager
    objects = ArchiveItemManager()
    
    archive = models.ForeignKey(
        DocumentArchive,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Parent archive"
    )
    
    # File metadata
    relative_path = models.CharField(
        max_length=1024,
        help_text="Path within archive"
    )
    item_name = models.CharField(
        max_length=255,
        help_text="Item name"
    )
    item_type = models.CharField(
        max_length=100,
        help_text="MIME type"
    )
    content_type = models.CharField(
        max_length=20,
        choices=ContentType.choices,
        default=ContentType.UNKNOWN,
        help_text="Content classification"
    )
    file_size = models.PositiveIntegerField(
        default=0,
        help_text="Item size in bytes"
    )
    content_hash = models.CharField(
        max_length=64,
        help_text="SHA-256 hash of item content"
    )
    
    # Content processing
    raw_content = models.TextField(
        blank=True,
        help_text="Extracted text content"
    )
    is_processable = models.BooleanField(
        default=False,
        help_text="Whether item can be processed for chunks"
    )
    
    # Metadata for context
    language = models.CharField(
        max_length=50,
        blank=True,
        help_text="Programming language or document language"
    )
    encoding = models.CharField(
        max_length=50,
        default='utf-8',
        help_text="Character encoding"
    )
    
    # Processing results
    chunks_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of chunks created"
    )
    total_tokens = models.PositiveIntegerField(
        default=0,
        help_text="Total tokens in all chunks"
    )
    processing_cost = models.FloatField(
        default=0.0,
        help_text="Processing cost for this item"
    )
    
    # Additional metadata
    metadata = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Item-specific metadata"
    )
    
    class Meta:
        db_table = 'django_cfg_knowbase_archive_items'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['archive', 'relative_path']),
            models.Index(fields=['content_type', 'is_processable']),
            models.Index(fields=['language']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['archive', 'relative_path'],
                name='unique_archive_item_path'
            )
        ]
        ordering = ['archive', 'relative_path']
        verbose_name = 'Archive Item'
        verbose_name_plural = 'Archive Items'
    
    def save(self, *args, **kwargs):
        """Override save to set computed fields."""
        if self.raw_content and not self.content_hash:
            self.content_hash = hashlib.sha256(self.raw_content.encode()).hexdigest()
        
        # Detect item type and programming language
        if not self.item_type:
            self.item_type, _ = mimetypes.guess_type(self.item_name)
            if not self.item_type:
                self.item_type = 'application/octet-stream'
        
        if not self.language:
            self.language = self.detect_programming_language()
        
        if not self.content_type or self.content_type == ContentType.UNKNOWN:
            self.content_type = self.detect_content_type()
        
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.relative_path} in {self.archive.title}"
    
    def detect_programming_language(self) -> str:
        """Detect programming language from file extension."""
        LANGUAGE_MAP = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.jsx': 'react',
            '.tsx': 'react-typescript',
            '.java': 'java',
            '.go': 'golang',
            '.rs': 'rust',
            '.cpp': 'cpp',
            '.c': 'c',
            '.php': 'php',
            '.rb': 'ruby',
            '.md': 'markdown',
            '.yml': 'yaml',
            '.yaml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sql': 'sql',
            '.sh': 'bash',
            '.dockerfile': 'dockerfile',
            '.tf': 'terraform',
        }
        
        file_path = Path(self.item_name)
        extension = file_path.suffix.lower()
        
        # Special cases
        if file_path.name.lower() in ['dockerfile', 'makefile']:
            return file_path.name.lower()
        
        return LANGUAGE_MAP.get(extension, '')
    
    def detect_content_type(self) -> str:
        """Detect content type from file extension and MIME type."""
        file_path = Path(self.item_name)
        extension = file_path.suffix.lower()
        
        # Code files
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs',
            '.cpp', '.c', '.h', '.hpp', '.php', '.rb', '.cs', '.swift',
            '.kt', '.scala', '.clj', '.hs', '.ml', '.fs', '.elm'
        }
        
        # Document files
        document_extensions = {
            '.md', '.txt', '.rst', '.adoc', '.pdf', '.docx', '.doc'
        }
        
        # Data files
        data_extensions = {
            '.json', '.csv', '.xml', '.yml', '.yaml', '.toml', '.ini'
        }
        
        # Image files
        image_extensions = {
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'
        }
        
        # Archive files
        archive_extensions = {
            '.zip', '.tar', '.gz', '.bz2', '.7z', '.rar'
        }
        
        if extension in code_extensions:
            return ContentType.CODE
        elif extension in document_extensions:
            return ContentType.DOCUMENT
        elif extension in data_extensions:
            return ContentType.DATA
        elif extension in image_extensions:
            return ContentType.IMAGE
        elif extension in archive_extensions:
            return ContentType.ARCHIVE
        else:
            return ContentType.UNKNOWN
    
    @property
    def file_extension(self) -> str:
        """Get file extension."""
        return Path(self.item_name).suffix.lower()
    
    @property
    def is_code_file(self) -> bool:
        """Check if item is a code file."""
        return self.content_type == ContentType.CODE
    
    @property
    def is_document_file(self) -> bool:
        """Check if item is a document file."""
        return self.content_type == ContentType.DOCUMENT


class ArchiveItemChunk(UserScopedModel):
    """Context-aware chunk with rich parent references."""
    
    # Custom managers
    from ..managers.archive import ArchiveItemChunkManager
    objects = ArchiveItemChunkManager()
    
    # Parent references
    archive = models.ForeignKey(
        DocumentArchive,
        on_delete=models.CASCADE,
        related_name='chunks',
        help_text="Parent archive"
    )
    item = models.ForeignKey(
        ArchiveItem,
        on_delete=models.CASCADE,
        related_name='chunks',
        help_text="Parent item"
    )
    
    # Chunk content
    content = models.TextField(
        help_text="Chunk text content"
    )
    chunk_index = models.PositiveIntegerField(
        help_text="Sequential chunk number within item"
    )
    chunk_type = models.CharField(
        max_length=20,
        choices=ChunkType.choices,
        default=ChunkType.TEXT,
        help_text="Type of content in chunk"
    )
    
    # Context preservation - rich metadata for AI understanding
    context_metadata = models.JSONField(
        default=dict,
        help_text="Rich context information for AI processing"
    )
    
    # Vector embedding (1536 dimensions for OpenAI text-embedding-ada-002)
    embedding = VectorField(
        dimensions=1536,
        null=True,
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
    
    class Meta:
        db_table = 'django_cfg_knowbase_archive_item_chunks'
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['archive']),
            models.Index(fields=['item', 'chunk_index']),
            models.Index(fields=['chunk_type']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['item', 'chunk_index'],
                name='unique_item_chunk'
            )
        ]
        ordering = ['item', 'chunk_index']
        verbose_name = 'Archive Item Chunk'
        verbose_name_plural = 'Archive Item Chunks'
    
    def save(self, *args, **kwargs):
        """Override save to set computed fields."""
        if self.content and not self.character_count:
            self.character_count = len(self.content)
        
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"Chunk {self.chunk_index} of {self.item.relative_path}"
    
    @classmethod
    def semantic_search(
        cls,
        user,
        query_embedding: List[float],
        limit: int = 5,
        similarity_threshold: float = 0.7,
        content_types: Optional[List[str]] = None,
        languages: Optional[List[str]] = None
    ):
        """Perform semantic search using pgvector with context filtering."""
        from pgvector.django import CosineDistance
        
        queryset = cls.objects.filter(
            user=user,
            embedding__isnull=False
        )
        
        # Apply content type filter
        if content_types:
            queryset = queryset.filter(
                item__content_type__in=content_types
            )
        
        # Apply language filter
        if languages:
            queryset = queryset.filter(
                item__language__in=languages
            )
        
        return queryset.annotate(
            similarity=1 - CosineDistance('embedding', query_embedding)
        ).filter(
            similarity__gte=similarity_threshold
        ).order_by('-similarity')[:limit]
    
    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of chunk context for display."""
        return {
            'archive_title': self.archive.title,
            'item_path': self.item.relative_path,
            'item_type': self.item.content_type,
            'language': self.item.language,
            'chunk_position': f"{self.chunk_index + 1}/{self.item.chunks_count}",
            'chunk_type': self.chunk_type,
        }
