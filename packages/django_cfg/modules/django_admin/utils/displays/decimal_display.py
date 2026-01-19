"""
Decimal display utilities with formatting options.
"""

from decimal import Decimal
from typing import Any, Dict, Optional, Union

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString


class DecimalDisplay:
    """Decimal number display with formatting options."""

    @classmethod
    def from_field(cls, obj: Any, field_name: str, config: Dict[str, Any]) -> SafeString:
        """
        Render decimal field with configuration.

        Config options:
            decimal_places: int - Decimal places to show (default: 2)
            prefix: str - Prefix symbol (e.g., "$")
            suffix: str - Suffix symbol (e.g., "%", "BTC")
            show_sign: bool - Show +/- sign (default: False)
            thousand_separator: bool - Use thousand separator (default: True)
            monospace: bool - Use monospace font (default: True)
        """
        value = getattr(obj, field_name, None)
        return cls.format_value(value, config)

    @classmethod
    def format_value(
        cls,
        value: Optional[Union[Decimal, float, int, str]],
        config: Optional[Dict[str, Any]] = None,
    ) -> SafeString:
        """
        Format decimal value with configuration.

        Args:
            value: Decimal/float/int value to format
            config: Formatting options

        Returns:
            Formatted HTML string
        """
        if config is None:
            config = {}

        if value is None:
            return format_html(
                '<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>'
            )

        # Parse config
        decimal_places = config.get('decimal_places', 2)
        prefix = config.get('prefix', '')
        suffix = config.get('suffix', '')
        show_sign = config.get('show_sign', False)
        thousand_separator = config.get('thousand_separator', True)
        monospace = config.get('monospace', True)

        # Convert to Decimal for precision
        try:
            if isinstance(value, str):
                value = Decimal(value)
            elif isinstance(value, float):
                value = Decimal(str(value))
            elif isinstance(value, int):
                value = Decimal(value)
            # Already Decimal - use as is
        except Exception:
            return format_html(
                '<span class="text-red-700 dark:text-red-400">{}</span>',
                escape(str(value))
            )

        # Format number
        is_negative = value < 0
        abs_value = abs(value)

        # Round to decimal places
        if decimal_places >= 0:
            quantize_str = '0.' + '0' * decimal_places if decimal_places > 0 else '0'
            abs_value = abs_value.quantize(Decimal(quantize_str))

        # Convert to string
        formatted = str(abs_value)

        # Add thousand separator
        if thousand_separator:
            parts = formatted.split('.')
            integer_part = parts[0]
            # Add separators
            integer_part = '{:,}'.format(int(integer_part))
            if len(parts) > 1:
                formatted = f"{integer_part}.{parts[1]}"
            else:
                formatted = integer_part

        # Build sign
        sign = ''
        if is_negative:
            sign = '-'
        elif show_sign and value > 0:
            sign = '+'

        # Build display text
        display_text = f"{sign}{prefix}{formatted}{suffix}"

        # Color based on sign (Unfold-compatible)
        color_class = ""
        if show_sign or is_negative:
            if is_negative:
                color_class = "text-red-700 dark:text-red-400"
            elif value > 0:
                color_class = "text-green-700 dark:text-green-400"

        # Build CSS classes
        classes = ["text-sm", "tabular-nums"]
        if monospace:
            classes.append("font-mono")
        if color_class:
            classes.append(color_class)

        return format_html(
            '<span class="{}">{}</span>',
            " ".join(classes),
            escape(display_text)
        )

    @classmethod
    def simple(
        cls,
        value: Optional[Union[Decimal, float, int]],
        decimal_places: int = 2,
        prefix: str = "",
        suffix: str = "",
    ) -> SafeString:
        """
        Simple decimal display without sign coloring.

        Args:
            value: Number to format
            decimal_places: Decimal places
            prefix: Prefix symbol
            suffix: Suffix symbol
        """
        return cls.format_value(value, {
            'decimal_places': decimal_places,
            'prefix': prefix,
            'suffix': suffix,
            'show_sign': False,
            'thousand_separator': True,
        })

    @classmethod
    def percentage(
        cls,
        value: Optional[Union[Decimal, float, int]],
        decimal_places: int = 2,
        show_sign: bool = True,
    ) -> SafeString:
        """
        Display as percentage with coloring.

        Args:
            value: Percentage value (e.g., 5.5 for 5.5%)
            decimal_places: Decimal places
            show_sign: Show +/- sign
        """
        return cls.format_value(value, {
            'decimal_places': decimal_places,
            'suffix': '%',
            'show_sign': show_sign,
            'thousand_separator': True,
        })

    @classmethod
    def currency(
        cls,
        value: Optional[Union[Decimal, float, int]],
        symbol: str = "$",
        decimal_places: int = 2,
    ) -> SafeString:
        """
        Display as currency.

        Args:
            value: Currency amount
            symbol: Currency symbol
            decimal_places: Decimal places
        """
        return cls.format_value(value, {
            'decimal_places': decimal_places,
            'prefix': symbol,
            'show_sign': False,
            'thousand_separator': True,
        })
