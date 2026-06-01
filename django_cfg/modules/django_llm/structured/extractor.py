"""
JSON extraction utilities for LLM responses.

Provides functionality to extract structured JSON data from LLM text responses.
"""

import json
import logging
import re
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# Smart / curly double-quotes a model sometimes emits inside JSON → straight.
# Kept in lockstep with the router (Python `_QUOTE_FIXES`) and cmdop_go
# (`quoteFixes`) so all three modules normalise the same way.
_QUOTE_FIXES = (
    ("“", '"'),  # left double  “
    ("”", '"'),  # right double ”
    ("„", '"'),  # low-9 double „
    ("‟", '"'),  # high-reversed-9 double ‟
)


def _normalize_quotes(text: str) -> str:
    """Replace smart double-quotes with straight quotes (JSON-safe)."""
    for bad, good in _QUOTE_FIXES:
        text = text.replace(bad, good)
    return text


def _balanced_span(text: str, open_ch: str, close_ch: str) -> Optional[str]:
    """Return the first balanced ``open_ch..close_ch`` span, or None.

    Tracks string literals + escapes so braces inside strings don't count,
    and nested objects/arrays are captured in full. This replaces the old
    greedy ``(\\{.*?\\})`` regex, which stopped at the first ``}`` and so
    failed on any nested JSON. Mirrors ``_balanced_span`` in the router and
    ``balancedSpan`` in cmdop_go.
    """
    start = text.find(open_ch)
    if start == -1:
        return None
    depth = 0
    in_str = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if in_str:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_str = False
            continue
        if ch == '"':
            in_str = True
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
    return None


class JSONExtractor:
    """Utility for extracting JSON from LLM responses."""

    @staticmethod
    def extract_json_from_response(content: str) -> Optional[Dict[str, Any]]:
        """
        Extract JSON from response content.

        Strategy (first hit wins): direct parse, then a fence-stripped
        block, then a balanced ``{...}`` object scan — all over the
        quote-normalised text. The balanced scan handles nested JSON and
        braces inside string literals, which the previous greedy regex
        could not.

        Returns a JSON **object** (dict) or ``None`` — this is the
        documented contract (callers do dict-style access). A top-level
        JSON array is NOT returned as a bare list (that would break the
        ``Optional[Dict]`` contract); a candidate that parses to a non-dict
        is skipped. (The router's separate ``extract_json`` keeps array
        support where lists are acceptable.)

        Args:
            content: Response content from LLM

        Returns:
            Extracted JSON dict or None if no valid JSON object found
        """
        if not content:
            return None

        text = _normalize_quotes(content)

        # Candidate substrings, cheapest/most-likely first.
        candidates: list[Optional[str]] = [text]
        for pattern in (r'```json\s*(.*?)\s*```', r'```\s*(.*?)\s*```'):
            candidates.extend(re.findall(pattern, text, re.DOTALL))
        candidates.append(_balanced_span(text, '{', '}'))

        for candidate in candidates:
            if not candidate:
                continue
            try:
                parsed = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            # Honor the dict-or-None contract: skip non-objects (e.g. a bare
            # array/number that the whole-string `text` candidate may parse to).
            if isinstance(parsed, dict):
                return parsed

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
