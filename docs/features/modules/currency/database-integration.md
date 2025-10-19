---
title: Database Integration
description: Django-CFG database integration feature guide. Production-ready database integration with built-in validation, type safety, and seamless Django integration.
sidebar_label: Database Integration
sidebar_position: 5
keywords:
  - django-cfg database integration
  - django database integration
  - database integration django-cfg
---

# Database Integration

Learn how to integrate the Django-CFG Currency Module with your database and Django ORM models.

## Overview

The currency module provides powerful tools for populating and maintaining currency data in your database, including:

- **Automated Currency Discovery** - Fetch all supported currencies from APIs
- **ORM-Ready Data Format** - Pydantic models that map directly to Django models
- **Rate Limiting** - Respect API limits during bulk operations
- **Flexible Configuration** - Control which currencies to include
- **Type Safety** - Full Pydantic validation for all data

## Database Loader

### Basic Usage

```python
from django_cfg.modules.django_currency.database import create_database_loader

# Create loader with default settings
loader = create_database_loader()

# Get currency data ready for ORM insertion
currency_data = loader.get_all_currencies_for_database()

print(f"Prepared {len(currency_data)} currencies for database")
```

### Advanced Configuration

```python
from django_cfg.modules.django_currency.database import (
    CurrencyDatabaseLoader,
    DatabaseLoaderConfig
)

# Custom configuration
config = DatabaseLoaderConfig(
    max_cryptocurrencies=200,           # Limit crypto count
    max_fiat_currencies=30,             # Limit fiat count  
    min_market_cap_usd=100_000_000,     # Only large-cap cryptos
    exclude_stablecoins=True,           # Skip stablecoins
    coingecko_delay=2.0,                # Increase API delay
    cache_ttl_hours=12                  # Cache for 12 hours
)

loader = CurrencyDatabaseLoader(config)
```

## Django Model Integration

### Currency Model Example

```python
# models.py
from django.db import models

class Currency(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    symbol = models.CharField(max_length=10)
    currency_type = models.CharField(max_length=10)  # 'fiat' or 'crypto'
    decimal_places = models.IntegerField(default=2)
    is_active = models.BooleanField(default=True)
    min_payment_amount = models.DecimalField(max_digits=20, decimal_places=8, default=1.0)
    usd_rate = models.DecimalField(max_digits=20, decimal_places=8)
    rate_updated_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'currencies'
        ordering = ['code']
    
    def __str__(self):
        return f"{self.code} - {self.name}"
```

### Bulk Currency Loading

```python
# management/commands/load_currencies.py
from django.core.management.base import BaseCommand
from django_cfg.modules.django_currency.database import load_currencies_to_database_format
from myapp.models import Currency

class Command(BaseCommand):
    help = 'Load currencies from external APIs'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--max-crypto',
            type=int,
            default=100,
            help='Maximum number of cryptocurrencies to load'
        )
        parser.add_argument(
            '--max-fiat',
            type=int,
            default=30,
            help='Maximum number of fiat currencies to load'
        )
        parser.add_argument(
            '--min-market-cap',
            type=float,
            default=50_000_000,
            help='Minimum market cap for cryptocurrencies (USD)'
        )
    
    def handle(self, *args, **options):
        self.stdout.write('Loading currency data...')
        
        # Create custom loader with command options
        from django_cfg.modules.django_currency.database import create_database_loader
        
        loader = create_database_loader(
            max_cryptocurrencies=options['max_crypto'],
            max_fiat_currencies=options['max_fiat'],
            min_market_cap_usd=options['min_market_cap'],
            exclude_stablecoins=True
        )
        
        # Get currency data
        currency_data = load_currencies_to_database_format(loader=loader)
        
        # Convert to Django model instances
        currency_objects = []
        for data in currency_data:
            currency_objects.append(Currency(**data.model_dump()))
        
        # Bulk create with conflict handling
        created_currencies = Currency.objects.bulk_create(
            currency_objects,
            ignore_conflicts=True,
            batch_size=100
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully loaded {len(created_currencies)} currencies'
            )
        )
        
        # Update existing currencies
        updated_count = 0
        for data in currency_data:
            updated_count += Currency.objects.filter(
                code=data.code
            ).update(
                usd_rate=data.usd_rate,
                rate_updated_at=data.rate_updated_at,
                name=data.name
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Updated {updated_count} existing currencies'
            )
        )

# Usage:
# python manage.py load_currencies --max-crypto 200 --min-market-cap 100000000
```

