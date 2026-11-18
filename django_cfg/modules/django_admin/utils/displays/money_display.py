"""Money display utilities."""
from __future__ import annotations

import logging
from decimal import Decimal
from typing import List, Optional, Union

from django.utils.html import format_html
from django.utils.safestring import SafeString, mark_safe

from ...models.display_models import MoneyDisplayConfig
from ..html import _classes as C

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
            return format_html('<span class="{}">—</span>', C.MUTED)

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
                '<span class="cfg-mono">{} <span class="cfg-muted cfg-small">{}</span></span>',
                formatted_amount, config.currency,
            )

        if amount < 0:
            color_class = "cfg-danger"
        elif amount == 0:
            color_class = ""
        else:
            color_class = "cfg-success"

        sign = "+" if config.show_sign and amount > 0 else ""
        return format_html('<span class="{}">{}{}{}</span>', C.join(C.MONO, color_class), sign, symbol, formatted_amount)

    @classmethod
    def with_breakdown(
        cls,
        main_amount: Union[Decimal, float, int, None],
        breakdown_items: Optional[List[dict]] = None,
        config: Optional[MoneyDisplayConfig] = None,
    ) -> SafeString:
        """Display with breakdown."""
        config = config or MoneyDisplayConfig()

        html = mark_safe('<div class="cfg-stack">')
        html += cls.amount(main_amount, config)

        if breakdown_items:
            for item in breakdown_items:
                label = item.get('label', 'Item')
                item_amount = item.get('amount', 0)
                color = item.get('color', 'secondary')
                html += format_html(
                    '<div class="{}">{}: {}</div>',
                    C.join(C.SMALL, C.text_tone(color) or C.MUTED), label, cls.amount(item_amount, config),
                )

        html += mark_safe('</div>')
        return html
