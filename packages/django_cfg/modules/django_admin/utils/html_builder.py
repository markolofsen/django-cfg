"""
HtmlBuilder - Facade class for backward compatibility.

This class provides the old `self.html.*` API by delegating to new modular components.
All existing admin code using `self.html.badge()`, `self.html.inline()`, etc. will continue to work.

New code should import and use the specific modules directly:
    from django_cfg.modules.django_admin.utils import BaseElements, FormattingElements, etc.
"""

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


class HtmlBuilder:
    """
    Facade class that delegates to modular HTML utilities.

    Provides backward compatibility for `self.html.*` API in admin classes.
    """

    # === BaseElements ===
    icon = staticmethod(BaseElements.icon)
    span = staticmethod(BaseElements.span)
    text = staticmethod(BaseElements.text)
    div = staticmethod(BaseElements.div)
    link = staticmethod(BaseElements.link)
    empty = staticmethod(BaseElements.empty)

    # === CodeElements ===
    code = staticmethod(CodeElements.code)
    code_block = staticmethod(CodeElements.code_block)

    # === BadgeElements ===
    badge = staticmethod(BadgeElements.badge)

    # === CompositionElements ===
    inline = staticmethod(CompositionElements.inline)
    join = staticmethod(CompositionElements.join)
    icon_text = staticmethod(CompositionElements.icon_text)
    colored_text = staticmethod(CompositionElements.colored_text)
    header = staticmethod(CompositionElements.header)

    # === FormattingElements ===
    number = staticmethod(FormattingElements.number)
    uuid_short = staticmethod(FormattingElements.uuid_short)
    truncate = staticmethod(FormattingElements.truncate)

    # === KeyValueElements ===
    key_value = staticmethod(KeyValueElements.key_value)
    breakdown = staticmethod(KeyValueElements.breakdown)
    divider = staticmethod(KeyValueElements.divider)
    key_value_list = staticmethod(KeyValueElements.key_value_list)

    # === ProgressElements ===
    segment = staticmethod(ProgressElements.segment)
    progress_bar = staticmethod(ProgressElements.progress_bar)

    # === MarkdownIntegration ===
    markdown = staticmethod(MarkdownIntegration.markdown)
    markdown_docs = staticmethod(MarkdownIntegration.markdown_docs)
