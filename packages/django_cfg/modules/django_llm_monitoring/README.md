# Django LLM Monitoring

Professional monitoring system for LLM provider account balances with automatic admin notifications via Email and Telegram.

## Features

- ✅ **Multi-provider Support**: OpenAI, OpenRouter (easily extensible)
- ✅ **Smart Balance Checking**:
  - OpenAI: API key validation (no public balance API available)
  - OpenRouter: Real prepaid balance tracking via `/api/v1/credits`
- ✅ **Type-Safe**: Pydantic v2 models for all responses
- ✅ **Modular Architecture**: Provider-specific implementations in `providers/`
- ✅ **Intelligent Caching**: 1-hour TTL for balance checks, 24-hour for notifications
- ✅ **Two-Tier Threshold System**:
  - **WARNING**: $10 USD - early warning notification
  - **CRITICAL**: $5 USD - critical alert
- ✅ **Multi-Channel Notifications**: Email + Telegram via `send_admin_notification()`
- ✅ **Anti-Spam Protection**: One notification per level per 24 hours
- ✅ **API Error Alerts**: Automatic notifications for invalid keys, quota exceeded, etc.
- ✅ **Async Telegram Queue**: Rate-limited message delivery (20 msg/sec)
- ✅ **Management Command**: Easy cron integration

## Installation

Module is built into `django-cfg`. Required dependencies:

```bash
pip install httpx openai pyTelegramBotAPI
```

Or with poetry:

```bash
poetry add httpx openai pyTelegramBotAPI
```

## Quick Start

### 1. Configure API Keys

```python
# api/config.py
from django_cfg import DjangoConfig, ApiKeys

class MyConfig(DjangoConfig):
    # API Keys
    api_keys: ApiKeys = ApiKeys(
        openai=env.api_keys.openai,
        openrouter=env.api_keys.openrouter,
    )

    # Admin Notifications
    admin_emails: list[str] = ["admin@example.com", "devops@example.com"]

    # Telegram (optional but recommended)
    telegram: TelegramConfig = TelegramConfig(
        bot_token=env.telegram.bot_token,
        chat_id=env.telegram.chat_id,
    )
```

Environment file (`.env` or `.env.secrets`):

```env
# API Keys
API_KEYS__OPENAI=sk-proj-...
API_KEYS__OPENROUTER=sk-or-v1-...

# Admin Emails (comma-separated or JSON array)
ADMIN_EMAILS=["admin@example.com"]

# Telegram
TELEGRAM__BOT_TOKEN=123456:ABC-DEF...
TELEGRAM__CHAT_ID=-1001234567890
```

### 2. Run Balance Check

```bash
# Normal check (with caching)
python manage.py check_llm_balance

# Force fresh API calls (bypass cache)
python manage.py check_llm_balance --force

# Force send notifications (bypass 24h cache)
python manage.py check_llm_balance --force-notify
```

### 3. Set Up Cron (Recommended)

```cron
# Check balances every hour
0 * * * * cd /path/to/project && /path/to/venv/bin/python manage.py check_llm_balance
```

## Usage

### Management Command

```bash
# Normal check
poetry run python manage.py check_llm_balance

# Output:
# ======================================================================
# LLM BALANCE CHECK
# ======================================================================
#
# Checking balances...
#
#   Openai: API Key Valid ✓ (Balance check not available via API...)
#   Openrouter: $0.69 USD 🚨 CRITICAL [limit: $217.50, usage: $216.81]
#
# Checking notification thresholds...
#   🚨 Sent CRITICAL notification: Openrouter
#
# ======================================================================
# CHECK COMPLETE
# ======================================================================
# Total balance across all providers: $0.69 USD
#
# ⚠️ Low balance alerts were sent to administrators
#
# Waiting for notification delivery...
# ✓ Notifications delivered
```

**Command Options:**

- `--force`: Bypass balance cache, fetch fresh data from API
- `--force-notify`: Force send notifications even if sent recently

### Programmatic Usage

```python
from django_cfg.modules.django_llm_monitoring import BalanceChecker, LLMBalanceNotifier

# Check balances
checker = BalanceChecker()
balances = checker.check_all_balances(force=False)

# Access balance data (Pydantic models)
for provider, balance_data in balances.items():
    print(f"{provider}:")
    print(f"  Balance: ${balance_data.balance}")
    print(f"  Status: {balance_data.status}")
    print(f"  Error: {balance_data.error}")
    print(f"  Note: {balance_data.note}")

# Send notifications if thresholds exceeded
notifier = LLMBalanceNotifier()
results = notifier.check_all_and_notify(balances, force=False)

# Check what was sent
for provider, level in results.items():
    if level:
        print(f"Sent {level} notification for {provider}")
```

