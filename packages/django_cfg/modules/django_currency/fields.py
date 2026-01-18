"""
Currency and Money model fields.

MoneyField - stores amount with currency, uses CurrencyRate for conversion.
CurrencyField - CharField for currency codes.
"""

from decimal import Decimal
from typing import Any, Optional

from django.db import models


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


class MoneyField(models.DecimalField):
    """
    DecimalField for monetary amounts with currency support.

    Stores amount in original currency. Conversion to target currency
    is done via CurrencyRate model dynamically.

    Usage:
        price = MoneyField(
            max_digits=15,
            decimal_places=2,
            default_currency="KRW",
            target_currency="USD",
        )

    Creates:
        price_currency - CharField for currency code
        price_target - property returning converted amount (via CurrencyRate)

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
        """Add currency field and target property to model."""
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
