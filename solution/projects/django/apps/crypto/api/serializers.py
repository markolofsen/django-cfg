"""DRF Serializers for Crypto app.

Mirrors `apps/crypto/models.py::CoinListing` fields verbatim
(symbol, name, price, market_cap, updated_at).
"""

from rest_framework import serializers

from apps.crypto.models import CoinListing


class CoinListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinListing
        fields = ["id", "symbol", "name", "price", "market_cap", "updated_at"]
        read_only_fields = ["id", "updated_at"]


class CoinListingWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoinListing
        fields = ["symbol", "name", "price", "market_cap"]
