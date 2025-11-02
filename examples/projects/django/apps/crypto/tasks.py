"""
RQ Background Tasks for Crypto App.

These are demo tasks that can be scheduled and executed by Django-RQ.
In production, these would integrate with real APIs (CoinGecko, CoinMarketCap, etc.).
"""

import logging
import random
from decimal import Decimal
from typing import Optional

# NOTE: Django models and utilities imported lazily inside functions
# to avoid Django settings initialization issues when RQ imports this module

logger = logging.getLogger(__name__)


def update_coin_prices(limit: int = 100, verbosity: int = 0, days: Optional[int] = None, force: bool = False) -> dict:
    """
    Update cryptocurrency prices for active coins.

    In production, this would fetch real data from CoinGecko/CoinMarketCap API.
    For demo purposes, it generates realistic price movements.

    Args:
        limit: Maximum number of coins to update
        verbosity: Logging verbosity (0=quiet, 1=normal, 2=verbose)
        days: Days of historical data to update (not used in demo)
        force: Force update even if recently updated

    Returns:
        dict with update statistics
    """
    # Lazy imports to avoid Django settings initialization issues
    from django.utils import timezone
    from apps.crypto.models import Coin

    if verbosity > 0:
        logger.info(f"Starting coin price update (limit={limit}, force={force})")

    # Get active coins to update
    queryset = Coin.objects.filter(is_active=True)[:limit]

    if not queryset.exists():
        logger.warning("No active coins found to update")
        return {
            "success": True,
            "updated": 0,
            "skipped": 0,
            "failed": 0,
            "message": "No active coins to update"
        }

    updated_count = 0
    skipped_count = 0
    failed_count = 0

    for coin in queryset:
        try:
            # Demo: Generate realistic price movements
            # In production, this would be: price = fetch_from_api(coin.symbol)

            # Generate random price change between -10% and +10%
            price_change_pct = Decimal(str(random.uniform(-0.10, 0.10)))
            old_price = coin.current_price_usd

            if old_price > 0:
                new_price = old_price * (1 + price_change_pct)
            else:
                # If no price set, generate a random starting price
                new_price = Decimal(str(random.uniform(0.01, 50000)))

            # Update coin data
            coin.current_price_usd = new_price
            coin.price_change_24h_percent = price_change_pct * 100

            # Generate random volume and market cap
            coin.volume_24h_usd = new_price * Decimal(str(random.randint(1000000, 100000000)))
            coin.market_cap_usd = new_price * Decimal(str(random.randint(1000000, 1000000000)))

            coin.save(update_fields=[
                'current_price_usd',
                'price_change_24h_percent',
                'volume_24h_usd',
                'market_cap_usd',
                'updated_at'
            ])

            updated_count += 1

            if verbosity >= 2:
                logger.info(
                    f"✓ Updated {coin.symbol}: "
                    f"${old_price:.2f} → ${new_price:.2f} "
                    f"({price_change_pct * 100:+.2f}%)"
                )

        except Exception as e:
            failed_count += 1
            logger.error(f"Failed to update {coin.symbol}: {e}")

    result = {
        "success": True,
        "updated": updated_count,
        "skipped": skipped_count,
        "failed": failed_count,
        "timestamp": timezone.now().isoformat(),
        "message": f"Successfully updated {updated_count} coins"
    }

    if verbosity > 0:
        logger.info(
            f"Price update completed: {updated_count} updated, "
            f"{skipped_count} skipped, {failed_count} failed"
        )

    return result


