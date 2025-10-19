---
title: Currency API Reference
description: Django-CFG api reference feature guide. Production-ready currency api reference with built-in validation, type safety, and seamless Django integration.
sidebar_label: API Reference
sidebar_position: 3
keywords:
  - django-cfg api reference
  - django api reference
  - api reference django-cfg
---

# API Reference

Complete API documentation for the Django-CFG Currency Module.

## Public API

### Convenience Functions

#### `convert_currency(amount, base_currency, quote_currency)`

Convert amount from one currency to another.

**Parameters:**
- `amount` (float): Amount to convert
- `base_currency` (str): Source currency code (e.g., 'USD', 'BTC')
- `quote_currency` (str): Target currency code (e.g., 'EUR', 'ETH')

**Returns:** `float` - Converted amount

**Raises:**
- `CurrencyNotFoundError`: If currency is not supported
- `RateFetchError`: If unable to fetch exchange rate
- `ConversionError`: If conversion fails

```python
from django_cfg.modules.django_currency import convert_currency

# Basic usage
eur_amount = convert_currency(100, 'USD', 'EUR')
btc_amount = convert_currency(50000, 'USD', 'BTC')
```

#### `get_exchange_rate(base_currency, quote_currency)`

Get current exchange rate between two currencies.

**Parameters:**
- `base_currency` (str): Base currency code
- `quote_currency` (str): Quote currency code

**Returns:** `float` - Exchange rate (1 base = X quote)

```python
from django_cfg.modules.django_currency import get_exchange_rate

rate = get_exchange_rate('USD', 'EUR')  # Returns ~0.85
```

## Core Classes

### CurrencyConverter

Main converter class with full functionality.

#### `__init__()`

Initialize the currency converter with default settings.

```python
from django_cfg.modules.django_currency import CurrencyConverter

converter = CurrencyConverter()
```

#### `convert(amount, base_currency, quote_currency)`

Convert currency with detailed result information.

**Parameters:**
- `amount` (float): Amount to convert
- `base_currency` (str): Source currency code
- `quote_currency` (str): Target currency code

**Returns:** `ConversionResult` - Detailed conversion result

```python
result = converter.convert(100, 'USD', 'EUR')

# Access detailed information
print(f"Amount: {result.result}")
print(f"Rate: {result.rate.rate}")
print(f"Source: {result.rate.source}")
print(f"Timestamp: {result.rate.timestamp}")
```

#### `get_supported_currencies()`

Get all supported currencies by provider.

**Returns:** `SupportedCurrencies` - Pydantic model with currency lists

```python
currencies = converter.get_supported_currencies()

print(f"Fiat: {len(currencies.yfinance.fiat)}")
print(f"Crypto: {len(currencies.coingecko.crypto)}")
print(f"VS Currencies: {len(currencies.coingecko.vs_currencies)}")
```

## Pydantic Models

### ConversionRequest

Input data for currency conversion.

```python
class ConversionRequest(BaseModel):
    amount: float = Field(gt=0, description="Amount to convert")
    base_currency: str = Field(min_length=3, max_length=10, description="Source currency")
    quote_currency: str = Field(min_length=3, max_length=10, description="Target currency")
```

### Rate

Exchange rate information.

```python
class Rate(BaseModel):
    base_currency: str = Field(description="Base currency code")
    quote_currency: str = Field(description="Quote currency code")
    rate: float = Field(gt=0, description="Exchange rate")
    source: str = Field(description="Data source (yfinance/coingecko)")
    timestamp: datetime = Field(description="Rate timestamp")
```

### ConversionResult

Complete conversion result.

```python
class ConversionResult(BaseModel):
    request: ConversionRequest = Field(description="Original request")
    rate: Rate = Field(description="Exchange rate used")
    result: float = Field(description="Converted amount")
```

### SupportedCurrencies

All supported currencies.

```python
class SupportedCurrencies(BaseModel):
    yfinance: YFinanceCurrencies = Field(description="YFinance currencies")
    coingecko: CoinGeckoCurrencies = Field(description="CoinGecko currencies")

class YFinanceCurrencies(BaseModel):
    fiat: List[str] = Field(description="Supported fiat currencies")

class CoinGeckoCurrencies(BaseModel):
    crypto: List[str] = Field(description="Supported cryptocurrencies")
    vs_currencies: List[str] = Field(description="Supported quote currencies")
```

