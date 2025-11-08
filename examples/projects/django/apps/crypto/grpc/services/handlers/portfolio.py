"""
Portfolio handler for Crypto gRPC service.

Handles GetPortfolio operation with complete portfolio calculation.
"""
import logging
from decimal import Decimal

from django.utils import timezone

from apps.crypto.models import Wallet
from ..proto.converters import ProtobufConverter
from ..generated import crypto_service_pb2


logger = logging.getLogger(__name__)


def handle_get_portfolio(
    user_id: int
) -> crypto_service_pb2.PortfolioResponse:
    """
    Get portfolio summary with all holdings.

    Args:
        user_id: User ID

    Returns:
        PortfolioResponse with complete portfolio data

    Example:
        >>> response = handle_get_portfolio(user_id=1)
        >>> print(f"Portfolio value: ${response.total_value_usd}")
    """
    # Get all non-zero wallets
    wallets = Wallet.objects.select_related('coin').filter(
        user_id=user_id,
        balance__gt=0
    ).order_by('-balance')

    # Calculate portfolio metrics
    total_value_usd = Decimal('0')
    total_change_24h_usd = Decimal('0')

    holdings = []
    for wallet in wallets:
        total_value_usd += wallet.value_usd

        # Calculate 24h change in USD
        change_24h = (
            wallet.value_usd * wallet.coin.price_change_24h_percent / 100
        )
        total_change_24h_usd += change_24h

        # Create holding
        holdings.append(
            ProtobufConverter.portfolio_holding_to_protobuf(
                wallet, total_value_usd
            )
        )

    # Calculate total change percentage
    total_change_24h_percent = Decimal('0')
    if total_value_usd > 0:
        total_change_24h_percent = (
            total_change_24h_usd / total_value_usd * 100
        )

    logger.info(
        f"📊 GetPortfolio: user={user_id}, "
        f"value=${total_value_usd}, coins={len(holdings)}"
    )

    return crypto_service_pb2.PortfolioResponse(
        success=True,
        message="Portfolio retrieved successfully",
        total_value_usd=ProtobufConverter.decimal_to_string(total_value_usd),
        total_change_24h_usd=ProtobufConverter.decimal_to_string(
            total_change_24h_usd
        ),
        total_change_24h_percent=ProtobufConverter.decimal_to_string(
            total_change_24h_percent
        ),
        coins_count=len(holdings),
        holdings=holdings,
        calculated_at=ProtobufConverter.datetime_to_timestamp(timezone.now()),
    )

