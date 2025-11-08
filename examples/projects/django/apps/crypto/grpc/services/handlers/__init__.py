"""
Crypto gRPC service handlers.

Each handler is a pure function that processes a specific operation.

This module also provides grpc_handlers() for django-cfg ServiceDiscovery.
"""
import logging

# Handler functions
from .coins import handle_get_coin, handle_list_coins, handle_search_coins, handle_get_top_coins
from .wallets import handle_get_wallet, handle_list_wallets
from .portfolio import handle_get_portfolio
from .transfers import handle_deposit, handle_withdraw, handle_transfer
from .market_stats import handle_get_market_stats, handle_get_trending_coins
from .streaming import handle_stream_prices


__all__ = [
    # Coin operations
    'handle_get_coin',
    'handle_list_coins',
    'handle_search_coins',
    'handle_get_top_coins',
    # Wallet operations
    'handle_get_wallet',
    'handle_list_wallets',
    # Portfolio
    'handle_get_portfolio',
    # Transfers
    'handle_deposit',
    'handle_withdraw',
    'handle_transfer',
    # Market stats
    'handle_get_market_stats',
    'handle_get_trending_coins',
    # Streaming
    'handle_stream_prices',
    # ServiceDiscovery
    'grpc_handlers',
]


# ============================================================================
# ServiceDiscovery Hook
# ============================================================================

logger = logging.getLogger(__name__)


def grpc_handlers(server):
    """
    Auto-discovered by django-cfg ServiceDiscovery.
    Registers CryptoService to gRPC server.

    IMPORTANT: This function is called EARLY during Django startup,
    so we must delay imports of Django models until the server is actually running.

    NO Django model imports allowed here!
    """
    logger.info("🔧 crypto/grpc_handlers called!")
    logger.info(f"   server = {server}")

    # Import here to avoid circular imports
    from ..server import CryptoService
    from ..generated import crypto_service_pb2_grpc

    if server is not None:
        # Server provided - manually register the service
        logger.info("✅ grpc_handlers called with server - registering CryptoService")

        servicer = CryptoService()
        logger.info(f"🔧 Servicer created: {servicer}")

        crypto_service_pb2_grpc.add_CryptoServiceServicer_to_server(servicer, server)

        logger.info("✅ Registered CryptoService (unary + streaming)")
    else:
        # Discovery mode - just return the list for discovery
        logger.info("ℹ️  grpc_handlers called for discovery (server=None)")

    # Return list for ServiceDiscovery.discover_services() compatibility
    result = [(CryptoService, crypto_service_pb2_grpc.add_CryptoServiceServicer_to_server)]
    return result

