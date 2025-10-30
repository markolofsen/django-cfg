# Wallet Model Documentation

## Overview

The `Wallet` model manages cryptocurrency holdings for users. Each wallet is associated with a specific user and coin, tracking both available and locked balances.

## Purpose

Wallets serve as the primary container for user cryptocurrency holdings, enabling:
- **Balance Management**: Track available and locked funds
- **Multi-currency Support**: Users can have multiple wallets for different coins
- **Transaction History**: All balance changes are recorded
- **Address Management**: Unique blockchain addresses for deposits

## Model Structure

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `user` | ForeignKey | ✅ | Owner of the wallet |
| `coin` | ForeignKey | ✅ | Cryptocurrency type |
| `balance` | DecimalField | ✅ | Available balance |
| `locked_balance` | DecimalField | ✅ | Funds locked in pending orders |
| `address` | CharField | ❌ | Blockchain address |

### Relationships

```python
# One-to-Many relationships
User → Wallet (one user can have many wallets)
Coin → Wallet (one coin can have many wallets)

# Constraints
unique_together = ('user', 'coin')  # One wallet per user per coin
```

## Balance Types

### Available Balance
- Funds that can be used immediately
- Available for trading, withdrawal, or transfer
- Updated in real-time with transactions

### Locked Balance
- Funds reserved for pending operations
- Locked during:
  - Active trading orders
  - Pending withdrawals
  - Staking or lending operations
- Automatically unlocked when operations complete or cancel

## Usage Examples

### Creating a Wallet

```python
from apps.crypto.models import Wallet, Coin
from django.contrib.auth import get_user_model

User = get_user_model()

# Get user and coin
user = User.objects.get(username='john_doe')
bitcoin = Coin.objects.get(symbol='BTC')

# Create wallet
wallet = Wallet.objects.create(
    user=user,
    coin=bitcoin,
    balance=0.5,
    locked_balance=0.0,
    address='1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa'
)
```

### Balance Operations

```python
# Check available balance
available = wallet.balance

# Check total balance (available + locked)
total = wallet.balance + wallet.locked_balance

# Lock funds (e.g., for trading order)
amount_to_lock = Decimal('0.1')
if wallet.balance >= amount_to_lock:
    wallet.balance -= amount_to_lock
    wallet.locked_balance += amount_to_lock
    wallet.save()

# Unlock funds (e.g., order cancelled)
wallet.balance += wallet.locked_balance
wallet.locked_balance = Decimal('0')
wallet.save()
```

### Querying Wallets

```python
# Get all user wallets
user_wallets = Wallet.objects.filter(user=user).select_related('coin')

# Get specific coin wallet
btc_wallet = Wallet.objects.get(user=user, coin__symbol='BTC')

# Get wallets with balance
active_wallets = Wallet.objects.filter(
    user=user,
    balance__gt=0
).select_related('coin')
```

## API Endpoints

### REST API

```http
GET    /api/wallets/           # List user's wallets
GET    /api/wallets/{id}/      # Get specific wallet
POST   /api/wallets/           # Create wallet
PATCH  /api/wallets/{id}/      # Update wallet
DELETE /api/wallets/{id}/      # Delete wallet
```

### Response Example

```json
{
  "id": 1,
  "user": {
    "id": 123,
    "username": "john_doe",
    "email": "john@example.com"
  },
  "coin": {
    "symbol": "BTC",
    "name": "Bitcoin"
  },
  "balance": "0.50000000",
  "locked_balance": "0.10000000",
  "address": "1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T15:45:00Z"
}
```

## Business Rules

### Wallet Creation
1. ✅ Users can create multiple wallets (one per coin)
2. ✅ Automatic wallet creation on first deposit
3. ❌ Cannot create duplicate wallets (user + coin must be unique)
4. ✅ Initial balance can be zero or positive

### Balance Updates
1. ✅ Balance cannot go negative
2. ✅ Locked balance cannot exceed total balance
3. ✅ All balance changes must be logged
4. ✅ Atomic operations for balance transfers

### Security Rules
1. 🔒 Only wallet owner can view/modify their wallet
2. 🔒 Admin can view all wallets (read-only recommended)
3. 🔒 Balance changes require transaction records
4. 🔒 Address generation must be cryptographically secure

## Advanced Features

### Transaction Integration

```python
from apps.crypto.models import Transaction

# Create deposit transaction
transaction = Transaction.objects.create(
    wallet=wallet,
    type='deposit',
    amount=Decimal('1.0'),
    status='completed'
)

# Update wallet balance
wallet.balance += transaction.amount
wallet.save()
```

### Aggregations

```python
from django.db.models import Sum

# Total portfolio value for user
user_total = Wallet.objects.filter(user=user).aggregate(
    total=Sum('balance')
)

# Wallets with locked funds
locked_wallets = Wallet.objects.filter(
    locked_balance__gt=0
).select_related('user', 'coin')
```

## Performance Optimization

### Database Indexes

```python
# Recommended indexes
class Meta:
    indexes = [
        models.Index(fields=['user', 'coin']),
        models.Index(fields=['user', '-created_at']),
        models.Index(fields=['balance']),
    ]
```

### Query Optimization

```python
# ✅ Good - Use select_related
wallets = Wallet.objects.select_related('user', 'coin').all()

# ❌ Bad - N+1 query problem
wallets = Wallet.objects.all()
for wallet in wallets:
    print(wallet.user.username)  # Extra query per wallet
```

### Caching Strategy

```python
from django.core.cache import cache

# Cache user wallets
cache_key = f'user_wallets_{user.id}'
wallets = cache.get(cache_key)

if not wallets:
    wallets = list(Wallet.objects.filter(user=user).select_related('coin'))
    cache.set(cache_key, wallets, timeout=300)  # 5 minutes
```

## Monitoring & Alerts

### Key Metrics

- **Total Wallets**: Track system growth
- **Active Wallets**: Wallets with balance > 0
- **Locked Funds Ratio**: Monitor trading activity
- **Zero Balance Wallets**: Cleanup candidates

### Alert Conditions

⚚ **Set up alerts for:**
- Negative balance attempts
- Unusual balance changes (>$10k in one transaction)
- Failed balance updates
- Orphaned wallets (inactive >90 days)

## Testing Examples

```python
from django.test import TestCase
from apps.crypto.models import Wallet, Coin
from django.contrib.auth import get_user_model

class WalletTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com'
        )
        self.coin = Coin.objects.create(
            symbol='BTC',
            name='Bitcoin'
        )

    def test_wallet_creation(self):
        wallet = Wallet.objects.create(
            user=self.user,
            coin=self.coin,
            balance=1.0
        )
        self.assertEqual(wallet.balance, Decimal('1.0'))

    def test_unique_constraint(self):
        Wallet.objects.create(user=self.user, coin=self.coin)
        with self.assertRaises(IntegrityError):
            Wallet.objects.create(user=self.user, coin=self.coin)
```

## Migration Notes

When updating the Wallet model:

1. **Adding Fields**: Always provide defaults or allow null
2. **Removing Fields**: Create two migrations (deprecate, then remove)
3. **Balance Changes**: Use database transactions
4. **Data Migration**: Create separate data migration file

## Related Documentation

- [Coin Model](./coin_documentation.md)
- [Transaction Model](./transaction_documentation.md)
- [Exchange Model](./exchange_documentation.md)
- [Security Best Practices](#)
- [API Reference](#)
