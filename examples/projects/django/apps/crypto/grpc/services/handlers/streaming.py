"""
Streaming operations handler for Crypto gRPC service.

Handles StreamPrices server-side streaming with Centrifugo WebSocket publishing.
"""
import asyncio
import logging

import grpc
from django.utils import timezone

from apps.crypto.models import Coin
from ..proto.converters import ProtobufConverter
from ..generated import crypto_service_pb2


logger = logging.getLogger(__name__)


async def handle_stream_prices(
    symbols: list[str],
    interval: int,
    context: grpc.aio.ServicerContext,
    centrifugo_client=None
):
    """
    Stream real-time price updates (server-side streaming).

    Publishes to Centrifugo WebSocket for browser clients.

    Args:
        symbols: List of coin symbols to stream (empty = top 10)
        interval: Update interval in seconds (min 1)
        context: gRPC async context
        centrifugo_client: Optional Centrifugo client for WebSocket publishing

    Yields:
        PriceUpdate messages
    """
    # Normalize symbols
    symbols = [s.upper() for s in symbols] if symbols else []
    interval = max(interval, 1)  # Min 1 second

    # Get default symbols if none provided
    if not symbols:
        coins = await Coin.objects.filter(is_active=True).order_by('rank')[:10].alist()
        symbols = [coin.symbol for coin in coins]

    logger.info(f"📡 StreamPrices started: symbols={symbols}, interval={interval}s")

    try:
        while not context.cancelled():
            # Get current prices (async ORM)
            coins = await Coin.objects.filter(
                symbol__in=symbols,
                is_active=True
            ).alist()

            for coin in coins:
                # Create price update message
                price_update = crypto_service_pb2.PriceUpdate(
                    symbol=coin.symbol,
                    price_usd=ProtobufConverter.decimal_to_string(coin.current_price_usd),
                    change_24h_percent=ProtobufConverter.decimal_to_string(
                        coin.price_change_24h_percent
                    ),
                    timestamp=ProtobufConverter.datetime_to_timestamp(timezone.now())
                )

                # Publish to Centrifugo WebSocket
                if centrifugo_client:
                    try:
                        # Publish to specific coin channel
                        await centrifugo_client.publish(
                            channel=f'crypto#prices#{coin.symbol}',
                            data={
                                'symbol': coin.symbol,
                                'price_usd': str(coin.current_price_usd),
                                'change_24h_percent': str(coin.price_change_24h_percent),
                                'timestamp': timezone.now().isoformat(),
                            }
                        )
                        # Publish to "all prices" channel
                        await centrifugo_client.publish(
                            channel='crypto#prices#all',
                            data={
                                'symbol': coin.symbol,
                                'price_usd': str(coin.current_price_usd),
                                'change_24h_percent': str(coin.price_change_24h_percent),
                                'timestamp': timezone.now().isoformat(),
                            }
                        )
                    except Exception as e:
                        logger.warning(f"Failed to publish to Centrifugo: {e}")

                # Send to gRPC client
                yield price_update

            # Wait for next interval
            await asyncio.sleep(interval)

        logger.info(f"📡 StreamPrices ended: symbols={symbols}")

    except Exception as e:
        logger.exception(f"❌ StreamPrices error: {e}")
        raise

