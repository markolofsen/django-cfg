"""
Formatting elements for Django Admin.

Provides number and UUID formatting utilities.
"""

from typing import Any, Optional

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString


class FormattingElements:
    """Formatting utilities for numbers and UUIDs."""

    @staticmethod
    def empty(text: str = "—") -> SafeString:
        """Helper for empty values."""
        from .base import BaseElements
        return BaseElements.empty(text)

    @staticmethod
    def number(
        value: Any,
        precision: int = 8,
        thousands_separator: bool = True,
        strip_zeros: bool = True,
        min_threshold: Optional[float] = None,
        compact: bool = False,
        prefix: str = "",
        suffix: str = "",
        css_class: str = ""
    ) -> SafeString:
        """
        Format numeric values with smart precision handling.

        Handles:
        - Trailing zeros removal (20.000000 → 20)
        - Scientific notation (0E-18 → 0)
        - Thousands separators (1000000 → 1,000,000)
        - Very small numbers (0.0000001 → < 0.00000001)
        - Compact notation with K/M/B/T suffixes (1500000 → 1.5M)
        - Negative values

        Args:
            value: Numeric value (int, float, Decimal, str)
            precision: Number of decimal places (default: 8)
            thousands_separator: Add thousands separator (default: True)
            strip_zeros: Remove trailing zeros (default: True)
            min_threshold: Show "< threshold" for very small numbers
            compact: Use compact notation with K/M/B/T suffixes (default: False)
            prefix: Text before number (e.g., "$", "BTC ")
            suffix: Text after number (e.g., " USD", "%")
            css_class: Additional CSS classes

        Usage:
            # Crypto balance
            html.number(0.00012345, precision=8)  # "0.00012345"
            html.number(20.000000, precision=8)   # "20"
            html.number(1000000.5)                # "1,000,000.5"

            # Currency
            html.number(1234.56, precision=2, prefix="$")  # "$1,234.56"

            # Compact notation
            html.number(1500, compact=True, prefix="$")           # "$1.5K"
            html.number(2500000, compact=True, prefix="$")        # "$2.5M"
            html.number(3500000000, compact=True, prefix="$")     # "$3.5B"
            html.number(1200000000000, compact=True, prefix="$")  # "$1.2T"

            # Very small numbers
            html.number(0.0000001, precision=8, min_threshold=1e-8)  # "< 0.00000001"

            # Scientific notation handling
            html.number("0E-18", precision=8)  # "0"

        Returns:
            SafeString with formatted number
        """
        from decimal import Decimal, InvalidOperation

        # Handle None/empty
        if value is None or value == "":
            return FormattingElements.empty("—")

        # Convert to Decimal for precise calculations
        try:
            if isinstance(value, str):
                # Handle scientific notation in strings
                decimal_value = Decimal(value)
            elif isinstance(value, (int, float)):
                decimal_value = Decimal(str(value))
            elif isinstance(value, Decimal):
                decimal_value = value
            else:
                return FormattingElements.empty(str(value))
        except (InvalidOperation, ValueError):
            return FormattingElements.empty(str(value))

        # Check if value is effectively zero (scientific notation like 0E-18)
        if decimal_value == 0:
            formatted = "0"
        else:
            # Check min_threshold for very small positive numbers
            if min_threshold and 0 < abs(decimal_value) < min_threshold:
                threshold_str = f"{min_threshold:.{precision}f}"
                if strip_zeros:
                    threshold_str = threshold_str.rstrip('0').rstrip('.')
                return format_html(
                    '<span class="{}">{}< {}{}</span>',
                    css_class,
                    escape(prefix),
                    threshold_str,
                    escape(suffix)
                )

            # Compact notation with K/M/B/T suffixes
            if compact:
                abs_value = abs(float(decimal_value))
                is_negative = decimal_value < 0
                compact_suffix = ""

                # Determine divisor and suffix
                if abs_value >= 1_000_000_000_000:  # Trillion
                    divided_value = abs_value / 1_000_000_000_000
                    compact_suffix = "T"
                elif abs_value >= 1_000_000_000:  # Billion
                    divided_value = abs_value / 1_000_000_000
                    compact_suffix = "B"
                elif abs_value >= 1_000_000:  # Million
                    divided_value = abs_value / 1_000_000
                    compact_suffix = "M"
                elif abs_value >= 1_000:  # Thousand
                    divided_value = abs_value / 1_000
                    compact_suffix = "K"
                else:
                    # Below 1000, use normal formatting
                    divided_value = abs_value
                    compact_suffix = ""

                # Format with precision (use 1 decimal for compact)
                compact_precision = 1 if compact_suffix else precision
                formatted = f"{divided_value:.{compact_precision}f}"

                # Strip trailing zeros if requested
                if strip_zeros:
                    formatted = formatted.rstrip('0').rstrip('.')

                # Add negative sign back
                if is_negative:
                    formatted = f"-{formatted}"

                # Add compact suffix
                formatted += compact_suffix
            else:
                # Format with precision
                formatted = f"{decimal_value:.{precision}f}"

                # Strip trailing zeros if requested (only for non-compact)
                if strip_zeros:
                    formatted = formatted.rstrip('0').rstrip('.')

                # Add thousands separator (only for non-compact)
                if thousands_separator:
                    parts = formatted.split('.')
                    integer_part = parts[0]
                    decimal_part = parts[1] if len(parts) > 1 else None

                    # Handle negative sign
                    is_negative = integer_part.startswith('-')
                    if is_negative:
                        integer_part = integer_part[1:]

                    # Add commas
                    integer_part = f"{int(integer_part):,}"

                    # Restore negative sign
                    if is_negative:
                        integer_part = f"-{integer_part}"

                    # Rebuild number
                    formatted = integer_part
                    if decimal_part:
                        formatted += f".{decimal_part}"

        # Add prefix/suffix
        result = f"{prefix}{formatted}{suffix}"

        # Wrap in span with CSS class if provided
        if css_class:
            return format_html('<span class="{}">{}</span>', css_class, result)

        return format_html('<span>{}</span>', result)

    @staticmethod
    def truncate(
        text: str,
        length: int = 100,
        suffix: str = "...",
        show_tooltip: bool = True
    ) -> SafeString:
        """
        Truncate text to specified length with optional tooltip.

        Args:
            text: Text to truncate
            length: Maximum length (default: 100)
            suffix: Text to append when truncated (default: "...")
            show_tooltip: Show full text on hover (default: True)

        Usage:
            html.truncate("Long message text here", length=50)
            html.truncate(obj.description, length=80, suffix="…")
            html.truncate(obj.message_text, show_tooltip=False)

        Returns:
            SafeString with truncated text
        """
        if not text:
            return FormattingElements.empty("—")

        # If text is shorter than limit, return as-is
        if len(text) <= length:
            return format_html('<span>{}</span>', text)

        # Truncate and add suffix
        truncated = text[:length].rstrip() + suffix

        if show_tooltip:
            return format_html(
                '<span class="cursor-help" title="{}">{}</span>',
                escape(text),
                truncated
            )

        return format_html('<span>{}</span>', truncated)

    @staticmethod
    def uuid_short(uuid_value: Any, length: int = 6, show_tooltip: bool = True) -> SafeString:
        """
        Shorten UUID to first N characters with optional tooltip.

        Args:
            uuid_value: UUID string or UUID object
            length: Number of characters to show (default: 6)
            show_tooltip: Show full UUID on hover (default: True)

        Usage:
            html.uuid_short(obj.id)  # "a1b2c3..."
            html.uuid_short(obj.id, length=8)  # "a1b2c3d4..."
            html.uuid_short(obj.id, show_tooltip=False)  # Just short version

        Returns:
            SafeString with shortened UUID
        """
        uuid_str = str(uuid_value)

        # Remove dashes for cleaner display
        uuid_clean = uuid_str.replace('-', '')

        # Take first N characters
        short_uuid = uuid_clean[:length]

        if show_tooltip:
            return format_html(
                '<code class="font-mono text-xs bg-base-100 dark:bg-base-800 px-1.5 py-0.5 rounded cursor-help" title="{}">{}</code>',
                uuid_str,
                short_uuid
            )

        return format_html(
            '<code class="font-mono text-xs bg-base-100 dark:bg-base-800 px-1.5 py-0.5 rounded">{}</code>',
            short_uuid
        )
