"""
Base chunker interface.

Abstract base class for content-specific chunking strategies.
"""

from abc import ABC, abstractmethod
from typing import List

from ....models.archive import ArchiveItem
from ..context.models import ChunkData


class BaseChunker(ABC):
    """
    Base class for content chunkers.

    Provides common interface and utilities for chunking strategies.
    """

    def __init__(self, chunk_size: int = 1000, overlap: int = 200):
        """
        Initialize chunker.

        Args:
            chunk_size: Default chunk size in characters
            overlap: Overlap between chunks in characters
        """
        self.chunk_size = chunk_size
        self.overlap = overlap

    @abstractmethod
    def can_handle(self, item: ArchiveItem) -> bool:
        """
        Check if this chunker can handle the item.

        Args:
            item: Archive item to check

        Returns:
            True if this chunker can process the item
        """
        pass

    @abstractmethod
    def chunk(self, item: ArchiveItem) -> List[ChunkData]:
        """
        Create chunks from item content.

        Args:
            item: Archive item to chunk

        Returns:
            List of ChunkData objects
        """
        pass

    def _find_good_break_point(self, content: str, start: int, end: int) -> int:
        """
        Find good break point for text chunking.

        Tries to break at sentence endings or word boundaries.

        Args:
            content: Content being chunked
            start: Start position
            end: Desired end position

        Returns:
            Actual break point position
        """
        # Look for sentence endings
        for i in range(end - 1, start, -1):
            if content[i] in '.!?\n':
                return i + 1

        # Look for word boundaries
        for i in range(end - 1, start, -1):
            if content[i].isspace():
                return i

        return end
