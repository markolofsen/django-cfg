"""
Composition elements for Django Admin.

Provides methods for composing multiple elements together: inline, icon_text, header.
"""

from typing import Any, Optional, Union

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString

from . import _classes as C


class CompositionElements:
    """Element composition utilities."""

    @staticmethod
    def icon(icon_name: str, size: str = "xs", css_class: str = "") -> SafeString:
        """
        Render Material Icon (helper for internal use).

        Args:
            icon_name: Icon name
            size: Icon size
            css_class: Additional CSS classes
        """
        from .base import BaseElements
        return BaseElements.icon(icon_name, size, css_class)

    @staticmethod
    def icon_text(icon_or_text: Union[str, Any], text: Any = None,
                  icon_size: str = "xs", separator: str = " ",
                  color: str | None = None) -> SafeString:
        """
        Render icon with text or emoji with text.

        Args:
            icon_or_text: Icon from Icons class, emoji, or text if text param is None
            text: Optional text to display after icon
            icon_size: Icon size (xs, sm, base, lg, xl)
            separator: Separator between icon and text
            color: Optional color (success, warning, danger, info, secondary, primary)

        Usage:
            html.icon_text(Icons.EDIT, 5)  # Icon with number
            html.icon_text("Active")  # Just text
            html.icon_text(Icons.CHECK, "Yes", color="success")  # Icon with color
        """
        color_class = C.text_tone(color)
        
        if text is None:
            # Just text
            if color_class:
                return format_html('<span class="{}">{}</span>', color_class, escape(str(icon_or_text)))
            return format_html('<span>{}</span>', escape(str(icon_or_text)))

        # Render icon (Material Icon from Icons class)
        icon_str = str(icon_or_text)
        icon_html = CompositionElements.icon(icon_str, size=icon_size)

        # DON'T escape SafeString - it's already safe HTML!
        from django.utils.safestring import SafeString
        if isinstance(text, SafeString):
            text_html = text
        else:
            text_html = escape(str(text))

        # Wrap in span with color class if provided
        if color_class:
            return format_html('<span class="{}">{}{}<span>{}</span></span>', 
                             color_class, icon_html, separator, text_html)

        return format_html('{}{}<span>{}</span>', icon_html, separator, text_html)

    @staticmethod
    def colored_text(text: Any, color: str | None = None) -> SafeString:
        """
        Render colored text.

        Args:
            text: Text to display
            color: Color (success, warning, danger, info, secondary, primary)

        Usage:
            html.colored_text("Active", "success")
            html.colored_text("5 minutes ago", "warning")
        """
        color_class = C.text_tone(color)
        
        if color_class:
            return format_html('<span class="{}">{}</span>', color_class, escape(str(text)))
        
        return format_html('<span>{}</span>', escape(str(text)))

    @staticmethod
    def inline(*items, separator: str = " | ",
               size: str = "small", css_class: str = "") -> SafeString:
        """
        Render items inline with separator.

        Args:
            *items: Variable number of SafeString/str items to join (filters out None values)
            separator: Separator between items
            size: small, medium, large
            css_class: Additional CSS classes

        Usage:
            html.inline(
                html.icon_text(Icons.EDIT, 5),
                html.icon_text(Icons.CHAT, 10),
                separator=" | "
            )
        """
        # Filter out None values
        filtered_items = [item for item in items if item is not None]
        return CompositionElements.join(filtered_items, separator, size, css_class)

    @staticmethod
    def join(items: list, separator: str = " ", 
             size: str = "small", css_class: str = "") -> SafeString:
        """
        Join a list of items with a separator.
        
        Args:
            items: List of items to join
            separator: Separator between items
            size: small, medium, large
            css_class: Additional CSS classes
        """
        # Filter out None values
        filtered_items = [item for item in items if item is not None]

        if not filtered_items:
            return format_html('<span class="{}">—</span>', C.MUTED)

        classes = C.join(C.SMALL if size == 'small' else '', css_class)

        # Convert items to strings, keeping SafeString as-is
        from django.utils.safestring import SafeString, mark_safe
        processed_items = []
        for item in filtered_items:
            if isinstance(item, (SafeString, str)):
                processed_items.append(item)
            else:
                processed_items.append(escape(str(item)))

        # Join with separator - str() doesn't lose SafeString when joined then mark_safe'd
        joined = mark_safe(separator.join(str(item) for item in processed_items))

        if classes:
            return format_html('<span class="{}">{}</span>', classes, joined)
        return format_html('<span>{}</span>', joined)

    @staticmethod
    def header(
        title: str,
        subtitle: Optional[str] = None,
        initials: Optional[str] = None,
        avatar_variant: str = "primary"
    ) -> SafeString:
        """
        Render header with avatar/initials, title and subtitle.

        Creates a horizontal layout with circular avatar badge and text content.
        Common pattern for displaying users, accounts, entities with identity.

        Args:
            title: Main title text
            subtitle: Optional subtitle text (smaller, muted)
            initials: Optional initials for avatar (e.g., "AB", "JD")
            avatar_variant: Color variant for avatar badge (primary, success, info, etc.)

        Usage:
            # User with avatar
            html.header(
                title="John Doe",
                subtitle="john@example.com • Admin",
                initials="JD"
            )

            # Account with info
            html.header(
                title="Trading Account",
                subtitle="Binance • SPOT • user@email.com",
                initials="TA",
                avatar_variant="success"
            )

            # Simple title only
            html.header(title="Item Name")

        Returns:
            SafeString with header component HTML
        """
        # Avatar/initials badge
        avatar_html = ""
        if initials:
            avatar_html = format_html(
                '<span class="{} cfg-avatar">{}</span>',
                C.badge(avatar_variant, default='primary'),
                escape(initials)
            )

        # Title
        title_html = format_html(
            '<div class="{}">{}</div>',
            C.STRONG,
            escape(title)
        )

        # Subtitle
        subtitle_html = ""
        if subtitle:
            subtitle_html = format_html(
                '<div class="{}">{}</div>',
                C.join(C.SMALL, C.MUTED),
                escape(subtitle)
            )

        # Combine
        return format_html(
            '<div class="{}">{}<div>{}{}</div></div>',
            C.ROW,
            avatar_html,
            title_html,
            subtitle_html
        )

    @staticmethod
    def stacked(items: list, css_class: str = "") -> SafeString:
        """
        Render items stacked vertically (one below another).

        Useful for computed fields that need multi-line display like StackedField.

        Args:
            items: List of SafeString/str items to stack vertically
            css_class: Additional CSS classes for container

        Usage:
            html.stacked([
                html.text("Line 1", bold=True),
                html.text("Line 2", muted=True),
            ])

        Returns:
            SafeString with stacked layout HTML
        """
        from django.utils.safestring import SafeString, mark_safe

        # Filter out None values
        filtered_items = [item for item in items if item is not None]

        if not filtered_items:
            return format_html('<span class="{}">—</span>', C.MUTED)

        # Convert items to divs
        divs = []
        for item in filtered_items:
            if isinstance(item, SafeString):
                divs.append(format_html('<div>{}</div>', item))
            else:
                divs.append(format_html('<div>{}</div>', escape(str(item))))

        # Join divs
        joined = mark_safe(''.join(str(d) for d in divs))

        classes = C.join(C.STACK, css_class)

        return format_html('<div class="{}">{}</div>', classes, joined)
