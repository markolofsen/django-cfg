# Crypto gRPC Service - Practical Examples

Real-world usage examples for the CryptoService gRPC API.

## Table of Contents

- [Basic Operations](#basic-operations)
- [Wallet Management](#wallet-management)
- [Portfolio Tracking](#portfolio-tracking)
- [Real-time Price Monitoring](#real-time-price-monitoring)
- [Market Analysis](#market-analysis)
- [Trading Bot Integration](#trading-bot-integration)
- [Error Handling](#error-handling)

## Basic Operations

### Get Single Coin

```python
from apps.crypto.grpc_services.client import CryptoClient

client = CryptoClient('localhost:50051')

# Get by symbol (recommended)
btc = client.get_coin(symbol='BTC')
print(f"""
Bitcoin Information:
- Price: ${btc.current_price_usd}
- Market Cap: ${btc.market_cap_usd}
- 24h Change: {btc.price_change_24h_percent}%
- Rank: #{btc.rank}
""")

# Get by ID
coin = client.get_coin(coin_id=1)

# Get by slug
eth = client.get_coin(slug='ethereum')
```

### List Top Cryptocurrencies

```python
# Get top 20 by market cap
top_coins = client.list_top_coins(limit=20)

for coin in top_coins:
    change_icon = "📈" if coin.is_price_up_24h else "📉"
    print(f"{change_icon} #{coin.rank} {coin.symbol}: ${coin.current_price_usd}")
```

### Search Coins

```python
# Search by name or symbol
results = client.search_coins('bit', limit=10)

print(f"Found {len(results)} coins matching 'bit':")
for coin in results:
    print(f"  - {coin.symbol} ({coin.name})")

# Output:
# Found 3 coins matching 'bit':
#   - BTC (Bitcoin)
#   - BCH (Bitcoin Cash)
#   - BSV (Bitcoin SV)
```

### Paginated Listing

```python
# Get coins with pagination
page_1 = client.list_coins(
    page=1,
    page_size=20,
    active_only=True,
    tradeable_only=True,
    sort_by=crypto_service_pb2.MARKET_CAP,
    sort_order=crypto_service_pb2.DESC
)

print(f"Page 1 of {page_1.total_pages}")
print(f"Total coins: {page_1.total_count}")

for coin in page_1.coins:
    print(f"{coin.symbol}: ${coin.current_price_usd}")
```

## Wallet Management

### Get User Wallet

```python
# Get Bitcoin wallet for user 1
wallet = client.get_wallet(user_id=1, symbol='BTC')

print(f"""
BTC Wallet:
- Balance: {wallet.balance} BTC
- Locked: {wallet.locked_balance} BTC
- Total: {wallet.total_balance} BTC
- Value: ${wallet.value_usd}
""")
```

### List All Wallets

```python
# Get all non-empty wallets
wallets = client.list_wallets(
    user_id=1,
    exclude_zero_balance=True
)

total_value = Decimal('0')
for wallet in wallets:
    print(f"{wallet.symbol}: {wallet.balance} (${wallet.value_usd})")
    total_value += Decimal(wallet.value_usd)

print(f"\nTotal Portfolio Value: ${total_value}")
```

### Deposit Funds

```python
# Deposit 0.5 BTC
wallet = client.deposit(
    user_id=1,
    symbol='BTC',
    amount='0.5',
    transaction_id='tx_abc123'
)

print(f"Deposited successfully!")
print(f"New balance: {wallet.balance} BTC")
```

### Withdraw Funds

```python
try:
    wallet = client.withdraw(
        user_id=1,
        symbol='BTC',
        amount='0.1',
        destination_address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
    )
    print(f"Withdrawal successful!")
    print(f"Remaining balance: {wallet.balance} BTC")
except grpc.RpcError as e:
    print(f"Withdrawal failed: {e.details()}")
```

### Transfer Between Users

```python
# Transfer 0.01 BTC from user 1 to user 2
transfer = client.transfer(
    from_user_id=1,
    to_user_id=2,
    symbol='BTC',
    amount='0.01',
    note='Payment for services'
)

print(f"Transfer complete!")
print(f"Transaction ID: {transfer.transaction_id}")
print(f"Sender balance: {transfer.from_wallet.balance} BTC")
print(f"Recipient balance: {transfer.to_wallet.balance} BTC")
```

## Portfolio Tracking

### Complete Portfolio Overview

```python
portfolio = client.get_portfolio(user_id=1)

# Summary
print(f"""
Portfolio Summary:
- Total Value: ${portfolio.total_value_usd}
- 24h Change: ${portfolio.total_change_24h_usd} ({portfolio.total_change_24h_percent}%)
- Number of Coins: {portfolio.coins_count}
""")

# Holdings
print("\nHoldings:")
for holding in portfolio.holdings:
    print(f"""
{holding.symbol} - {holding.coin_name}
  Balance: {holding.balance}
  Value: ${holding.value_usd}
  Allocation: {holding.percentage}%
  24h Change: {holding.change_24h_percent}%
""")
```

### Portfolio Performance Tracker

```python
import time
from decimal import Decimal

def track_portfolio(user_id: int, interval: int = 60):
    """Track portfolio performance over time."""
    client = CryptoClient()
    previous_value = None

    while True:
        portfolio = client.get_portfolio(user_id=user_id)
        current_value = Decimal(portfolio.total_value_usd)

        print(f"[{portfolio.calculated_at}]")
        print(f"Portfolio Value: ${current_value}")

        if previous_value:
            change = current_value - previous_value
            change_pct = (change / previous_value * 100) if previous_value > 0 else 0
            print(f"Change: ${change} ({change_pct:.2f}%)")

        previous_value = current_value
        time.sleep(interval)

# Track every minute
track_portfolio(user_id=1, interval=60)
```

## Real-time Price Monitoring

### Simple Price Stream

```python
# Stream prices for BTC and ETH
for update in client.stream_prices(['BTC', 'ETH'], interval=5):
    timestamp = update.timestamp.ToDatetime()
    print(f"[{timestamp}] {update.symbol}: ${update.price_usd} ({update.change_24h_percent}%)")
```

### Price Alert System

```python
from decimal import Decimal

def price_alert_monitor(symbol: str, target_price: Decimal, interval: int = 5):
    """
    Monitor price and alert when target is reached.

    Example:
        # Alert when BTC reaches $100,000
        price_alert_monitor('BTC', Decimal('100000'))
    """
    client = CryptoClient()
    print(f"🔔 Monitoring {symbol} for target price: ${target_price}")

    for update in client.stream_prices([symbol], interval=interval):
        current_price = Decimal(update.price_usd)
        print(f"Current {symbol} price: ${current_price}")

        if current_price >= target_price:
            print(f"🎯 TARGET REACHED! {symbol} is now ${current_price}")
            # Send notification (email, Telegram, etc.)
            break

# Monitor BTC
price_alert_monitor('BTC', Decimal('100000'))
```

### Multi-Coin Price Dashboard

```python
from collections import defaultdict
from datetime import datetime

def price_dashboard(symbols: List[str], interval: int = 10):
    """Real-time price dashboard for multiple coins."""
    client = CryptoClient()
    prices = defaultdict(list)

    for update in client.stream_prices(symbols, interval=interval):
        # Store price history
        prices[update.symbol].append({
            'price': Decimal(update.price_usd),
            'change': Decimal(update.change_24h_percent),
            'time': datetime.now()
        })

        # Clear screen and display dashboard
        print("\033[2J\033[H")  # Clear screen
        print("=" * 60)
        print(f"Crypto Price Dashboard - {datetime.now()}")
        print("=" * 60)

        for symbol in symbols:
            if symbol in prices:
                latest = prices[symbol][-1]
                change_icon = "📈" if latest['change'] > 0 else "📉"
                print(f"{change_icon} {symbol}: ${latest['price']} ({latest['change']}%)")

# Monitor top coins
price_dashboard(['BTC', 'ETH', 'BNB', 'SOL', 'ADA'], interval=10)
```

## Market Analysis

### Market Overview

```python
stats = client.get_market_stats()

print(f"""
📊 Market Statistics:
- Total Market Cap: ${stats.total_market_cap_usd}
- 24h Volume: ${stats.total_volume_24h_usd}
- Active Coins: {stats.active_coins_count}
- Coins Up: {stats.coins_up_24h} ✅
- Coins Down: {stats.coins_down_24h} ❌
- Average Change: {stats.average_change_24h}%
""")
```

### Top Gainers & Losers

```python
# Get top gainers
gainers = client.get_trending_coins(
    trending_type=crypto_service_pb2.TOP_GAINERS,
    limit=10
)

print("📈 Top 10 Gainers (24h):")
for coin in gainers:
    print(f"  {coin.symbol}: +{coin.price_change_24h_percent}% (${coin.current_price_usd})")

# Get top losers
losers = client.get_trending_coins(
    trending_type=crypto_service_pb2.TOP_LOSERS,
    limit=10
)

print("\n📉 Top 10 Losers (24h):")
for coin in losers:
    print(f"  {coin.symbol}: {coin.price_change_24h_percent}% (${coin.current_price_usd})")
```

### Most Traded Coins

```python
most_traded = client.get_trending_coins(
    trending_type=crypto_service_pb2.MOST_TRADED,
    limit=10
)

print("💰 Most Traded Coins (24h Volume):")
for coin in most_traded:
    print(f"  {coin.symbol}: ${coin.volume_24h_usd}")
```

### Daily Market Report

```python
def generate_daily_report():
    """Generate comprehensive daily market report."""
    client = CryptoClient()

    # Market stats
    stats = client.get_market_stats()

    # Top coins
    top_10 = client.list_top_coins(10)

    # Trending
    gainers = client.get_trending_coins(crypto_service_pb2.TOP_GAINERS, 5)
    losers = client.get_trending_coins(crypto_service_pb2.TOP_LOSERS, 5)

    # Generate report
    report = f"""
    ═══════════════════════════════════════
    📊 Daily Crypto Market Report
    {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ═══════════════════════════════════════

    Market Overview:
    ----------------
    Total Market Cap: ${stats.total_market_cap_usd}
    24h Volume: ${stats.total_volume_24h_usd}
    Coins Up: {stats.coins_up_24h} | Down: {stats.coins_down_24h}

    Top 10 by Market Cap:
    ---------------------
    """

    for coin in top_10:
        change_icon = "📈" if coin.is_price_up_24h else "📉"
        report += f"\n{change_icon} #{coin.rank} {coin.symbol}: ${coin.current_price_usd}"

    report += "\n\n    Top 5 Gainers:\n    --------------"
    for coin in gainers:
        report += f"\n    ✅ {coin.symbol}: +{coin.price_change_24h_percent}%"

    report += "\n\n    Top 5 Losers:\n    -------------"
    for coin in losers:
        report += f"\n    ❌ {coin.symbol}: {coin.price_change_24h_percent}%"

    report += "\n\n    ═══════════════════════════════════════"

    print(report)
    return report

# Generate and save report
report = generate_daily_report()
with open('daily_report.txt', 'w') as f:
    f.write(report)
```

## Trading Bot Integration

### Simple Trading Bot

```python
class SimpleTradingBot:
    """
    Simple trading bot using CryptoService.

    Strategy: Buy when price drops 5%, sell when it rises 5%.
    """

    def __init__(self, user_id: int, symbol: str, base_amount: str):
        self.client = CryptoClient()
        self.user_id = user_id
        self.symbol = symbol
        self.base_amount = Decimal(base_amount)
        self.entry_price = None

    def run(self):
        """Run trading bot."""
        print(f"🤖 Trading Bot Started: {self.symbol}")

        for update in self.client.stream_prices([self.symbol], interval=10):
            current_price = Decimal(update.price_usd)

            if self.entry_price is None:
                # Initial price
                self.entry_price = current_price
                print(f"📍 Entry price set: ${current_price}")
                continue

            # Calculate change
            change_pct = (current_price - self.entry_price) / self.entry_price * 100

            print(f"💹 {self.symbol}: ${current_price} ({change_pct:+.2f}%)")

            # Buy signal (5% drop)
            if change_pct <= -5:
                self.execute_buy(current_price)
                self.entry_price = current_price

            # Sell signal (5% rise)
            elif change_pct >= 5:
                self.execute_sell(current_price)
                self.entry_price = current_price

    def execute_buy(self, price: Decimal):
        """Execute buy order."""
        print(f"🟢 BUY SIGNAL: ${price}")
        try:
            wallet = self.client.deposit(
                user_id=self.user_id,
                symbol=self.symbol,
                amount=str(self.base_amount),
                transaction_id=f"buy_{int(time.time())}"
            )
            print(f"✅ Bought {self.base_amount} {self.symbol}")
            print(f"   Balance: {wallet.balance}")
        except Exception as e:
            print(f"❌ Buy failed: {e}")

    def execute_sell(self, price: Decimal):
        """Execute sell order."""
        print(f"🔴 SELL SIGNAL: ${price}")
        try:
            wallet = self.client.withdraw(
                user_id=self.user_id,
                symbol=self.symbol,
                amount=str(self.base_amount),
                destination_address="exchange_wallet"
            )
            print(f"✅ Sold {self.base_amount} {self.symbol}")
            print(f"   Balance: {wallet.balance}")
        except Exception as e:
            print(f"❌ Sell failed: {e}")

# Run bot
bot = SimpleTradingBot(user_id=1, symbol='BTC', base_amount='0.01')
bot.run()
```

## Error Handling

### Proper Error Handling

```python
import grpc
from google.protobuf.json_format import MessageToDict

def safe_get_coin(symbol: str):
    """Get coin with proper error handling."""
    client = CryptoClient()

    try:
        coin = client.get_coin(symbol=symbol)
        return MessageToDict(coin)

    except grpc.RpcError as e:
        if e.code() == grpc.StatusCode.NOT_FOUND:
            print(f"Coin {symbol} not found")
            return None
        elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
            print(f"Invalid argument: {e.details()}")
            return None
        elif e.code() == grpc.StatusCode.UNAVAILABLE:
            print("Service unavailable, retrying...")
            # Implement retry logic
            return None
        else:
            print(f"Unexpected error: {e.code()} - {e.details()}")
            raise

    except Exception as e:
        print(f"Client error: {e}")
        raise

# Usage
coin_data = safe_get_coin('BTC')
if coin_data:
    print(f"Got coin: {coin_data['symbol']}")
```

### Retry Logic

```python
import time
from typing import Optional, Callable, Any

def retry_on_failure(
    func: Callable,
    max_retries: int = 3,
    delay: int = 1,
    backoff: int = 2
) -> Optional[Any]:
    """
    Retry function on failure with exponential backoff.

    Args:
        func: Function to retry
        max_retries: Maximum number of retries
        delay: Initial delay in seconds
        backoff: Backoff multiplier

    Returns:
        Function result or None if all retries failed
    """
    for attempt in range(max_retries):
        try:
            return func()
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.UNAVAILABLE:
                if attempt < max_retries - 1:
                    wait_time = delay * (backoff ** attempt)
                    print(f"Retry {attempt + 1}/{max_retries} in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"All retries failed")
                    raise
            else:
                # Don't retry other errors
                raise

# Usage
client = CryptoClient()
coin = retry_on_failure(lambda: client.get_coin(symbol='BTC'))
```

### Connection Management

```python
class ManagedCryptoClient:
    """Client with automatic reconnection."""

    def __init__(self, address: str = 'localhost:50051'):
        self.address = address
        self.client = None
        self.connect()

    def connect(self):
        """Connect to gRPC server."""
        try:
            self.client = CryptoClient(self.address)
            print(f"✅ Connected to {self.address}")
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            raise

    def reconnect(self):
        """Reconnect to server."""
        print("Reconnecting...")
        try:
            if self.client:
                self.client.close()
        except:
            pass
        self.connect()

    def call_with_reconnect(self, method: str, *args, **kwargs):
        """Call method with automatic reconnection."""
        max_attempts = 3

        for attempt in range(max_attempts):
            try:
                func = getattr(self.client, method)
                return func(*args, **kwargs)

            except grpc.RpcError as e:
                if e.code() == grpc.StatusCode.UNAVAILABLE:
                    if attempt < max_attempts - 1:
                        print(f"Connection lost, reconnecting...")
                        self.reconnect()
                    else:
                        raise
                else:
                    raise

# Usage
managed_client = ManagedCryptoClient()
coin = managed_client.call_with_reconnect('get_coin', symbol='BTC')
```

## Tips & Tricks

### Batch Operations

```python
def get_multiple_coins(symbols: List[str]):
    """Get multiple coins efficiently."""
    client = CryptoClient()
    coins = []

    for symbol in symbols:
        try:
            coin = client.get_coin(symbol=symbol)
            coins.append(coin)
        except grpc.RpcError as e:
            print(f"Failed to get {symbol}: {e.details()}")

    return coins

# Get multiple coins
coins = get_multiple_coins(['BTC', 'ETH', 'BNB', 'SOL'])
```

### Caching Results

```python
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def get_coin_cached(symbol: str, cache_time: int):
    """Get coin with caching (cache_time is used to invalidate cache)."""
    client = CryptoClient()
    return client.get_coin(symbol=symbol)

# Usage (cache invalidates every 60 seconds)
current_minute = int(time.time() / 60)
btc = get_coin_cached('BTC', current_minute)
```

## Next Steps

- See [README.md](./README.md) for setup guide
- Check [API.md](./API.md) for complete API reference
- Review [proto file](../../../proto/crypto_service.proto) for message definitions
