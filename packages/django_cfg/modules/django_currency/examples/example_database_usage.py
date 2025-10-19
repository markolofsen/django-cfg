"""
Example usage of the database loader for populating currency data.
"""

import logging

from .database_loader import (
    CurrencyDatabaseLoader,
    DatabaseLoaderConfig,
    create_database_loader,
    load_currencies_to_database_format,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(name)s:%(levelname)s: %(message)s')


def example_basic_usage():
    """Basic example of using the database loader."""
    print("🔄 Creating database loader...")

    # Create loader with default settings
    loader = create_database_loader(
        max_cryptocurrencies=100,  # Limit to top 100 cryptos
        max_fiat_currencies=30,    # Top 30 fiat currencies
        min_market_cap_usd=10_000_000,  # 10M USD minimum
        coingecko_delay=2.0        # 2 second delay between requests
    )

    # Get statistics
    print("📊 Statistics:")
    stats = loader.get_statistics()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n🪙 Building currency database data...")

    # Build complete currency data
    currencies = loader.build_currency_database_data()

    print(f"\n✅ Successfully loaded {len(currencies)} currencies")

    # Show sample data
    print("\n📋 Sample currencies:")
    for i, currency in enumerate(currencies[:10]):
        print(f"   {i+1}. {currency.code} ({currency.currency_type}): "
              f"{currency.name} = ${currency.usd_rate:.6f}")

    return currencies


def example_django_integration():
    """Example of how to integrate with Django ORM."""
    print("🔄 Loading currencies in Django format...")

    # Get currencies in Django-ready format
    currency_dicts = load_currencies_to_database_format()

    print(f"✅ Ready to insert {len(currency_dicts)} currencies into Django ORM")

    # This is how you would use it in Django:
    print("\n💡 Django integration example:")
    print("""
    # In your Django management command or view:
    from django_cfg.modules.django_currency.database_loader import load_currencies_to_database_format
    from django_cfg.apps.payments.models import Currency
    
    # Load currency data
    currency_data = load_currencies_to_database_format()
    
    # Bulk create currencies
    currencies_to_create = []
    for data in currency_data:
        currency = Currency(**data)
        currencies_to_create.append(currency)
    
    # Insert into database
    Currency.objects.bulk_create(currencies_to_create, ignore_conflicts=True)
    print(f"Inserted {len(currencies_to_create)} currencies")
    """)

    return currency_dicts


def example_advanced_config():
    """Example with advanced configuration."""
    print("🔧 Advanced configuration example...")

    # Custom configuration
    config = DatabaseLoaderConfig(
        # Rate limiting
        coingecko_delay=3.0,           # Slower requests for stability
        yfinance_delay=1.0,
        max_requests_per_minute=20,    # Conservative rate limit

        # Limits
        max_cryptocurrencies=50,       # Smaller set
        max_fiat_currencies=20,

        # Filtering
        min_market_cap_usd=50_000_000, # Higher threshold - 50M USD
        exclude_stablecoins=True,      # Skip stablecoins

        # Cache
        cache_ttl_hours=12            # Cache for 12 hours
    )

    loader = CurrencyDatabaseLoader(config)

    print("📊 Configuration:")
    print(f"   Max cryptocurrencies: {config.max_cryptocurrencies}")
    print(f"   Min market cap: ${config.min_market_cap_usd:,.0f}")
    print(f"   Exclude stablecoins: {config.exclude_stablecoins}")
    print(f"   CoinGecko delay: {config.coingecko_delay}s")

    return loader


if __name__ == "__main__":
    print("🧪 CURRENCY DATABASE LOADER EXAMPLES")
    print("=" * 50)

    try:
        # Basic usage
        print("\n1️⃣ BASIC USAGE:")
        currencies = example_basic_usage()

        print("\n" + "=" * 50)

        # Django integration
        print("\n2️⃣ DJANGO INTEGRATION:")
        django_data = example_django_integration()

        print("\n" + "=" * 50)

        # Advanced config
        print("\n3️⃣ ADVANCED CONFIGURATION:")
        advanced_loader = example_advanced_config()

        print("\n🎉 All examples completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
