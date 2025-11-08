"""
Crypto gRPC Service.

Clean implementation with handlers separation and Centrifugo WebSocket bridge.

Features:
- Unary RPC for CRUD operations (coins, wallets, portfolio)
- Server-side streaming for real-time price updates
- Centrifugo bridge for WebSocket publishing
- Handlers-based architecture for clean code separation
"""

import asyncio
import logging

import grpc
from django.contrib.auth import get_user_model
from django.utils import timezone

from django_cfg.apps.integrations.grpc.services import BaseService
from django_cfg.apps.integrations.grpc.services.centrifugo.bridge import CentrifugoBridgeMixin

# Import generated proto files
from .generated import crypto_service_pb2, crypto_service_pb2_grpc

# Import models and converters
from apps.crypto.models import Coin, Wallet
from .proto.converters import ProtobufConverter

# Import configuration
from .channels import CryptoChannels
from .config import ProductionConfig

# Import handlers
from .handlers import (
    # Coin operations
    handle_get_coin,
    handle_list_coins,
    handle_search_coins,
    handle_get_top_coins,
    # Wallet operations
    handle_get_wallet,
    handle_list_wallets,
    # Portfolio
    handle_get_portfolio,
    # Transfers
    handle_deposit,
    handle_withdraw,
    handle_transfer,
    # Market stats
    handle_get_market_stats,
    handle_get_trending_coins,
    # Streaming
    handle_stream_prices,
)

logger = logging.getLogger(__name__)
User = get_user_model()


