# Environment Configuration

Environment configuration system for Django CFG with **priority chain** loading.

## 🔄 Loading Strategy

**Priority order (highest to lowest):**

1. **Environment Variables** (from `.env` file or system)
2. **YAML Config** (environment-specific)
3. **Default Values** (in Pydantic models)

```
ENV > YAML > Defaults
```

## 📁 Files

- **`.env`** - Local environment variables (secrets, API keys) ⚠️ **NEVER COMMIT**
- **`.env.example`** - Template for `.env` file (safe to commit)
- **`config.dev.yaml`** - Development environment config
- **`config.prod.yaml`** - Production environment config
- **`config.test.yaml`** - Test environment config
- **`loader.py`** - Configuration loader with priority chain

## 🚀 Quick Start

### 1. Create `.env` file

```bash
# Copy example file
cp .env.example .env

# Edit with your actual values
nano .env
```

### 2. Configure environment variables

```bash
# .env
API_KEYS__OPENAI="sk-proj-your-key-here"
EMAIL__HOST="smtp.gmail.com"
EMAIL__PASSWORD="your-password"
TELEGRAM__BOT_TOKEN="your-bot-token"
```

### 3. Use in your code

```python
from api.environment import env

# Access configuration
print(env.api_keys.openai)      # From .env
print(env.email.host)            # From .env or YAML
print(env.database.url)          # From YAML
```

## 🔧 How It Works

### Priority Chain Example

**Scenario:** Configure email host

**1. Default (loader.py:36-38)**
```python
class EmailConfig(BaseModel):
    host: str = "localhost"  # ← Default value
```

**2. YAML Override (config.dev.yaml)**
```yaml
email:
  host: "mail.example.com"  # ← YAML overrides default
```

**3. ENV Override (.env)**
```
EMAIL__HOST="smtp.gmail.com"  # ← ENV wins!
```

**Result:** `env.email.host = "smtp.gmail.com"` ✅

### Environment Variable Notation

Use `__` (double underscore) to navigate nested config:

```bash
# Flat values
SECRET_KEY="my-secret"
DEBUG="true"

# Nested values (__ = dot notation)
EMAIL__HOST="smtp.gmail.com"              # → env.email.host
EMAIL__PORT=465                            # → env.email.port
API_KEYS__OPENAI="sk-..."                 # → env.api_keys.openai
PAYMENTS_API_KEYS__NOWPAYMENTS_API_KEY="..." # → env.payments_api_keys.nowpayments_api_key
TELEGRAM__BOT_TOKEN="123:ABC"             # → env.telegram.bot_token
TELEGRAM__CHAT_ID=-12345                  # → env.telegram.chat_id
```

### Type Conversion

Loader automatically converts types:

```bash
# Boolean
DEBUG="true"         # → bool: True
EMAIL__USE_TLS="1"   # → bool: True
EMAIL__USE_SSL="no"  # → bool: False

# Integer
EMAIL__PORT=465      # → int: 465
TELEGRAM__CHAT_ID=-796503018  # → int: -796503018

# String (default)
EMAIL__HOST="smtp.gmail.com"  # → str: "smtp.gmail.com"
API_KEYS__OPENAI="sk-..."     # → str: "sk-..."
```

## 📦 Configuration Structure

```python
EnvironmentConfig
├── secret_key: str
├── debug: bool
├── database: DatabaseConfig
│   └── url: str
├── email: EmailConfig
│   ├── backend: str
│   ├── host: str
│   ├── port: int
│   ├── username: str
│   ├── password: str
│   ├── use_tls: bool
│   ├── use_ssl: bool
│   └── default_from: str
├── telegram: TelegramConfig
│   ├── bot_token: str
│   └── chat_id: int
├── api_keys: ApiKeysConfig
│   ├── openrouter: str
│   └── openai: str
├── payments_api_keys: PaymentsApiKeysConfig
│   ├── nowpayments_api_key: str
│   ├── nowpayments_ipn_secret: str
│   └── nowpayments_sandbox_mode: bool
├── app: AppConfig
│   ├── name: str
│   ├── domain: str
│   ├── api_url: str
│   ├── site_url: str
│   └── ...
├── rpc: RPCConfig
│   ├── enabled: bool
│   ├── redis_url: str
│   └── ...
└── env: EnvironmentMode
    ├── is_dev: bool
    ├── is_prod: bool
    ├── is_test: bool
    └── env_mode: str
```

## 🌍 Environment Modes