## 🔌 Client Classes

### YFinanceClient

Handles fiat currency conversions via Yahoo Finance.

#### `__init__(cache_ttl=300)`

Initialize YFinance client.

**Parameters:**
- `cache_ttl` (int): Cache TTL in seconds (default: 300)

#### `fetch_rate(base, quote)`

Fetch exchange rate for fiat currencies.

**Parameters:**
- `base` (str): Base currency code
- `quote` (str): Quote currency code

**Returns:** `Rate` - Exchange rate information

#### `fetch_multiple_rates(pairs)`

Fetch multiple rates in parallel.

**Parameters:**
- `pairs` (List[Tuple[str, str]]): Currency pairs to fetch

**Returns:** `Dict[str, Rate]` - Mapping of pair keys to rates

```python
from django_cfg.modules.django_currency.clients import YFinanceClient

client = YFinanceClient()

# Single rate
rate = client.fetch_rate('USD', 'EUR')

# Multiple rates (parallel)
pairs = [('USD', 'EUR'), ('USD', 'GBP'), ('EUR', 'GBP')]
rates = client.fetch_multiple_rates(pairs)
```

#### `get_fiat_currencies()`

Get all supported fiat currencies.

**Returns:** `Set[str]` - Set of fiat currency codes

### CoinGeckoClient

Handles cryptocurrency conversions via CoinGecko API.

#### `__init__(cache_ttl=300, rate_limit_delay=1.2)`

Initialize CoinGecko client.

**Parameters:**
- `cache_ttl` (int): Cache TTL in seconds (default: 300)
- `rate_limit_delay` (float): Delay between API calls (default: 1.2)

#### `fetch_rate(base, quote)`

Fetch exchange rate for cryptocurrencies.

**Parameters:**
- `base` (str): Cryptocurrency ID (e.g., 'bitcoin')
- `quote` (str): Quote currency (e.g., 'usd', 'eur')

**Returns:** `Rate` - Exchange rate information

#### `fetch_multiple_rates(pairs)`

Fetch multiple crypto rates in parallel.

**Parameters:**
- `pairs` (List[Tuple[str, str]]): Crypto pairs to fetch

**Returns:** `Dict[str, Rate]` - Mapping of pair keys to rates

```python
from django_cfg.modules.django_currency.clients import CoinGeckoClient

client = CoinGeckoClient()

# Single rate
rate = client.fetch_rate('bitcoin', 'usd')

# Multiple rates (parallel, rate-limited)
pairs = [('bitcoin', 'usd'), ('ethereum', 'usd'), ('cardano', 'usd')]
rates = client.fetch_multiple_rates(pairs)
```

#### `get_crypto_ids()`

Get all supported cryptocurrency IDs.

**Returns:** `Dict[str, str]` - Mapping of crypto IDs to names

#### `get_vs_currencies()`

Get all supported quote currencies.

**Returns:** `Set[str]` - Set of quote currency codes

## Database Integration

### CurrencyDatabaseLoader

Tool for loading currency data into ORM models.

#### `__init__(config)`

Initialize database loader.

**Parameters:**
- `config` (DatabaseLoaderConfig): Configuration object

```python
from django_cfg.modules.django_currency.database import (
    CurrencyDatabaseLoader,
    DatabaseLoaderConfig
)

config = DatabaseLoaderConfig(
    max_cryptocurrencies=100,
    max_fiat_currencies=20,
    min_market_cap_usd=100_000_000,
    exclude_stablecoins=True
)

loader = CurrencyDatabaseLoader(config)
```

#### `get_cryptocurrencies_for_database()`

Get cryptocurrency data formatted for ORM insertion.

**Returns:** `List[CoinGeckoCoinInfo]` - List of crypto data

#### `get_fiat_currencies_for_database()`

Get fiat currency data formatted for ORM insertion.

**Returns:** `List[YFinanceCurrencyInfo]` - List of fiat data

#### `get_all_currencies_for_database()`

