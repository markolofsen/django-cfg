"""
Protobuf Converters for Crypto App.

Utilities for converting between Django models and protobuf messages.

Best Practices:
- Use strings for Decimal fields (precise financial data)
- Handle None values gracefully
- Include computed properties
- Denormalize data for convenience
"""

from decimal import Decimal
from typing import Optional
from datetime import datetime

from google.protobuf.timestamp_pb2 import Timestamp

# Import generated proto files
from ..generated import crypto_service_pb2

from apps.crypto.models import Coin, Wallet


class ProtobufConverter:
    """
    Converter utilities for Django ORM ↔ Protobuf.

    Handles type conversions with proper null handling and decimal precision.
    """

    @staticmethod
    def datetime_to_timestamp(dt: Optional[datetime]) -> Optional[Timestamp]:
        """
        Convert datetime to protobuf Timestamp.

        Args:
            dt: Python datetime object

        Returns:
            Protobuf Timestamp or None

        Example:
            >>> from django.utils import timezone
            >>> now = timezone.now()
            >>> ts = ProtobufConverter.datetime_to_timestamp(now)
        """
        if dt is None:
            return None

        ts = Timestamp()
        ts.FromDatetime(dt)
        return ts

    @staticmethod
    def timestamp_to_datetime(ts: Timestamp) -> datetime:
        """
        Convert protobuf Timestamp to datetime.

        Args:
            ts: Protobuf Timestamp

        Returns:
            Python datetime object

        Example:
            >>> dt = ProtobufConverter.timestamp_to_datetime(timestamp)
        """
        return ts.ToDatetime()

    @staticmethod
    def decimal_to_string(value: Optional[Decimal]) -> str:
        """
        Convert Decimal to string for protobuf.

        Preserves full decimal precision. Returns "0" for None values.

        Args:
            value: Decimal value

        Returns:
            String representation

        Example:
            >>> price = Decimal('0.00012345')
            >>> ProtobufConverter.decimal_to_string(price)
            '0.00012345'
        """
        if value is None:
            return "0"
        return str(value)

    @staticmethod
    def string_to_decimal(value: str) -> Decimal:
        """
        Convert string to Decimal.

        Args:
            value: String representation

        Returns:
            Decimal value

        Example:
            >>> dec = ProtobufConverter.string_to_decimal("123.45")
            >>> dec
            Decimal('123.45')
        """
        try:
            return Decimal(value) if value else Decimal('0')
        except (ValueError, TypeError):
            return Decimal('0')

    @staticmethod
    def coin_to_protobuf(coin: Coin):
        """
        Convert Django Coin model to protobuf message.

        Args:
            coin: Coin Django model instance

        Returns:
            Protobuf Coin message

        Example:
            >>> from apps.crypto.models import Coin
            >>> coin = Coin.objects.get(symbol='BTC')
            >>> pb_coin = ProtobufConverter.coin_to_protobuf(coin)
        """
        if crypto_service_pb2 is None:
            raise ImportError("Proto files not generated. Run: python manage.py generate_proto")

        return crypto_service_pb2.Coin(
            # Identity
            id=coin.id,
            symbol=coin.symbol,
            name=coin.name,
            slug=coin.slug,
            # Market data (as strings for precision)
            current_price_usd=ProtobufConverter.decimal_to_string(coin.current_price_usd),
            market_cap_usd=ProtobufConverter.decimal_to_string(coin.market_cap_usd),
            volume_24h_usd=ProtobufConverter.decimal_to_string(coin.volume_24h_usd),
            # Price changes
            price_change_24h_percent=ProtobufConverter.decimal_to_string(coin.price_change_24h_percent),
            price_change_7d_percent=ProtobufConverter.decimal_to_string(coin.price_change_7d_percent),
            price_change_30d_percent=ProtobufConverter.decimal_to_string(coin.price_change_30d_percent),
            # Metadata
            logo_url=coin.logo_url or "",
            description=coin.description or "",
            website=coin.website or "",
            whitepaper_url=coin.whitepaper_url or "",
            # Rankings & flags
            rank=coin.rank,
            is_active=coin.is_active,
            is_tradeable=coin.is_tradeable,
            is_price_up_24h=coin.is_price_up_24h,  # Computed property
            # Timestamps
            created_at=ProtobufConverter.datetime_to_timestamp(coin.created_at),
            updated_at=ProtobufConverter.datetime_to_timestamp(coin.updated_at),
        )

    @staticmethod
    def wallet_to_protobuf(wallet: Wallet):
        """
        Convert Django Wallet model to protobuf message.

        Includes denormalized coin data for convenience.

        Args:
            wallet: Wallet Django model instance

        Returns:
            Protobuf Wallet message

        Example:
            >>> from apps.crypto.models import Wallet
            >>> wallet = Wallet.objects.select_related('coin').get(id=1)
            >>> pb_wallet = ProtobufConverter.wallet_to_protobuf(wallet)
        """
        if crypto_service_pb2 is None:
            raise ImportError("Proto files not generated. Run: python manage.py generate_proto")

        return crypto_service_pb2.Wallet(
            # Identity
            id=wallet.id,
            user_id=wallet.user_id,
            coin_id=wallet.coin_id,
            # Denormalized coin info
            symbol=wallet.coin.symbol,
            coin_name=wallet.coin.name,
            # Balances (as strings for precision)
            balance=ProtobufConverter.decimal_to_string(wallet.balance),
            locked_balance=ProtobufConverter.decimal_to_string(wallet.locked_balance),
            total_balance=ProtobufConverter.decimal_to_string(wallet.total_balance),
            value_usd=ProtobufConverter.decimal_to_string(wallet.value_usd),
            # Wallet address
            address=wallet.address or "",
            # Timestamps
            created_at=ProtobufConverter.datetime_to_timestamp(wallet.created_at),
            updated_at=ProtobufConverter.datetime_to_timestamp(wallet.updated_at),
        )

    @staticmethod
    def portfolio_holding_to_protobuf(wallet: Wallet, portfolio_total: Decimal):
        """
        Convert Wallet to PortfolioHolding with percentage.

        Args:
            wallet: Wallet instance
            portfolio_total: Total portfolio value in USD

        Returns:
            Protobuf PortfolioHolding message

        Example:
            >>> holding = ProtobufConverter.portfolio_holding_to_protobuf(
            ...     wallet, total_value
            ... )
        """
        if crypto_service_pb2 is None:
            raise ImportError("Proto files not generated. Run: python manage.py generate_proto")

        # Calculate percentage of portfolio
        percentage = Decimal('0')
        if portfolio_total > 0:
            percentage = (wallet.value_usd / portfolio_total) * 100

        return crypto_service_pb2.PortfolioHolding(
            symbol=wallet.coin.symbol,
            coin_name=wallet.coin.name,
            balance=ProtobufConverter.decimal_to_string(wallet.total_balance),
            value_usd=ProtobufConverter.decimal_to_string(wallet.value_usd),
            percentage=ProtobufConverter.decimal_to_string(percentage),
            change_24h_percent=ProtobufConverter.decimal_to_string(
                wallet.coin.price_change_24h_percent
            ),
        )
