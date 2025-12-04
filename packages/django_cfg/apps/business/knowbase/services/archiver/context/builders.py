"""
Context metadata builders for chunks.

Builds rich context metadata for different types of content chunks.
"""

from typing import Any, Dict, Optional

from ....models.archive import ArchiveItem


class ChunkContextBuilder:
    """Build context metadata for different chunk types."""

    @staticmethod
    def build_code_context(
        item: ArchiveItem,
        chunk_index: int,
        content: str,
        start_line: int,
        end_line: int,
        code_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build context metadata for code chunk.

        Args:
            item: Archive item being chunked
            chunk_index: Index of this chunk
            content: Chunk content
            start_line: Starting line number
            end_line: Ending line number
            code_info: Code analysis info (element_name, type, etc.)

        Returns:
            Context metadata dictionary
        """
        from ..analyzers import TagGenerator

        return {
            'archive_info': {
                'id': str(item.archive.id),
                'title': item.archive.title,
                'description': item.archive.description,
            },
            'item_info': {
                'id': str(item.id),
                'relative_path': item.relative_path,
                'item_name': item.item_name,
                'content_type': item.content_type,
                'language': item.language,
            },
            'position_info': {
                'chunk_index': chunk_index,
                'start_line': start_line + 1,
                'end_line': end_line,
                'total_lines': len(item.raw_content.split('\n')),
            },
            'structure_info': {
                'element_name': code_info.get('element_name'),
                'element_type': code_info.get('element_type'),
                'is_async': code_info.get('is_async', False),
                'has_docstring': bool(code_info.get('docstring')),
            },
            'semantic_info': {
                'chunk_type': 'code',
                'content_purpose': code_info.get('purpose', 'implementation'),
                'complexity_score': code_info.get('complexity_score', 0.0),
                'technical_tags': TagGenerator.generate_code_tags(content, code_info),
            },
            'processing_info': {
                'extraction_method': 'ast_parser',
                'chunking_strategy': 'logical_units',
                'quality_score': code_info.get('quality_score', 0.5),
            }
        }

    @staticmethod
    def build_document_context(
        item: ArchiveItem,
        chunk_index: int,
        content: str,
        section_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build context metadata for document chunk.

        Args:
            item: Archive item being chunked
            chunk_index: Index of this chunk
            content: Chunk content
            section_info: Section info (title, level, etc.)

        Returns:
            Context metadata dictionary
        """
        from ..analyzers import TagGenerator

        return {
            'archive_info': {
                'id': str(item.archive.id),
                'title': item.archive.title,
            },
            'item_info': {
                'id': str(item.id),
                'relative_path': item.relative_path,
                'content_type': item.content_type,
                'language': item.language,
            },
            'position_info': {
                'chunk_index': chunk_index,
            },
            'structure_info': {
                'section_title': section_info.get('title'),
                'section_level': section_info.get('level', 0),
            },
            'semantic_info': {
                'chunk_type': 'heading' if section_info.get('title') else 'text',
                'content_purpose': 'documentation',
                'topic_tags': TagGenerator.generate_document_tags(content),
            },
            'processing_info': {
                'extraction_method': 'markdown_parser',
                'chunking_strategy': 'heading_based',
            }
        }

    @staticmethod
    def build_data_context(
        item: ArchiveItem,
        chunk_index: int,
        content: str,
        data_type: str,
        key_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build context metadata for data chunk.

        Args:
            item: Archive item being chunked
            chunk_index: Index of this chunk
            content: Chunk content
            data_type: Type of data (e.g., 'json_object')
            key_name: Optional key name for object property

        Returns:
            Context metadata dictionary
        """
        return {
            'archive_info': {
                'id': str(item.archive.id),
                'title': item.archive.title,
            },
            'item_info': {
                'id': str(item.id),
                'relative_path': item.relative_path,
                'content_type': item.content_type,
            },
            'position_info': {
                'chunk_index': chunk_index,
            },
            'structure_info': {
                'data_key': key_name,
                'data_type': data_type,
            },
            'semantic_info': {
                'chunk_type': 'metadata',
                'content_purpose': 'data_definition',
            },
            'processing_info': {
                'extraction_method': 'json_parser',
                'chunking_strategy': 'object_properties',
            }
        }

    @staticmethod
    def build_generic_context(
        item: ArchiveItem,
        chunk_index: int,
        content: str,
        start_pos: int,
        end_pos: int
    ) -> Dict[str, Any]:
        """
        Build context metadata for generic text chunk.

        Args:
            item: Archive item being chunked
            chunk_index: Index of this chunk
            content: Chunk content
            start_pos: Starting character position
            end_pos: Ending character position

        Returns:
            Context metadata dictionary
        """
        return {
            'archive_info': {
                'id': str(item.archive.id),
                'title': item.archive.title,
            },
            'item_info': {
                'id': str(item.id),
                'relative_path': item.relative_path,
                'content_type': item.content_type,
            },
            'position_info': {
                'chunk_index': chunk_index,
                'start_char': start_pos,
                'end_char': end_pos,
                'relative_position': start_pos / len(item.raw_content) if item.raw_content else 0.0,
            },
            'semantic_info': {
                'chunk_type': 'text',
                'content_purpose': 'content',
            },
            'processing_info': {
                'extraction_method': 'text_splitting',
                'chunking_strategy': 'fixed_size_overlap',
            }
        }
