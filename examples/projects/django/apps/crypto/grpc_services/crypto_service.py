"""
Crypto gRPC Service.

Django gRPC service for cryptocurrency operations:
- Coin information (get, list, search, top coins)
- Real-time price streaming (server-side streaming)
- Wallet operations (get, list, deposit, withdraw, transfer)
- Portfolio management
- Market statistics

Auto-discovered by django-cfg when GRPCConfig.enabled_apps includes "crypto"

Example Usage (from bot/client):
    >>> import grpc
    >>> from generated import crypto_service_pb2, crypto_service_pb2_grpc
    >>>
    >>> channel = grpc.insecure_channel('localhost:50051')
    >>> stub = crypto_service_pb2_grpc.CryptoServiceStub(channel)
    >>>
    >>> # Get Bitcoin info
    >>> request = crypto_service_pb2.GetCoinRequest(symbol='BTC')
    >>> response = stub.GetCoin(request)
    >>> print(f"BTC Price: ${response.coin.current_price_usd}")
"""

import logging
import time
from decimal import Decimal
from typing import Optional

import grpc
from django.db import transaction
from django.db.models import Q, Sum, F, Count
from django.utils import timezone
from django.contrib.auth import get_user_model

from django_cfg.apps.integrations.grpc.services import BaseService

# Import generated proto files from local package
from .generated import crypto_service_pb2, crypto_service_pb2_grpc

from ..models import Coin, Wallet
from .converters import ProtobufConverter

logger = logging.getLogger(__name__)
User = get_user_model()