### Periodic Currency Updates

```python
# tasks.py (using Celery)
from celery import shared_task
from django_cfg.modules.django_currency.database import load_currencies_to_database_format
from myapp.models import Currency
import logging

logger = logging.getLogger(__name__)

@shared_task
def update_currency_rates():
    """Periodic task to update currency rates."""
    try:
        # Load fresh currency data
        currency_data = load_currencies_to_database_format()
        
        updated_count = 0
        for data in currency_data:
            # Update only rate and timestamp, keep other fields
            updated = Currency.objects.filter(
                code=data.code
            ).update(
                usd_rate=data.usd_rate,
                rate_updated_at=data.rate_updated_at
            )
            updated_count += updated
        
        logger.info(f"Updated rates for {updated_count} currencies")
        return f"Updated {updated_count} currency rates"
        
    except Exception as e:
        logger.error(f"Failed to update currency rates: {e}")
        raise

# settings.py - Celery Beat Schedule
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'update-currency-rates': {
        'task': 'myapp.tasks.update_currency_rates',
        'schedule': crontab(minute=0, hour='*/6'),  # Every 6 hours
    },
}
```

## Data Models

### Pydantic Models for Database

The database loader provides strongly-typed Pydantic models:

```python
from django_cfg.modules.django_currency.database import (
    CoinGeckoCoinInfo,
    YFinanceCurrencyInfo, 
    CurrencyRateInfo
)

# Cryptocurrency data model
class CoinGeckoCoinInfo(BaseModel):
    id: str                              # e.g., "bitcoin"
    symbol: str                          # e.g., "BTC" 
    name: str                           # e.g., "Bitcoin"
    market_cap_usd: Optional[float]     # Market cap in USD
    current_price_usd: Optional[float]  # Current price in USD

# Fiat currency data model  
class YFinanceCurrencyInfo(BaseModel):
    code: str                           # e.g., "USD"
    name: Optional[str]                 # e.g., "US Dollar"

# Combined currency data ready for ORM
class CurrencyRateInfo(BaseModel):
    code: str                           # Currency code
    name: str                           # Display name
    symbol: str                         # Trading symbol
    currency_type: str                  # "fiat" or "crypto"
    decimal_places: int                 # Precision for amounts
    is_active: bool                     # Whether currency is active
    min_payment_amount: float           # Minimum transaction amount
    usd_rate: float                     # Current USD exchange rate
    rate_updated_at: datetime           # When rate was last updated
```

### Data Validation

```python
# Example of data validation and transformation
def validate_currency_data(raw_data):
    """Validate and transform currency data before database insertion."""
    try:
        # Create Pydantic model for validation
        currency_info = CurrencyRateInfo(**raw_data)
        
        # Additional business logic validation
        if currency_info.currency_type == 'crypto' and currency_info.usd_rate > 1_000_000:
            raise ValueError(f"Crypto rate seems too high: {currency_info.usd_rate}")
        
        if currency_info.min_payment_amount <= 0:
            raise ValueError("Minimum payment amount must be positive")
        
        return currency_info
        
    except ValidationError as e:
        logger.error(f"Validation failed for currency data: {e}")
        raise
```

## Database Operations

### Smart Currency Sync

