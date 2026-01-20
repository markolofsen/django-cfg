"""
MoneyField unified widget for Django Admin.

Single widget that handles both:
- Editable mode: amount input + currency dropdown
- Readonly mode: compact display with conversion info

Uses CurrencyRate model from django_cfg.apps.tools.currency for live rate data.
Uses PriceFormatter from django_cfg.modules.django_currency for consistent formatting.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from django import forms
from django.forms.widgets import MultiWidget, Select, TextInput
from django.utils.safestring import mark_safe

from django_cfg.modules.django_currency.formatter import (
    price_formatter,
    CURRENCY_CONFIGS,
)

if TYPE_CHECKING:
    from django_cfg.apps.tools.currency.models import CurrencyRate

# Build CURRENCY_SYMBOLS from CURRENCY_CONFIGS for backwards compatibility
CURRENCY_SYMBOLS = {code: cfg.symbol for code, cfg in CURRENCY_CONFIGS.items()}

# Fallback currency choices (used when Currency model is empty)
FALLBACK_CURRENCY_CHOICES = [
    ("USD", "USD ($)"), ("EUR", "EUR (€)"), ("GBP", "GBP (£)"), ("JPY", "JPY (¥)"),
    ("CNY", "CNY (¥)"), ("KRW", "KRW (₩)"), ("RUB", "RUB (₽)"), ("CHF", "CHF (Fr)"),
    ("AUD", "AUD (A$)"), ("CAD", "CAD (C$)"), ("INR", "INR (₹)"), ("BRL", "BRL (R$)"),
    ("BTC", "BTC (₿)"), ("ETH", "ETH (Ξ)"),
]

# Unfold-compatible CSS classes
INPUT_CLASSES = " ".join([
    "border", "border-base-200", "bg-white", "font-medium", "px-3", "py-2",
    "min-w-20", "placeholder-base-400", "rounded-default", "shadow-xs",
    "text-font-default-light", "text-sm", "w-full",
    "focus:outline-2", "focus:-outline-offset-2", "focus:outline-primary-600",
    "dark:bg-base-900", "dark:border-base-700", "dark:text-font-default-dark",
])

SELECT_CLASSES = " ".join([
    *INPUT_CLASSES.split(),
    "pr-8!", "max-w-2xl", "appearance-none", "text-ellipsis",
])

# Unfold autocomplete classes for Select2
AUTOCOMPLETE_CLASSES = "unfold-admin-autocomplete admin-autocomplete"


def get_currency_choices() -> List[Tuple[str, str]]:
    """
    Get currency choices from Currency model.

    Falls back to FALLBACK_CURRENCY_CHOICES if Currency model is empty or unavailable.
    CurrencyManager handles database routing automatically.
    """
    try:
        from django_cfg.apps.tools.currency.models import Currency
        currencies = Currency.objects.filter(is_active=True).order_by("code")
        if currencies.exists():
            return [
                (c.code, f"{c.code} ({c.symbol or c.name})")
                for c in currencies
            ]
    except Exception:
        pass
    return FALLBACK_CURRENCY_CHOICES


def get_currency_rate(base: str, quote: str) -> Optional["CurrencyRate"]:
    """
    Get rate from CurrencyRate model.

    Returns None if:
    - Currency app not installed
    - Rate not found in database

    CurrencyManager handles database routing automatically.
    """
    try:
        from django_cfg.apps.tools.currency.models import CurrencyRate
        return CurrencyRate.objects.filter(
            base_currency=base.upper(),
            quote_currency=quote.upper()
        ).first()
    except ImportError:
        # Currency app not installed
        return None
    except Exception:
        return None


class DecimalInput(TextInput):
    """
    TextInput that formats decimal values with dot separator.

    Avoids Django's localization that uses comma in some locales.
    """
    input_type = "text"

    def __init__(self, attrs=None):
        default_attrs = {"inputmode": "decimal"}  # Mobile keyboard with numbers and dot
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)

    def format_value(self, value):
        """Format value with dot decimal separator."""
        if value is None or value == "":
            return ""
        if isinstance(value, Decimal):
            return f"{value:.2f}"
        if isinstance(value, (int, float)):
            return f"{value:.2f}"
        return str(value)


def format_money(
    amount: Any,
    currency: str,
    precision: int = 2,
    smart_precision: bool = False,
) -> str:
    """
    Format amount with currency symbol.

    Uses PriceFormatter for consistent formatting across the app.

    Args:
        amount: The amount to format
        currency: Currency code (e.g., "USD", "KRW")
        precision: Ignored (kept for backwards compatibility)
        smart_precision: Ignored (PriceFormatter always uses smart abbreviations)
    """
    if amount is None:
        return "—"
    return price_formatter.format(amount, currency)


class MoneyFieldWidget(MultiWidget):
    """
    Unified MoneyField widget for Django Admin.

    Editable mode: [amount input 2/3] [currency select 1/3] + conversion info below
    Readonly mode: ₩15,700,000 → $10,645.05 (rate info below)

    Usage:
        # Auto-applied to MoneyField in PydanticAdmin
        # Or manually:
        formfield_overrides = {
            MoneyField: {'widget': MoneyFieldWidget(default_currency='KRW')}
        }
    """

    template_name = "django_admin/widgets/money_field_input.html"

    def __init__(
        self,
        attrs: Optional[Dict[str, Any]] = None,
        currency_choices: Optional[List[Tuple[str, str]]] = None,
        default_currency: str = "USD",
        target_currency: str = "USD",
        use_autocomplete: bool = False,  # Disabled - use styled static select
        # Conversion data for edit mode display
        target_amount: Any = None,
        rate: Any = None,
        rate_at: Any = None,
    ):
        self.default_currency = default_currency
        self.target_currency = target_currency
        self.use_autocomplete = use_autocomplete
        # Get choices from Currency model or use provided/fallback
        self.currency_choices = currency_choices or get_currency_choices()
        # Store conversion data for edit mode
        self.target_amount = target_amount
        self.rate = rate
        self.rate_at = rate_at

        # Currency select widget - use Unfold autocomplete style
        if use_autocomplete:
            select_attrs = {
                "class": AUTOCOMPLETE_CLASSES,
                "data-theme": "admin-autocomplete",
                "data-allow-clear": "false",
                "data-placeholder": "Select currency",
            }
        else:
            select_attrs = {"class": SELECT_CLASSES}

        # Use DecimalInput to ensure dot decimal separator (not comma)
        widgets = [
            DecimalInput(attrs={
                "class": INPUT_CLASSES,
                "placeholder": "0.00",
                **(attrs or {})
            }),
            Select(attrs=select_attrs, choices=self.currency_choices),
        ]
        super().__init__(widgets, attrs)

    def decompress(self, value: Any) -> List[Any]:
        """Split value into [amount, currency]."""
        if value is None:
            return [None, self.default_currency]
        if isinstance(value, (Decimal, float, int)):
            return [value, self.default_currency]
        if isinstance(value, (list, tuple)) and len(value) >= 2:
            return list(value[:2])
        if isinstance(value, dict):
            return [value.get("amount"), value.get("currency", self.default_currency)]
        return [value, self.default_currency]

    def value_from_datadict(self, data, files, name):
        """
        Return only the amount value for DecimalField compatibility.

        MultiWidget returns list, but DecimalField expects single value.
        Currency is stored in separate field ({name}_currency).
        """
        # Get amount from first subwidget
        amount = self.widgets[0].value_from_datadict(data, files, f"{name}_0")
        return amount

    def get_context(self, name: str, value: Any, attrs: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Add conversion data to widget context for template."""
        import json
        context = super().get_context(name, value, attrs)

        # Get amount and currency from value
        decomposed = self.decompress(value)
        amount, currency = decomposed[0], decomposed[1] if len(decomposed) > 1 else self.default_currency

        # Get live rate from CurrencyRate if not already provided
        target_amount, rate, rate_at = self._get_live_rate_data(amount, currency)

        # Add conversion info for edit mode display
        context["widget"]["conversion_info"] = self._format_conversion_info(target_amount, rate, rate_at, currency)
        context["widget"]["target_currency"] = self.target_currency

        # Add rates data for live recalculation
        context["widget"]["rates_json"] = json.dumps(self._get_all_rates())
        context["widget"]["symbols_json"] = json.dumps(CURRENCY_SYMBOLS)

        # Add admin URL for currency rates
        context["widget"]["currency_admin_url"] = self._get_currency_admin_url()

        return context

    def _get_currency_admin_url(self) -> str:
        """Get URL to CurrencyRate admin changelist."""
        try:
            from django.urls import reverse
            return reverse("admin:cfg_currency_currencyrate_changelist")
        except Exception:
            return ""

    def _get_all_rates(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all rates to target_currency as dict with timestamps.

        Returns:
            Dict mapping currency code to {rate, updated_at}.
        """
        rates = {}
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
        """
        Get live rate data from CurrencyRate model.

        Returns (target_amount, rate, rate_at) tuple.
        Falls back to stored values if CurrencyRate not available.
        """
        # If currency equals target, no conversion needed
        if currency and currency.upper() == self.target_currency.upper():
            return None, None, None

        # Try to get live rate from CurrencyRate
        rate_obj = get_currency_rate(currency, self.target_currency)

        if rate_obj:
            rate = rate_obj.rate
            rate_at = rate_obj.updated_at
            target_amount = Decimal(str(amount)) * rate if amount else None
            return target_amount, rate, rate_at

        # Fallback to stored values
        return self.target_amount, self.rate, self.rate_at

    def _format_conversion_info(
        self,
        target_amount: Any = None,
        rate: Any = None,
        rate_at: Any = None,
        currency: Optional[str] = None,
    ) -> str:
        """
        Format conversion info for edit mode display.

        Shows: → $10,645.05 | 1 KRW = 0.000678 USD • 2h ago

        Args:
            target_amount: Converted amount in target currency
            rate: Exchange rate
            rate_at: Rate timestamp
            currency: Source currency code
        """
        if not target_amount and not rate:
            return ""

        display_currency = currency or self.default_currency
        parts = []

        # Target amount - use smart precision (no cents for large USD amounts)
        if target_amount:
            target_str = format_money(target_amount, self.target_currency, smart_precision=True)
            parts.append(f'<span class="text-primary-600 dark:text-primary-400 font-medium">→ {target_str}</span>')

        # Rate info
        if rate:
            rate_str = f"{float(rate):.10f}".rstrip('0').rstrip('.')
            rate_html = f'<span class="text-base-400 dark:text-base-500">1 {display_currency} = {rate_str} {self.target_currency}</span>'

            if rate_at:
                from django.utils.timesince import timesince
                time_str = timesince(rate_at)
                rate_html += f'<span class="text-base-400 dark:text-base-500"> • {time_str} ago</span>'

            parts.append(rate_html)

        if not parts:
            return ""

        return mark_safe(
            '<div class="flex items-center gap-3 mt-1 text-xs">' +
            '<span class="text-base-300 dark:text-base-600">|</span>'.join(parts) +
            '</div>'
        )

    def format_readonly(
        self,
        amount: Any,
        currency: str,
        target_amount: Any = None,
        rate: Any = None,
        rate_at: Any = None,
    ) -> str:
        """
        Render compact readonly display.

        Uses live rate from CurrencyRate if target_amount/rate not provided.

        Returns HTML: ₩15,700,000 → $10,645.05 (with rate info)
        """
        if amount is None:
            return "—"

        # Get live rate data from CurrencyRate if not provided
        if target_amount is None and rate is None:
            target_amount, rate, rate_at = self._get_live_rate_data(amount, currency)

        # Original amount - keep natural precision (user entered it)
        amount_str = format_money(amount, currency)
        # Converted amount - use smart precision (no cents for large USD amounts)
        target_str = format_money(target_amount, self.target_currency, smart_precision=True) if target_amount else None

        parts = ['<div class="money-field-display flex flex-col gap-0.5">']
        parts.append('<div class="flex items-center gap-2 text-sm">')
        parts.append(f'<span class="font-semibold text-font-default-light dark:text-font-default-dark">{amount_str}</span>')

        if target_amount and currency.upper() != self.target_currency.upper():
            parts.append('<span class="text-base-400 dark:text-base-500">→</span>')
            parts.append(f'<span class="text-primary-600 dark:text-primary-400 font-medium">{target_str}</span>')
        parts.append('</div>')

        # Rate info line
        if rate:
            rate_str = f"{float(rate):.10f}".rstrip('0').rstrip('.')
            parts.append('<div class="flex items-center gap-1.5 text-xs text-base-400 dark:text-base-500">')
            parts.append(f'<span>1 {currency} = {rate_str} {self.target_currency}</span>')
            if rate_at:
                from django.utils.timesince import timesince
                parts.append('<span>•</span>')
                parts.append(f'<span title="{rate_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(rate_at, "strftime") else rate_at}">{timesince(rate_at)} ago</span>')
            parts.append('</div>')
        parts.append('</div>')

        return mark_safe(''.join(parts))


class MoneyFieldFormField(forms.MultiValueField):
    """Form field for MoneyField."""

    widget = MoneyFieldWidget

    def __init__(
        self,
        *,
        currency_choices: Optional[List[Tuple[str, str]]] = None,
        default_currency: str = "USD",
        max_digits: int = 15,
        decimal_places: int = 2,
        **kwargs,
    ):
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
                localize=False,  # Prevent comma decimal separator
            ),
            forms.ChoiceField(choices=currency_choices or FALLBACK_CURRENCY_CHOICES, required=False),
        ]
        super().__init__(fields=fields, require_all_fields=False, **kwargs)

    def compress(self, data_list: List[Any]) -> Optional[Dict[str, Any]]:
        """Combine [amount, currency] into dict."""
        if not data_list or data_list[0] is None:
            return None
        return {
            "amount": data_list[0],
            "currency": data_list[1] if len(data_list) > 1 else self.default_currency,
        }
