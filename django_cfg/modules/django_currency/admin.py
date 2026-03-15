"""
MoneyField Admin Mixin.

Provides admin integration for MoneyField with currency conversion display.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional, Set, Tuple

from django.contrib import admin
from django.db import models


class MoneyFieldAdminMixin:
    """
    Admin mixin for models with MoneyField.

    Auto-detects MoneyField fields and:
    - Adds readonly fields for target_amount, rate, rate_at
    - Configures MoneyFieldWidget for edit forms
    - Shows conversion info in list display
    """

    # Cache for detected MoneyField fields
    _money_fields_cache: Dict[str, List[str]] = {}

    def get_readonly_fields(self, request, obj=None):
        """Add MoneyField conversion fields to readonly."""
        readonly = list(super().get_readonly_fields(request, obj))

        # Add MoneyField auxiliary fields as readonly
        for field_name in self._get_money_field_names():
            for suffix in ["_target", "_rate", "_rate_at"]:
                aux_field = f"{field_name}{suffix}"
                if aux_field not in readonly and self._field_exists(aux_field):
                    readonly.append(aux_field)

        return readonly

    def get_list_display(self, request):
        """Override to use MoneyField display formatter."""
        list_display = list(super().get_list_display(request))
        return list_display

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """Configure MoneyFieldWidget for MoneyField fields."""
        if db_field.__class__.__name__ == "MoneyField":
            from django_cfg.modules.django_admin.widgets import MoneyFieldWidget

            # Get target currency from field
            target_currency = getattr(db_field, "target_currency", "USD")
            default_currency = getattr(db_field, "default_currency", "USD")

            # Get current currency from object if editing
            current_currency = default_currency
            obj = getattr(request, '_editing_obj', None)
            if obj:
                currency_field = f"{db_field.name}_currency"
                current_currency = getattr(obj, currency_field, None) or default_currency

            kwargs["widget"] = MoneyFieldWidget(
                default_currency=current_currency,  # Use current value, not default
                target_currency=target_currency,
            )

        return super().formfield_for_dbfield(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        """Save currency from widget dropdown to model field."""
        # Handle MoneyField currency from POST data
        for field_name in self._get_money_field_names():
            currency_key = f"{field_name}_currency"
            if currency_key in request.POST:
                setattr(obj, currency_key, request.POST[currency_key])

        super().save_model(request, obj, form, change)

    def _get_money_field_names(self) -> List[str]:
        """Get list of MoneyField field names for this model."""
        model_key = self.model._meta.label

        if model_key not in self._money_fields_cache:
            money_fields = []
            for field in self.model._meta.get_fields():
                if field.__class__.__name__ == "MoneyField":
                    money_fields.append(field.name)
            self._money_fields_cache[model_key] = money_fields

        return self._money_fields_cache[model_key]

    def _field_exists(self, field_name: str) -> bool:
        """Check if field exists on model."""
        try:
            self.model._meta.get_field(field_name)
            return True
        except Exception:
            return False