class CryptoService(
    BaseService,
    crypto_service_pb2_grpc.CryptoServiceServicer,
    CentrifugoBridgeMixin
):
    """
    Crypto gRPC service.

    Minimal service with handlers separation and Centrifugo WebSocket bridge.

    Architecture:
    - Unary RPC methods delegate to handlers
    - StreamPrices publishes to Centrifugo WebSocket
    - Clean separation of concerns
    """

    # Centrifugo channel configuration
    centrifugo_channels = CryptoChannels()

    def __init__(self):
        """Initialize service with Centrifugo bridge."""
        super().__init__()
        # Explicitly initialize CentrifugoBridgeMixin (multiple inheritance)
        CentrifugoBridgeMixin.__init__(self)

        logger.info("CryptoService initialized with Centrifugo bridge")

    # ========================================================================
    # Coin Operations
    # ========================================================================

    def GetCoin(
        self,
        request: crypto_service_pb2.GetCoinRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.CoinResponse:
        """Get single coin. Delegates to handler."""
        try:
            return handle_get_coin(
                coin_id=request.id if request.HasField('id') else None,
                symbol=request.symbol if request.HasField('symbol') else None,
                slug=request.slug if request.HasField('slug') else None
            )
        except ValueError as e:
            self.abort_invalid_argument(context, str(e))
        except Coin.DoesNotExist as e:
            self.abort_not_found(context, str(e))
        except Exception as e:
            logger.exception(f"❌ GetCoin error: {e}")
            self.abort_internal(context, f"Failed to get coin: {str(e)}")

    def ListCoins(
        self,
        request: crypto_service_pb2.ListCoinsRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.ListCoinsResponse:
        """List coins. Delegates to handler."""
        try:
            return handle_list_coins(
                page=request.page or 1,
                page_size=request.page_size or 20,
                active_only=request.active_only,
                tradeable_only=request.tradeable_only,
                sort_by=request.sort_by,
                sort_order=request.sort_order
            )
        except Exception as e:
            logger.exception(f"❌ ListCoins error: {e}")
            self.abort_internal(context, f"Failed to list coins: {str(e)}")

    def SearchCoins(
        self,
        request: crypto_service_pb2.SearchCoinsRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.ListCoinsResponse:
        """Search coins. Delegates to handler."""
        try:
            return handle_search_coins(query=request.query)
        except ValueError as e:
            self.abort_invalid_argument(context, str(e))
        except Exception as e:
            logger.exception(f"❌ SearchCoins error: {e}")
            self.abort_internal(context, f"Search failed: {str(e)}")

    def GetTopCoins(
        self,
        request: crypto_service_pb2.GetTopCoinsRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.ListCoinsResponse:
        """Get top coins. Delegates to handler."""
        try:
            return handle_get_top_coins(limit=request.limit or 10)
        except Exception as e:
            logger.exception(f"❌ GetTopCoins error: {e}")
            self.abort_internal(context, f"Failed to get top coins: {str(e)}")

    async def StreamPrices(
        self,
        request: crypto_service_pb2.StreamPricesRequest,
        context: grpc.aio.ServicerContext
    ):
        """Stream prices. Delegates to handler."""
        try:
            centrifugo_client = self._centrifugo_client if self._centrifugo_enabled else None
            
            async for price_update in handle_stream_prices(
                symbols=list(request.symbols) if request.symbols else [],
                interval=request.interval_seconds or 5,
                context=context,
                centrifugo_client=centrifugo_client
            ):
                yield price_update
                
        except Exception as e:
            logger.exception(f"❌ StreamPrices error: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Price streaming failed: {str(e)}")

    # ========================================================================
    # Wallet Operations (delegated to handlers)
    # ========================================================================

    def GetWallet(
        self,
        request: crypto_service_pb2.GetWalletRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.WalletResponse:
        """Get wallet. Delegates to handler."""
        try:
            return handle_get_wallet(
                user_id=request.user_id,
                coin_id=request.coin_id if request.HasField('coin_id') else None,
                symbol=request.symbol if request.HasField('symbol') else None
            )
        except ValueError as e:
            self.abort_invalid_argument(context, str(e))
        except Wallet.DoesNotExist:
            self.abort_not_found(context, f"Wallet not found for user {request.user_id}")
        except Exception as e:
            logger.exception(f"❌ GetWallet error: {e}")
            self.abort_internal(context, f"Failed to get wallet: {str(e)}")

    def ListWallets(
        self,
        request: crypto_service_pb2.ListWalletsRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.ListWalletsResponse:
        """List wallets. Delegates to handler."""
        try:
            return handle_list_wallets(
                user_id=request.user_id,
                exclude_zero_balance=request.exclude_zero_balance
            )
        except Exception as e:
            logger.exception(f"❌ ListWallets error: {e}")
            self.abort_internal(context, f"Failed to list wallets: {str(e)}")

    def GetPortfolio(
        self,
        request: crypto_service_pb2.GetPortfolioRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.PortfolioResponse:
        """Get portfolio summary. Delegates to handler."""
        try:
            return handle_get_portfolio(user_id=request.user_id)
        except Exception as e:
            logger.exception(f"❌ GetPortfolio error: {e}")
            self.abort_internal(context, f"Failed to get portfolio: {str(e)}")

    def Deposit(
        self,
        request: crypto_service_pb2.DepositRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.WalletResponse:
        """Deposit funds. Delegates to handler."""
        try:
            return handle_deposit(
                user_id=request.user_id,
                symbol=request.symbol,
                amount=request.amount,
                transaction_id=request.transaction_id
            )
        except ValueError as e:
            self.abort_invalid_argument(context, str(e))
        except Coin.DoesNotExist:
            self.abort_not_found(context, f"Coin not found: {request.symbol}")
        except Exception as e:
            logger.exception(f"❌ Deposit error: {e}")
            self.abort_internal(context, f"Deposit failed: {str(e)}")

    def Withdraw(
        self,
        request: crypto_service_pb2.WithdrawRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.WalletResponse:
        """Withdraw funds. Delegates to handler."""
        try:
            return handle_withdraw(
                user_id=request.user_id,
                symbol=request.symbol,
                amount=request.amount,
                destination_address=request.destination_address
            )
        except ValueError as e:
            self.abort_invalid_argument(context, str(e))
        except Wallet.DoesNotExist:
            self.abort_not_found(context, f"Wallet not found for {request.symbol}")
        except Exception as e:
            logger.exception(f"❌ Withdraw error: {e}")
            self.abort_internal(context, f"Withdrawal failed: {str(e)}")

    def Transfer(
        self,
        request: crypto_service_pb2.TransferRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.TransferResponse:
        """Transfer funds between users. Delegates to handler."""
        try:
            return handle_transfer(
                from_user_id=request.from_user_id,
                to_user_id=request.to_user_id,
                symbol=request.symbol,
                amount=request.amount,
                note=request.note
            )
        except ValueError as e:
            self.abort_invalid_argument(context, str(e))
        except (Coin.DoesNotExist, Wallet.DoesNotExist) as e:
            self.abort_not_found(context, str(e))
        except Exception as e:
            logger.exception(f"❌ Transfer error: {e}")
            self.abort_internal(context, f"Transfer failed: {str(e)}")

    # ========================================================================
    # Market Statistics (delegated to handlers)
    # ========================================================================

    def GetMarketStats(
        self,
        request,  # google.protobuf.Empty
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.MarketStatsResponse:
        """Get market statistics. Delegates to handler."""
        try:
            return handle_get_market_stats()
        except Exception as e:
            logger.exception(f"❌ GetMarketStats error: {e}")
            self.abort_internal(context, f"Failed to get market stats: {str(e)}")

    def GetTrendingCoins(
        self,
        request: crypto_service_pb2.GetTrendingCoinsRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.TrendingCoinsResponse:
        """Get trending coins. Delegates to handler."""
        try:
            return handle_get_trending_coins(
                limit=request.limit or 10,
                timeframe=request.timeframe or "24h"
            )
        except Exception as e:
            logger.exception(f"❌ GetTrendingCoins error: {e}")
            self.abort_internal(context, f"Failed to get trending coins: {str(e)}")


# ============================================================================
# Server Startup Helper
# ============================================================================

async def serve(host: str = '[::]', port: int = 50051):
    """
    Start gRPC server.

    Args:
        host: Host to bind to (default: all interfaces)
        port: Port to bind to (default: 50051)
    """
    server = grpc.aio.server()
    service = CryptoService()
    crypto_service_pb2_grpc.add_CryptoServiceServicer_to_server(service, server)

    listen_addr = f'{host}:{port}'
    server.add_insecure_port(listen_addr)

    logger.info(f"Starting Crypto gRPC server on {listen_addr}")
    await server.start()

    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Server interrupted, shutting down...")
        await server.stop(grace=5)


if __name__ == '__main__':
    """Run server standalone."""
    import sys
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s'
    )

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 50051
    asyncio.run(serve(port=port))
