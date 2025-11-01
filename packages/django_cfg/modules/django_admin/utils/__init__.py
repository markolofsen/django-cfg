"""
Display and utility modules for Django Admin.

Refactored structure with logical organization:
- badges/ - Status badges, progress badges, counter badges
- displays/ - User displays, money displays, datetime displays
- html/ - HTML building utilities (organized by functionality)
- markdown/ - Markdown rendering with Mermaid support
- decorators.py - Admin field decorators
- html_builder.py - Backward-compatible facade for self.html.* API
"""

# Badges
from .badges import CounterBadge, ProgressBadge, StatusBadge

# Decorators
from .decorators import (
    annotated_field,
    badge_field,
    computed_field,
    currency_field,
)

# Displays
from .displays import DateTimeDisplay, MoneyDisplay, UserDisplay

# HTML Builders (organized by functionality)
from .html import (
    BadgeElements,
    BaseElements,
    CodeElements,
    CompositionElements,
    FormattingElements,
    KeyValueElements,
    MarkdownIntegration,
    ProgressElements,
)

# HtmlBuilder - Backward-compatible facade
from .html_builder import HtmlBuilder

# Markdown
from .markdown import MarkdownRenderer

__all__ = [
    # Display utilities
    "UserDisplay",
    "MoneyDisplay",
    "DateTimeDisplay",
    # Badge utilities
    "StatusBadge",
    "ProgressBadge",
    "CounterBadge",
    # HTML Builders (modular)
    "BaseElements",
    "CodeElements",
    "BadgeElements",
    "CompositionElements",
    "FormattingElements",
    "KeyValueElements",
    "ProgressElements",
    "MarkdownIntegration",
    # HTML Builder (backward-compatible facade)
    "HtmlBuilder",
    # Markdown Renderer
    "MarkdownRenderer",
    # Decorators
    "computed_field",
    "badge_field",
    "currency_field",
    "annotated_field",
]
