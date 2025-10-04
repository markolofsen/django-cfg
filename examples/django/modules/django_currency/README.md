# Django Currency Module

🚀 **Universal currency converter with decomposed provider logic**

A simple, KISS-principle currency conversion module that provides seamless bidirectional conversion between fiat and cryptocurrency rates.

## ✨ Features

- **🔄 Universal Conversion**: Fiat ⇄ Fiat, Crypto ⇄ Fiat, Crypto ⇄ Crypto
- **📡 Dynamic Loading**: All currencies loaded dynamically from APIs (no hardcoded lists)
- **🎯 Provider Separation**: YFinance for fiat, CoinGecko for crypto
- **⚡ TTL Caching**: Fast in-memory caching with configurable TTL
- **🔧 Pydantic Models**: All data structures typed with Pydantic v2
- **🚫 No API Keys**: Uses only public APIs
- **🔀 Smart Routing**: Automatic provider selection and indirect conversions

## 🏗️ Architecture

```
django_currency/
├── models.py           # Pydantic v2 data models
├── exceptions.py       # Custom exceptions
├── cache.py           # TTL cache manager  
├── converter.py       # Main conversion logic
├── clients/
│   ├── yfinance_client.py    # Fiat currencies only
│   └── coingecko_client.py   # Cryptocurrencies only
└── __init__.py        # Public API
```

## 🚀 Quick Start

### Simple API

```python
from django_cfg.modules.django_currency import convert_currency, get_exchange_rate

# Convert currencies
eur_amount = convert_currency(100, "USD", "EUR")
btc_price = convert_currency(50000, "USD", "BTC")

# Get exchange rates
usd_eur_rate = get_exchange_rate("USD", "EUR")
btc_usd_rate = get_exchange_rate("BTC", "USD")
```

### Advanced Usage

```python
from django_cfg.modules.django_currency import CurrencyConverter

converter = CurrencyConverter()

# Get conversion result with details
result = converter.convert(100, "USD", "EUR")
print(f"Amount: {result.result}")
print(f"Rate: {result.rate.rate}")
print(f"Source: {result.rate.source}")

# Get all supported currencies  
currencies = converter.get_supported_currencies()
print(f"Fiat currencies: {len(currencies.yfinance.fiat)}")
print(f"Cryptocurrencies: {len(currencies.coingecko.crypto)}")
```

## 🎯 Provider Logic

### YFinance Client
- **Purpose**: Fiat currency pairs only
- **Symbols**: `EURUSD=X`, `GBPJPY=X`, etc.
- **Dynamic Loading**: Uses `yf.Lookup().get_currency()` to get all available pairs
- **Coverage**: All major and minor fiat currencies

### CoinGecko Client  
- **Purpose**: Cryptocurrency pairs only
- **API**: CoinGecko Public API v3
- **Dynamic Loading**: Uses `get_coins_list()` and `get_supported_vs_currencies()`
- **Coverage**: 17,000+ cryptocurrencies

## 🔄 Conversion Routes

```python
# Direct routes
USD → EUR    # YFinance
BTC → USD    # CoinGecko  

# Indirect routes (via USD bridge)
EUR → BTC    # EUR → USD → BTC
ETH → BTC    # ETH → USD → BTC
```

## 📊 Data Models

All responses use Pydantic v2 models:

```python
class Rate(BaseModel):
    source: str           # "yfinance" or "coingecko"
    base_currency: str    # "USD"
    quote_currency: str   # "EUR" 
    rate: float          # 0.85
    timestamp: datetime   # Auto-generated

class ConversionResult(BaseModel):
    request: ConversionRequest
    result: float
    rate: Rate
    path: Optional[str]   # "EUR→USD→BTC" for indirect
```

## ⚡ Caching

- **TTL Cache**: Configurable time-to-live (default: 5 minutes)
- **Per-Source**: Separate cache for each provider
- **Statistics**: Cache hit/miss monitoring
- **Memory Efficient**: Uses `cachetools.TTLCache`

## 🧪 Testing

```bash
cd django_cfg/modules/django_currency/
python test_currency.py
```

## 🎨 Example Output

```
🧪 Testing Django Currency Module...
==================================================

💱 Test 1: Fiat Currency Conversion
✅ 100 USD = 85.23 EUR

📊 Test 2: Exchange Rate  
✅ 1 USD = 0.8523 EUR

🪙 Test 3: Crypto Conversion
✅ 1 BTC = 45,230.50 USD

📋 Test 4: Supported Currencies
✅ YFinance fiat currencies: 168
✅ CoinGecko cryptocurrencies: 17,247  
✅ CoinGecko vs_currencies: 61

🎉 All tests completed successfully!
```

## 🚫 No Fallbacks Policy

- **Strict Mode**: If API fails, module fails (no backup hardcoded lists)
- **Dynamic Only**: All currencies loaded from live APIs
- **Fail Fast**: Clear error messages when providers unavailable

## 📝 Error Handling

```python
try:
    result = convert_currency(100, "INVALID", "USD")
except CurrencyNotFoundError:
    print("Currency not supported")
except RateFetchError:
    print("API temporarily unavailable")
except ConversionError:
    print("Conversion failed")
```

---

**Built with ❤️ following KISS principles and decomposed architecture**
