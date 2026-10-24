from django.contrib import admin
from .models import CoinListing


@admin.register(CoinListing)
class CoinListingAdmin(admin.ModelAdmin):
    list_display = ["symbol", "name", "price", "price_currency", "price_full_display", "updated_at"]
    readonly_fields = ["price_target", "price_full_display", "market_cap_full_display"]