class CryptoService(BaseService, crypto_service_pb2_grpc.CryptoServiceServicer):
    """
    Django gRPC service for cryptocurrency operations.

    This service is automatically discovered and registered by django-cfg.

    Features:
    - Complete CRUD for coins and wallets
    - Real-time price streaming
    - Portfolio management
    - Market analytics
    """

    # ========================================================================
    # Coin Operations
    # ========================================================================

    def GetCoin(
        self,
        request: crypto_service_pb2.GetCoinRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.CoinResponse:
        """
        Get single coin by ID, symbol, or slug.

        Args:
            request: GetCoinRequest with identifier
            context: gRPC context

        Returns:
            CoinResponse with coin data

        Example:
            >>> request = GetCoinRequest(symbol='BTC')
            >>> response = stub.GetCoin(request)
        """
        try:
            # Determine lookup field
            lookup = {}
            if request.HasField('id'):
                lookup['id'] = request.id
            elif request.HasField('symbol'):
                lookup['symbol'] = request.symbol.upper()
            elif request.HasField('slug'):
                lookup['slug'] = request.slug.lower()
            else:
                self.abort_invalid_argument(context, "Must provide id, symbol, or slug")

            # Get coin
            try:
                coin = Coin.objects.get(**lookup)
            except Coin.DoesNotExist:
                self.abort_not_found(context, f"Coin not found: {lookup}")

            logger.info(f"📊 GetCoin: {coin.symbol}")

            return crypto_service_pb2.CoinResponse(
                success=True,
                message="Coin retrieved successfully",
                coin=ProtobufConverter.coin_to_protobuf(coin)
            )

        except Exception as e:
            logger.exception(f"❌ GetCoin error: {e}")
            self.abort_internal(context, f"Failed to get coin: {str(e)}")

    def ListCoins(
        self,
        request: crypto_service_pb2.ListCoinsRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.ListCoinsResponse:
        """
        List all coins with pagination and filtering.

        Args:
            request: ListCoinsRequest with pagination/filters
            context: gRPC context

        Returns:
            ListCoinsResponse with paginated coins

        Example:
            >>> request = ListCoinsRequest(page=1, page_size=10, active_only=True)
            >>> response = stub.ListCoins(request)
        """
        try:
            # Pagination
            page = max(request.page or 1, 1)
            page_size = min(request.page_size or 20, 100)  # Max 100
            offset = (page - 1) * page_size

            # Build queryset
            queryset = Coin.objects.all()

            # Apply filters
            if request.active_only:
                queryset = queryset.filter(is_active=True)

            if request.tradeable_only:
                queryset = queryset.filter(is_tradeable=True)

            # Apply sorting
            sort_map = {
                crypto_service_pb2.RANK: 'rank',
                crypto_service_pb2.PRICE: 'current_price_usd',
                crypto_service_pb2.MARKET_CAP: 'market_cap_usd',
                crypto_service_pb2.VOLUME_24H: 'volume_24h_usd',
                crypto_service_pb2.CHANGE_24H: 'price_change_24h_percent',
                crypto_service_pb2.NAME: 'name',
                crypto_service_pb2.SYMBOL: 'symbol',
            }

            sort_field = sort_map.get(request.sort_by, 'rank')
            if request.sort_order == crypto_service_pb2.DESC:
                sort_field = f'-{sort_field}'

            queryset = queryset.order_by(sort_field)

            # Get total count
            total_count = queryset.count()
            total_pages = (total_count + page_size - 1) // page_size

            # Paginate
            coins = list(queryset[offset:offset + page_size])

            # Convert to protobuf
            pb_coins = [ProtobufConverter.coin_to_protobuf(coin) for coin in coins]

            logger.info(f"📋 ListCoins: page={page}, count={len(pb_coins)}, total={total_count}")

            return crypto_service_pb2.ListCoinsResponse(
                success=True,
                message=f"Found {total_count} coins",
                coins=pb_coins,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
            )

        except Exception as e:
            logger.exception(f"❌ ListCoins error: {e}")
            self.abort_internal(context, f"Failed to list coins: {str(e)}")

    def SearchCoins(
        self,
        request: crypto_service_pb2.SearchCoinsRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.ListCoinsResponse:
        """
        Search coins by name or symbol.

        Args:
            request: SearchCoinsRequest with query
            context: gRPC context

        Returns:
            ListCoinsResponse with matching coins

        Example:
            >>> request = SearchCoinsRequest(query='bitcoin', limit=5)
            >>> response = stub.SearchCoins(request)
        """
        try:
            query = request.query.strip()
            if not query:
                self.abort_invalid_argument(context, "Search query cannot be empty")

            limit = min(request.limit or 10, 50)  # Max 50

            # Search by symbol or name
            coins = Coin.objects.filter(
                Q(symbol__icontains=query) | Q(name__icontains=query),
                is_active=True
            ).order_by('rank')[:limit]

            # Convert to protobuf
            pb_coins = [ProtobufConverter.coin_to_protobuf(coin) for coin in coins]

            logger.info(f"🔍 SearchCoins: query='{query}', found={len(pb_coins)}")

            return crypto_service_pb2.ListCoinsResponse(
                success=True,
                message=f"Found {len(pb_coins)} coins matching '{query}'",
                coins=pb_coins,
                total_count=len(pb_coins),
                page=1,
                page_size=limit,
                total_pages=1,
            )

        except Exception as e:
            logger.exception(f"❌ SearchCoins error: {e}")
            self.abort_internal(context, f"Failed to search coins: {str(e)}")

    def GetTopCoins(
        self,
        request: crypto_service_pb2.GetTopCoinsRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.ListCoinsResponse:
        """
        Get top coins by market cap.

        Args:
            request: GetTopCoinsRequest with limit
            context: gRPC context

        Returns:
            ListCoinsResponse with top coins

        Example:
            >>> request = GetTopCoinsRequest(limit=10)
            >>> response = stub.GetTopCoins(request)
        """
        try:
            limit = min(request.limit or 10, 100)  # Max 100

            # Get top coins by rank
            coins = Coin.objects.filter(
                is_active=True
            ).order_by('rank')[:limit]

            # Convert to protobuf
            pb_coins = [ProtobufConverter.coin_to_protobuf(coin) for coin in coins]

            logger.info(f"🏆 GetTopCoins: limit={limit}, found={len(pb_coins)}")

            return crypto_service_pb2.ListCoinsResponse(
                success=True,
                message=f"Top {len(pb_coins)} coins by market cap",
                coins=pb_coins,
                total_count=len(pb_coins),
                page=1,
                page_size=limit,
                total_pages=1,
            )

        except Exception as e:
            logger.exception(f"❌ GetTopCoins error: {e}")
            self.abort_internal(context, f"Failed to get top coins: {str(e)}")

    def StreamPrices(
        self,
        request: crypto_service_pb2.StreamPricesRequest,
        context: grpc.ServicerContext
    ):
        """
        Stream real-time price updates (server-side streaming).

        Sends price updates at specified intervals.

        Args:
            request: StreamPricesRequest with symbols and interval
            context: gRPC context

        Yields:
            PriceUpdate messages

        Example:
            >>> request = StreamPricesRequest(symbols=['BTC', 'ETH'], interval_seconds=5)
            >>> for update in stub.StreamPrices(request):
            ...     print(f"{update.symbol}: ${update.price_usd}")
        """
        try:
            symbols = [s.upper() for s in request.symbols] if request.symbols else []
            interval = max(request.interval_seconds or 5, 1)  # Min 1 second

            if not symbols:
                # Stream all active coins if no symbols specified
                coins = Coin.objects.filter(is_active=True).order_by('rank')[:10]
                symbols = [coin.symbol for coin in coins]

            logger.info(f"📡 StreamPrices started: symbols={symbols}, interval={interval}s")

            while context.is_active():
                # Get current prices
                coins = Coin.objects.filter(symbol__in=symbols, is_active=True)

                for coin in coins:
                    # Send price update
                    yield crypto_service_pb2.PriceUpdate(
                        symbol=coin.symbol,
                        price_usd=ProtobufConverter.decimal_to_string(coin.current_price_usd),
                        change_24h_percent=ProtobufConverter.decimal_to_string(
                            coin.price_change_24h_percent
                        ),
                        timestamp=ProtobufConverter.datetime_to_timestamp(timezone.now())
                    )

                # Wait for next interval
                time.sleep(interval)

            logger.info(f"📡 StreamPrices ended: symbols={symbols}")

        except Exception as e:
            logger.exception(f"❌ StreamPrices error: {e}")
            self.abort_internal(context, f"Price streaming failed: {str(e)}")

    # ========================================================================
    # Wallet Operations
    # ========================================================================

    def GetWallet(
        self,
        request: crypto_service_pb2.GetWalletRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.WalletResponse:
        """
        Get user's wallet for specific coin.

        Args:
            request: GetWalletRequest with user_id and coin identifier
            context: gRPC context

        Returns:
            WalletResponse with wallet data

        Example:
            >>> request = GetWalletRequest(user_id=1, symbol='BTC')
            >>> response = stub.GetWallet(request)
        """
        try:
            # Get coin lookup
            if request.HasField('coin_id'):
                coin_lookup = {'coin_id': request.coin_id}
            elif request.HasField('symbol'):
                coin_lookup = {'coin__symbol': request.symbol.upper()}
            else:
                self.abort_invalid_argument(context, "Must provide coin_id or symbol")

            # Get wallet (select_related for coin data)
            try:
                wallet = Wallet.objects.select_related('coin').get(
                    user_id=request.user_id,
                    **coin_lookup
                )
            except Wallet.DoesNotExist:
                self.abort_not_found(
                    context,
                    f"Wallet not found for user {request.user_id}"
                )

            logger.info(f"💰 GetWallet: user={request.user_id}, coin={wallet.coin.symbol}")

            return crypto_service_pb2.WalletResponse(
                success=True,
                message="Wallet retrieved successfully",
                wallet=ProtobufConverter.wallet_to_protobuf(wallet)
            )

        except Exception as e:
            logger.exception(f"❌ GetWallet error: {e}")
            self.abort_internal(context, f"Failed to get wallet: {str(e)}")

    def ListWallets(
        self,
        request: crypto_service_pb2.ListWalletsRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.ListWalletsResponse:
        """
        List all user wallets.

        Args:
            request: ListWalletsRequest with user_id
            context: gRPC context

        Returns:
            ListWalletsResponse with all wallets and portfolio total

        Example:
            >>> request = ListWalletsRequest(user_id=1, exclude_zero_balance=True)
            >>> response = stub.ListWallets(request)
        """
        try:
            # Build queryset
            queryset = Wallet.objects.select_related('coin').filter(
                user_id=request.user_id
            )

            # Exclude zero balances if requested
            if request.exclude_zero_balance:
                queryset = queryset.filter(balance__gt=0)

            wallets = list(queryset.order_by('-balance'))

            # Calculate total portfolio value
            total_value_usd = sum(
                wallet.value_usd for wallet in wallets
            )

            # Convert to protobuf
            pb_wallets = [ProtobufConverter.wallet_to_protobuf(w) for w in wallets]

            logger.info(
                f"💼 ListWallets: user={request.user_id}, "
                f"count={len(pb_wallets)}, total=${total_value_usd}"
            )

            return crypto_service_pb2.ListWalletsResponse(
                success=True,
                message=f"Found {len(pb_wallets)} wallets",
                wallets=pb_wallets,
                total_value_usd=ProtobufConverter.decimal_to_string(total_value_usd),
            )

        except Exception as e:
            logger.exception(f"❌ ListWallets error: {e}")
            self.abort_internal(context, f"Failed to list wallets: {str(e)}")

    def GetPortfolio(
        self,
        request: crypto_service_pb2.GetPortfolioRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.PortfolioResponse:
        """
        Get portfolio summary with all holdings.

        Args:
            request: GetPortfolioRequest with user_id
            context: gRPC context

        Returns:
            PortfolioResponse with complete portfolio data

        Example:
            >>> request = GetPortfolioRequest(user_id=1)
            >>> response = stub.GetPortfolio(request)
            >>> print(f"Portfolio value: ${response.total_value_usd}")
        """
        try:
            # Get all non-zero wallets
            wallets = Wallet.objects.select_related('coin').filter(
                user_id=request.user_id,
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
                f"📊 GetPortfolio: user={request.user_id}, "
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

        except Exception as e:
            logger.exception(f"❌ GetPortfolio error: {e}")
            self.abort_internal(context, f"Failed to get portfolio: {str(e)}")

    def Deposit(
        self,
        request: crypto_service_pb2.DepositRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.WalletResponse:
        """
        Deposit funds to wallet.

        Args:
            request: DepositRequest with user_id, symbol, amount
            context: gRPC context

        Returns:
            WalletResponse with updated wallet

        Example:
            >>> request = DepositRequest(
            ...     user_id=1,
            ...     symbol='BTC',
            ...     amount='0.5',
            ...     transaction_id='tx123'
            ... )
            >>> response = stub.Deposit(request)
        """
        try:
            amount = ProtobufConverter.string_to_decimal(request.amount)
            if amount <= 0:
                self.abort_invalid_argument(context, "Amount must be positive")

            # Get coin
            try:
                coin = Coin.objects.get(symbol=request.symbol.upper())
            except Coin.DoesNotExist:
                self.abort_not_found(context, f"Coin not found: {request.symbol}")

            # Get or create wallet
            with transaction.atomic():
                wallet, created = Wallet.objects.select_related('coin').get_or_create(
                    user_id=request.user_id,
                    coin=coin,
                    defaults={'balance': Decimal('0')}
                )

                # Add deposit
                wallet.balance += amount
                wallet.save(update_fields=['balance', 'updated_at'])

            logger.info(
                f"💵 Deposit: user={request.user_id}, coin={coin.symbol}, "
                f"amount={amount}, tx={request.transaction_id}"
            )

            return crypto_service_pb2.WalletResponse(
                success=True,
                message=f"Deposited {amount} {coin.symbol} successfully",
                wallet=ProtobufConverter.wallet_to_protobuf(wallet)
            )

        except Exception as e:
            logger.exception(f"❌ Deposit error: {e}")
            self.abort_internal(context, f"Deposit failed: {str(e)}")

    def Withdraw(
        self,
        request: crypto_service_pb2.WithdrawRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.WalletResponse:
        """
        Withdraw funds from wallet.

        Args:
            request: WithdrawRequest with user_id, symbol, amount, address
            context: gRPC context

        Returns:
            WalletResponse with updated wallet

        Example:
            >>> request = WithdrawRequest(
            ...     user_id=1,
            ...     symbol='BTC',
            ...     amount='0.1',
            ...     destination_address='1A1zP1...'
            ... )
            >>> response = stub.Withdraw(request)
        """
        try:
            amount = ProtobufConverter.string_to_decimal(request.amount)
            if amount <= 0:
                self.abort_invalid_argument(context, "Amount must be positive")

            # Get wallet
            try:
                wallet = Wallet.objects.select_related('coin').get(
                    user_id=request.user_id,
                    coin__symbol=request.symbol.upper()
                )
            except Wallet.DoesNotExist:
                self.abort_not_found(
                    context,
                    f"Wallet not found for {request.symbol}"
                )

            # Check balance
            if wallet.balance < amount:
                self.abort_invalid_argument(
                    context,
                    f"Insufficient balance. Available: {wallet.balance}, "
                    f"Requested: {amount}"
                )

            # Process withdrawal
            with transaction.atomic():
                wallet.balance -= amount
                wallet.save(update_fields=['balance', 'updated_at'])

            logger.info(
                f"💸 Withdraw: user={request.user_id}, coin={wallet.coin.symbol}, "
                f"amount={amount}, to={request.destination_address}"
            )

            return crypto_service_pb2.WalletResponse(
                success=True,
                message=f"Withdrew {amount} {wallet.coin.symbol} successfully",
                wallet=ProtobufConverter.wallet_to_protobuf(wallet)
            )

        except Exception as e:
            logger.exception(f"❌ Withdraw error: {e}")
            self.abort_internal(context, f"Withdrawal failed: {str(e)}")

    def Transfer(
        self,
        request: crypto_service_pb2.TransferRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.TransferResponse:
        """
        Transfer funds between users.

        Args:
            request: TransferRequest with from/to user_id, symbol, amount
            context: gRPC context

        Returns:
            TransferResponse with both updated wallets

        Example:
            >>> request = TransferRequest(
            ...     from_user_id=1,
            ...     to_user_id=2,
            ...     symbol='BTC',
            ...     amount='0.01',
            ...     note='Payment for services'
            ... )
            >>> response = stub.Transfer(request)
        """
        try:
            amount = ProtobufConverter.string_to_decimal(request.amount)
            if amount <= 0:
                self.abort_invalid_argument(context, "Amount must be positive")

            if request.from_user_id == request.to_user_id:
                self.abort_invalid_argument(context, "Cannot transfer to yourself")

            # Get coin
            try:
                coin = Coin.objects.get(symbol=request.symbol.upper())
            except Coin.DoesNotExist:
                self.abort_not_found(context, f"Coin not found: {request.symbol}")

            # Process transfer atomically
            with transaction.atomic():
                # Get sender wallet
                try:
                    from_wallet = Wallet.objects.select_for_update().select_related(
                        'coin'
                    ).get(
                        user_id=request.from_user_id,
                        coin=coin
                    )
                except Wallet.DoesNotExist:
                    self.abort_not_found(
                        context,
                        f"Sender wallet not found for {coin.symbol}"
                    )

                # Check balance
                if from_wallet.balance < amount:
                    self.abort_invalid_argument(
                        context,
                        f"Insufficient balance. Available: {from_wallet.balance}"
                    )

                # Get or create recipient wallet
                to_wallet, created = Wallet.objects.select_for_update().select_related(
                    'coin'
                ).get_or_create(
                    user_id=request.to_user_id,
                    coin=coin,
                    defaults={'balance': Decimal('0')}
                )

                # Execute transfer
                from_wallet.balance -= amount
                to_wallet.balance += amount

                from_wallet.save(update_fields=['balance', 'updated_at'])
                to_wallet.save(update_fields=['balance', 'updated_at'])

                # Generate transaction ID
                import uuid
                tx_id = str(uuid.uuid4())

            logger.info(
                f"🔄 Transfer: {request.from_user_id} → {request.to_user_id}, "
                f"amount={amount} {coin.symbol}, tx={tx_id}"
            )

            return crypto_service_pb2.TransferResponse(
                success=True,
                message=f"Transferred {amount} {coin.symbol} successfully",
                from_wallet=ProtobufConverter.wallet_to_protobuf(from_wallet),
                to_wallet=ProtobufConverter.wallet_to_protobuf(to_wallet),
                transaction_id=tx_id,
            )

        except Exception as e:
            logger.exception(f"❌ Transfer error: {e}")
            self.abort_internal(context, f"Transfer failed: {str(e)}")

    # ========================================================================
    # Market Statistics
    # ========================================================================

    def GetMarketStats(
        self,
        request,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.MarketStatsResponse:
        """
        Get overall market statistics.

        Args:
            request: Empty request
            context: gRPC context

        Returns:
            MarketStatsResponse with market data

        Example:
            >>> from google.protobuf.empty_pb2 import Empty
            >>> response = stub.GetMarketStats(Empty())
            >>> print(f"Total market cap: ${response.total_market_cap_usd}")
        """
        try:
            # Get active coins
            coins = Coin.objects.filter(is_active=True)

            # Calculate totals
            stats = coins.aggregate(
                total_market_cap=Sum('market_cap_usd'),
                total_volume=Sum('volume_24h_usd'),
                coins_count=Count('id'),
            )

            # Count gainers/losers
            coins_up = coins.filter(price_change_24h_percent__gt=0).count()
            coins_down = coins.filter(price_change_24h_percent__lt=0).count()

            # Average change
            avg_change = coins.aggregate(
                avg=Sum('price_change_24h_percent')
            )['avg'] or Decimal('0')

            if coins_count := stats['coins_count']:
                avg_change = avg_change / coins_count

            logger.info(f"📈 GetMarketStats: coins={coins_count}, up={coins_up}, down={coins_down}")

            return crypto_service_pb2.MarketStatsResponse(
                success=True,
                message="Market statistics retrieved successfully",
                total_market_cap_usd=ProtobufConverter.decimal_to_string(
                    stats['total_market_cap'] or Decimal('0')
                ),
                total_volume_24h_usd=ProtobufConverter.decimal_to_string(
                    stats['total_volume'] or Decimal('0')
                ),
                active_coins_count=coins_count,
                coins_up_24h=coins_up,
                coins_down_24h=coins_down,
                average_change_24h=ProtobufConverter.decimal_to_string(avg_change),
                calculated_at=ProtobufConverter.datetime_to_timestamp(timezone.now()),
            )

        except Exception as e:
            logger.exception(f"❌ GetMarketStats error: {e}")
            self.abort_internal(context, f"Failed to get market stats: {str(e)}")

    def GetTrendingCoins(
        self,
        request: crypto_service_pb2.GetTrendingCoinsRequest,
        context: grpc.ServicerContext
    ) -> crypto_service_pb2.TrendingCoinsResponse:
        """
        Get trending coins (gainers/losers/most traded).

        Args:
            request: GetTrendingCoinsRequest with type and limit
            context: gRPC context

        Returns:
            TrendingCoinsResponse with trending coins

        Example:
            >>> request = GetTrendingCoinsRequest(
            ...     type=TrendingType.TOP_GAINERS,
            ...     limit=10
            ... )
            >>> response = stub.GetTrendingCoins(request)
        """
        try:
            limit = min(request.limit or 10, 50)  # Max 50
            queryset = Coin.objects.filter(is_active=True)

            # Sort based on type
            if request.type == crypto_service_pb2.TOP_GAINERS:
                queryset = queryset.order_by('-price_change_24h_percent')
            elif request.type == crypto_service_pb2.TOP_LOSERS:
                queryset = queryset.order_by('price_change_24h_percent')
            elif request.type == crypto_service_pb2.MOST_TRADED:
                queryset = queryset.order_by('-volume_24h_usd')
            else:
                self.abort_invalid_argument(context, "Invalid trending type")

            coins = list(queryset[:limit])

            # Convert to protobuf
            pb_coins = [ProtobufConverter.coin_to_protobuf(coin) for coin in coins]

            type_name = crypto_service_pb2.TrendingType.Name(request.type)
            logger.info(f"📊 GetTrendingCoins: type={type_name}, count={len(pb_coins)}")

            return crypto_service_pb2.TrendingCoinsResponse(
                success=True,
                message=f"Found {len(pb_coins)} trending coins",
                type=request.type,
                coins=pb_coins,
            )

        except Exception as e:
            logger.exception(f"❌ GetTrendingCoins error: {e}")
            self.abort_internal(context, f"Failed to get trending coins: {str(e)}")


def grpc_handlers(server):
    """
    Register gRPC handlers for crypto app.

    This function is auto-discovered by django-cfg ServiceDiscovery.

    Args:
        server: gRPC server instance or None (for discovery)

    Returns:
        List of (service_class, add_to_server_func) tuples

    Example:
        >>> # Called automatically by django-cfg
        >>> handlers = grpc_handlers(server)
    """
    # If server is provided, register the service
    if server is not None:
        crypto_service = CryptoService()
        crypto_service_pb2_grpc.add_CryptoServiceServicer_to_server(
            crypto_service, server
        )

    # Return list of services for discovery
    return [
        (CryptoService, crypto_service_pb2_grpc.add_CryptoServiceServicer_to_server)
    ]
