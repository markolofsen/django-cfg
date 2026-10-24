from django.db import models
from django_cfg.modules.django_currency.fields import MoneyField


class CoinListing(models.Model):
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    price = MoneyField(
        default_currency="USD",
        target_currency="USD",
    )
    market_cap = MoneyField(
        default_currency="USD",
        target_currency="USD",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "crypto"
        ordering = ["-market_cap"]

    def __str__(self):
        return f"{self.symbol} — {self.price_full_display}"