```python
from django_cfg.modules.django_currency.database import create_database_loader
from myapp.models import Currency
from django.db import transaction

class CurrencySync:
    def __init__(self):
        self.loader = create_database_loader(
            max_cryptocurrencies=150,
            max_fiat_currencies=25,
            min_market_cap_usd=75_000_000
        )
    
    @transaction.atomic
    def sync_currencies(self, dry_run=False):
        """Synchronize currency data with database."""
        
        # Get fresh data from APIs
        currency_data = self.loader.get_all_currencies_for_database()
        
        # Track changes
        stats = {
            'new': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0
        }
        
        for data in currency_data:
            try:
                currency, created = Currency.objects.get_or_create(
                    code=data.code,
                    defaults=data.model_dump()
                )
                
                if created:
                    stats['new'] += 1
                    if not dry_run:
                        logger.info(f"Created new currency: {data.code}")
                else:
                    # Update existing currency
                    updated_fields = []
                    
                    # Check if rate needs updating
                    if abs(float(currency.usd_rate) - data.usd_rate) > 0.0001:
                        currency.usd_rate = data.usd_rate
                        currency.rate_updated_at = data.rate_updated_at
                        updated_fields.extend(['usd_rate', 'rate_updated_at'])
                    
                    # Update name if changed
                    if currency.name != data.name:
                        currency.name = data.name
                        updated_fields.append('name')
                    
                    if updated_fields and not dry_run:
                        currency.save(update_fields=updated_fields)
                        stats['updated'] += 1
                        logger.info(f"Updated currency {data.code}: {updated_fields}")
                    elif not updated_fields:
                        stats['skipped'] += 1
                        
            except Exception as e:
                stats['errors'] += 1
                logger.error(f"Error processing currency {data.code}: {e}")
        
        # Deactivate currencies no longer available
        current_codes = {data.code for data in currency_data}
        inactive_count = 0
        
        if not dry_run:
            inactive_count = Currency.objects.exclude(
                code__in=current_codes
            ).update(is_active=False)
        
        return {
            **stats,
            'deactivated': inactive_count,
            'total_processed': len(currency_data),
            'dry_run': dry_run
        }

# Usage
sync_service = CurrencySync()

# Test run first
dry_run_results = sync_service.sync_currencies(dry_run=True)
print(f"Dry run results: {dry_run_results}")

# Actual sync
sync_results = sync_service.sync_currencies(dry_run=False)
print(f"Sync completed: {sync_results}")
```

### Query Optimization

```python
# Efficient currency queries
class CurrencyQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)
    
    def fiat_only(self):
        return self.filter(currency_type='fiat')
    
    def crypto_only(self):
        return self.filter(currency_type='crypto')
    
    def by_market_cap(self, min_cap_usd=None):
        if min_cap_usd:
            # Approximate market cap calculation
            return self.filter(usd_rate__gte=min_cap_usd / 1_000_000_000)
        return self
    
    def with_fresh_rates(self, max_age_hours=6):
        from django.utils import timezone
        cutoff = timezone.now() - timedelta(hours=max_age_hours)
        return self.filter(rate_updated_at__gte=cutoff)

class Currency(models.Model):
    # ... model fields ...
    
    objects = CurrencyQuerySet.as_manager()

# Usage examples
active_fiat = Currency.objects.active().fiat_only()
fresh_crypto = Currency.objects.crypto_only().with_fresh_rates(max_age_hours=2)
major_cryptos = Currency.objects.crypto_only().by_market_cap(min_cap_usd=1_000_000_000)
```

## Performance Optimization

### Batch Processing