Get all currency data formatted for ORM insertion.

**Returns:** `List[CurrencyRateInfo]` - List of currency data ready for ORM

```python
# Get all currencies for database
currency_data = loader.get_all_currencies_for_database()

# Insert into Django model
from myapp.models import Currency
currencies = [Currency(**data.dict()) for data in currency_data]
Currency.objects.bulk_create(currencies, ignore_conflicts=True)
```

### DatabaseLoaderConfig

Configuration for database loader.

```python
class DatabaseLoaderConfig(BaseModel):
    max_cryptocurrencies: int = 50
    max_fiat_currencies: int = 10
    min_market_cap_usd: Optional[float] = None
    exclude_stablecoins: bool = False
    coingecko_delay: float = 1.5
    cache_ttl_hours: int = 24
```

### Helper Functions

#### `create_database_loader(**kwargs)`

Create database loader with default configuration.

```python
from django_cfg.modules.django_currency.database import create_database_loader

loader = create_database_loader(
    max_cryptocurrencies=100,
    exclude_stablecoins=True,
    min_market_cap_usd=50_000_000
)
```

#### `load_currencies_to_database_format(loader=None)`

Load currencies in database format using default or custom loader.

```python
from django_cfg.modules.django_currency.database import load_currencies_to_database_format

# With default loader
currency_data = load_currencies_to_database_format()

# With custom loader
currency_data = load_currencies_to_database_format(loader=my_loader)
```

## 🚨 Exceptions

### CurrencyError

Base exception for all currency-related errors.

### CurrencyNotFoundError

Raised when a specified currency is not found or supported.

```python
try:
    convert_currency(100, 'USD', 'INVALID')
except CurrencyNotFoundError as e:
    print(f"Currency not supported: {e}")
```

### RateFetchError

Raised when there is an issue fetching rates from external APIs.

```python
try:
    convert_currency(100, 'USD', 'EUR')
except RateFetchError as e:
    print(f"API error: {e}")
```

### ConversionError

Raised when a currency conversion cannot be performed.

```python
try:
    convert_currency(-100, 'USD', 'EUR')  # Negative amount
except ConversionError as e:
    print(f"Conversion error: {e}")
```

### CacheError

Raised when there is an issue with cache operations.

## Utilities

### CacheManager

Manages TTL caching for rates and currency lists.

```python
from django_cfg.modules.django_currency.utils import CacheManager

cache = CacheManager(ttl=300, max_size=1000)

# Cache operations
cache.set("USD_EUR", rate_data)
cached_rate = cache.get("USD_EUR")
cache.clear()
```

## Performance Features

### Multi-threading

Both YFinance and CoinGecko clients support parallel operations:

- **YFinance**: 8 parallel workers for fiat currencies
- **CoinGecko**: 3 parallel workers with rate limiting

### Retry Logic

Automatic retry with exponential backoff:

- **YFinance**: 3 attempts, 1-10 second wait
- **CoinGecko**: 4 attempts, 2-30 second wait

### Caching

Intelligent TTL caching:

- **Rates**: 5-minute cache
- **Currency Lists**: 1-hour cache
- **Thread-safe**: Concurrent access protection

## Usage Examples

### Django Model Integration

```python
from django.db import models
from django_cfg.modules.django_currency import convert_currency

class Product(models.Model):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    
    def get_price_in_currency(self, target_currency):
        if self.currency == target_currency:
            return self.price
        
        converted = convert_currency(
            float(self.price), 
            self.currency, 
            target_currency
        )
        return round(converted, 2)
```

### Django REST API

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_cfg.modules.django_currency import convert_currency

@api_view(['POST'])
def convert_currency_api(request):
    amount = request.data.get('amount')
    from_currency = request.data.get('from')
    to_currency = request.data.get('to')
    
    try:
        result = convert_currency(amount, from_currency, to_currency)
        return Response({
            'success': True,
            'result': result,
            'amount': amount,
            'from': from_currency,
            'to': to_currency
        })
    except Exception as e:
        return Response({
            'success': False,
            'error': str(e)
        }, status=400)
```

For more examples, see the [Examples Guide](./examples/overview). 💱
