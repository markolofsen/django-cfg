---
title: Currency Module Quick Start
description: Django-CFG quick start feature guide. Production-ready currency module quick start with built-in validation, type safety, and seamless Django integration.
sidebar_label: Quick Start
sidebar_position: 2
keywords:
  - django-cfg quick start
  - django quick start
  - quick start django-cfg
---

# Quick Start

Get up and running with Django-CFG Currency Module in less than 5 minutes.

## Installation

The currency module is included with Django-CFG. Make sure you have the required dependencies:

```bash
# Install dependencies
poetry add yfinance pycoingecko cachetools tenacity

# Or with pip
pip install yfinance pycoingecko cachetools tenacity
```

## Basic Usage

### Simple Conversions

```python
from django_cfg.modules.django_currency import convert_currency

# Fiat to Fiat
eur_amount = convert_currency(100, 'USD', 'EUR')
print(f"100 USD = {eur_amount:.2f} EUR")

# Crypto to Fiat
usd_value = convert_currency(1, 'BTC', 'USD')
print(f"1 BTC = ${usd_value:,.2f} USD")

# Fiat to Crypto
btc_amount = convert_currency(50000, 'USD', 'BTC')
print(f"$50,000 = {btc_amount:.8f} BTC")
```

### Get Exchange Rates

```python
from django_cfg.modules.django_currency import get_exchange_rate

# Get current exchange rate
usd_eur_rate = get_exchange_rate('USD', 'EUR')
print(f"1 USD = {usd_eur_rate:.4f} EUR")

# Crypto rates
btc_usd_rate = get_exchange_rate('BTC', 'USD')
print(f"1 BTC = ${btc_usd_rate:,.2f} USD")
```

## Advanced Usage

### Using the Main Converter

```python
from django_cfg.modules.django_currency import CurrencyConverter

# Initialize converter
converter = CurrencyConverter()

# Convert with detailed result
result = converter.convert(100, 'USD', 'EUR')

print(f"Original amount: {result.request.amount} {result.request.base_currency}")
print(f"Converted amount: {result.result:.2f} {result.request.quote_currency}")
print(f"Exchange rate: {result.rate.rate:.4f}")
print(f"Rate source: {result.rate.source}")
print(f"Updated at: {result.rate.timestamp}")
```

### Check Supported Currencies

```python
# Get all supported currencies
currencies = converter.get_supported_currencies()

print(f"📊 Currency Coverage:")
print(f"Fiat currencies: {len(currencies.yfinance.fiat)}")
print(f"Cryptocurrencies: {len(currencies.coingecko.crypto)}")
print(f"Quote currencies: {len(currencies.coingecko.vs_currencies)}")

# List some examples
print("\n💰 Sample Fiat Currencies:")
print(currencies.yfinance.fiat[:10])

print("\n🪙 Sample Cryptocurrencies:")
print(currencies.coingecko.crypto[:10])
```

## 🏃‍♂️ Real-World Examples

### E-commerce Price Display

```python
def display_product_price(product):
    """Display product price in multiple currencies."""
    base_price = product.price  # Assume in USD
    
    currencies_to_show = ['EUR', 'GBP', 'CAD', 'AUD']
    prices = {}
    
    for currency in currencies_to_show:
        try:
            converted = convert_currency(base_price, 'USD', currency)
            prices[currency] = f"{converted:.2f} {currency}"
        except Exception as e:
            prices[currency] = "Not available"
    
    return prices

# Usage
product_prices = display_product_price(my_product)
# Output: {'EUR': '85.30 EUR', 'GBP': '78.45 GBP', ...}
```

### Portfolio Valuation

```python
def calculate_crypto_portfolio_value(holdings):
    """Calculate total portfolio value in USD."""
    converter = CurrencyConverter()
    total_usd = 0
    
    for crypto, amount in holdings.items():
        try:
            result = converter.convert(amount, crypto, 'USD')
            total_usd += result.result
            print(f"{amount} {crypto} = ${result.result:,.2f}")
        except Exception as e:
            print(f"Could not convert {crypto}: {e}")
    
    return total_usd

# Usage
portfolio = {
    'BTC': 0.5,
    'ETH': 2.3,
    'ADA': 1000,
    'DOT': 50
}

total_value = calculate_crypto_portfolio_value(portfolio)
print(f"\nTotal Portfolio Value: ${total_value:,.2f} USD")
```

### Multi-Currency Order Processing

```python
def process_international_order(order_data):
    """Process order with automatic currency conversion."""
    customer_currency = order_data['customer_currency']
    order_total = order_data['total_amount']  # In customer currency
    
    # Convert to USD for processing
    usd_amount = convert_currency(
        order_total, 
        customer_currency, 
        'USD'
    )
    
    # Process payment in USD
    payment_result = process_payment(usd_amount, 'USD')
    
    return {
        'customer_amount': f"{order_total:.2f} {customer_currency}",
        'usd_amount': f"${usd_amount:.2f}",
        'payment_status': payment_result.status
    }
```

## 🚨 Error Handling

The currency module uses specific exceptions for different error types:

```python
from django_cfg.modules.django_currency import (
    convert_currency,
    CurrencyNotFoundError,
    RateFetchError,
    ConversionError
)

def safe_currency_conversion(amount, from_currency, to_currency):
    """Convert currency with proper error handling."""
    try:
        result = convert_currency(amount, from_currency, to_currency)
        return {
            'success': True,
            'amount': result,
            'message': 'Conversion successful'
        }
    except CurrencyNotFoundError as e:
        return {
            'success': False,
            'error': 'Currency not supported',
            'message': str(e)
        }
    except RateFetchError as e:
        return {
            'success': False,
            'error': 'API unavailable',
            'message': str(e)
        }
    except ConversionError as e:
        return {
            'success': False,
            'error': 'Conversion failed',
            'message': str(e)
        }
    except Exception as e:
        return {
            'success': False,
            'error': 'Unknown error',
            'message': str(e)
        }

# Usage
result = safe_currency_conversion(100, 'USD', 'INVALID')
if result['success']:
    print(f"Converted: {result['amount']}")
else:
    print(f"Error: {result['error']} - {result['message']}")
```

## Performance Tips

### Batch Conversions

```python
from django_cfg.modules.django_currency.clients import YFinanceClient, CoinGeckoClient

# For multiple fiat conversions - use YFinance batch
yf_client = YFinanceClient()
fiat_pairs = [('USD', 'EUR'), ('USD', 'GBP'), ('EUR', 'GBP')]
fiat_results = yf_client.fetch_multiple_rates(fiat_pairs)

# For multiple crypto conversions - use CoinGecko batch  
cg_client = CoinGeckoClient()
crypto_pairs = [('bitcoin', 'usd'), ('ethereum', 'usd'), ('cardano', 'usd')]
crypto_results = cg_client.fetch_multiple_rates(crypto_pairs)
```

### Caching Best Practices

```python
# Cache is automatic, but you can verify cache usage
converter = CurrencyConverter()

# First call - fetches from API
result1 = converter.convert(100, 'USD', 'EUR')
print(f"Source: {result1.rate.source}")  # Will show API source

# Second call within 5 minutes - uses cache
result2 = converter.convert(200, 'USD', 'EUR')  
print(f"Source: {result2.rate.source}")  # Will show cache source
```

## Next Steps

Now that you have the basics, explore more advanced features:

- **[API Reference](./api-reference)** - Complete method documentation
- **[Examples](./examples/overview)** - More real-world examples
- **[Database Integration](./database-integration)** - ORM integration guide

Happy converting! 💱
