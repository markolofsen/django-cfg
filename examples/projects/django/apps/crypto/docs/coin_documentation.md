# Coin Model Documentation

## Overview

The `Coin` model represents cryptocurrency assets in the system. It tracks market data, pricing information, and trading status for various cryptocurrencies.

## Key Features

- **Real-time Market Data**: Track current price, market cap, and 24h volume
- **Trading Status**: Monitor which coins are active and tradeable
- **Ranking System**: Keep track of market cap rankings
- **Slug-based URLs**: SEO-friendly URLs for each coin

## Model Fields

### Basic Information

| Field | Type | Description |
|-------|------|-------------|
| `symbol` | CharField | Coin ticker symbol (e.g., BTC, ETH) |
| `name` | CharField | Full name of the cryptocurrency |
| `slug` | SlugField | URL-friendly identifier |
| `description` | TextField | Detailed information about the coin |

### Market Data

| Field | Type | Description |
|-------|------|-------------|
| `current_price_usd` | DecimalField | Current price in USD |
| `market_cap_usd` | DecimalField | Total market capitalization |
| `volume_24h_usd` | DecimalField | 24-hour trading volume |
| `rank` | IntegerField | Market cap ranking |

### Status Flags

- **`is_active`**: Whether the coin is currently active in the system
- **`is_tradeable`**: Whether trading is enabled for this coin

## Usage Examples

### Creating a New Coin

```python
from apps.crypto.models import Coin

# Create Bitcoin
btc = Coin.objects.create(
    symbol="BTC",
    name="Bitcoin",
    slug="bitcoin",
    description="The first and most popular cryptocurrency",
    current_price_usd=45000.00,
    market_cap_usd=850000000000,
    volume_24h_usd=25000000000,
    rank=1,
    is_active=True,
    is_tradeable=True
)
```

### Querying Coins

```python
# Get top 10 coins by market cap
top_coins = Coin.objects.filter(is_active=True).order_by('rank')[:10]

# Get all tradeable coins
tradeable_coins = Coin.objects.filter(is_tradeable=True)

# Search by symbol
bitcoin = Coin.objects.get(symbol='BTC')
```

## API Integration

The Coin model is exposed through REST API endpoints:

- `GET /api/coins/` - List all coins
- `GET /api/coins/{slug}/` - Retrieve specific coin
- `POST /api/coins/` - Create new coin (admin only)
- `PATCH /api/coins/{slug}/` - Update coin data
- `DELETE /api/coins/{slug}/` - Delete coin (admin only)

## Best Practices

1. **Always use slug for URLs**: Instead of exposing database IDs, use the slug field for SEO-friendly URLs
2. **Keep market data updated**: Implement regular updates from market data providers
3. **Validate symbol uniqueness**: Ensure each symbol is unique across the system
4. **Cache expensive queries**: Market data queries can be cached for better performance

## Related Models

- **Wallet**: Users can have wallets for each coin
- **Exchange**: Coins can be traded on various exchanges
- **Transaction**: Track coin transfers and trades

## Security Considerations

⚠️ **Important Security Notes:**

- Only administrators should be able to create/delete coins
- Market data updates should come from verified sources
- Validate all price inputs to prevent manipulation
- Implement rate limiting on API endpoints

## Performance Tips

💡 **Optimization Strategies:**

1. Use `select_related()` when querying with related models
2. Cache frequently accessed coin data (top 100 coins)
3. Index the `rank` field for faster sorting
4. Use database triggers for automatic timestamp updates

## Troubleshooting

### Common Issues

**Problem**: Coin prices not updating
- **Solution**: Check your market data API credentials and rate limits

**Problem**: Duplicate symbols
- **Solution**: Ensure unique constraint on symbol field in database

**Problem**: Slow queries on coin list
- **Solution**: Add database indexes on commonly filtered fields (is_active, is_tradeable, rank)

## Version History

- **v1.0** - Initial implementation with basic market data
- **v1.1** - Added slug field for SEO optimization
- **v1.2** - Added is_tradeable flag for trading controls
- **v2.0** - Integrated with django-cfg admin system
