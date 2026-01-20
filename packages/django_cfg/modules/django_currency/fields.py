"""
Currency and Money model fields.

MoneyField - stores amount with currency, uses CurrencyRate for conversion.
CurrencyField - CharField for currency codes.

Auto-generated properties:
    {field}_currency - CharField for currency code
    {field}_target - Decimal amount in target currency (via CurrencyRate)
    {field}_display - Formatted original price (e.g., "Rp 150M")
    {field}_target_display - Formatted target price (e.g., "$9,500")
    {field}_full_display - Combined display (e.g., "$9,500 (Rp 150M)")
"""

from decimal import Decimal
from typing import Any, Optional

from django.db import models

from .formatter import price_formatter


class CurrencyField(models.CharField):
    """
    CharField for storing currency codes (ISO 4217).

    Usage:
        currency = CurrencyField(default="USD")
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault("max_length", 10)
        kwargs.setdefault("default", "USD")
        super().__init__(*args, **kwargs)


class MoneyTargetDescriptor:
    """
    Descriptor for dynamic {field}_target property.

    Returns converted amount using CurrencyRate from database.
    """

    def __init__(self, field_name: str, target_currency: str):
        self.field_name = field_name
        self.target_currency = target_currency

    def __get__(self, obj, objtype=None) -> Optional[Decimal]:
        if obj is None:
            return None

        amount = getattr(obj, self.field_name, None)
        if amount is None:
            return None

        currency = getattr(obj, f"{self.field_name}_currency", None)
        if not currency:
            return None

        # Same currency - no conversion needed
        if currency.upper() == self.target_currency.upper():
            return Decimal(str(amount))

        # Get rate from CurrencyRate (CurrencyManager handles DB routing)
        try:
            from django_cfg.apps.tools.currency.models import CurrencyRate
            rate = CurrencyRate.objects.filter(
                base_currency=currency.upper(),
                quote_currency=self.target_currency.upper()
            ).first()
            if rate:
                return Decimal(str(amount)) * rate.rate
        except ImportError:
            pass
        except Exception:
            pass

        return None


class MoneyDisplayDescriptor:
    """
    Descriptor for {field}_display property.

    Returns formatted price in original currency.
    """

    def __init__(self, field_name: str):
        self.field_name = field_name

    def __get__(self, obj, objtype=None) -> str:
        if obj is None:
            return ""

        amount = getattr(obj, self.field_name, None)
        currency = getattr(obj, f"{self.field_name}_currency", None)

        if amount is None:
            return "N/A"

        return price_formatter.format(amount, currency or "USD")


class MoneyTargetDisplayDescriptor:
    """
    Descriptor for {field}_target_display property.

    Returns formatted price in target currency.
    """

    def __init__(self, field_name: str, target_currency: str):
        self.field_name = field_name
        self.target_currency = target_currency

    def __get__(self, obj, objtype=None) -> str:
        if obj is None:
            return ""

        # Try to get converted amount first
        target_amount = getattr(obj, f"{self.field_name}_target", None)
        if target_amount is not None:
            return price_formatter.format(target_amount, self.target_currency)

        # Fallback: if same currency, use original amount
        amount = getattr(obj, self.field_name, None)
        currency = getattr(obj, f"{self.field_name}_currency", None)

        if currency and currency.upper() == self.target_currency.upper() and amount is not None:
            return price_formatter.format(amount, self.target_currency)

        return "N/A"


class MoneyFullDisplayDescriptor:
    """
    Descriptor for {field}_full_display property.

    Returns target currency as primary with original in parentheses.
    Example: "$9,500 (Rp 150M)"
    """

    def __init__(self, field_name: str, target_currency: str):
        self.field_name = field_name
        self.target_currency = target_currency

    def __get__(self, obj, objtype=None) -> str:
        if obj is None:
            return ""

        amount = getattr(obj, self.field_name, None)
        currency = getattr(obj, f"{self.field_name}_currency", None)
        target_amount = getattr(obj, f"{self.field_name}_target", None)

        return price_formatter.format_full(
            amount=amount,
            currency=currency or "USD",
            target_amount=target_amount,
            target_currency=self.target_currency,
        )


class MoneyField(models.DecimalField):
    """
    DecimalField for monetary amounts with currency support.

    Stores amount in original currency. Conversion to target currency
    is done via CurrencyRate model dynamically.

    Usage:
        price = MoneyField(
            max_digits=15,
            decimal_places=2,
            default_currency="IDR",
            target_currency="USD",
        )

    Auto-creates these attributes on the model:
        price              - Original amount (DecimalField)
        price_currency     - Currency code (CharField, e.g., "IDR")
        price_target       - Converted amount in target currency (property)
        price_display      - Formatted original price (e.g., "Rp 150M")
        price_target_display - Formatted target price (e.g., "$9,500")
        price_full_display - Combined display (e.g., "$9,500 (Rp 150M)")

    Conversion is handled by MoneyFieldWidget using CurrencyRate.
    """

    def __init__(
        self,
        *args,
        default_currency: str = "USD",
        target_currency: str = "USD",
        **kwargs
    ):
        self.default_currency = default_currency
        self.target_currency = target_currency

        # Set defaults for monetary values
        kwargs.setdefault("max_digits", 15)
        kwargs.setdefault("decimal_places", 2)
        kwargs.setdefault("null", True)
        kwargs.setdefault("blank", True)

        super().__init__(*args, **kwargs)

    def deconstruct(self):
        """Return enough info to recreate field."""
        name, path, args, kwargs = super().deconstruct()
        kwargs["default_currency"] = self.default_currency
        kwargs["target_currency"] = self.target_currency
        return name, path, args, kwargs

    def contribute_to_class(self, cls, name, private_only=False):
        """Add currency field, target property, and display properties to model."""
        super().contribute_to_class(cls, name, private_only)

        # Add currency field
        currency_field = CurrencyField(
            default=self.default_currency,
            db_index=True,
        )
        cls.add_to_class(f"{name}_currency", currency_field)

        # Add target property (dynamic conversion via CurrencyRate)
        target_descriptor = MoneyTargetDescriptor(name, self.target_currency)
        setattr(cls, f"{name}_target", target_descriptor)

        # Add display properties for formatted output
        setattr(cls, f"{name}_display", MoneyDisplayDescriptor(name))
        setattr(cls, f"{name}_target_display", MoneyTargetDisplayDescriptor(name, self.target_currency))
        setattr(cls, f"{name}_full_display", MoneyFullDisplayDescriptor(name, self.target_currency))

    def formfield(self, **kwargs):
        """Return form field with MoneyFieldWidget."""
        from django_cfg.modules.django_admin.widgets import MoneyFieldWidget

        defaults = {
            "widget": MoneyFieldWidget(
                default_currency=self.default_currency,
                target_currency=self.target_currency,
            ),
        }
        defaults.update(kwargs)
        return super().formfield(**defaults)
