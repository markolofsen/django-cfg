"""
Centrifugo channel configurations for crypto service.

This module defines channel patterns and rate limiting rules for
real-time crypto price updates via Centrifugo WebSocket.

Created: 2025-01-08
Status: %%PRODUCTION%%
"""

from django_cfg.apps.integrations.grpc.services.centrifugo.config import (
    CentrifugoChannels,
    ChannelConfig,
)


class CryptoChannels(CentrifugoChannels):
    """
    Channel definitions for crypto price streaming.

    Inherits from universal CentrifugoChannels for:
    - Type-safe Pydantic v2 validation
    - Consistent configuration structure
    - Built-in graceful degradation

    **Channel Templates**:
    - `crypto#prices#{symbol}` - Real-time price updates for specific coin
    - `crypto#prices#all` - All price updates (high-volume)
    - `crypto#market#stats` - Market statistics updates
    - `crypto#wallet#{user_id}` - User wallet updates
    - `crypto#portfolio#{user_id}` - Portfolio value updates

    **Usage Example**:
    ```python
    from django_cfg.apps.integrations.grpc.services.centrifugo import CentrifugoBridgeMixin
    from .channels import CryptoChannels

    class CryptoService(
        crypto_service_pb2_grpc.CryptoServiceServicer,
        CentrifugoBridgeMixin
    ):
        centrifugo_channels = CryptoChannels()

        async def StreamPrices(self, request, context):
            # Your streaming logic
            for price_update in generate_prices():
                # Auto-publish to WebSocket
                await self._notify_centrifugo(
                    price_update,
                    symbol=price_update.symbol
                )
                yield price_update
    ```
    """

    # Real-time price updates for specific coin
    # IMPORTANT: Field name should match protobuf message field if using auto-mapping
    price_update: ChannelConfig = ChannelConfig(
        template='crypto#prices#{symbol}',
        rate_limit=0.5,  # Max 2 updates per second per coin
        critical=False,
        metadata={'event_type': 'price_update', 'category': 'market_data'}
    )

    # All price updates (high-volume channel)
    prices_all: ChannelConfig = ChannelConfig(
        template='crypto#prices#all',
        rate_limit=0.1,  # Max 10 updates per second total
        critical=False,
        metadata={'event_type': 'price_update_all', 'category': 'market_data'}
    )

    # Market statistics updates
    market_stats: ChannelConfig = ChannelConfig(
        template='crypto#market#stats',
        rate_limit=5.0,  # Max once per 5 seconds
        critical=False,
        metadata={'event_type': 'market_stats', 'category': 'analytics'}
    )

    # User wallet updates (critical - balance changes)
    wallet_update: ChannelConfig = ChannelConfig(
        template='crypto#wallet#{user_id}',
        rate_limit=None,  # No rate limit for wallet updates
        critical=True,  # Critical - user needs to know about balance changes
        metadata={'event_type': 'wallet_update', 'category': 'user_data'}
    )

    # Portfolio value updates
    portfolio_update: ChannelConfig = ChannelConfig(
        template='crypto#portfolio#{user_id}',
        rate_limit=2.0,  # Max once per 2 seconds
        critical=False,
        metadata={'event_type': 'portfolio_update', 'category': 'user_data'}
    )

    # Transaction confirmations (deposits/withdrawals)
    transaction: ChannelConfig = ChannelConfig(
        template='crypto#transaction#{user_id}',
        rate_limit=None,  # No rate limit for transactions
        critical=True,  # Critical - user needs immediate notification
        metadata={'event_type': 'transaction', 'category': 'user_data'}
    )

    # Trending coins updates
    trending: ChannelConfig = ChannelConfig(
        template='crypto#trending',
        rate_limit=60.0,  # Max once per minute
        critical=False,
        metadata={'event_type': 'trending', 'category': 'analytics'}
    )