### Using Individual Providers

```python
from django_cfg.modules.django_llm_monitoring.providers import (
    OpenAIProvider,
    OpenRouterProvider,
)

# OpenAI - validates API key
openai_provider = OpenAIProvider()
result = openai_provider.check_balance(force=True)

if result.status == "valid":
    print("OpenAI API key is valid")
else:
    print(f"OpenAI error: {result.error}")

# OpenRouter - checks real prepaid balance
openrouter_provider = OpenRouterProvider()
result = openrouter_provider.check_balance(force=True)

print(f"Balance: ${result.balance}")
print(f"Total credits: ${result.limit}")
print(f"Total usage: ${result.usage}")
```

## Configuration

### Admin Emails

Notifications are sent to all addresses in `config.admin_emails`:

```python
# api/config.py
class MyConfig(DjangoConfig):
    admin_emails: list[str] = env.admin_emails
```

```env
# .env
ADMIN_EMAILS=["admin@example.com", "devops@example.com"]
```

### Telegram Configuration

For Telegram notifications:

```python
# api/config.py
from django_cfg import TelegramConfig

class MyConfig(DjangoConfig):
    telegram: TelegramConfig = TelegramConfig(
        bot_token=env.telegram.bot_token,
        chat_id=env.telegram.chat_id,
    )
```

```env
# .env
TELEGRAM__BOT_TOKEN=*********
TELEGRAM__CHAT_ID=-00000000
```

**How to get Telegram credentials:**

