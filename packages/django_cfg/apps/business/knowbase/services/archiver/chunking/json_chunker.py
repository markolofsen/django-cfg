"""
JSON data chunker.

Chunks JSON by object structure.
"""

import json
from typing import List

from ....models.archive import ArchiveItem, ChunkType
from ..context.builders import ChunkContextBuilder
from ..context.models import ChunkData
from .base import BaseChunker


class JsonChunker(BaseChunker):
    """
    Chunk JSON by object structure.

    Splits JSON documents by top-level keys.
    """

    def can_handle(self, item: ArchiveItem) -> bool:
        """Can handle JSON files."""
        return item.language == 'json'

    def chunk(self, item: ArchiveItem) -> List[ChunkData]:
        """
        Chunk JSON by object structure.

        Args:
            item: Archive item to chunk

        Returns:
            List of ChunkData objects
        """
        try:
            data = json.loads(item.raw_content)
            chunks = []

            if isinstance(data, dict):
                # Chunk by top-level keys
                for key, value in data.items():
                    chunk_content = json.dumps({key: value}, indent=2)

                    context = ChunkContextBuilder.build_data_context(
                        item, len(chunks), chunk_content, 'json_object', key
                    )

                    chunks.append(ChunkData(
                        content=chunk_content,
                        chunk_index=len(chunks),
                        chunk_type=ChunkType.METADATA,
                        context_metadata=context
                    ))

            return chunks

        except json.JSONDecodeError:
            # Fallback to text chunking on parse errors
            from .text_chunker import TextChunker
            text_chunker = TextChunker(self.chunk_size, self.overlap)
            return text_chunker.chunk(item)
