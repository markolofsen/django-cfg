# Payment Management Commands

Optimized management commands for Django CFG payments system.

## Available Commands

### 1. `manage_currencies` - Currency and Rate Management

Universal command for all currency-related operations.

#### Usage Examples:

```bash
# Update USD exchange rates only
python manage.py manage_currencies --rates-only

# Update specific currency rate
python manage.py manage_currencies --rates-only --currency ETH

# Initial population (empty database)
python manage.py manage_currencies --populate

# Full update with fresh rates
python manage.py manage_currencies --force

# Dry run to see what would be updated
python manage.py manage_currencies --dry-run

# Limit number of currencies processed
python manage.py manage_currencies --populate --max-crypto 100 --max-fiat 20
```

#### Options:
- `--populate` - Initial population mode for empty database
- `--rates-only` - Only update USD exchange rates  
- `--currency CODE` - Update specific currency (e.g., BTC, ETH)
- `--force` - Force refresh all data even if fresh
- `--dry-run` - Show what would be done without changes
- `--max-crypto N` - Limit crypto currencies (default: 200)
- `--max-fiat N` - Limit fiat currencies (default: 50)

---

### 2. `manage_providers` - Payment Provider Management

Universal command for all provider-related operations.

#### Usage Examples:

```bash
# Sync all active providers
python manage.py manage_providers

# Sync specific provider
python manage.py manage_providers --provider nowpayments

# Sync multiple providers
python manage.py manage_providers --provider nowpayments,cryptomus

# Sync providers + update USD rates
python manage.py manage_providers --with-rates

# Show provider statistics
python manage.py manage_providers --stats

# Dry run to see what would be synced
python manage.py manage_providers --dry-run --verbose
```

#### Options:
- `--provider NAME` - Specific provider(s) to sync (comma-separated)
- `--all` - Sync all available providers
- `--with-rates` - Also update USD exchange rates after sync
- `--stats` - Show provider statistics
- `--dry-run` - Show what would be synced without changes
- `--verbose` - Show detailed progress information

---

### 3. `currency_stats` - Statistics and Reports

Display currency database statistics and health information.

#### Usage Examples:

```bash
# Basic statistics
python manage.py currency_stats

# Detailed breakdown
python manage.py currency_stats --detailed

# Top currencies by value
python manage.py currency_stats --top 10

# Check rate freshness
python manage.py currency_stats --check-rates
```

---

## Migration from Old Commands

| Old Command | New Command |
|-------------|-------------|
| `populate_currencies` | `manage_currencies --populate` |
| `update_currencies` | `manage_currencies` |
| `update_currency_rates` | `manage_currencies --rates-only` |
| `sync_providers` | `manage_providers` |
| `currency_stats` | `currency_stats` (unchanged) |

## Automation Examples

### Daily Rate Updates (Crontab)
```bash
# Update rates every 6 hours
0 */6 * * * cd /path/to/project && python manage.py manage_currencies --rates-only

# Sync providers once daily
0 2 * * * cd /path/to/project && python manage.py manage_providers --with-rates
```

### Initial Setup
```bash
# 1. Populate base currencies
python manage.py manage_currencies --populate

# 2. Sync payment providers
python manage.py manage_providers

# 3. Check statistics
python manage.py manage_providers --stats
python manage.py currency_stats
```

---

## Features

- **🚀 Fast**: Optimized database queries and caching
- **📊 Progress**: Real-time progress reporting and statistics  
- **🔄 Atomic**: Transaction safety with rollback on errors
- **🎯 Flexible**: Multiple operation modes and options
- **📈 Pydantic**: Full type safety with Pydantic models
- **🛡️ Safe**: Dry-run mode for testing changes
- **📝 Verbose**: Detailed logging and error reporting