1. **Bot Token**: Create bot via [@BotFather](https://t.me/botfather)
   - Send `/newbot` command
   - Follow instructions
   - Copy token (format: `123456:ABC-DEF...`)

2. **Chat ID**:
   - For private chat: Use [@userinfobot](https://t.me/userinfobot)
   - For group chat: Add [@raw_data_bot](https://t.me/raw_data_bot), get `chat.id`
   - For channel: Channel ID (starts with `-100`)

### Notification Thresholds

Default thresholds can be customized:

```python
from django_cfg.modules.django_llm_monitoring import LLMBalanceNotifier

# Customize thresholds
LLMBalanceNotifier.THRESHOLD_WARNING = 20.0   # $20 USD
LLMBalanceNotifier.THRESHOLD_CRITICAL = 10.0  # $10 USD
```

Or modify in `notifier.py`:

```python
class LLMBalanceNotifier:
    THRESHOLD_WARNING = 20.0   # Default: 10.0
    THRESHOLD_CRITICAL = 10.0  # Default: 5.0
```

### Cache TTL

**Balance Cache** (1 hour by default):

```python
# providers/base.py
class BaseLLMProvider:
    CACHE_TTL = 60 * 60 * 2  # Change to 2 hours
```

**Notification Cache** (24 hours by default):

```python
# notifier.py (line 50)
cache.set(cache_key, True, 60 * 60 * 48)  # Change to 48 hours
```

## API Endpoints

### OpenAI

**Endpoint**: No public balance API available

**Workaround**: Validate API key via test request

```python
# providers/openai.py
client = OpenAI(api_key=api_key)
models = client.models.list()  # Validates key

# Returns:
BalanceResponse(
    balance=None,  # Not available
    status="valid",
    note="Balance check not available via API. Check manually at: ..."
)
```

**Manual Check**: https://platform.openai.com/settings/organization/billing/overview

### OpenRouter

**Endpoint**: `GET https://openrouter.ai/api/v1/credits`

**Headers**:
```
Authorization: Bearer YOUR_OPENROUTER_KEY
```

**Response**:
```json
{
  "data": {
    "total_credits": 217.50,
    "total_usage": 216.81
  }
}
```

**Calculated Balance**:
```python
balance = total_credits - total_usage  # $0.69
```

## Notification Format

### Email Notification

**Subject**: `🚨 CRITICAL: Openrouter Balance Low`

**Body**:
```
🚨 Openrouter API Balance Alert

Current Balance: $0.69 USD
Threshold: $5.00 USD

Please add funds to your Openrouter account to avoid service interruption.

---
This is an automated alert from LLM Balance Monitoring.
You will receive this notification once per 24 hours until the balance is restored.
```

### Telegram Notification

Same message with Markdown formatting:

```markdown
*🚨 CRITICAL: Openrouter Balance Low*

🚨 Openrouter API Balance Alert

Current Balance: $0.69 USD
Threshold: $5.00 USD

Please add funds to your Openrouter account to avoid service interruption.

---
This is an automated alert from LLM Balance Monitoring.
You will receive this notification once per 24 hours until the balance is restored.
```

### API Error Notifications

When API key errors occur:

**Subject**: `🔴 CRITICAL: OpenAI API Key Error`

**Body**:
```
🔴 OpenAI API Key Error

Error: Incorrect API key provided

This is a critical issue that requires immediate attention:
- Check if the API key is valid and correctly configured
- Verify the API key has not expired
- Ensure sufficient funds are available in the account

Configuration location:
- Check .env or .env.secrets file
- Verify API_KEYS__OPENAI environment variable

---
This is an automated alert from LLM Balance Monitoring.
You will receive this notification once per 24 hours until the issue is resolved.
```

## Architecture

```
django_llm_monitoring/
├── __init__.py                    # Exports: BalanceChecker, LLMBalanceNotifier
├── models.py                      # Pydantic models (BalanceResponse)
├── balance_checker.py             # Main checker (uses providers)
├── notifier.py                    # Threshold checks + notifications
├── README.md                      # This file
├── providers/
│   ├── __init__.py               # Export all providers
│   ├── base.py                   # BaseLLMProvider (caching, error handling)
│   ├── openai.py                 # OpenAIProvider (key validation)
│   └── openrouter.py             # OpenRouterProvider (balance check)
└── management/
    └── commands/
        └── check_llm_balance.py  # Django management command
```

### Pydantic Models

```python
# models.py
class BalanceResponse(BaseModel):
    balance: Optional[float] = None      # USD balance (None if unavailable)
    currency: str = "usd"                # Currency code
    usage: Optional[float] = None        # Total usage
    limit: Optional[float] = None        # Total limit/credits
    status: Optional[Literal["valid", "invalid", "error", "unavailable"]] = None
    note: Optional[str] = None           # Additional information
    error: Optional[str] = None          # Error message if check failed
```

## How It Works

### 1. Balance Checking Flow

```
┌─────────────────────────────────────────────────┐
│  Management Command / Programmatic Call         │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│  BalanceChecker.check_all_balances()            │
│  - Iterates through all providers               │
│  - Uses caching (1 hour TTL)                    │
└─────────────────┬───────────────────────────────┘
                  │
      ┌───────────┴──────────┐
      │                      │
      ▼                      ▼
┌──────────────┐      ┌─────────────────┐
│ OpenAI       │      │ OpenRouter      │
│ Provider     │      │ Provider        │
│              │      │                 │
│ - Validate   │      │ - GET /credits  │
│   API key    │      │ - Calculate     │
│ - Return     │      │   balance       │
│   status     │      │                 │
└──────┬───────┘      └────────┬────────┘
       │                       │
       └───────────┬───────────┘
                   │
                   ▼
         ┌─────────────────┐
         │ BalanceResponse │
         │ (Pydantic)      │
         └─────────────────┘
```

### 2. Notification Flow

```
┌─────────────────────────────────────────────────┐
│  LLMBalanceNotifier.check_all_and_notify()      │
│  - For each provider balance                    │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
         ┌────────────────┐
         │ Check Balance  │──Yes──▶ Skip (balance OK)
         │ > $10 USD?     │
         └────────┬───────┘
                  │ No
                  ▼
         ┌────────────────────┐
         │ Check Cache        │──Yes──▶ Skip (sent recently)
         │ (24h anti-spam)    │
         └────────┬───────────┘
                  │ No
                  ▼
         ┌─────────────────────────────────────┐
         │ send_admin_notification()           │
         │ - Email: send_admin_email()         │
         │ - Telegram: send_telegram_message() │
         └────────┬────────────────────────────┘
                  │
      ┌───────────┴───────────┐
      │                       │
      ▼                       ▼
┌──────────┐         ┌─────────────────┐
│  Email   │         │ Telegram Queue  │
│  Queue   │         │ (async worker)  │
└──────────┘         │ - Rate limit    │
                     │ - 20 msg/sec    │
                     └─────────────────┘
```

### 3. Telegram Queue System

The Telegram notification system uses an asynchronous queue with rate limiting:

**Key Features:**
- **Singleton Queue**: Global instance shared across all Django processes
- **Worker Thread**: Background daemon thread processes queue continuously
- **Rate Limiting**: Max 20 messages/second (0.05s delay between messages)
- **Priority Support**: CRITICAL (1) > HIGH (2) > NORMAL (3) > LOW (4)
- **Auto-Cleanup**: Drops low-priority messages when queue is full
- **Management Command Wait**: 2-second delay ensures delivery before exit

**Why the Delay?**

Management commands exit immediately after execution. Without the 2-second wait, the worker thread might not have time to process the queue before the Python process terminates.

```python
# check_llm_balance.py (line 142)
if notifications_sent:
    time.sleep(2)  # Give queue worker time to send messages
```

## Logging

Module uses logger `django_cfg.llm_monitoring`:

```python
import logging

# Enable debug logging
logging.getLogger("django_cfg.llm_monitoring").setLevel(logging.DEBUG)
```

**Example Logs:**

```
[INFO] Fetching Openai balance from API
[INFO] Openai API key status: valid
[INFO] Fetching Openrouter balance from API
[INFO] Openrouter balance: $0.69
[INFO] Sent critical notification for openrouter (email: True, telegram: True)
[DEBUG] Skipping critical notification for openrouter - already sent in last 24h
[DEBUG] Telegram message queued with priority 3 (size: 1/1000)
[DEBUG] Processed telegram message with priority 3
```

## Troubleshooting

### Notifications Not Arriving in Telegram

**Symptoms**: Command shows "Sent notification" but no Telegram message

**Solutions**:

1. **Check Bot Token & Chat ID**:
   ```bash
   python manage.py shell -c "
   from django_cfg.core.config import get_current_config
   config = get_current_config()
   print('Telegram config:', config.telegram)
   "
   ```

2. **Test Direct Send**:
   ```bash
   python manage.py shell -c "
   from django_cfg.modules.django_telegram import send_telegram_message
   result = send_telegram_message('Test message')
   print('Sent:', result)
   import time; time.sleep(2)  # Wait for queue
   "
   ```

3. **Check Queue Stats**:
   ```python
   from django_cfg.modules.django_telegram.service import _telegram_queue
   print(_telegram_queue.get_stats())
   ```

4. **Verify Bot Has Access**:
   - For groups: Bot must be added as member
   - For channels: Bot must be admin
   - Check bot is not blocked

### Notifications Cached (Not Sending)

**Symptoms**: Balance is low but no notifications sent

**Cause**: Notifications were sent in last 24 hours

**Solutions**:

1. **Force Send**:
   ```bash
   python manage.py check_llm_balance --force-notify
   ```

2. **Clear Cache Manually**:
   ```python
   from django.core.cache import cache
   for provider in ['openai', 'openrouter']:
       for level in ['warning', 'critical', 'api_error']:
           cache.delete(f'llm_monitoring:notification_sent:{provider}:{level}')
   ```

### OpenAI Shows $0.00 Balance

**This is expected!** OpenAI does not provide a public balance API.

The module validates the API key and returns:
```python
BalanceResponse(
    balance=None,  # Not $0.00, but None
    status="valid",
    note="Balance check not available via API..."
)
```

**To check real balance**: Visit https://platform.openai.com/settings/organization/billing/overview

### API Key Errors

**Error**: `Incorrect API key provided`

**Solutions**:
1. Verify key in `.env` file
2. Check key format (OpenAI: `sk-proj-...`, OpenRouter: `sk-or-v1-...`)
3. Ensure key has not expired
4. Test key manually via provider's dashboard

**Error**: `Insufficient funds`

This means the account balance is depleted. Add funds to the provider account.

### HTTP Request Errors

**Error**: `Connection timeout`

**Solutions**:
- Check internet connection
- Verify firewall allows HTTPS to api.openai.com / openrouter.ai
- Try manual curl request to test connectivity

## Extension

### Adding a New Provider

**Example: Adding Anthropic**

#### 1. Create Provider Class

```python
# providers/anthropic.py
import httpx
from .base import BaseLLMProvider
from ..models import BalanceResponse

class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude balance checker."""

    API_URL = "https://api.anthropic.com/v1/organization/balance"

    def get_provider_name(self) -> str:
        return "anthropic"

    def _fetch_balance(self) -> BalanceResponse:
        """Fetch balance from Anthropic API."""
        from django_cfg.core.config import get_current_config

        config = get_current_config()
        api_key = config.api_keys.anthropic

        if hasattr(api_key, 'get_secret_value'):
            api_key = api_key.get_secret_value()

        client = httpx.Client()
        response = client.get(
            self.API_URL,
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            },
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()

        return BalanceResponse(
            balance=data.get("balance"),
            currency="usd",
            limit=data.get("limit"),
            usage=data.get("usage")
        )
```

#### 2. Export Provider

```python
# providers/__init__.py
from .anthropic import AnthropicProvider

__all__ = [
    # ...
    "AnthropicProvider",
]
```

#### 3. Update Balance Checker

```python
# balance_checker.py
from .providers import OpenAIProvider, OpenRouterProvider, AnthropicProvider

class BalanceChecker:
    def check_all_balances(self, force: bool = False) -> Dict[str, BalanceResponse]:
        providers = {
            "openai": OpenAIProvider(),
            "openrouter": OpenRouterProvider(),
            "anthropic": AnthropicProvider(),  # New
        }

        balances = {}
        for name, provider in providers.items():
            balances[name] = provider.check_balance(force=force)

        return balances
```

#### 4. Add API Key to Config

```python
# django_cfg/core/base/config_model.py
class ApiKeys(BaseModel):
    openai: SecretStr = Field(default=SecretStr(""))
    openrouter: SecretStr = Field(default=SecretStr(""))
    anthropic: SecretStr = Field(default=SecretStr(""))  # New
```

#### 5. Configure in Project

```python
# api/config.py
api_keys: ApiKeys = ApiKeys(
    openai=env.api_keys.openai,
    openrouter=env.api_keys.openrouter,
    anthropic=env.api_keys.anthropic,  # New
)
```

```env
# .env
API_KEYS__ANTHROPIC=sk-ant-...
```

Done! The new provider will be automatically checked.

## Dashboard Integration

The module also provides a REST API endpoint for dashboard integration:

```http
GET /cfg/dashboard/api/metrics/llm-balances/
```

**Response**:
```json
{
  "name": "LLM Provider Balances",
  "description": "API key status and account balances for LLM providers",
  "status": "critical",
  "items": [
    {
      "provider": "openai",
      "provider_display": "Openai",
      "balance": null,
      "currency": "usd",
      "status": "valid",
      "status_level": "info",
      "note": "Balance check not available via API..."
    },
    {
      "provider": "openrouter",
      "provider_display": "Openrouter",
      "balance": 0.69,
      "currency": "usd",
      "usage": 216.81,
      "limit": 217.50,
      "status": null,
      "status_level": "critical"
    }
  ],
  "summary": {
    "total_providers": 2,
    "total_balance": 0.69,
    "providers_with_errors": 0,
    "providers_critical": 1
  }
}
```

See Dashboard Metrics API documentation for more details.

## Best Practices

### Production Deployment

1. **Use Secrets File**: Store API keys in `.env.secrets` (git-ignored)
2. **Set Up Cron**: Run checks hourly with proper logging
3. **Monitor Notifications**: Test Telegram/email delivery monthly
4. **Configure Thresholds**: Adjust based on your usage patterns
5. **Enable Logging**: Set up log aggregation (Sentry, CloudWatch, etc.)

### Cron Setup

```bash
# /etc/cron.d/llm-monitoring
SHELL=/bin/bash
PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin

# Check LLM balances every hour
0 * * * * app cd /app && /app/.venv/bin/python manage.py check_llm_balance >> /var/log/llm-balance.log 2>&1
```

### Docker Integration

```dockerfile
# Dockerfile
RUN pip install httpx openai pyTelegramBotAPI

# Add cron job
COPY cron/llm-monitoring /etc/cron.d/llm-monitoring
RUN chmod 0644 /etc/cron.d/llm-monitoring
RUN crontab /etc/cron.d/llm-monitoring
```

### Testing

```python
# tests/test_llm_monitoring.py
import pytest
from django_cfg.modules.django_llm_monitoring import BalanceChecker, LLMBalanceNotifier

def test_balance_checker():
    checker = BalanceChecker()
    balances = checker.check_all_balances(force=True)

    assert "openai" in balances
    assert "openrouter" in balances

    # OpenAI should return valid status
    assert balances["openai"].status == "valid"

    # OpenRouter should return balance
    assert isinstance(balances["openrouter"].balance, (float, type(None)))

def test_notifier_threshold():
    notifier = LLMBalanceNotifier()

    # Mock low balance
    from django_cfg.modules.django_llm_monitoring.models import BalanceResponse

    low_balance = BalanceResponse(balance=3.0, currency="usd")
    level = notifier.check_and_notify("test", low_balance, force=True)

    assert level == "critical"
```

## Support

For questions, issues, or feature requests:

- **GitHub**: [django-cfg repository](https://github.com/anthropics/django-cfg)
- **Documentation**: [djangocfg.com](https://djangocfg.com)
- **Telegram**: Check module logs for troubleshooting

## License

Part of django-cfg package. See main package license.
