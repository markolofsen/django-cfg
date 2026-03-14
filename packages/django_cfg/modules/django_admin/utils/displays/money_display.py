"""Money display utilities."""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, List, Optional, Union

from django.utils.html import escape, format_html
from django.utils.safestring import SafeString

from ...models.display_models import MoneyDisplayConfig

logger = logging.getLogger(__name__)


class MoneyDisplay:
    """Money display utilities."""

    @classmethod
    def amount(
        cls,
        amount: Union[Decimal, float, int, None],
        config: Optional[MoneyDisplayConfig] = None,
    ) -> SafeString:
        """Format money amount with smart formatting."""
        config = config or MoneyDisplayConfig()

        if amount is None:
            return format_html('<span class="text-font-subtle-light dark:text-font-subtle-dark">—</span>')

        amount = Decimal(str(amount))

        decimal_places = config.decimal_places
        if config.smart_decimal_places or config.rate_mode:
            if amount >= 1000:
                decimal_places = 0
            elif amount >= 100:
                decimal_places = 1
            elif amount >= 10:
                decimal_places = 2
            elif amount >= 1:
                decimal_places = 3
            elif amount >= Decimal("0.01"):
                decimal_places = 4
            else:
                decimal_places = 8

        symbols = {'USD': '$', 'EUR': '€', 'GBP': '£', 'JPY': '¥', 'BTC': '₿', 'ETH': 'Ξ'}
        symbol = symbols.get(config.currency, config.currency) if config.show_currency_symbol else ""

        if config.thousand_separator:
            formatted_amount = f"{amount:,.{decimal_places}f}" if decimal_places else f"{amount:,.0f}"
        else:
            formatted_amount = f"{amount:.{decimal_places}f}"

        if config.rate_mode:
            return format_html(
                '<span class="font-mono text-sm">{} <span class="text-font-subtle-light dark:text-font-subtle-dark text-xs">{}</span></span>',
                formatted_amount, config.currency,
            )

        if amount < 0:
            color_class = "text-red-600 dark:text-red-400"
        elif amount == 0:
            color_class = "text-font-default-light dark:text-font-default-dark"
        else:
            color_class = "text-green-600 dark:text-green-400"

        sign = "+" if config.show_sign and amount > 0 else ""
        return format_html('<span class="font-mono {}">{}{}{}</span>', color_class, sign, symbol, formatted_amount)

    @classmethod
    def with_breakdown(
        cls,
        main_amount: Union[Decimal, float, int, None],
        breakdown_items: Optional[List[dict]] = None,
        config: Optional[MoneyDisplayConfig] = None,
    ) -> SafeString:
        """Display with breakdown."""
        config = config or MoneyDisplayConfig()

        html = format_html('<div class="text-right">')
        html += cls.amount(main_amount, config)

        if breakdown_items:
            color_classes = {
                'success': 'text-green-600 dark:text-green-400',
                'warning': 'text-yellow-600 dark:text-yellow-400',
                'danger': 'text-red-600 dark:text-red-400',
                'secondary': 'text-font-subtle-light dark:text-font-subtle-dark',
            }
            for item in breakdown_items:
                label = item.get('label', 'Item')
                item_amount = item.get('amount', 0)
                color = item.get('color', 'secondary')
                color_class = color_classes.get(color, 'text-font-subtle-light dark:text-font-subtle-dark')
                html += format_html(
                    '<div class="text-xs {}">{}: {}</div>',
                    color_class, escape(label), cls.amount(item_amount, config),
                )

        html += format_html('</div>')
        return html
