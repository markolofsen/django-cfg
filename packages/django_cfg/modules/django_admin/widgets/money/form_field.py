"""MoneyFieldFormField — MultiValueField wrapping MoneyFieldWidget."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

from django import forms

from ._rate_utils import FALLBACK_CURRENCY_CHOICES, get_currency_choices
from .widget import MoneyFieldWidget


class MoneyFieldFormField(forms.MultiValueField):
    """Form field for MoneyField — combines amount + currency into a dict."""

    widget = MoneyFieldWidget

    def __init__(
        self,
        *,
        currency_choices: Optional[List[Tuple[str, str]]] = None,
        default_currency: str = "USD",
        max_digits: int = 15,
        decimal_places: int = 2,
        **kwargs: Any,
    ) -> None:
        self.default_currency = default_currency

        if "widget" not in kwargs:
            kwargs["widget"] = MoneyFieldWidget(
                currency_choices=currency_choices,
                default_currency=default_currency,
            )

        fields = [
            forms.DecimalField(
                max_digits=max_digits,
                decimal_places=decimal_places,
                required=False,
                localize=False,
            ),
            forms.ChoiceField(
                choices=currency_choices or get_currency_choices() or FALLBACK_CURRENCY_CHOICES,
                required=False,
            ),
        ]
        super().__init__(fields=fields, require_all_fields=False, **kwargs)

    def compress(self, data_list: List[Any]) -> Optional[Dict[str, Any]]:
        """Combine [amount, currency] into a dict."""
        if not data_list or data_list[0] is None:
            return None
        return {
            "amount": data_list[0],
            "currency": data_list[1] if len(data_list) > 1 else self.default_currency,
        }