```python
def bulk_update_currency_rates():
    """Efficiently update many currency rates."""
    
    # Get currencies that need updates
    stale_cutoff = timezone.now() - timedelta(hours=6)
    stale_currencies = Currency.objects.filter(
        is_active=True,
        rate_updated_at__lt=stale_cutoff
    )
    
    # Group by type for efficient API usage
    fiat_codes = list(stale_currencies.fiat_only().values_list('code', flat=True))
    crypto_codes = list(stale_currencies.crypto_only().values_list('code', flat=True))
    
    # Batch fetch rates
    from django_cfg.modules.django_currency.clients import YFinanceClient, CoinGeckoClient
    
    yf_client = YFinanceClient()
    cg_client = CoinGeckoClient()
    
    # Parallel fiat rate updates
    if fiat_codes:
        fiat_pairs = [(code, 'USD') for code in fiat_codes if code != 'USD']
        fiat_rates = yf_client.fetch_multiple_rates(fiat_pairs)
        
        # Bulk update fiat currencies
        fiat_updates = []
        for pair_key, rate in fiat_rates.items():
            base_currency = pair_key.split('_')[0]
            fiat_updates.append(Currency(
                code=base_currency,
                usd_rate=1.0 / rate.rate,  # Invert rate for non-USD base
                rate_updated_at=rate.timestamp
            ))
        
        Currency.objects.bulk_update(
            fiat_updates,
            ['usd_rate', 'rate_updated_at'],
            batch_size=50
        )
    
    # Parallel crypto rate updates  
    if crypto_codes:
        crypto_pairs = [(code.lower(), 'usd') for code in crypto_codes]
        crypto_rates = cg_client.fetch_multiple_rates(crypto_pairs)
        
        # Bulk update crypto currencies
        crypto_updates = []
        for pair_key, rate in crypto_rates.items():
            crypto_code = pair_key.split('_')[0].upper()
            crypto_updates.append(Currency(
                code=crypto_code,
                usd_rate=rate.rate,
                rate_updated_at=rate.timestamp
            ))
        
        Currency.objects.bulk_update(
            crypto_updates,
            ['usd_rate', 'rate_updated_at'],
            batch_size=50
        )
```

### Database Indexing

```python
# migrations/xxxx_add_currency_indexes.py
from django.db import migrations

class Migration(migrations.Migration):
    
    dependencies = [
        ('myapp', '0001_initial'),
    ]
    
    operations = [
        migrations.RunSQL([
            # Index for active currency lookups
            "CREATE INDEX IF NOT EXISTS idx_currency_active_type ON currencies(is_active, currency_type) WHERE is_active = true;",
            
            # Index for rate freshness queries
            "CREATE INDEX IF NOT EXISTS idx_currency_rate_updated ON currencies(rate_updated_at) WHERE is_active = true;",
            
            # Composite index for common queries
            "CREATE INDEX IF NOT EXISTS idx_currency_type_rate_updated ON currencies(currency_type, rate_updated_at, is_active);",
            
            # Partial index for active currencies only
            "CREATE INDEX IF NOT EXISTS idx_currency_code_active ON currencies(code) WHERE is_active = true;",
        ]),
    ]
```

## Monitoring & Maintenance

### Health Checks

```python
from django_cfg.modules.django_currency.database import create_database_loader
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Check currency data health'
    
    def handle(self, *args, **options):
        # Check database state
        total_currencies = Currency.objects.count()
        active_currencies = Currency.objects.active().count()
        stale_cutoff = timezone.now() - timedelta(hours=24)
        stale_currencies = Currency.objects.filter(
            rate_updated_at__lt=stale_cutoff
        ).count()
        
        self.stdout.write(f"📊 Currency Database Health Check")
        self.stdout.write(f"Total currencies: {total_currencies}")
        self.stdout.write(f"Active currencies: {active_currencies}")
        self.stdout.write(f"Stale rates (>24h): {stale_currencies}")
        
        # Check API connectivity
        try:
            loader = create_database_loader(max_cryptocurrencies=1, max_fiat_currencies=1)
            test_data = loader.get_all_currencies_for_database()
            self.stdout.write(self.style.SUCCESS("✅ API connectivity: OK"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ API connectivity: {e}"))
        
        # Check rate accuracy
        if stale_currencies > active_currencies * 0.1:  # >10% stale
            self.stdout.write(self.style.WARNING("⚠️ Many currencies have stale rates"))
        else:
            self.stdout.write(self.style.SUCCESS("✅ Rate freshness: OK"))
```

The database integration provides a robust foundation for managing currency data in production applications, with comprehensive tools for loading, updating, and maintaining currency information at scale. 💱
