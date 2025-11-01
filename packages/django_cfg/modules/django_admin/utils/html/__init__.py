"""
HTML builder module - organized and modular.

Exports all HTML building classes for easy access.
"""

from .badges import BadgeElements
from .base import BaseElements
from .code import CodeElements
from .composition import CompositionElements
from .formatting import FormattingElements
from .keyvalue import KeyValueElements
from .markdown_integration import MarkdownIntegration
from .progress import ProgressElements

__all__ = [
    # Core elements
    "BaseElements",
    "CodeElements",
    "BadgeElements",
    "CompositionElements",
    "FormattingElements",
    "KeyValueElements",
    "ProgressElements",
    "MarkdownIntegration",
]
