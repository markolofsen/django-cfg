"""
CurrencyRate Admin Configuration

Admin interface for CurrencyRate model using django_cfg.
"""

from django.contrib import admin
from django.contrib import messages
from unfold.decorators import action as unfold_action

from django_cfg.modules.django_admin import (
    AdminConfig,
    BadgeField,
    DateTimeField,
    DecimalField,
    FieldsetConfig,
    TextField,
    Icons,
    computed_field,
)
from django_cfg.modules.django_admin.base import PydanticAdmin

from django_cfg.apps.tools.currency.models import CurrencyRate


# ========== ADMIN CONFIG ==========
currency_rate_admin_config = AdminConfig(
    model=CurrencyRate,

    # ========== LIST VIEW ==========
    list_display=[
        "pair_display",
        "rate",
        "provider",
        "is_stale",
        "is_expired_display",
        "updated_at",
    ],

    # ========== DISPLAY FIELDS ==========
    display_fields=[
        TextField(
            name="base_currency",
            title="Base",
        ),
        TextField(
            name="quote_currency",
            title="Quote",
        ),
        DecimalField(
            name="rate",
            title="Rate",
        ),
        TextField(
            name="provider",
            title="Provider",
        ),
        BadgeField(
            name="is_stale",
            title="Stale",
            label_map={
                True: "warning",
                False: "success",
            },
            icon=Icons.WARNING,
        ),
        DateTimeField(
            name="updated_at",
            title="Updated",
            show_relative=True,
        ),
        DateTimeField(
            name="created_at",
            title="Created",
            show_relative=True,
        ),
    ],

    # ========== LIST OPTIONS ==========
    list_filter=["provider", "is_stale", "base_currency"],
    search_fields=["base_currency", "quote_currency"],
    ordering=["base_currency", "quote_currency"],

    # ========== FORM OPTIONS ==========
    readonly_fields=["created_at", "updated_at"],

    # ========== FIELDSETS ==========
    fieldsets=[
        FieldsetConfig(
            title="Currency Pair",
            fields=["base_currency", "quote_currency"],
        ),
        FieldsetConfig(
            title="Rate Info",
            fields=["rate", "provider", "is_stale"],
        ),
        FieldsetConfig(
            title="Timestamps",
            fields=["created_at", "updated_at"],
            collapsed=True,
        ),
    ],
)


@admin.register(CurrencyRate)
class CurrencyRateAdmin(PydanticAdmin):
    """Admin for CurrencyRate model."""

    config = currency_rate_admin_config

    # ========== CHANGELIST ACTIONS (buttons above list) ==========
    actions_list = ["update_all_rates_action"]

    @unfold_action(
        description="Update All Rates",
        url_path="update-all-rates",
        attrs={"class": "button-primary"},
    )
    def update_all_rates_action(self, request):
        """Update all currency rates from providers."""
        from django_cfg.apps.tools.currency.services import update_rates

        try:
            result = update_rates()
            messages.success(
                request,
                f"Updated {result['updated']} rates. "
                f"Failed: {result['failed']}."
            )
        except Exception as e:
            messages.error(request, f"Failed to update rates: {e}")

        from django.http import HttpResponseRedirect
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '../'))

    # ========== COMPUTED FIELDS ==========
    @computed_field("Pair")
    def pair_display(self, obj):
        """Display currency pair with badges."""
        return self.html.inline(
            self.html.badge(obj.base_currency, variant="info"),
            self.html.span("→", "text-gray-400"),
            self.html.badge(obj.quote_currency, variant="primary"),
            separator=" ",
        )

    @computed_field("Expired")
    def is_expired_display(self, obj):
        """Display expired status."""
        if obj.is_expired:
            return self.html.badge("Expired", variant="danger")
        return self.html.badge("Fresh", variant="success")

    # ========== BULK ACTIONS (require selection) ==========
    actions = ["refresh_selected_rates", "mark_as_stale"]

    @admin.action(description="Refresh selected rates")
    def refresh_selected_rates(self, request, queryset):
        """Refresh rates from providers."""
        from django_cfg.apps.tools.currency.services import get_converter

        converter = get_converter()
        refreshed = 0

        for rate in queryset:
            try:
                converter.refresh_rate(rate.base_currency, rate.quote_currency)
                refreshed += 1
            except Exception as e:
                self.message_user(
                    request,
                    f"Failed to refresh {rate}: {e}",
                    level="warning",
                )

        self.message_user(request, f"Refreshed {refreshed} rates")

    @admin.action(description="Mark as stale")
    def mark_as_stale(self, request, queryset):
        """Mark selected rates as stale."""
        count = queryset.update(is_stale=True)
        self.message_user(request, f"Marked {count} rates as stale")
