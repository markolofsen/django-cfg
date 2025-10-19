"""
DRF Serializers for Trading app.
"""

from rest_framework import serializers
from .models import Portfolio, Order


class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for trading portfolios."""

    user_info = serializers.SerializerMethodField()
    win_rate = serializers.FloatField(read_only=True)

    class Meta:
        model = Portfolio
        fields = [
            'id', 'user', 'user_info', 'total_balance_usd', 'available_balance_usd',
            'total_profit_loss', 'total_trades', 'winning_trades', 'losing_trades',
            'win_rate', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'total_balance_usd', 'total_profit_loss', 'total_trades', 'winning_trades', 'losing_trades']

    def get_user_info(self, obj) -> dict:
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
        }


class OrderSerializer(serializers.ModelSerializer):
    """Serializer for orders."""

    class Meta:
        model = Order
        fields = [
            'id', 'portfolio', 'symbol', 'order_type', 'side',
            'quantity', 'price', 'filled_quantity', 'status', 'total_usd',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'filled_quantity', 'status', 'total_usd']


class OrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating orders."""

    class Meta:
        model = Order
        fields = ['symbol', 'order_type', 'side', 'quantity', 'price']

    def validate(self, data):
        if data['order_type'] == 'limit' and not data.get('price'):
            raise serializers.ValidationError({'price': 'Price is required for limit orders.'})
        if data['order_type'] == 'market' and data.get('price'):
            raise serializers.ValidationError({'price': 'Price should not be specified for market orders.'})
        return data


class PortfolioStatsSerializer(serializers.Serializer):
    """Serializer for portfolio statistics."""

    total_portfolios = serializers.IntegerField()
    total_volume_usd = serializers.DecimalField(max_digits=20, decimal_places=2)
    total_orders = serializers.IntegerField()
