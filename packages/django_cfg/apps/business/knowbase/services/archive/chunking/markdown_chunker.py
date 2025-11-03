"""
Markdown document chunker.

Chunks markdown by headings and sections.
"""

from typing import Any, Dict, List

from ....models.archive import ArchiveItem, ChunkType
from ..context.builders import ChunkContextBuilder
from ..context.models import ChunkData
from .base import BaseChunker


class MarkdownChunker(BaseChunker):
    """
    Chunk markdown by headings and sections.

    Splits markdown documents into logical sections based on heading structure.
    """

    def can_handle(self, item: ArchiveItem) -> bool:
        """Can handle markdown files."""
        return item.language == 'markdown'

    def chunk(self, item: ArchiveItem) -> List[ChunkData]:
        """
        Chunk markdown by headings and sections.

        Args:
            item: Archive item to chunk

        Returns:
            List of ChunkData objects
        """
        content = item.raw_content
        lines = content.split('\n')
        chunks = []

        current_section = {'title': '', 'level': 0, 'start_line': 0}

        for i, line in enumerate(lines):
            if line.startswith('#'):
                # New section found
                if current_section['start_line'] < i:
                    # Create chunk for previous section
                    chunk = self._create_section_chunk(
                        lines[current_section['start_line']:i],
                        current_section,
                        item,
                        len(chunks)
                    )
                    chunks.append(chunk)

                # Start new section
                level = len(line) - len(line.lstrip('#'))
                current_section = {
                    'title': line.lstrip('# ').strip(),
                    'level': level,
                    'start_line': i
                }

        # Handle last section
        if current_section['start_line'] < len(lines):
            chunk = self._create_section_chunk(
                lines[current_section['start_line']:],
                current_section,
                item,
                len(chunks)
            )
            chunks.append(chunk)

        return chunks

    def _create_section_chunk(
        self,
        section_lines: List[str],
        section_info: Dict[str, Any],
        item: ArchiveItem,
        chunk_index: int
    ) -> ChunkData:
        """
        Create chunk for markdown section.

        Args:
            section_lines: Lines of the section
            section_info: Section metadata (title, level)
            item: Archive item
            chunk_index: Index of this chunk

        Returns:
            ChunkData for the section
        """
        content = '\n'.join(section_lines)

        # Build context metadata
        context = ChunkContextBuilder.build_document_context(
            item, chunk_index, content, section_info
        )

        chunk_type = ChunkType.HEADING if section_info['title'] else ChunkType.TEXT

        return ChunkData(
            content=content,
            chunk_index=chunk_index,
            chunk_type=chunk_type,
            context_metadata=context
        )
