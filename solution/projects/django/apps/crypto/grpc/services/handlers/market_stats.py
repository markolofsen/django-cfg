"""
Market statistics handlers for Crypto gRPC service.

Handles GetMarketStats and GetTrendingCoins operations.
"""
import logging
from decimal import Decimal

from django.db.models import Sum, Count, Q
from django.utils import timezone

from apps.crypto.models import Coin
from ..proto.converters import ProtobufConverter
from ..generated import crypto_service_pb2


logger = logging.getLogger(__name__)


def handle_get_market_stats() -> crypto_service_pb2.MarketStatsResponse:
    """
    Get market statistics.

    Returns:
        MarketStatsResponse with market data

    Example:
        >>> response = handle_get_market_stats()
        >>> print(f"Total market cap: ${response.total_market_cap_usd}")
    """
    # Get all active coins
    coins = Coin.objects.filter(is_active=True)

    # Calculate aggregates
    total_market_cap = coins.aggregate(
        total=Sum('market_cap_usd')
    )['total'] or Decimal('0')

    total_volume_24h = coins.aggregate(
        total=Sum('volume_24h_usd')
    )['total'] or Decimal('0')

    # Count coins by price change
    gainers_count = coins.filter(price_change_24h_percent__gt=0).count()
    losers_count = coins.filter(price_change_24h_percent__lt=0).count()
    stable_count = coins.filter(price_change_24h_percent=0).count()

    # Calculate average price change
    avg_change = coins.aggregate(
        avg=Sum('price_change_24h_percent')
    )['avg'] or Decimal('0')

    if coins.count() > 0:
        avg_change = avg_change / coins.count()

    logger.info(
        f"📈 GetMarketStats: market_cap=${total_market_cap}, "
        f"volume=${total_volume_24h}, coins={coins.count()}"
    )

    return crypto_service_pb2.MarketStatsResponse(
        success=True,
        message="Market statistics retrieved successfully",
        total_market_cap_usd=ProtobufConverter.decimal_to_string(total_market_cap),
        total_volume_24h_usd=ProtobufConverter.decimal_to_string(total_volume_24h),
        total_coins=coins.count(),
        active_coins=coins.count(),
        gainers_count=gainers_count,
        losers_count=losers_count,
        stable_count=stable_count,
        average_change_24h_percent=ProtobufConverter.decimal_to_string(avg_change),
        timestamp=ProtobufConverter.datetime_to_timestamp(timezone.now()),
    )


def handle_get_trending_coins(
    limit: int = 10,
    timeframe: str = "24h"
) -> crypto_service_pb2.TrendingCoinsResponse:
    """
    Get trending coins (biggest gainers/losers).

    Args:
        limit: Number of coins to return (default: 10)
        timeframe: Timeframe for trending ('24h', '7d', '30d')

    Returns:
        TrendingCoinsResponse with gainers and losers

    Example:
        >>> response = handle_get_trending_coins(limit=5)
        >>> for coin in response.gainers:
        ...     print(f"{coin.symbol}: +{coin.price_change_24h_percent}%")
    """
    limit = min(limit, 100)  # Max 100

    # Select price change field based on timeframe
    change_field = {
        '24h': 'price_change_24h_percent',
        '7d': 'price_change_7d_percent',
        '30d': 'price_change_30d_percent',
    }.get(timeframe, 'price_change_24h_percent')

    # Get gainers (biggest positive changes)
    gainers = Coin.objects.filter(
        is_active=True,
        **{f'{change_field}__gt': 0}
    ).order_by(f'-{change_field}')[:limit]

    # Get losers (biggest negative changes)
    losers = Coin.objects.filter(
        is_active=True,
        **{f'{change_field}__lt': 0}
    ).order_by(change_field)[:limit]

    # Convert to protobuf
    pb_gainers = [ProtobufConverter.coin_to_protobuf(coin) for coin in gainers]
    pb_losers = [ProtobufConverter.coin_to_protobuf(coin) for coin in losers]

    logger.info(
        f"🔥 GetTrendingCoins: timeframe={timeframe}, "
        f"gainers={len(pb_gainers)}, losers={len(pb_losers)}"
    )

    return crypto_service_pb2.TrendingCoinsResponse(
        success=True,
        message=f"Trending coins for {timeframe} retrieved successfully",
        gainers=pb_gainers,
        losers=pb_losers,
        timeframe=timeframe,
        timestamp=ProtobufConverter.datetime_to_timestamp(timezone.now()),
    )

