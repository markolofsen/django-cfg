"""
Archive processing exceptions.

Custom exception hierarchy for archive processing operations.
"""

from typing import Optional, Dict, Any


class ArchiveProcessingError(Exception):
    """Base exception for archive processing errors."""
    
    def __init__(
        self, 
        message: str, 
        code: str, 
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(message)


class ArchiveValidationError(ArchiveProcessingError):
    """Archive validation errors."""
    pass


class ExtractionError(ArchiveProcessingError):
    """Archive extraction errors."""
    pass


class ChunkingError(ArchiveProcessingError):
    """Content chunking errors."""
    pass


class VectorizationError(ArchiveProcessingError):
    """Vectorization processing errors."""
    pass


class ContentTypeDetectionError(ArchiveProcessingError):
    """Content type detection errors."""
    pass


class ProcessingTimeoutError(ArchiveProcessingError):
    """Processing timeout errors."""
    pass
