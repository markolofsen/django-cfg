"""
Contextual chunking service.

Creates context-aware chunks with rich metadata for AI understanding.
"""

import re
import ast
import logging
from typing import List, Dict, Any, Optional, Tuple
from django.contrib.auth import get_user_model
from pydantic import BaseModel

from ...models.archive import ArchiveItem, ArchiveItemChunk, ContentType, ChunkType
from ...utils.chunk_settings import get_chunking_params_for_type
from ..base import BaseService
from .exceptions import ChunkingError

User = get_user_model()

logger = logging.getLogger(__name__)


class ChunkContextMetadata(BaseModel):
    """Rich context metadata for chunks."""
    
    # Parent hierarchy
    archive_info: Dict[str, Any]
    item_info: Dict[str, Any]
    
    # Position and structure
    position_info: Dict[str, Any]
    structure_info: Dict[str, Any]
    
    # Semantic context
    semantic_info: Dict[str, Any]
    
    # Relational context
    relationship_info: Dict[str, Any]
    
    # Processing provenance
    processing_info: Dict[str, Any]


class ChunkData(BaseModel):
    """Data structure for created chunk."""
    
    content: str
    chunk_index: int
    chunk_type: str
    context_metadata: Dict[str, Any]


class ContextualChunkingService(BaseService):
    """Service for creating context-aware chunks."""
    
    def __init__(self, user: User):
        super().__init__(user)
        # Get dynamic settings from Constance
        chunking_params = get_chunking_params_for_type('archive')
        self.chunk_size = chunking_params['chunk_size']
        self.overlap = chunking_params['overlap']
        
        logger.info(f"📦 Archive chunking initialized: chunk_size={self.chunk_size}, overlap={self.overlap}")
    
    def create_chunks_with_context(
        self, 
        item: ArchiveItem,
        chunk_size: Optional[int] = None,
        overlap: Optional[int] = None
    ) -> List[ArchiveItemChunk]:
        """Create chunks with rich context metadata."""
        
        if not item.raw_content or not item.is_processable:
            return []
        
        # Use instance settings if parameters not provided
        final_chunk_size = chunk_size or self.chunk_size
        final_overlap = overlap or self.overlap
        
        logger.debug(f"📦 Chunking {item.relative_path}: size={final_chunk_size}, overlap={final_overlap}")
        
        try:
            # Debug logging
            logger.info(f"Creating chunks for item: {item.relative_path}, content_type: {item.content_type}")
            
            # Choose chunking strategy based on content type
            if item.content_type == ContentType.CODE:
                logger.debug(f"Using code chunking for {item.relative_path}")
                chunks_data = self._chunk_code_content(item, final_chunk_size, final_overlap)
            elif item.content_type == ContentType.DOCUMENT:
                logger.debug(f"Using document chunking for {item.relative_path}")
                chunks_data = self._chunk_document_content(item, final_chunk_size, final_overlap)
            elif item.content_type == ContentType.DATA:
                logger.debug(f"Using data chunking for {item.relative_path}")
                chunks_data = self._chunk_data_content(item, final_chunk_size, final_overlap)
            else:
                logger.debug(f"Using generic chunking for {item.relative_path}")
                chunks_data = self._chunk_generic_content(item, final_chunk_size, final_overlap)
            
            logger.info(f"Generated {len(chunks_data)} chunks for {item.relative_path}")
            
            # Create chunk records
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
            logger.error(f"Chunking failed for {item.relative_path}: {str(e)}", exc_info=True)
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
    
    def _chunk_code_content(
        self, 
        item: ArchiveItem, 
        chunk_size: int, 
        overlap: int
    ) -> List[ChunkData]:
        """Chunk code files by logical boundaries."""
        
        if item.language == 'python':
            return self._chunk_python_code(item)
        elif item.language in ['javascript', 'typescript']:
            return self._chunk_js_code(item)
        else:
            return self._chunk_generic_code(item, chunk_size, overlap)
    
    def _chunk_python_code(self, item: ArchiveItem) -> List[ChunkData]:
        """Chunk Python code by classes and functions."""
        
        content = item.raw_content
        lines = content.split('\n')
        chunks = []
        
        try:
            tree = ast.parse(content)
            
            # Extract imports first
            imports_chunk = self._extract_python_imports(tree, lines, item, 0)
            if imports_chunk:
                chunks.append(imports_chunk)
            
            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                    chunk = self._create_python_element_chunk(
                        node, lines, item, len(chunks)
                    )
                    chunks.append(chunk)
            
            # Handle module-level code
            remaining_chunk = self._extract_python_remaining_code(
                tree, lines, item, len(chunks)
            )
            if remaining_chunk:
                chunks.append(remaining_chunk)
        
        except SyntaxError:
            # Fallback to line-based chunking
            return self._chunk_generic_code(item, self.chunk_size, self.overlap)
        
        return chunks
    
    def _create_python_element_chunk(
        self, 
        node: ast.AST, 
        lines: List[str], 
        item: ArchiveItem,
        chunk_index: int
    ) -> ChunkData:
        """Create chunk for Python code element."""
        
        start_line = node.lineno - 1
        end_line = self._find_python_block_end(node, lines)
        
        content = '\n'.join(lines[start_line:end_line])
        
        # Analyze code structure
        code_info = self._analyze_python_structure(node, content)
        
        # Build context metadata
        context = self._build_code_chunk_context(
            item, chunk_index, content, start_line, end_line, code_info
        )
        
        return ChunkData(
            content=content,
            chunk_index=chunk_index,
            chunk_type=ChunkType.CODE,
            context_metadata=context
        )
    
    def _analyze_python_structure(self, node: ast.AST, content: str) -> Dict[str, Any]:
        """Analyze Python code structure for context."""
        
        info = {
            'element_name': node.name,
            'element_type': 'class' if isinstance(node, ast.ClassDef) else 'function',
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'docstring': ast.get_docstring(node),
            'decorators': [d.id for d in getattr(node, 'decorator_list', []) if hasattr(d, 'id')],
            'complexity_score': self._calculate_code_complexity(content),
            'purpose': self._detect_code_purpose(node.name, content),
        }
        
        # Extract function/method arguments
        if hasattr(node, 'args'):
            info['arguments'] = [arg.arg for arg in node.args.args]
        
        # Extract class bases
        if isinstance(node, ast.ClassDef):
            info['base_classes'] = [base.id for base in node.bases if hasattr(base, 'id')]
        
        return info
    
    def _chunk_document_content(
        self, 
        item: ArchiveItem, 
        chunk_size: int, 
        overlap: int
    ) -> List[ChunkData]:
        """Chunk document files by structure."""
        
        if item.language == 'markdown':
            return self._chunk_markdown_content(item)
        else:
            return self._chunk_generic_content(item, chunk_size, overlap)
    
    def _chunk_markdown_content(self, item: ArchiveItem) -> List[ChunkData]:
        """Chunk markdown by headings and sections."""
        
        content = item.raw_content
        lines = content.split('\n')
        chunks = []
        
        current_section = {'title': '', 'level': 0, 'start_line': 0}
        
        for i, line in enumerate(lines):
            if line.startswith('#'):
                # New section found
                if current_section['start_line'] < i:
                    # Create chunk for previous section
                    chunk = self._create_markdown_section_chunk(
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
            chunk = self._create_markdown_section_chunk(
                lines[current_section['start_line']:],
                current_section,
                item,
                len(chunks)
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_markdown_section_chunk(
        self, 
        section_lines: List[str], 
        section_info: Dict[str, Any], 
        item: ArchiveItem,
        chunk_index: int
    ) -> ChunkData:
        """Create chunk for markdown section."""
        
        content = '\n'.join(section_lines)
        
        # Build context metadata
        context = self._build_document_chunk_context(
            item, chunk_index, content, section_info
        )
        
        chunk_type = ChunkType.HEADING if section_info['title'] else ChunkType.TEXT
        
        return ChunkData(
            content=content,
            chunk_index=chunk_index,
            chunk_type=chunk_type,
            context_metadata=context
        )
    
    def _chunk_data_content(
        self, 
        item: ArchiveItem, 
        chunk_size: int, 
        overlap: int
    ) -> List[ChunkData]:
        """Chunk data files by logical structure."""
        
        if item.language == 'json':
            return self._chunk_json_content(item)
        elif item.language in ['yaml', 'yml']:
            return self._chunk_yaml_content(item)
        else:
            return self._chunk_generic_content(item, chunk_size, overlap)
    
    def _chunk_json_content(self, item: ArchiveItem) -> List[ChunkData]:
        """Chunk JSON by object structure."""
        
        import json
        
        try:
            data = json.loads(item.raw_content)
            chunks = []
            
            if isinstance(data, dict):
                # Chunk by top-level keys
                for key, value in data.items():
                    chunk_content = json.dumps({key: value}, indent=2)
                    
                    context = self._build_data_chunk_context(
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
            # Fallback to text chunking
            return self._chunk_generic_content(item, self.chunk_size, self.overlap)
    
    def _chunk_generic_content(
        self, 
        item: ArchiveItem, 
        chunk_size: int, 
        overlap: int
    ) -> List[ChunkData]:
        """Generic text chunking with overlap."""
        
        content = item.raw_content
        chunks = []
        
        # Simple text splitting with overlap
        start = 0
        chunk_index = 0
        
        while start < len(content):
            end = start + chunk_size
            
            # Try to break at word boundary
            if end < len(content):
                # Look for good break points
                break_point = self._find_good_break_point(content, start, end)
                if break_point > start:
                    end = break_point
            
            chunk_content = content[start:end].strip()
            
            if chunk_content:
                context = self._build_generic_chunk_context(
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
            start = max(start + chunk_size - overlap, end)
        
        return chunks
    
    def _find_good_break_point(self, content: str, start: int, end: int) -> int:
        """Find good break point for text chunking."""
        
        # Look for sentence endings
        for i in range(end - 1, start, -1):
            if content[i] in '.!?\n':
                return i + 1
        
        # Look for word boundaries
        for i in range(end - 1, start, -1):
            if content[i].isspace():
                return i
        
        return end
    
    def _build_code_chunk_context(
        self,
        item: ArchiveItem,
        chunk_index: int,
        content: str,
        start_line: int,
        end_line: int,
        code_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build context metadata for code chunk."""
        
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
                'technical_tags': self._generate_code_tags(content, code_info),
            },
            'processing_info': {
                'extraction_method': 'ast_parser',
                'chunking_strategy': 'logical_units',
                'quality_score': self._assess_code_quality(content),
            }
        }
    
    def _build_document_chunk_context(
        self,
        item: ArchiveItem,
        chunk_index: int,
        content: str,
        section_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build context metadata for document chunk."""
        
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
                'topic_tags': self._generate_document_tags(content),
            },
            'processing_info': {
                'extraction_method': 'markdown_parser',
                'chunking_strategy': 'heading_based',
            }
        }
    
    def _build_data_chunk_context(
        self,
        item: ArchiveItem,
        chunk_index: int,
        content: str,
        data_type: str,
        key_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build context metadata for data chunk."""
        
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
    
    def _build_generic_chunk_context(
        self,
        item: ArchiveItem,
        chunk_index: int,
        content: str,
        start_pos: int,
        end_pos: int
    ) -> Dict[str, Any]:
        """Build context metadata for generic text chunk."""
        
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
                'relative_position': start_pos / len(item.raw_content),
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
    
    def _generate_code_tags(self, content: str, code_info: Dict[str, Any]) -> List[str]:
        """Generate technical tags for code content."""
        
        tags = []
        
        # Element type tags
        if code_info.get('element_type'):
            tags.append(f"contains:{code_info['element_type']}")
        
        # Async tag
        if code_info.get('is_async'):
            tags.append('async')
        
        # Pattern detection
        if 'import ' in content or 'from ' in content:
            tags.append('contains:imports')
        
        if 'class ' in content:
            tags.append('contains:class_definition')
        
        if 'def ' in content:
            tags.append('contains:function_definition')
        
        if 'test' in code_info.get('element_name', '').lower():
            tags.append('purpose:testing')
        
        return tags
    
    def _generate_document_tags(self, content: str) -> List[str]:
        """Generate topic tags for document content."""
        
        tags = []
        
        # Detect headings
        if content.strip().startswith('#'):
            tags.append('contains:heading')
        
        # Detect lists
        if re.search(r'^\s*[-*+]\s', content, re.MULTILINE):
            tags.append('contains:list')
        
        # Detect code blocks
        if '```' in content or '    ' in content:
            tags.append('contains:code_block')
        
        return tags
    
    def _calculate_code_complexity(self, content: str) -> float:
        """Calculate code complexity score."""
        
        # Simple complexity based on lines and control structures
        lines = content.split('\n')
        complexity = len(lines) / 100.0  # Base complexity
        
        # Add complexity for control structures
        control_keywords = ['if', 'for', 'while', 'try', 'except', 'with']
        for keyword in control_keywords:
            complexity += content.count(keyword) * 0.1
        
        return min(1.0, complexity)
    
    def _assess_code_quality(self, content: str) -> float:
        """Assess code quality score."""
        
        # Simple quality assessment
        quality = 0.5  # Base quality
        
        # Boost for docstrings
        if '"""' in content or "'''" in content:
            quality += 0.2
        
        # Boost for comments
        comment_lines = len([line for line in content.split('\n') if line.strip().startswith('#')])
        quality += min(0.2, comment_lines / 10.0)
        
        # Penalty for very long lines
        long_lines = len([line for line in content.split('\n') if len(line) > 100])
        quality -= min(0.2, long_lines / 10.0)
        
        return max(0.0, min(1.0, quality))
    
    def _detect_code_purpose(self, element_name: str, content: str) -> str:
        """Detect purpose of code element."""
        
        name_lower = element_name.lower()
        
        if name_lower.startswith('test_'):
            return 'test'
        elif name_lower.startswith('_'):
            return 'private_method'
        elif 'config' in name_lower:
            return 'configuration'
        elif 'init' in name_lower:
            return 'initialization'
        elif 'main' in name_lower:
            return 'main_function'
        else:
            return 'implementation'
    
    def _find_python_block_end(self, node: ast.AST, lines: List[str]) -> int:
        """Find end line of Python code block."""
        
        # Start from the node's end line
        start_line = getattr(node, 'end_lineno', node.lineno) or node.lineno
        
        # Look for the actual end by checking indentation
        for i in range(start_line, len(lines)):
            line = lines[i]
            if line.strip() and not line.startswith(' ') and not line.startswith('\t'):
                return i
        
        return len(lines)
    
    def _extract_python_imports(
        self, 
        tree: ast.AST, 
        lines: List[str], 
        item: ArchiveItem, 
        chunk_index: int
    ) -> Optional[ChunkData]:
        """Extract imports as separate chunk."""
        
        import_lines = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                import_lines.append(node.lineno - 1)
        
        if not import_lines:
            return None
        
        # Get all import lines
        import_content = '\n'.join(lines[min(import_lines):max(import_lines) + 1])
        
        context = self._build_code_chunk_context(
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
    
    def _extract_python_remaining_code(
        self, 
        tree: ast.AST, 
        lines: List[str], 
        item: ArchiveItem, 
        chunk_index: int
    ) -> Optional[ChunkData]:
        """Extract remaining module-level code."""
        
        # This is a simplified implementation
        # In practice, you'd want to identify module-level statements
        # that aren't part of classes or functions
        
        return None  # Skip for now
    
    def _chunk_generic_code(
        self, 
        item: ArchiveItem, 
        chunk_size: int, 
        overlap: int
    ) -> List[ChunkData]:
        """Generic code chunking for unsupported languages."""
        
        return self._chunk_generic_content(item, chunk_size, overlap)
    
    def _chunk_js_code(self, item: ArchiveItem) -> List[ChunkData]:
        """Chunk JavaScript/TypeScript code."""
        
        # Simplified implementation - could be enhanced with proper JS parsing
        return self._chunk_generic_content(item, self.chunk_size, self.overlap)
    
    def _chunk_yaml_content(self, item: ArchiveItem) -> List[ChunkData]:
        """Chunk YAML content."""
        
        # Simplified implementation - could be enhanced with YAML parsing
        return self._chunk_generic_content(item, self.chunk_size, self.overlap)


class ChunkContextBuilder:
    """Helper class for building chunk context metadata."""
    
    @staticmethod
    def build_context(
        archive_info: Dict[str, Any],
        item_info: Dict[str, Any],
        position_info: Dict[str, Any],
        structure_info: Dict[str, Any],
        semantic_info: Dict[str, Any],
        processing_info: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build complete context metadata."""
        
        return {
            'archive_info': archive_info,
            'item_info': item_info,
            'position_info': position_info,
            'structure_info': structure_info,
            'semantic_info': semantic_info,
            'processing_info': processing_info
        }
