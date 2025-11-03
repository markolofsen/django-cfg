"""
gRPC Client Example for Crypto Service.

This module demonstrates how to use the CryptoService from a Python client.
Can be used for:
- Testing the gRPC service
- Building bot clients
- Integration with other services

Example Usage:
    >>> from apps.crypto.grpc_services.client import CryptoClient
    >>>
    >>> # Create client
    >>> client = CryptoClient('localhost:50051')
    >>>
    >>> # Get Bitcoin info
    >>> coin = client.get_coin('BTC')
    >>> print(f"BTC Price: ${coin.current_price_usd}")
    >>>
    >>> # List top coins
    >>> coins = client.list_top_coins(10)
    >>> for coin in coins:
    ...     print(f"{coin.symbol}: ${coin.current_price_usd}")
    >>>
    >>> # Stream prices in real-time
    >>> for update in client.stream_prices(['BTC', 'ETH'], interval=5):
    ...     print(f"{update.symbol}: ${update.price_usd}")
"""

import grpc
import logging
from typing import List, Optional, Iterator
from decimal import Decimal

# Import generated proto files
try:
    from apps.crypto.grpc_services.generated import crypto_service_pb2, crypto_service_pb2_grpc
    from google.protobuf.empty_pb2 import Empty
except ImportError as e:
    raise ImportError(
        "Proto files not generated. Run: python manage.py generate_proto\n"
        f"Missing: {e.name}"
    )

logger = logging.getLogger(__name__)


