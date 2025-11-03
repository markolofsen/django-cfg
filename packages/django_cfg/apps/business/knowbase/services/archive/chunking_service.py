"""
Contextual chunking service orchestrator.

Creates context-aware chunks with rich metadata for AI understanding.
Uses specialized chunkers for different content types.
"""

import logging
from typing import List, Optional

from django.contrib.auth import get_user_model

from ...models.archive import ArchiveItem, ArchiveItemChunk
from ...utils.chunk_settings import get_chunking_params_for_type
from ..base import BaseService

# Import chunkers
from .chunking import JsonChunker, MarkdownChunker, PythonChunker, TextChunker
from .exceptions import ChunkingError

User = get_user_model()
logger = logging.getLogger(__name__)


class ContextualChunkingService(BaseService):
    """
    Service for creating context-aware chunks.

    Orchestrates specialized chunkers using chain of responsibility pattern.
    """

    def __init__(self, user: User):
        super().__init__(user)

        # Get dynamic settings from Constance
        chunking_params = get_chunking_params_for_type('archive')
        self.chunk_size = chunking_params['chunk_size']
        self.overlap = chunking_params['overlap']

        # Initialize chunkers in priority order
        self.chunkers = [
            PythonChunker(self.chunk_size, self.overlap),
            MarkdownChunker(self.chunk_size, self.overlap),
            JsonChunker(self.chunk_size, self.overlap),
            TextChunker(self.chunk_size, self.overlap),  # Fallback - handles anything
        ]

        logger.info(
            f"📦 Archive chunking initialized: "
            f"chunk_size={self.chunk_size}, overlap={self.overlap}"
        )

    def create_chunks_with_context(
        self,
        item: ArchiveItem,
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None
    ) -> List[ArchiveItemChunk]:
        """
        Create chunks with rich context metadata.

        Uses specialized chunkers based on content type.

        Args:
            item: Archive item to chunk
            chunk_size: Optional custom chunk size
            overlap: Optional custom overlap size

        Returns:
            List of created chunk objects
        """
        if not item.raw_content or not item.is_processable:
            return []

        # Use instance settings if parameters not provided
        final_chunk_size = chunk_size or self.chunk_size
        final_overlap = overlap or self.overlap

        # Update chunkers if custom sizes provided
        if chunk_size or overlap:
            self._update_chunker_settings(final_chunk_size, final_overlap)

        logger.debug(
            f"📦 Chunking {item.relative_path}: "
            f"size={final_chunk_size}, overlap={final_overlap}"
        )

        try:
            logger.info(
                f"Creating chunks for item: {item.relative_path}, "
                f"content_type: {item.content_type}"
            )

            # Find appropriate chunker using chain of responsibility
            chunker = self._select_chunker(item)
            logger.debug(
                f"Using {chunker.__class__.__name__} for {item.relative_path}"
            )

            # Create chunks using selected chunker
            chunks_data = chunker.chunk(item)
            logger.info(f"Generated {len(chunks_data)} chunks for {item.relative_path}")

            # Create chunk records in database
            chunk_objects = []

            for chunk_data in chunks_data:
                # Use objects to avoid custom manager issues
                chunk = ArchiveItemChunk.objects.create(
                    user=self.user,
                    archive=item.archive,
                    item=item,
                    content=chunk_data.content,
                    chunk_index=chunk_data.chunk_index,
                    chunk_type=chunk_data.chunk_type,
                    context_metadata=chunk_data.context_metadata
                )
                chunk_objects.append(chunk)

            return chunk_objects

        except Exception as e:
            logger.error(
                f"Chunking failed for {item.relative_path}: {str(e)}",
                exc_info=True
            )
            raise ChunkingError(
                message=f"Failed to create chunks for item {item.relative_path}",
                code="CHUNKING_FAILED",
                details={
                    "item_id": str(item.id),
                    "item_path": item.relative_path,
                    "error": str(e),
                    "content_type": str(item.content_type),
                    "content_length": len(item.raw_content) if item.raw_content else 0
                }
            ) from e

    def _select_chunker(self, item: ArchiveItem):
        """
        Select appropriate chunker for item.

        Uses chain of responsibility - first chunker that can handle wins.

        Args:
            item: Archive item to chunk

        Returns:
            Chunker instance
        """
        for chunker in self.chunkers:
            if chunker.can_handle(item):
                return chunker

        # Should never happen since TextChunker handles everything
        return self.chunkers[-1]

    def _update_chunker_settings(self, chunk_size: int, overlap: int):
        """
        Update all chunkers with new settings.

        Args:
            chunk_size: New chunk size
            overlap: New overlap size
        """
        for chunker in self.chunkers:
            chunker.chunk_size = chunk_size
            chunker.overlap = overlap
