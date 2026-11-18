"""
Basic HTML elements for Django Admin.

Provides fundamental HTML building blocks: icons, spans, text, divs, links, and empty placeholders.
"""

from typing import Any, Literal, Optional

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString

from . import _classes as C


class BaseElements:
    """Basic HTML building blocks."""

    @staticmethod
    def icon(
        icon_name: str,
        size: Literal['xs', 'sm', 'base', 'lg', 'xl'] = "xs",
        css_class: str = "",
    ) -> SafeString:
        """
        Render Material Icon.

        Args:
            icon_name: Icon name from Icons class
            size: xs, sm, base, lg, xl
            css_class: Additional CSS classes
        """
        # xs/sm shrink the glyph; base and larger follow the surrounding text.
        classes = C.join(C.ICON, C.SMALL if size in ("xs", "sm") else "", css_class)

        return format_html('<span class="{}">{}</span>', classes, icon_name)

    @staticmethod
    def span(text: Any, css_class: str = "") -> SafeString:
        """
        Render text in span with optional CSS class.

        Args:
            text: Text to display
            css_class: CSS classes
        """
        if css_class:
            return format_html('<span class="{}">{}</span>', css_class, escape(str(text)))
        return format_html('<span>{}</span>', escape(str(text)))

    @staticmethod
    def text(
        content: Any,
        variant: Literal['success', 'warning', 'danger', 'info', 'primary'] | None = None,
        size: Literal['xs', 'sm', 'base', 'lg', 'xl', '2xl'] | None = None,
        weight: Literal['normal', 'medium', 'semibold', 'bold'] | None = None,
        muted: bool = False,
    ) -> SafeString:
        """
        Render styled text with semantic variants.

        Args:
            content: Text content (can be SafeString from other html methods)
            variant: Color variant - 'success', 'warning', 'danger', 'info', 'primary'
            size: Size - 'xs', 'sm', 'base', 'lg', 'xl', '2xl'
            weight: Font weight - 'normal', 'medium', 'semibold', 'bold'
            muted: Use muted/subtle color

        Usage:
            # Success text
            html.text("$1,234.56", variant="success", size="lg")

            # Muted small text
            html.text("(12.5%)", muted=True, size="sm")

            # Combined with other methods
            total = html.number(1234.56, prefix="$")
            html.text(total, variant="success", size="lg")

        Returns:
            SafeString with styled text
        """
        classes = []

        if variant:
            classes.append(C.text_tone(variant))
        if muted:
            classes.append(C.MUTED)
        if size in ('xs', 'sm'):
            classes.append(C.SMALL)
        if weight in ('medium', 'semibold', 'bold'):
            classes.append(C.STRONG)

        css_class = C.join(*classes)

        if css_class:
            return format_html('<span class="{}">{}</span>', css_class, content)
        return format_html('<span>{}</span>', content)

    @staticmethod
    def div(content: Any, css_class: str = "") -> SafeString:
        """
        Render content in div with optional CSS class.

        Args:
            content: Content to display (can be SafeString)
            css_class: CSS classes
        """
        if css_class:
            return format_html('<div class="{}">{}</div>', css_class, content)
        return format_html('<div>{}</div>', content)

    @staticmethod
    def link(
        url: str,
        text: str,
        css_class: str = "",
        target: str = "",
        icon: Optional[str] = None,
        variant: Literal['success', 'warning', 'danger', 'info', 'primary'] | None = None,
    ) -> SafeString:
        """
        Render link.

        Args:
            url: URL
            text: Link text
            css_class: CSS classes
            target: Target attribute (_blank, _self, etc)
            icon: Icon name from Icons class
            variant: Color variant
        """
        classes = []
        if css_class:
            classes.append(css_class)
            
        if variant:
            classes.append(C.text_tone(variant))

        final_css_class = C.join(*classes)
        
        content = escape(text)
        if icon:
            # Use BaseElements.icon directly
            icon_html = BaseElements.icon(icon, size="sm")
            content = format_html("{} {}", icon_html, content)

        if target:
            return format_html(
                '<a href="{}" class="{}" target="{}">{}</a>',
                url, final_css_class, target, content
            )
        return format_html('<a href="{}" class="{}">{}</a>', url, final_css_class, content)

    @staticmethod
    def empty(text: str = "—") -> SafeString:
        """Render empty/placeholder value."""
        return format_html('<span class="{}">{}</span>', C.MUTED, text)