class CryptoClient:
    """
    Python client for CryptoService gRPC API.

    Features:
    - Synchronous API calls
    - Automatic error handling
    - Convenient methods for all operations
    - Real-time price streaming

    Example:
        >>> client = CryptoClient('localhost:50051')
        >>> coin = client.get_coin('BTC')
        >>> print(f"BTC: ${coin.current_price_usd}")
    """

    def __init__(self, address: str = 'localhost:50051', timeout: int = 10):
        """
        Initialize gRPC client.

        Args:
            address: gRPC server address (host:port)
            timeout: Default timeout for requests in seconds

        Example:
            >>> client = CryptoClient('localhost:50051')
        """
        self.address = address
        self.timeout = timeout
        self.channel = grpc.insecure_channel(address)
        self.stub = crypto_service_pb2_grpc.CryptoServiceStub(self.channel)

        logger.info(f"🔌 CryptoClient connected to {address}")

    def close(self):
        """Close gRPC channel."""
        self.channel.close()
        logger.info(f"🔌 CryptoClient disconnected from {self.address}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    # ========================================================================
    # Coin Operations
    # ========================================================================

    def get_coin(
        self,
        symbol: Optional[str] = None,
        coin_id: Optional[int] = None,
        slug: Optional[str] = None
    ) -> crypto_service_pb2.Coin:
        """
        Get coin by symbol, ID, or slug.

        Args:
            symbol: Coin symbol (e.g., 'BTC')
            coin_id: Coin database ID
            slug: Coin slug (e.g., 'bitcoin')

        Returns:
            Coin protobuf message

        Example:
            >>> client = CryptoClient()
            >>> btc = client.get_coin(symbol='BTC')
            >>> print(f"Bitcoin: ${btc.current_price_usd}")
        """
        request = crypto_service_pb2.GetCoinRequest()

        if symbol:
            request.symbol = symbol.upper()
        elif coin_id:
            request.id = coin_id
        elif slug:
            request.slug = slug.lower()
        else:
            raise ValueError("Must provide symbol, coin_id, or slug")

        try:
            response = self.stub.GetCoin(request, timeout=self.timeout)
            return response.coin
        except grpc.RpcError as e:
            logger.error(f"❌ GetCoin failed: {e.code()} - {e.details()}")
            raise

    def list_coins(
        self,
        page: int = 1,
        page_size: int = 20,
        active_only: bool = False,
        tradeable_only: bool = False,
        sort_by: crypto_service_pb2.SortBy = crypto_service_pb2.RANK,
        sort_order: crypto_service_pb2.SortOrder = crypto_service_pb2.ASC
    ) -> List[crypto_service_pb2.Coin]:
        """
        List coins with pagination and filtering.

        Args:
            page: Page number (starts at 1)
            page_size: Items per page (max 100)
            active_only: Only active coins
            tradeable_only: Only tradeable coins
            sort_by: Sort field
            sort_order: Sort direction

        Returns:
            List of Coin protobuf messages

        Example:
            >>> client = CryptoClient()
            >>> coins = client.list_coins(page=1, page_size=10, active_only=True)
            >>> for coin in coins:
            ...     print(f"{coin.symbol}: ${coin.current_price_usd}")
        """
        request = crypto_service_pb2.ListCoinsRequest(
            page=page,
            page_size=page_size,
            active_only=active_only,
            tradeable_only=tradeable_only,
            sort_by=sort_by,
            sort_order=sort_order,
        )

        try:
            response = self.stub.ListCoins(request, timeout=self.timeout)
            return list(response.coins)
        except grpc.RpcError as e:
            logger.error(f"❌ ListCoins failed: {e.code()} - {e.details()}")
            raise

    def search_coins(self, query: str, limit: int = 10) -> List[crypto_service_pb2.Coin]:
        """
        Search coins by name or symbol.

        Args:
            query: Search term
            limit: Max results (max 50)

        Returns:
            List of matching Coin protobuf messages

        Example:
            >>> client = CryptoClient()
            >>> results = client.search_coins('bitcoin')
            >>> print(f"Found {len(results)} coins")
        """
        request = crypto_service_pb2.SearchCoinsRequest(
            query=query,
            limit=limit,
        )

        try:
            response = self.stub.SearchCoins(request, timeout=self.timeout)
            return list(response.coins)
        except grpc.RpcError as e:
            logger.error(f"❌ SearchCoins failed: {e.code()} - {e.details()}")
            raise

    def list_top_coins(self, limit: int = 10) -> List[crypto_service_pb2.Coin]:
        """
        Get top coins by market cap.

        Args:
            limit: Number of coins (max 100)

        Returns:
            List of top Coin protobuf messages

        Example:
            >>> client = CryptoClient()
            >>> top_10 = client.list_top_coins(10)
            >>> for coin in top_10:
            ...     print(f"#{coin.rank} {coin.symbol}: ${coin.current_price_usd}")
        """
        request = crypto_service_pb2.GetTopCoinsRequest(limit=limit)

        try:
            response = self.stub.GetTopCoins(request, timeout=self.timeout)
            return list(response.coins)
        except grpc.RpcError as e:
            logger.error(f"❌ GetTopCoins failed: {e.code()} - {e.details()}")
            raise

    def stream_prices(
        self,
        symbols: List[str],
        interval: int = 5
    ) -> Iterator[crypto_service_pb2.PriceUpdate]:
        """
        Stream real-time price updates (blocking).

        Args:
            symbols: List of coin symbols to watch
            interval: Update interval in seconds

        Yields:
            PriceUpdate messages

        Example:
            >>> client = CryptoClient()
            >>> for update in client.stream_prices(['BTC', 'ETH'], interval=5):
            ...     print(f"{update.symbol}: ${update.price_usd} ({update.change_24h_percent}%)")
        """
        request = crypto_service_pb2.StreamPricesRequest(
            symbols=[s.upper() for s in symbols],
            interval_seconds=interval,
        )

        try:
            for update in self.stub.StreamPrices(request):
                yield update
        except grpc.RpcError as e:
            logger.error(f"❌ StreamPrices failed: {e.code()} - {e.details()}")
            raise

    # ========================================================================
    # Wallet Operations
    # ========================================================================

    def get_wallet(
        self,
        user_id: int,
        symbol: Optional[str] = None,
        coin_id: Optional[int] = None
    ) -> crypto_service_pb2.Wallet:
        """
        Get user's wallet for specific coin.

        Args:
            user_id: User ID
            symbol: Coin symbol (preferred)
            coin_id: Coin ID

        Returns:
            Wallet protobuf message

        Example:
            >>> client = CryptoClient()
            >>> wallet = client.get_wallet(user_id=1, symbol='BTC')
            >>> print(f"Balance: {wallet.balance} BTC (${wallet.value_usd})")
        """
        request = crypto_service_pb2.GetWalletRequest(user_id=user_id)

        if symbol:
            request.symbol = symbol.upper()
        elif coin_id:
            request.coin_id = coin_id
        else:
            raise ValueError("Must provide symbol or coin_id")

        try:
            response = self.stub.GetWallet(request, timeout=self.timeout)
            return response.wallet
        except grpc.RpcError as e:
            logger.error(f"❌ GetWallet failed: {e.code()} - {e.details()}")
            raise

    def list_wallets(
        self,
        user_id: int,
        exclude_zero_balance: bool = True
    ) -> List[crypto_service_pb2.Wallet]:
        """
        List all user wallets.

        Args:
            user_id: User ID
            exclude_zero_balance: Hide empty wallets

        Returns:
            List of Wallet protobuf messages

        Example:
            >>> client = CryptoClient()
            >>> wallets = client.list_wallets(user_id=1)
            >>> for wallet in wallets:
            ...     print(f"{wallet.symbol}: {wallet.balance} (${wallet.value_usd})")
        """
        request = crypto_service_pb2.ListWalletsRequest(
            user_id=user_id,
            exclude_zero_balance=exclude_zero_balance,
        )

        try:
            response = self.stub.ListWallets(request, timeout=self.timeout)
            return list(response.wallets)
        except grpc.RpcError as e:
            logger.error(f"❌ ListWallets failed: {e.code()} - {e.details()}")
            raise

    def get_portfolio(self, user_id: int) -> crypto_service_pb2.PortfolioResponse:
        """
        Get portfolio summary.

        Args:
            user_id: User ID

        Returns:
            PortfolioResponse with complete portfolio data

        Example:
            >>> client = CryptoClient()
            >>> portfolio = client.get_portfolio(user_id=1)
            >>> print(f"Total: ${portfolio.total_value_usd}")
            >>> print(f"24h Change: {portfolio.total_change_24h_percent}%")
            >>> for holding in portfolio.holdings:
            ...     print(f"  {holding.symbol}: ${holding.value_usd} ({holding.percentage}%)")
        """
        request = crypto_service_pb2.GetPortfolioRequest(user_id=user_id)

        try:
            return self.stub.GetPortfolio(request, timeout=self.timeout)
        except grpc.RpcError as e:
            logger.error(f"❌ GetPortfolio failed: {e.code()} - {e.details()}")
            raise

    def deposit(
        self,
        user_id: int,
        symbol: str,
        amount: str,
        transaction_id: str = ''
    ) -> crypto_service_pb2.Wallet:
        """
        Deposit funds to wallet.

        Args:
            user_id: User ID
            symbol: Coin symbol
            amount: Amount as string (for precision)
            transaction_id: External transaction ID

        Returns:
            Updated Wallet protobuf message

        Example:
            >>> client = CryptoClient()
            >>> wallet = client.deposit(
            ...     user_id=1,
            ...     symbol='BTC',
            ...     amount='0.5',
            ...     transaction_id='tx123'
            ... )
            >>> print(f"New balance: {wallet.balance} BTC")
        """
        request = crypto_service_pb2.DepositRequest(
            user_id=user_id,
            symbol=symbol.upper(),
            amount=amount,
            transaction_id=transaction_id,
        )

        try:
            response = self.stub.Deposit(request, timeout=self.timeout)
            return response.wallet
        except grpc.RpcError as e:
            logger.error(f"❌ Deposit failed: {e.code()} - {e.details()}")
            raise

    def withdraw(
        self,
        user_id: int,
        symbol: str,
        amount: str,
        destination_address: str
    ) -> crypto_service_pb2.Wallet:
        """
        Withdraw funds from wallet.

        Args:
            user_id: User ID
            symbol: Coin symbol
            amount: Amount as string (for precision)
            destination_address: Withdrawal address

        Returns:
            Updated Wallet protobuf message

        Example:
            >>> client = CryptoClient()
            >>> wallet = client.withdraw(
            ...     user_id=1,
            ...     symbol='BTC',
            ...     amount='0.1',
            ...     destination_address='1A1zP1...'
            ... )
            >>> print(f"New balance: {wallet.balance} BTC")
        """
        request = crypto_service_pb2.WithdrawRequest(
            user_id=user_id,
            symbol=symbol.upper(),
            amount=amount,
            destination_address=destination_address,
        )

        try:
            response = self.stub.Withdraw(request, timeout=self.timeout)
            return response.wallet
        except grpc.RpcError as e:
            logger.error(f"❌ Withdraw failed: {e.code()} - {e.details()}")
            raise

    def transfer(
        self,
        from_user_id: int,
        to_user_id: int,
        symbol: str,
        amount: str,
        note: str = ''
    ) -> crypto_service_pb2.TransferResponse:
        """
        Transfer funds between users.

        Args:
            from_user_id: Sender user ID
            to_user_id: Recipient user ID
            symbol: Coin symbol
            amount: Amount as string (for precision)
            note: Optional transfer note

        Returns:
            TransferResponse with both updated wallets

        Example:
            >>> client = CryptoClient()
            >>> transfer = client.transfer(
            ...     from_user_id=1,
            ...     to_user_id=2,
            ...     symbol='BTC',
            ...     amount='0.01',
            ...     note='Payment'
            ... )
            >>> print(f"Transaction ID: {transfer.transaction_id}")
            >>> print(f"From: {transfer.from_wallet.balance} BTC")
            >>> print(f"To: {transfer.to_wallet.balance} BTC")
        """
        request = crypto_service_pb2.TransferRequest(
            from_user_id=from_user_id,
            to_user_id=to_user_id,
            symbol=symbol.upper(),
            amount=amount,
            note=note,
        )

        try:
            return self.stub.Transfer(request, timeout=self.timeout)
        except grpc.RpcError as e:
            logger.error(f"❌ Transfer failed: {e.code()} - {e.details()}")
            raise

    # ========================================================================
    # Market Statistics
    # ========================================================================

    def get_market_stats(self) -> crypto_service_pb2.MarketStatsResponse:
        """
        Get overall market statistics.

        Returns:
            MarketStatsResponse with market data

        Example:
            >>> client = CryptoClient()
            >>> stats = client.get_market_stats()
            >>> print(f"Total Market Cap: ${stats.total_market_cap_usd}")
            >>> print(f"24h Volume: ${stats.total_volume_24h_usd}")
            >>> print(f"Coins Up: {stats.coins_up_24h}")
            >>> print(f"Coins Down: {stats.coins_down_24h}")
        """
        try:
            return self.stub.GetMarketStats(Empty(), timeout=self.timeout)
        except grpc.RpcError as e:
            logger.error(f"❌ GetMarketStats failed: {e.code()} - {e.details()}")
            raise

    def get_trending_coins(
        self,
        trending_type: crypto_service_pb2.TrendingType = crypto_service_pb2.TOP_GAINERS,
        limit: int = 10
    ) -> List[crypto_service_pb2.Coin]:
        """
        Get trending coins (gainers/losers/most traded).

        Args:
            trending_type: Type of trending (TOP_GAINERS, TOP_LOSERS, MOST_TRADED)
            limit: Number of coins (max 50)

        Returns:
            List of trending Coin protobuf messages

        Example:
            >>> client = CryptoClient()
            >>> # Top gainers
            >>> gainers = client.get_trending_coins(
            ...     trending_type=crypto_service_pb2.TOP_GAINERS,
            ...     limit=10
            ... )
            >>> for coin in gainers:
            ...     print(f"{coin.symbol}: +{coin.price_change_24h_percent}%")
        """
        request = crypto_service_pb2.GetTrendingCoinsRequest(
            type=trending_type,
            limit=limit,
        )

        try:
            response = self.stub.GetTrendingCoins(request, timeout=self.timeout)
            return list(response.coins)
        except grpc.RpcError as e:
            logger.error(f"❌ GetTrendingCoins failed: {e.code()} - {e.details()}")
            raise


# ============================================================================
# Example Usage / Testing
# ============================================================================

def main():
    """
    Example usage of CryptoClient.

    Run with: python -m apps.crypto.grpc_services.client
    """
    # Create client with context manager
    with CryptoClient('localhost:50051') as client:
        print("=" * 60)
        print("CryptoService Client Demo")
        print("=" * 60)

        # Get Bitcoin
        print("\n1. Get Bitcoin info:")
        btc = client.get_coin(symbol='BTC')
        print(f"   {btc.symbol} - {btc.name}")
        print(f"   Price: ${btc.current_price_usd}")
        print(f"   24h Change: {btc.price_change_24h_percent}%")

        # List top coins
        print("\n2. Top 5 coins by market cap:")
        top_coins = client.list_top_coins(5)
        for coin in top_coins:
            print(f"   #{coin.rank} {coin.symbol}: ${coin.current_price_usd}")

        # Search
        print("\n3. Search for 'bit' coins:")
        results = client.search_coins('bit', limit=3)
        for coin in results:
            print(f"   {coin.symbol} - {coin.name}")

        # Market stats
        print("\n4. Market statistics:")
        stats = client.get_market_stats()
        print(f"   Total Market Cap: ${stats.total_market_cap_usd}")
        print(f"   Coins Up: {stats.coins_up_24h}")
        print(f"   Coins Down: {stats.coins_down_24h}")

        # Portfolio (example user_id=1)
        print("\n5. Portfolio for user 1:")
        try:
            portfolio = client.get_portfolio(user_id=1)
            print(f"   Total Value: ${portfolio.total_value_usd}")
            print(f"   Coins: {portfolio.coins_count}")
            for holding in portfolio.holdings[:3]:  # Show first 3
                print(f"   - {holding.symbol}: ${holding.value_usd} ({holding.percentage}%)")
        except grpc.RpcError as e:
            print(f"   No portfolio found (user may not exist)")

        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("=" * 60)


if __name__ == '__main__':
    main()
