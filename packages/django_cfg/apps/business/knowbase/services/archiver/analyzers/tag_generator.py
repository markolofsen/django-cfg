"""
Tag generation for chunks.

Generates semantic tags for code and document chunks.
"""

import re
from typing import Any, Dict, List


class TagGenerator:
    """Generate tags for different content types."""

    @staticmethod
    def generate_code_tags(content: str, code_info: Dict[str, Any]) -> List[str]:
        """
        Generate technical tags for code content.

        Args:
            content: Code content
            code_info: Code analysis info (element_name, element_type, etc.)

        Returns:
            List of technical tags
        """
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

    @staticmethod
    def generate_document_tags(content: str) -> List[str]:
        """
        Generate topic tags for document content.

        Args:
            content: Document content

        Returns:
            List of topic tags
        """
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

    @staticmethod
    def detect_code_purpose(element_name: str, content: str) -> str:
        """
        Detect purpose of code element.

        Args:
            element_name: Name of code element
            content: Code content

        Returns:
            Purpose string (test, configuration, initialization, etc.)
        """
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