Set environment mode with variables:

```bash
# Development (default)
IS_DEV=true

# Production
IS_PROD=true

# Test
IS_TEST=true
```

**Config file selection:**
- `IS_PROD=true` → `config.prod.yaml`
- `IS_TEST=true` → `config.test.yaml`
- Default → `config.dev.yaml`

## 🔐 Security Best Practices

### ✅ DO:

1. **Add `.env` to `.gitignore`** (already done ✅)
2. **Use `.env.example`** as template
3. **Store secrets in `.env`** only
4. **Never commit** real API keys
5. **Use environment variables** in production (Docker, Kubernetes)

### ❌ DON'T:

1. **Don't commit `.env`** to git
2. **Don't hardcode** API keys in YAML
3. **Don't share** `.env` file
4. **Don't use** weak secrets in production

## 📝 Examples

### Example 1: Development Setup

```bash
# .env
IS_DEV=true
DEBUG=true

# Use local services
EMAIL__BACKEND="console"
DATABASE__URL="postgresql://localhost/djangocfg_dev"

# Real API keys (for testing)
API_KEYS__OPENAI="sk-proj-your-dev-key"
TELEGRAM__BOT_TOKEN="123:ABC-dev-bot"
```

### Example 2: Production Setup

```bash
# .env
IS_PROD=true
DEBUG=false
SECRET_KEY="production-secret-key-minimum-50-chars"

# Production services
EMAIL__BACKEND="smtp"
EMAIL__HOST="smtp.sendgrid.net"
EMAIL__USERNAME="${SENDGRID_USERNAME}"
EMAIL__PASSWORD="${SENDGRID_API_KEY}"

# Production database (from cloud provider)
DATABASE__URL="${DATABASE_URL}"

# Production API keys
API_KEYS__OPENAI="${OPENAI_API_KEY}"
PAYMENTS_API_KEYS__NOWPAYMENTS_API_KEY="${NOWPAYMENTS_KEY}"
```

### Example 3: Docker Deployment

```yaml
# docker-compose.yml
services:
  django:
    environment:
      # Pass from host environment or secrets
      - IS_PROD=true
      - SECRET_KEY=${SECRET_KEY}
      - DATABASE__URL=postgresql://postgres:${DB_PASSWORD}@db:5432/djangocfg
      - EMAIL__HOST=${EMAIL_HOST}
      - EMAIL__PASSWORD=${EMAIL_PASSWORD}
      - API_KEYS__OPENAI=${OPENAI_API_KEY}
      - TELEGRAM__BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
```

## 🐛 Troubleshooting

### Problem: Variables not loading

**Solution:** Check loading output on startup:

```
✅ Loaded environment variables from: /path/to/.env
Loading config file: config.dev.yaml
✅ Environment variables applied (5): API_KEYS__OPENAI, EMAIL__HOST, ...
```

### Problem: Wrong value used

**Check priority chain:**

1. Is it in `.env`? → Should win
2. Is it in YAML? → Second priority
3. Check default in `loader.py`

### Problem: Type conversion error

**Example:**
```bash
# ❌ Wrong
EMAIL__PORT="465"  # String "465"

# ✅ Correct
EMAIL__PORT=465    # Integer 465 (no quotes)
```

### Problem: Nested config not working

**Example:**
```bash
# ❌ Wrong (single underscore)
API_KEYS_OPENAI="sk-..."

# ✅ Correct (double underscore)
API_KEYS__OPENAI="sk-..."
```

## 📚 Dependencies

- `pydantic` - Data validation
- `pydantic-yaml` - YAML file parsing
- `python-dotenv` - `.env` file loading (optional but recommended)

Install:
```bash
pip install pydantic pydantic-yaml python-dotenv
```

## 🔍 Debugging

Enable verbose output:

```python
# loader.py already prints:
print(f"✅ Loaded environment variables from: {env_path}")
print(f"Loading config file: {config_file}")
print(f"✅ Environment variables applied (5): EMAIL__HOST, ...")
```

Check loaded values:

```python
from api.environment import env

# Print all config
print(env.model_dump())

# Check specific values
print(f"Email host: {env.email.host}")
print(f"API key: {env.api_keys.openai[:10]}...")  # Show first 10 chars
```

## 📖 See Also

- [Pydantic Documentation](https://docs.pydantic.dev/)
- [python-dotenv Documentation](https://github.com/theskumar/python-dotenv)
- [12-Factor App - Config](https://12factor.net/config)
