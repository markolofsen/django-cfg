"""
JSON extraction utilities for LLM responses.

Provides functionality to extract structured JSON data from LLM text responses.
"""

import json
import re
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class JSONExtractor:
    """Utility for extracting JSON from LLM responses."""
    
    @staticmethod
    def extract_json_from_response(content: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from response content.
        
        Args:
            content: Response content from LLM
            
        Returns:
            Extracted JSON dict or None if no valid JSON found
        """
        try:
            # First try to parse as direct JSON
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON in the text
            json_patterns = [
                r'```json\s*(\{.*?\})\s*```',
                r'```\s*(\{.*?\})\s*```',
                r'(\{.*?\})',
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, content, re.DOTALL)
                for match in matches:
                    try:
                        return json.loads(match)
                    except json.JSONDecodeError:
                        continue
            
            logger.debug(f"No valid JSON found in response: {content[:100]}...")
            return None
    
    @staticmethod
    def extract_code_blocks(content: str, language: Optional[str] = None) -> list[str]:
        """
        Extract code blocks from response content.
        
        Args:
            content: Response content from LLM
            language: Specific language to extract (e.g., 'python', 'json')
            
        Returns:
            List of extracted code blocks
        """
        if language:
            pattern = rf'```{language}\s*(.*?)\s*```'
        else:
            pattern = r'```(?:\w+)?\s*(.*?)\s*```'
        
        matches = re.findall(pattern, content, re.DOTALL)
        return [match.strip() for match in matches]
    
    @staticmethod
    def extract_markdown_sections(content: str, section_title: str) -> list[str]:
        """
        Extract specific markdown sections from response.
        
        Args:
            content: Response content from LLM
            section_title: Title of the section to extract
            
        Returns:
            List of extracted sections
        """
        pattern = rf'#{1,6}\s*{re.escape(section_title)}\s*\n(.*?)(?=\n#{1,6}|\Z)'
        matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
        return [match.strip() for match in matches]
