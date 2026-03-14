"""
MoneyFieldWidget — unified money input for Django Admin.

Editable: [amount DecimalInput] [currency Select] + live conversion info.
Readonly: ₩15,700,000 → $10,645.05 (rate info line below).
"""
from __future__ import annotations

from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from django.forms.widgets import MultiWidget, Select, TextInput
from django.utils.safestring import SafeString, mark_safe

from django_cfg.modules.django_currency.formatter import CURRENCY_CONFIGS, price_formatter

from ._rate_utils import FALLBACK_CURRENCY_CHOICES, get_currency_choices, get_currency_rate

# Build CURRENCY_SYMBOLS from CURRENCY_CONFIGS for backwards compatibility
CURRENCY_SYMBOLS: Dict[str, str] = {code: cfg.symbol for code, cfg in CURRENCY_CONFIGS.items()}

# Unfold-compatible CSS classes
INPUT_CLASSES = " ".join([
    "border", "border-base-200", "bg-white", "font-medium", "px-3", "py-2",
    "min-w-20", "placeholder-base-400", "rounded-default", "shadow-xs",
    "text-font-default-light", "text-sm", "w-full",
    "focus:outline-2", "focus:-outline-offset-2", "focus:outline-primary-600",
    "dark:bg-base-900", "dark:border-base-700", "dark:text-font-default-dark",
])

SELECT_CLASSES = " ".join([*INPUT_CLASSES.split(), "pr-8!", "max-w-2xl", "appearance-none", "text-ellipsis"])
AUTOCOMPLETE_CLASSES = "unfold-admin-autocomplete admin-autocomplete"


def format_money(
    amount: Any,
    currency: str,
    precision: int = 2,
    smart_precision: bool = False,
) -> str:
    """Format amount with currency symbol using PriceFormatter."""
    if amount is None:
        return "—"
    return price_formatter.format(amount, currency)


class DecimalInput(TextInput):
    """TextInput that formats decimal values with dot separator."""

    input_type = "text"

    def __init__(self, attrs: Optional[Dict[str, Any]] = None) -> None:
        default_attrs: Dict[str, Any] = {"inputmode": "decimal"}
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    def format_value(self, value: Any) -> str:
        if value is None or value == "":
            return ""
        if isinstance(value, Decimal):
            return f"{value:.2f}"
        if isinstance(value, (int, float)):
            return f"{value:.2f}"
        return str(value)


