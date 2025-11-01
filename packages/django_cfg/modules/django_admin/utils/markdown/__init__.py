"""
Markdown rendering utilities for Django Admin.

Provides MarkdownRenderer and mermaid plugin support.
"""

from .mermaid_plugin import (
    get_mermaid_resources,
    get_mermaid_script,
    get_mermaid_styles,
    mermaid_plugin,
)
from .renderer import MarkdownRenderer

__all__ = [
    "MarkdownRenderer",
    "mermaid_plugin",
    "get_mermaid_styles",
    "get_mermaid_script",
    "get_mermaid_resources",
]
