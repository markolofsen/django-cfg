# Exchange Model Documentation

## Overview

The `Exchange` model represents cryptocurrency trading platforms and marketplaces. It manages exchange information, API credentials, and trading pair configurations.

---

## Table of Contents

1. [Key Features](#key-features)
2. [Model Fields](#model-fields)
3. [Usage Examples](#usage-examples)
4. [API Integration](#api-integration)
5. [Security](#security)
6. [Best Practices](#best-practices)

---

## Key Features

✨ **Core Capabilities:**

- **Multi-Exchange Support**: Connect to multiple exchanges (Binance, Coinbase, Kraken, etc.)
- **API Management**: Secure storage of API credentials
- **Trading Pairs**: Configure available trading pairs per exchange
- **Fee Tracking**: Monitor and track exchange fees
- **Status Monitoring**: Real-time exchange health and connectivity status

---

## Model Fields

### Basic Information

```python
class Exchange(models.Model):
    name = models.CharField(max_length=100)           # Exchange name
    slug = models.SlugField(unique=True)              # URL-friendly ID
    code = models.CharField(max_length=20)            # Exchange code (BINANCE, COINBASE)
    website = models.URLField()                        # Official website
    logo = models.ImageField()                         # Exchange logo
    description = models.TextField()                   # Detailed info
```

### API Configuration

```python
api_key = models.CharField(max_length=255)           # Public API key
api_secret = models.CharField(max_length=255)        # Secret key (encrypted)
api_endpoint = models.URLField()                      # Base API URL
api_version = models.CharField(max_length=10)        # API version
```

### Trading Configuration

```python
trading_fee_percentage = models.DecimalField()       # Default trading fee
withdrawal_fee_percentage = models.DecimalField()    # Withdrawal fee
min_order_amount = models.DecimalField()             # Minimum order size
max_order_amount = models.DecimalField()             # Maximum order size
```

### Status Fields

```python
is_active = models.BooleanField(default=True)        # Exchange enabled
is_verified = models.BooleanField(default=False)     # KYC verified
supports_margin = models.BooleanField(default=False) # Margin trading
supports_futures = models.BooleanField(default=False)# Futures trading
```

---

## Usage Examples

### Creating an Exchange

```python
from apps.crypto.models import Exchange

# Create Binance exchange
binance = Exchange.objects.create(
    name="Binance",
    slug="binance",
    code="BINANCE",
    website="https://www.binance.com",
    description="World's largest cryptocurrency exchange by volume",
    api_endpoint="https://api.binance.com",
    api_version="v3",
    trading_fee_percentage=0.1,  # 0.1%
    withdrawal_fee_percentage=0.0005,  # 0.05%
    min_order_amount=10.00,
    max_order_amount=1000000.00,
    is_active=True,
    is_verified=True,
    supports_margin=True,
    supports_futures=True
)
```

### Querying Exchanges

```python
# Get all active exchanges
active_exchanges = Exchange.objects.filter(is_active=True)

# Get exchanges supporting margin trading
margin_exchanges = Exchange.objects.filter(
    is_active=True,
    supports_margin=True
)

# Get specific exchange by code
binance = Exchange.objects.get(code='BINANCE')

# Get exchanges with low fees
low_fee_exchanges = Exchange.objects.filter(
    trading_fee_percentage__lt=0.2
).order_by('trading_fee_percentage')
```

### Working with Trading Pairs

```python
# Get available trading pairs
pairs = binance.trading_pairs.filter(is_active=True)

# Check if pair is available
btc_usdt_available = binance.trading_pairs.filter(
    base_coin__symbol='BTC',
    quote_coin__symbol='USDT',
    is_active=True
).exists()

# Calculate trading fee
order_amount = Decimal('1000.00')
fee = order_amount * (binance.trading_fee_percentage / 100)
```

---

## API Integration

### REST API Endpoints

```http
GET    /api/exchanges/              # List all exchanges
GET    /api/exchanges/{slug}/       # Get exchange details
POST   /api/exchanges/              # Create exchange (admin)
PATCH  /api/exchanges/{slug}/       # Update exchange
DELETE /api/exchanges/{slug}/       # Delete exchange (admin)

# Trading pairs
GET    /api/exchanges/{slug}/pairs/ # Get available pairs
POST   /api/exchanges/{slug}/sync/  # Sync with exchange API
```

### Response Example

```json
{
  "id": 1,
  "name": "Binance",
  "slug": "binance",
  "code": "BINANCE",
  "website": "https://www.binance.com",
  "description": "World's largest cryptocurrency exchange",
  "trading_fee_percentage": "0.10",
  "withdrawal_fee_percentage": "0.05",
  "min_order_amount": "10.00",
  "max_order_amount": "1000000.00",
  "is_active": true,
  "is_verified": true,
  "supports_margin": true,
  "supports_futures": true,
  "trading_pairs_count": 450,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-20T10:00:00Z"
}
```

---

## Security

### 🔐 API Credentials Management

**Storage:**
```python
from cryptography.fernet import Fernet

# Encrypt API secret before saving
def encrypt_api_secret(secret):
    key = settings.ENCRYPTION_KEY
    f = Fernet(key)
    return f.encrypt(secret.encode()).decode()

# Decrypt when needed
def decrypt_api_secret(encrypted_secret):
    key = settings.ENCRYPTION_KEY
    f = Fernet(key)
    return f.decrypt(encrypted_secret.encode()).decode()
```

**Best Practices:**
- ✅ Store API secrets encrypted in database
- ✅ Use environment variables for encryption keys
- ✅ Rotate API keys regularly (every 90 days)
- ✅ Implement rate limiting on API calls
- ❌ Never log API secrets
- ❌ Don't expose secrets in error messages

### 🛡️ Access Control

```python
# Only admins can create/update exchanges
class ExchangeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [IsAuthenticated()]
        return [IsAdminUser()]
```

---

## Best Practices

### 1. Exchange Initialization

```python
# Use get_or_create for idempotent setup
exchange, created = Exchange.objects.get_or_create(
    code='BINANCE',
    defaults={
        'name': 'Binance',
        'slug': 'binance',
        'website': 'https://www.binance.com',
        # ... other fields
    }
)

if not created:
    # Exchange exists, update if needed
    exchange.is_active = True
    exchange.save()
```

### 2. Fee Calculations

```python
class Exchange(models.Model):
    # ... fields ...

    def calculate_trading_fee(self, amount):
        """Calculate trading fee for given amount."""
        return amount * (self.trading_fee_percentage / 100)

    def calculate_withdrawal_fee(self, amount):
        """Calculate withdrawal fee for given amount."""
        return amount * (self.withdrawal_fee_percentage / 100)

    def calculate_net_amount(self, amount, include_withdrawal=False):
        """Calculate net amount after fees."""
        trading_fee = self.calculate_trading_fee(amount)
        net = amount - trading_fee

        if include_withdrawal:
            withdrawal_fee = self.calculate_withdrawal_fee(net)
            net -= withdrawal_fee

        return net
```

### 3. Error Handling

```python
from requests.exceptions import RequestException

def sync_with_exchange_api(exchange):
    """Sync exchange data with external API."""
    try:
        response = requests.get(
            f"{exchange.api_endpoint}/api/{exchange.api_version}/info",
            timeout=10
        )
        response.raise_for_status()

        data = response.json()
        # Process data...

    except RequestException as e:
        logger.error(f"Failed to sync {exchange.name}: {e}")
        # Send alert to admins
        send_admin_alert(f"Exchange {exchange.name} sync failed")

    except Exception as e:
        logger.exception(f"Unexpected error syncing {exchange.name}")
        raise
```

### 4. Monitoring & Health Checks

```python
from django.utils import timezone
from datetime import timedelta

class Exchange(models.Model):
    # ... fields ...
    last_health_check = models.DateTimeField(null=True)
    health_status = models.CharField(
        max_length=20,
        choices=[
            ('healthy', 'Healthy'),
            ('degraded', 'Degraded'),
            ('down', 'Down'),
        ],
        default='healthy'
    )

    def check_health(self):
        """Perform health check on exchange API."""
        try:
            response = requests.get(
                f"{self.api_endpoint}/ping",
                timeout=5
            )

            if response.status_code == 200:
                self.health_status = 'healthy'
            else:
                self.health_status = 'degraded'

        except RequestException:
            self.health_status = 'down'

        finally:
            self.last_health_check = timezone.now()
            self.save()
```

---

## Performance Optimization

### Caching

```python
from django.core.cache import cache

def get_exchange_fees(exchange_code):
    """Get exchange fees with caching."""
    cache_key = f'exchange_fees_{exchange_code}'
    fees = cache.get(cache_key)

    if not fees:
        exchange = Exchange.objects.get(code=exchange_code)
        fees = {
            'trading': exchange.trading_fee_percentage,
            'withdrawal': exchange.withdrawal_fee_percentage
        }
        cache.set(cache_key, fees, timeout=3600)  # 1 hour

    return fees
```

### Database Indexes

```python
class Meta:
    indexes = [
        models.Index(fields=['code']),
        models.Index(fields=['is_active', 'is_verified']),
        models.Index(fields=['trading_fee_percentage']),
    ]
```

---

## Testing

```python
from django.test import TestCase
from apps.crypto.models import Exchange

class ExchangeTestCase(TestCase):
    def setUp(self):
        self.exchange = Exchange.objects.create(
            name="Test Exchange",
            code="TEST",
            slug="test-exchange",
            trading_fee_percentage=0.1,
            withdrawal_fee_percentage=0.05
        )

    def test_fee_calculation(self):
        """Test trading fee calculation."""
        amount = Decimal('1000.00')
        fee = self.exchange.calculate_trading_fee(amount)
        self.assertEqual(fee, Decimal('1.00'))

    def test_unique_code(self):
        """Test exchange code must be unique."""
        with self.assertRaises(IntegrityError):
            Exchange.objects.create(
                name="Duplicate",
                code="TEST",  # Same code
                slug="duplicate"
            )
```

---

## Related Models

- **TradingPair**: Available trading pairs on exchange
- **Order**: User orders placed on exchange
- **Transaction**: Deposits/withdrawals from exchange
- **PriceHistory**: Historical price data from exchange

---

## Troubleshooting

### Common Issues

**Problem**: API connection timeout
- **Solution**: Check `api_endpoint` and firewall settings
- **Check**: Verify exchange API status page

**Problem**: Invalid API credentials
- **Solution**: Regenerate API keys and update in admin
- **Check**: Ensure API permissions are correctly set

**Problem**: Fee calculations incorrect
- **Solution**: Verify `trading_fee_percentage` format (use 0.1 for 0.1%, not 10)

---

## Changelog

- **v1.0** - Initial exchange model
- **v1.1** - Added API credential encryption
- **v1.2** - Added health check functionality
- **v2.0** - Integrated with django-cfg admin system
- **v2.1** - Added margin and futures support flags