class MoneyFieldWidget(MultiWidget):
    """
    Unified MoneyField widget for Django Admin.

    Usage:
        formfield_overrides = {
            MoneyField: {"widget": MoneyFieldWidget(default_currency="KRW")}
        }
    """

    template_name = "django_admin/widgets/money_field_input.html"

    def __init__(
        self,
        attrs: Optional[Dict[str, Any]] = None,
        currency_choices: Optional[List[Tuple[str, str]]] = None,
        default_currency: str = "USD",
        target_currency: str = "USD",
        use_autocomplete: bool = False,
        target_amount: Any = None,
        rate: Any = None,
        rate_at: Any = None,
    ) -> None:
        self.default_currency = default_currency
        self.target_currency = target_currency
        self.use_autocomplete = use_autocomplete
        self.currency_choices = currency_choices or get_currency_choices()
        self.target_amount = target_amount
        self.rate = rate
        self.rate_at = rate_at

        select_attrs: Dict[str, Any] = (
            {
                "class": AUTOCOMPLETE_CLASSES,
                "data-theme": "admin-autocomplete",
                "data-allow-clear": "false",
                "data-placeholder": "Select currency",
            }
            if use_autocomplete
            else {"class": SELECT_CLASSES}
        )

        widgets = [
            DecimalInput(attrs={"class": INPUT_CLASSES, "placeholder": "0.00", **(attrs or {})}),
            Select(attrs=select_attrs, choices=self.currency_choices),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value: Any) -> List[Any]:
        if value is None:
            return [None, self.default_currency]
        if isinstance(value, (Decimal, float, int)):
            return [value, self.default_currency]
        if isinstance(value, (list, tuple)) and len(value) >= 2:
            return list(value[:2])
        if isinstance(value, dict):
            return [value.get("amount"), value.get("currency", self.default_currency)]
        return [value, self.default_currency]

    def value_from_datadict(self, data: Any, files: Any, name: str) -> Any:
        """Return only the amount for DecimalField compatibility."""
        return self.widgets[0].value_from_datadict(data, files, f"{name}_0")

    def get_context(self, name: str, value: Any, attrs: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        import json
        context = super().get_context(name, value, attrs)
        decomposed = self.decompress(value)
        amount = decomposed[0]
        currency = decomposed[1] if len(decomposed) > 1 else self.default_currency

        target_amount, rate, rate_at = self._get_live_rate_data(amount, currency)

        context["widget"]["conversion_info"] = self._format_conversion_info(target_amount, rate, rate_at, currency)
        context["widget"]["target_currency"] = self.target_currency
        context["widget"]["rates_json"] = json.dumps(self._get_all_rates())
        context["widget"]["symbols_json"] = json.dumps(CURRENCY_SYMBOLS)
        context["widget"]["currency_admin_url"] = self._get_currency_admin_url()
        return context

    def _get_currency_admin_url(self) -> str:
        try:
            from django.urls import reverse
            return reverse("admin:cfg_currency_currencyrate_changelist")
        except Exception:
            return ""

    def _get_all_rates(self) -> Dict[str, Dict[str, Any]]:
        rates: Dict[str, Dict[str, Any]] = {}
        try:
            from django_cfg.apps.tools.currency.models import CurrencyRate
            for rate_obj in CurrencyRate.objects.filter(quote_currency=self.target_currency.upper()):
                rates[rate_obj.base_currency] = {
                    "rate": float(rate_obj.rate),
                    "updated_at": rate_obj.updated_at.isoformat() if rate_obj.updated_at else None,
                }
        except Exception:
            pass
        return rates

    def _get_live_rate_data(
        self, amount: Any, currency: str
    ) -> Tuple[Optional[Decimal], Optional[Decimal], Any]:
        if currency and currency.upper() == self.target_currency.upper():
            return None, None, None

        rate_obj = get_currency_rate(currency, self.target_currency)
        if rate_obj:
            rate = rate_obj.rate
            rate_at = rate_obj.updated_at
            target_amount = Decimal(str(amount)) * rate if amount else None
            return target_amount, rate, rate_at

        return self.target_amount, self.rate, self.rate_at

    def _format_conversion_info(
        self,
        target_amount: Any = None,
        rate: Any = None,
        rate_at: Any = None,
        currency: Optional[str] = None,
    ) -> str:
        if not target_amount and not rate:
            return ""

        display_currency = currency or self.default_currency
        parts = []

        if target_amount:
            target_str = format_money(target_amount, self.target_currency, smart_precision=True)
            parts.append(f'<span class="text-primary-600 dark:text-primary-400 font-medium">→ {target_str}</span>')

        if rate:
            rate_str = f"{float(rate):.10f}".rstrip("0").rstrip(".")
            rate_html = f'<span class="text-base-400 dark:text-base-500">1 {display_currency} = {rate_str} {self.target_currency}</span>'
            if rate_at:
                from django.utils.timesince import timesince
                rate_html += f'<span class="text-base-400 dark:text-base-500"> • {timesince(rate_at)} ago</span>'
            parts.append(rate_html)

        if not parts:
            return ""

        return mark_safe(
            '<div class="flex items-center gap-3 mt-1 text-xs">'
            + '<span class="text-base-300 dark:text-base-600">|</span>'.join(parts)
            + "</div>"
        )

    def format_readonly(
        self,
        amount: Any,
        currency: str,
        target_amount: Any = None,
        rate: Any = None,
        rate_at: Any = None,
    ) -> SafeString:
        """Render compact readonly display: ₩15,700,000 → $10,645.05"""
        if amount is None:
            return "—"  # type: ignore[return-value]

        if target_amount is None and rate is None:
            target_amount, rate, rate_at = self._get_live_rate_data(amount, currency)

        amount_str = format_money(amount, currency)
        target_str = format_money(target_amount, self.target_currency, smart_precision=True) if target_amount else None

        parts = ['<div class="money-field-display flex flex-col gap-0.5">']
        parts.append('<div class="flex items-center gap-2 text-sm">')
        parts.append(f'<span class="font-semibold text-font-default-light dark:text-font-default-dark">{amount_str}</span>')

        if target_amount and currency.upper() != self.target_currency.upper():
            parts.append('<span class="text-base-400 dark:text-base-500">→</span>')
            parts.append(f'<span class="text-primary-600 dark:text-primary-400 font-medium">{target_str}</span>')
        parts.append("</div>")

        if rate:
            rate_str = f"{float(rate):.10f}".rstrip("0").rstrip(".")
            parts.append('<div class="flex items-center gap-1.5 text-xs text-base-400 dark:text-base-500">')
            parts.append(f"<span>1 {currency} = {rate_str} {self.target_currency}</span>")
            if rate_at:
                from django.utils.timesince import timesince
                ts = rate_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(rate_at, "strftime") else rate_at
                parts.append(f'<span>•</span><span title="{ts}">{timesince(rate_at)} ago</span>')
            parts.append("</div>")

        parts.append("</div>")
        return mark_safe("".join(parts))
