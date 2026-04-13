"""PII Redaction Service for MCP."""

import re
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class RedactionMode(Enum):
    """Redaction behavior modes."""
    NONE = "none"  # Pass through
    REDACT = "redact"  # Mask sensitive data
    BLOCK = "block"  # Reject entirely


@dataclass
class RedactionPattern:
    """Regex pattern for PII detection."""
    name: str
    pattern: str
    replacement: str
    severity: str  # low, medium, high, critical


# Default PII patterns
DEFAULT_PATTERNS = [
    RedactionPattern(
        name="email",
        pattern=r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
        replacement="[EMAIL_REDACTED]",
        severity="medium",
    ),
    RedactionPattern(
        name="phone_us",
        pattern=r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
        replacement="[PHONE_REDACTED]",
        severity="medium",
    ),
    RedactionPattern(
        name="ssn",
        pattern=r"\b\d{3}-\d{2}-\d{4}\b",
        replacement="[SSN_REDACTED]",
        severity="critical",
    ),
    RedactionPattern(
        name="credit_card",
        pattern=r"\b(?:\d{4}[-\s]?){3}\d{4}\b",
        replacement="[CC_REDACTED]",
        severity="critical",
    ),
    RedactionPattern(
        name="api_key_generic",
        pattern=r"\b(?:api[_-]?key|apikey|token|secret)[\s:=]+['\"]?([A-Za-z0-9_\-]{20,})['\"]?",
        replacement="[API_KEY_REDACTED]",
        severity="high",
    ),
    RedactionPattern(
        name="aws_key",
        pattern=r"\bAKIA[0-9A-Z]{16}\b",
        replacement="[AWS_KEY_REDACTED]",
        severity="critical",
    ),
    RedactionPattern(
        name="private_key",
        pattern=r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----",
        replacement="[PRIVATE_KEY_BLOCKED]",
        severity="critical",
    ),
]


class PiiRedactor:
    """Automatic PII redaction service."""

    def __init__(self, patterns: Optional[List[RedactionPattern]] = None):
        self.patterns = patterns or DEFAULT_PATTERNS[:]
        self._compiled_patterns = [
            (re.compile(p.pattern), p)
            for p in self.patterns
        ]

    def add_pattern(self, pattern: RedactionPattern):
        """Add custom redaction pattern."""
        self.patterns.append(pattern)
        self._compiled_patterns.append((re.compile(pattern.pattern), pattern))

    def redact_string(self, text: str, mode: RedactionMode = RedactionMode.REDACT) -> str:
        """Redact PII from a string."""
        if mode == RedactionMode.NONE:
            return text

        result = text
        for regex, pattern in self._compiled_patterns:
            if mode == RedactionMode.REDACT:
                result = regex.sub(pattern.replacement, result)
            elif mode == RedactionMode.BLOCK:
                if regex.search(result):
                    return "[CONTENT_BLOCKED_BY_REDACTOR]"

        return result

    def redact_dict(self, data: Dict[str, Any], mode: RedactionMode = RedactionMode.REDACT) -> Dict[str, Any]:
        """Redact PII from a dictionary recursively."""
        if mode == RedactionMode.NONE:
            return data

        result = {}
        for key, value in data.items():
            if isinstance(value, str):
                result[key] = self.redact_string(value, mode)
            elif isinstance(value, dict):
                result[key] = self.redact_dict(value, mode)
            elif isinstance(value, list):
                result[key] = self.redact_list(value, mode)
            else:
                result[key] = value

        return result

    def redact_list(self, data: List[Any], mode: RedactionMode = RedactionMode.REDACT) -> List[Any]:
        """Redact PII from a list recursively."""
        result = []
        for item in data:
            if isinstance(item, str):
                result.append(self.redact_string(item, mode))
            elif isinstance(item, dict):
                result.append(self.redact_dict(item, mode))
            elif isinstance(item, list):
                result.append(self.redact_list(item, mode))
            else:
                result.append(item)
        return result

    def redact(self, data: Any, mode: RedactionMode = RedactionMode.REDACT) -> Any:
        """Redact PII from any data type."""
        if isinstance(data, str):
            return self.redact_string(data, mode)
        elif isinstance(data, dict):
            return self.redact_dict(data, mode)
        elif isinstance(data, list):
            return self.redact_list(data, mode)
        return data


# Global redactor instance
redactor = PiiRedactor()


def apply_redaction(data: Any, mode: RedactionMode = RedactionMode.REDACT,
                    custom_patterns: Optional[Dict[str, str]] = None) -> Any:
    """Apply redaction based on configuration."""
    if mode == RedactionMode.NONE:
        return data

    # Add custom patterns if provided
    if custom_patterns:
        for name, pattern in custom_patterns.items():
            redactor.add_pattern(RedactionPattern(
                name=name,
                pattern=pattern,
                replacement=f"[{name.upper()}_REDACTED]",
                severity="medium",
            ))

    return redactor.redact(data, mode)