def import_coins(source: str = "demo", batch_size: int = 10) -> dict:
    """
    Import new cryptocurrency coins.

    In production, this would fetch data from external APIs or CSV files.
    For demo purposes, it creates sample coins.

    Args:
        source: Data source (demo, api, csv)
        batch_size: Number of coins to import in this batch

    Returns:
        dict with import statistics
    """
    # Lazy imports to avoid Django settings initialization issues
    from django.utils import timezone
    from apps.crypto.models import Coin

    logger.info(f"Starting coin import from {source} (batch_size={batch_size})")

    # Demo coin data
    demo_coins = [
        {"symbol": "BTC", "name": "Bitcoin", "rank": 1},
        {"symbol": "ETH", "name": "Ethereum", "rank": 2},
        {"symbol": "BNB", "name": "Binance Coin", "rank": 3},
        {"symbol": "SOL", "name": "Solana", "rank": 4},
        {"symbol": "XRP", "name": "Ripple", "rank": 5},
        {"symbol": "ADA", "name": "Cardano", "rank": 6},
        {"symbol": "DOGE", "name": "Dogecoin", "rank": 7},
        {"symbol": "TRX", "name": "TRON", "rank": 8},
        {"symbol": "AVAX", "name": "Avalanche", "rank": 9},
        {"symbol": "DOT", "name": "Polkadot", "rank": 10},
    ]

    imported_count = 0
    updated_count = 0
    skipped_count = 0

    for coin_data in demo_coins[:batch_size]:
        symbol = coin_data["symbol"]

        # Check if coin already exists
        coin, created = Coin.objects.get_or_create(
            symbol=symbol,
            defaults={
                "name": coin_data["name"],
                "slug": coin_data["name"].lower().replace(" ", "-"),
                "rank": coin_data["rank"],
                "is_active": True,
                "is_tradeable": True,
                "current_price_usd": Decimal(str(random.uniform(0.01, 50000))),
                "market_cap_usd": Decimal(str(random.randint(1000000, 1000000000))),
                "volume_24h_usd": Decimal(str(random.randint(1000000, 100000000))),
            }
        )

        if created:
            imported_count += 1
            logger.info(f"✓ Imported new coin: {symbol} - {coin_data['name']}")
        else:
            # Update existing coin
            coin.name = coin_data["name"]
            coin.rank = coin_data["rank"]
            coin.save(update_fields=['name', 'rank', 'updated_at'])
            updated_count += 1
            logger.info(f"↻ Updated existing coin: {symbol}")

    result = {
        "success": True,
        "imported": imported_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "timestamp": timezone.now().isoformat(),
        "message": f"Imported {imported_count} new coins, updated {updated_count}"
    }

    logger.info(
        f"Import completed: {imported_count} imported, "
        f"{updated_count} updated, {skipped_count} skipped"
    )

    return result


def generate_report(report_type: str = "daily") -> dict:
    """
    Generate cryptocurrency market report.

    Collects statistics and generates insights about the crypto market.
    In production, this could send emails, store in DB, or export to PDF.

    Args:
        report_type: Type of report (daily, weekly, monthly)

    Returns:
        dict with report data
    """
    # Lazy imports to avoid Django settings initialization issues
    from django.utils import timezone
    from django.db.models import Count, Avg, Sum
    from apps.crypto.models import Coin

    logger.info(f"Generating {report_type} crypto market report")

    # Get statistics
    total_coins = Coin.objects.filter(is_active=True).count()

    if total_coins == 0:
        logger.warning("No coins found for report generation")
        return {
            "success": False,
            "message": "No coins available for reporting"
        }

    # Calculate aggregate statistics
    stats = Coin.objects.filter(is_active=True).aggregate(
        avg_price_change_24h=Avg('price_change_24h_percent'),
        total_volume_24h=Sum('volume_24h_usd'),
        total_market_cap=Sum('market_cap_usd'),
    )

    # Get top gainers and losers
    top_gainers = list(
        Coin.objects.filter(is_active=True)
        .order_by('-price_change_24h_percent')[:5]
        .values('symbol', 'name', 'price_change_24h_percent', 'current_price_usd')
    )

    top_losers = list(
        Coin.objects.filter(is_active=True)
        .order_by('price_change_24h_percent')[:5]
        .values('symbol', 'name', 'price_change_24h_percent', 'current_price_usd')
    )

    # Get top by market cap
    top_by_market_cap = list(
        Coin.objects.filter(is_active=True)
        .order_by('-market_cap_usd')[:10]
        .values('symbol', 'name', 'market_cap_usd', 'current_price_usd')
    )

    report = {
        "success": True,
        "report_type": report_type,
        "generated_at": timezone.now().isoformat(),
        "summary": {
            "total_coins": total_coins,
            "avg_price_change_24h": float(stats['avg_price_change_24h'] or 0),
            "total_volume_24h": float(stats['total_volume_24h'] or 0),
            "total_market_cap": float(stats['total_market_cap'] or 0),
        },
        "top_gainers": top_gainers,
        "top_losers": top_losers,
        "top_by_market_cap": top_by_market_cap,
    }

    logger.info(
        f"Report generated: {total_coins} coins, "
        f"avg 24h change: {stats['avg_price_change_24h']:.2f}%"
    )

    # In production, you could:
    # - Send email with report
    # - Store in database
    # - Export to PDF
    # - Send to Telegram/Slack

    return report
