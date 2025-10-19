"""
Trading models - Portfolio and Orders.
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


class Portfolio(models.Model):
    """User's trading portfolio."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trading_portfolio')

    # Balances
    total_balance_usd = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Total portfolio value in USD"
    )
    available_balance_usd = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        default=Decimal('10000.00'),
        help_text="Available balance for trading"
    )

    # Statistics
    total_profit_loss = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0.00'))
    total_trades = models.PositiveIntegerField(default=0)
    winning_trades = models.PositiveIntegerField(default=0)
    losing_trades = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Portfolio'
        verbose_name_plural = 'Portfolios'

    def __str__(self):
        return f"{self.user.username}'s Portfolio (${self.total_balance_usd})"

    @property
    def win_rate(self):
        if self.total_trades == 0:
            return 0
        return round((self.winning_trades / self.total_trades) * 100, 2)


class Order(models.Model):
    """Trading order."""

    ORDER_TYPES = [
        ('market', 'Market'),
        ('limit', 'Limit'),
        ('stop_loss', 'Stop Loss'),
    ]

    ORDER_SIDES = [
        ('buy', 'Buy'),
        ('sell', 'Sell'),
    ]

    ORDER_STATUSES = [
        ('pending', 'Pending'),
        ('filled', 'Filled'),
        ('cancelled', 'Cancelled'),
    ]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='orders')

    # Order details
    symbol = models.CharField(max_length=20, help_text="Trading pair (e.g., BTC/USDT)")
    order_type = models.CharField(max_length=20, choices=ORDER_TYPES, default='market')
    side = models.CharField(max_length=10, choices=ORDER_SIDES)

    # Pricing
    quantity = models.DecimalField(max_digits=20, decimal_places=8, validators=[MinValueValidator(Decimal('0.00000001'))])
    price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    filled_quantity = models.DecimalField(max_digits=20, decimal_places=8, default=Decimal('0'))

    # Status
    status = models.CharField(max_length=20, choices=ORDER_STATUSES, default='pending')
    total_usd = models.DecimalField(max_digits=20, decimal_places=2, default=Decimal('0'))

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Order'
        verbose_name_plural = 'Orders'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.side.upper()} {self.quantity} {self.symbol}"
