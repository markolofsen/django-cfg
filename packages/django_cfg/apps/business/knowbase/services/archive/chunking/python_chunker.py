"""
Python code chunker using AST parsing.

Chunks Python code by logical boundaries (classes, functions, imports).
"""

import ast
from typing import Any, Dict, List, Optional

from ....models.archive import ArchiveItem, ChunkType
from ..context.builders import ChunkContextBuilder
from ..context.models import ChunkData
from .base import BaseChunker


class PythonChunker(BaseChunker):
    """
    Chunk Python code by logical boundaries using AST.

    Extracts:
    - Import statements
    - Class definitions
    - Function definitions
    - Module-level code
    """

    def can_handle(self, item: ArchiveItem) -> bool:
        """Can handle Python code files."""
        return item.language == 'python'

    def chunk(self, item: ArchiveItem) -> List[ChunkData]:
        """
        Chunk Python code by classes and functions.

        Args:
            item: Archive item to chunk

        Returns:
            List of ChunkData objects
        """
        content = item.raw_content
        lines = content.split('\n')
        chunks = []

        try:
            tree = ast.parse(content)

            # Extract imports first
            imports_chunk = self._extract_imports(tree, lines, item, 0)
            if imports_chunk:
                chunks.append(imports_chunk)

            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    chunk = self._create_element_chunk(
                        node, lines, item, len(chunks)
                    )
                    chunks.append(chunk)

            # Handle module-level code
            remaining_chunk = self._extract_remaining_code(
                tree, lines, item, len(chunks)
            )
            if remaining_chunk:
                chunks.append(remaining_chunk)

        except SyntaxError:
            # Fallback to text chunking on syntax errors
            from .text_chunker import TextChunker
            text_chunker = TextChunker(self.chunk_size, self.overlap)
            return text_chunker.chunk(item)

        return chunks

    def _create_element_chunk(
        self,
        node: ast.AST,
        lines: List[str],
        item: ArchiveItem,
        chunk_index: int
    ) -> ChunkData:
        """
        Create chunk for Python code element.

        Args:
            node: AST node (ClassDef, FunctionDef, etc.)
            lines: File lines
            item: Archive item
            chunk_index: Index of this chunk

        Returns:
            ChunkData for the element
        """
        start_line = node.lineno - 1
        end_line = self._find_block_end(node, lines)

        content = '\n'.join(lines[start_line:end_line])

        # Analyze code structure
        from ..analyzers import ComplexityAnalyzer, PurposeDetector, QualityAnalyzer
        code_info = self._analyze_structure(
            node, content,
            ComplexityAnalyzer, QualityAnalyzer, PurposeDetector
        )

        # Build context metadata
        context = ChunkContextBuilder.build_code_context(
            item, chunk_index, content, start_line, end_line, code_info
        )

        return ChunkData(
            content=content,
            chunk_index=chunk_index,
            chunk_type=ChunkType.CODE,
            context_metadata=context
        )

    def _analyze_structure(
        self,
        node: ast.AST,
        content: str,
        complexity_analyzer,
        quality_analyzer,
        purpose_detector
    ) -> Dict[str, Any]:
        """
        Analyze Python code structure for context.

        Args:
            node: AST node
            content: Code content
            complexity_analyzer: Analyzer for complexity
            quality_analyzer: Analyzer for quality
            purpose_detector: Detector for purpose

        Returns:
            Dictionary with code analysis info
        """
        info = {
            'element_name': node.name,
            'element_type': 'class' if isinstance(node, ast.ClassDef) else 'function',
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'docstring': ast.get_docstring(node),
            'decorators': [d.id for d in getattr(node, 'decorator_list', []) if hasattr(d, 'id')],
            'complexity_score': complexity_analyzer.calculate_code_complexity(content),
            'quality_score': quality_analyzer.assess_code_quality(content),
            'purpose': purpose_detector.detect_code_purpose(node.name, content),
        }

        # Extract function/method arguments
        if hasattr(node, 'args'):
            info['arguments'] = [arg.arg for arg in node.args.args]

        # Extract class bases
        if isinstance(node, ast.ClassDef):
            info['base_classes'] = [base.id for base in node.bases if hasattr(base, 'id')]

        return info

    def _find_block_end(self, node: ast.AST, lines: List[str]) -> int:
        """
        Find end line of Python code block.

        Args:
            node: AST node
            lines: File lines

        Returns:
            End line number
        """
        # Start from the node's end line
        start_line = getattr(node, 'end_lineno', node.lineno) or node.lineno

        # Look for the actual end by checking indentation
        for i in range(start_line, len(lines)):
            line = lines[i]
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                return i

        return len(lines)

    def _extract_imports(
        self,
        tree: ast.AST,
        lines: List[str],
        item: ArchiveItem,
        chunk_index: int
    ) -> Optional[ChunkData]:
        """
        Extract imports as separate chunk.

        Args:
            tree: Parsed AST
            lines: File lines
            item: Archive item
            chunk_index: Chunk index

        Returns:
            ChunkData for imports or None
        """
        import_lines = []

        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_lines.append(node.lineno - 1)

        if not import_lines:
            return None

        # Get all import lines
        import_content = '\n'.join(lines[min(import_lines):max(import_lines) + 1])

        context = ChunkContextBuilder.build_code_context(
            item, chunk_index, import_content,
            min(import_lines), max(import_lines) + 1,
            {'element_name': 'imports', 'element_type': 'imports', 'purpose': 'imports'}
        )

        return ChunkData(
            content=import_content,
            chunk_index=chunk_index,
            chunk_type=ChunkType.METADATA,
            context_metadata=context
        )

    def _extract_remaining_code(
        self,
        tree: ast.AST,
        lines: List[str],
        item: ArchiveItem,
        chunk_index: int
    ) -> Optional[ChunkData]:
        """
        Extract remaining module-level code.

        Args:
            tree: Parsed AST
            lines: File lines
            item: Archive item
            chunk_index: Chunk index

        Returns:
            ChunkData for module-level code or None
        """
        # Simplified implementation - skip module-level code for now
        # Could be enhanced to identify module-level statements
        # that aren't part of classes or functions
        return None
