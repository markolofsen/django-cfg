"""
Display utilities with humanize integration.
"""

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, List, Optional, Union

from django.contrib.humanize.templatetags.humanize import naturaltime
from django.utils import timezone
from django.utils.html import escape, format_html
from django.utils.safestring import SafeString

from ..icons import Icons
from ..models.display_models import DateTimeDisplayConfig, MoneyDisplayConfig, UserDisplayConfig

logger = logging.getLogger(__name__)


class UserDisplay:
    """User display utilities."""

    @classmethod
    def with_avatar(cls, user: Any, config: Optional[UserDisplayConfig] = None) -> List[str]:
        """Display user with avatar for @display(header=True)."""
        config = config or UserDisplayConfig()

        if not user:
            return ["No user", "", "", {}]

        name = getattr(user, 'get_full_name', lambda: '')() or getattr(user, 'username', 'Unknown')
        email = getattr(user, 'email', '') if config.show_email else ''

        # Generate initials
        name_parts = name.split()
        if len(name_parts) >= 2:
            initials = f"{name_parts[0][0]}{name_parts[1][0]}".upper()
        elif name:
            initials = name[0].upper()
        else:
            initials = "U"

        avatar_data = {"size": config.avatar_size, "initials": initials, "show": config.show_avatar}

        return [name, email, initials, avatar_data]

    @classmethod
    def simple(cls, user: Any, config: Optional[UserDisplayConfig] = None) -> SafeString:
        """Simple user display."""
        config = config or UserDisplayConfig()

        if not user:
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">No user</span>')

        name = getattr(user, 'get_full_name', lambda: '')() or getattr(user, 'username', 'Unknown')
        html = format_html('<span class="font-medium">{}</span>', escape(name))

        if config.show_email:
            email = getattr(user, 'email', '')
            if email:
                html = format_html('{}<br><span class="text-xs text-font-subtle-light dark:text-font-subtle-dark">{}</span>', html, escape(email))

        return html


class MoneyDisplay:
    """Money display utilities."""

    @classmethod
    def amount(cls, amount: Union[Decimal, float, int], config: Optional[MoneyDisplayConfig] = None) -> SafeString:
        """Format money amount with smart formatting."""
        config = config or MoneyDisplayConfig()

        if amount is None:
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>')

        amount = Decimal(str(amount))

        # Smart decimal places for rates or auto-adjustment
        decimal_places = config.decimal_places
        if config.smart_decimal_places or config.rate_mode:
            if amount >= 1000:
                decimal_places = 0  # 1,234 (whole numbers for large amounts)
            elif amount >= 100:
                decimal_places = 1  # 123.4
            elif amount >= 10:
                decimal_places = 2  # 12.34
            elif amount >= 1:
                decimal_places = 3  # 1.234
            elif amount >= 0.01:
                decimal_places = 4  # 0.1234
            else:
                decimal_places = 8  # 0.00001234 (for very small amounts)

        # Currency symbols
        symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'BTC': '₿', 'ETH': 'Ξ'}
        symbol = symbols.get(config.currency, config.currency) if config.show_currency_symbol else ""

        # Format with appropriate decimal places
        if config.thousand_separator:
            if decimal_places == 0:
                formatted_amount = f"{amount:,.0f}"
            else:
                formatted_amount = f"{amount:,.{decimal_places}f}"
        else:
            formatted_amount = f"{amount:.{decimal_places}f}"

        # Special formatting for rate mode
        if config.rate_mode:
            # For rates, show number + small currency label instead of symbol
            return format_html(
                '<span class="font-mono text-sm">{} <span class="text-font-subtle-light dark:text-font-subtle-dark text-xs">{}</span></span>',
                formatted_amount,
                config.currency
            )

        # Color coding for regular amounts
        if amount < 0:
            color_class = "text-red-600 dark:text-red-400"
        elif amount == 0:
            color_class = "text-font-default-light dark:text-font-default-dark"
        else:
            color_class = "text-green-600 dark:text-green-400"

        # Show sign
        sign = "+" if config.show_sign and amount > 0 else ""

        return format_html('<span class="font-mono {}">{}{}{}</span>', color_class, sign, symbol, formatted_amount)

    @classmethod
    def with_breakdown(cls, main_amount: Union[Decimal, float, int], breakdown_items: List[dict] = None,
                      config: Optional[MoneyDisplayConfig] = None) -> SafeString:
        """Display with breakdown."""
        config = config or MoneyDisplayConfig()

        html = format_html('<div class="text-right">')
        html += cls.amount(main_amount, config)

        if breakdown_items:
            for item in breakdown_items:
                label = item.get('label', 'Item')
                amount = item.get('amount', 0)
                color = item.get('color', 'secondary')

                color_classes = {
                    'success': 'text-green-600 dark:text-green-400',
                    'warning': 'text-yellow-600 dark:text-yellow-400',
                    'danger': 'text-red-600 dark:text-red-400',
                    'secondary': 'text-font-subtle-light dark:text-font-subtle-dark'
                }

                color_class = color_classes.get(color, 'text-font-subtle-light dark:text-font-subtle-dark')
                html += format_html('<div class="text-xs {}">{}: {}</div>', color_class, escape(label), cls.amount(amount, config))

        html += format_html('</div>')
        return html


class DateTimeDisplay:
    """DateTime display utilities."""

    @classmethod
    def relative(cls, dt: datetime, config: Optional[DateTimeDisplayConfig] = None) -> SafeString:
        """Display with relative time."""
        config = config or DateTimeDisplayConfig()

        if not dt:
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>')

        absolute_time = dt.strftime(config.datetime_format)
        relative_time = naturaltime(dt)

        if config.show_relative:
            return format_html(
                '<div class="text-xs"><div class="font-medium">{}</div><div class="text-font-subtle-light dark:text-font-subtle-dark">{}</div></div>',
                escape(absolute_time), escape(relative_time)
            )
        else:
            return format_html('<span class="text-sm">{}</span>', escape(absolute_time))

    @classmethod
    def compact(cls, dt: datetime, config: Optional[DateTimeDisplayConfig] = None) -> SafeString:
        """Compact datetime display."""
        config = config or DateTimeDisplayConfig()

        if not dt:
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>')

        now = timezone.now()
        diff = now - dt

        if diff.days < 1:
            display_text = naturaltime(dt)
        elif diff.days < 7:
            display_text = dt.strftime('%a %H:%M')
        else:
            display_text = dt.strftime('%m/%d/%y')

        return format_html(
            '<span class="text-xs text-font-default-light dark:text-font-default-dark" title="{}">{}</span>',
            escape(dt.strftime(config.datetime_format)), escape(display_text)
        )
