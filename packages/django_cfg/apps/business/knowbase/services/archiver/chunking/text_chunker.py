"""
Generic text chunker.

Simple text chunking with fixed size and overlap.
"""

from typing import List

from ....models.archive import ArchiveItem, ChunkType
from ..context.builders import ChunkContextBuilder
from ..context.models import ChunkData
from .base import BaseChunker


class TextChunker(BaseChunker):
    """
    Generic text chunker with overlap.

    Uses fixed-size chunking with overlap and smart break points.
    """

    def can_handle(self, item: ArchiveItem) -> bool:
        """Can handle any content as fallback."""
        return True

    def chunk(self, item: ArchiveItem) -> List[ChunkData]:
        """
        Chunk text with fixed size and overlap.

        Args:
            item: Archive item to chunk

        Returns:
            List of ChunkData objects
        """
        content = item.raw_content
        chunks = []

        # Simple text splitting with overlap
        start = 0
        chunk_index = 0

        while start < len(content):
            end = start + self.chunk_size

            # Try to break at word boundary
            if end < len(content):
                break_point = self._find_good_break_point(content, start, end)
                if break_point > start:
                    end = break_point

            chunk_content = content[start:end].strip()

            if chunk_content:
                context = ChunkContextBuilder.build_generic_context(
                    item, chunk_index, chunk_content, start, end
                )

                chunks.append(ChunkData(
                    content=chunk_content,
                    chunk_index=chunk_index,
                    chunk_type=ChunkType.TEXT,
                    context_metadata=context
                ))

                chunk_index += 1

            # Move start position with overlap
            start = max(start + self.chunk_size - self.overlap, end)

        return chunks
