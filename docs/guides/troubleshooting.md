---
title: Troubleshooting Guide
description: Django-CFG troubleshooting guide. Practical tutorial for troubleshooting guide with real-world examples, troubleshooting tips, and production patterns.
sidebar_label: Troubleshooting
sidebar_position: 10
keywords:
  - django-cfg troubleshooting
  - django-cfg errors
  - fix django-cfg issues
  - django-cfg debugging
---

import { FAQPageSchema } from '@site/src/components/Schema';
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

<FAQPageSchema
  faqs={[
    {
      question: 'How do I fix "ConfigurationError: At least one database must be configured"?',
      answer: 'Add a default database to your configuration. Use DatabaseConfig with at least the default alias. Example: databases = {"default": DatabaseConfig(engine="django.db.backends.sqlite3", name="db.sqlite3")}'
    },
    {
      question: 'How do I fix "ValidationError: SECRET_KEY must be at least 50 characters"?',
      answer: 'Generate a secure secret key using get_random_secret_key() from django.core.management.utils or use an environment variable with "${SECRET_KEY}" placeholder.'
    },
    {
      question: 'How do I fix "ImportError: cannot import name DjangoConfig"?',
      answer: 'Ensure django-cfg is installed with "pip install django-cfg" and use the correct import: "from django_cfg import DjangoConfig" or "from django_cfg.core import DjangoConfig".'
    },
    {
      question: 'Why are my migrations running on the wrong database?',
      answer: 'Use migrate_to parameter in DatabaseConfig to control where migrations run. Example: DatabaseConfig(migrate_to="default") will run migrations on the default database.'
    },
    {
      question: 'How do I fix CORS errors in Django-CFG?',
      answer: 'In production, configure security_domains with allowed origins (e.g., security_domains = ["frontend.example.com"]). In development, CORS is fully open automatically. Django-CFG handles all CORS configuration based on environment mode.'
    },
    {
      question: 'Why are my static files returning 404 in production?',
      answer: 'Run "python manage.py collectstatic --noinput" to collect static files. WhiteNoise is configured automatically in Django-CFG. Check STATIC_ROOT with "python manage.py show_config | grep STATIC".'
    },
    {
      question: 'How do I fix "Tasks not being processed" with ReArq?',
      answer: 'Start the ReArq worker with "rearq main:rearq worker" or specify queues with "rearq main:rearq worker --queues default high_priority". Check worker status with "rearq main:rearq info".'
    },
    {
      question: 'How do I debug configuration issues in Django-CFG?',
      answer: 'Use built-in debug commands: "python manage.py show_config --debug" to display configuration, "python manage.py validate_config --verbose" to validate settings, and "python manage.py check_settings" to check Django settings.'
    },
    {
      question: 'How do I find where RuntimeWarning about database access is coming from?',
      answer: 'Enable debug_warnings in your config (debug_warnings = True) or set DJANGO_CFG_DEBUG_WARNINGS=1. This shows full stack traceback for warnings, helping you identify exactly which file and line is causing the warning.'
    }
  ]}
/>

# Troubleshooting Guide

:::tip[Quick Troubleshooting]
Common issues and solutions when using Django-CFG. Use **Details** to expand specific problems, or search with Ctrl+F.
:::

Common issues and solutions when using django-cfg.

## Configuration Issues

<details>
<summary>**ConfigurationError: At least one database must be configured**</summary>

**Problem:**
```python
django_cfg.core.exceptions.ConfigurationError: At least one database must be configured
```

**Cause:**
No databases defined in configuration.

**Solution:**
```python
from django_cfg import DjangoConfig
from django_cfg.models import DatabaseConfig

class MyConfig(DjangoConfig):
    databases = {
        "default": DatabaseConfig(
            engine="django.db.backends.sqlite3",
            name="db.sqlite3",
        )
    }
```

:::info[Quick Fix]
Django requires at least one database with the alias `"default"`. Even if you don't use a database, configure SQLite as a placeholder.
:::
</details>

<details>
<summary>**ConfigurationError: 'default' database is required**</summary>

**Problem:**
```python
ConfigurationError: 'default' database is required
```

**Cause:**
Databases configured but no 'default' alias.

**Solution:**
```python
databases = {
    "default": DatabaseConfig(...),  # ← Must have 'default'
    "other": DatabaseConfig(...),
}
```

:::warning[Required Alias]
Django always requires a database with the alias `"default"`. You can have additional databases, but `"default"` is mandatory.
:::
</details>

<details>
<summary>**ValidationError: SECRET_KEY must be at least 50 characters**</summary>

**Problem:**
```python
ValidationError: SECRET_KEY must be at least 50 characters long
```

**Solution:**
```python
# Generate a secure secret key
from django.core.management.utils import get_random_secret_key

secret_key = get_random_secret_key()

# Or use environment variable
secret_key = "${SECRET_KEY}"
```

:::danger[Security Critical]
**Never use short or weak SECRET_KEY in production:**
- ❌ "changeme" - Too short and obvious
- ❌ "django-insecure-..." - Development only
- ✅ Generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- ✅ Store in environment variables, never commit to git
:::
</details>

<details>
<summary>**Extra inputs are not permitted**</summary>

**Problem:**
```python
pydantic_core._pydantic_core.ValidationError: Extra inputs are not permitted
```

**Cause:**
Using invalid or non-existent field name in configuration.

**Solution:**
```python
# Ensure you only use valid DjangoConfig fields
class MyConfig(DjangoConfig):
    security_domains = [...]  # ✅ Valid field
    # Check documentation for all available fields
```

:::tip[Finding Valid Fields]
Check available fields in:
- [DjangoConfig reference](/fundamentals/configuration/django-settings)
- Use IDE autocomplete with type hints
- Run `python manage.py show_config --help`
:::
</details>

## Import Errors

<details>
<summary>**ImportError: cannot import name 'get_current_config'**</summary>

**Problem:**
```python
ImportError: cannot import name 'get_current_config' from 'django_cfg.core.config'
```

**Solution:**
```python
# Update import path
from django_cfg.core import get_current_config  # ✅ Correct

# Or
from django_cfg.core.state import get_current_config  # ✅ Also correct

# Not this:
# from django_cfg.core.config import get_current_config  # ❌ Old path
```

:::tip[Correct Import Paths]
Django-CFG reorganized imports in recent versions. Always import from:
- `from django_cfg import DjangoConfig, get_current_config` (recommended)
- `from django_cfg.core import DjangoConfig, get_current_config` (also works)
:::
</details>

<details>
<summary>**ImportError: cannot import name 'DjangoConfig'**</summary>

**Problem:**
```python
ImportError: cannot import name 'DjangoConfig'
```

**Solution:**
```python
# Make sure django-cfg is installed
pip install django-cfg

# Correct import
from django_cfg import DjangoConfig

# Or
from django_cfg.core import DjangoConfig
```

:::info[Installation Check]
Verify django-cfg is installed:
```bash
pip show django-cfg
# Should show package information

pip list | grep django-cfg
# Should list the package
```
:::
</details>

<details>
<summary>**Circular Import Error**</summary>

**Problem:**
```python
ImportError: cannot import name 'DjangoConfig' from partially initialized module 'django_cfg'
```

**Cause:**
Circular import between settings and config.

**Solution:**
```python
# settings.py
from myproject.config import MyConfig  # ✅ Import config class

config = MyConfig()
globals().update(config.get_all_settings())

# Don't import settings in config.py!
```

:::danger[Circular Import Prevention]
**Never do this:**
```python
# config.py
from django.conf import settings  # ❌ Creates circular import
```

**Instead, use lazy imports or dependency injection:**
```python
# config.py
def get_setting_value():
    from django.conf import settings  # ✅ Lazy import inside function
    return settings.SOME_VALUE
```
:::
</details>

## Database Issues

<details>
<summary>**Database routing references non-existent databases**</summary>

**Problem:**
```python
ConfigurationError: Database routing references non-existent databases: {'analytics'}
```

**Cause:**
`migrate_to` references database that doesn't exist.

**Solution:**
```python
databases = {
    "default": DatabaseConfig(...),
    "analytics": DatabaseConfig(
        ...,
        migrate_to="default",  # ← Ensure 'default' exists
    ),
}
```

:::warning[Database Routing Validation]
Django-CFG validates that all `migrate_to` references point to existing databases. Common mistakes:
- ❌ Typo in database alias: `migrate_to="defualt"`
- ❌ Reference to database not in `databases` dict
- ✅ Always reference existing database aliases
:::
</details>

<details>
<summary>**django.db.utils.OperationalError: FATAL: database does not exist**</summary>

**Problem:**
Database connection fails because database doesn't exist.

**Solution:**
```bash
# Create the database first
createdb mydb

# Or configure to create automatically
databases = {
    "default": DatabaseConfig(
        ...,
        options={"autocommit": True},
    )
}
```

:::info[Database Creation]
**PostgreSQL:**
```bash
createdb mydb
# Or with user: createdb -U myuser mydb
```

**MySQL:**
```bash
mysql -u root -p -e "CREATE DATABASE mydb;"
```

**SQLite:**
Django creates SQLite databases automatically if they don't exist.
:::
</details>

<details>
<summary>**Migrations not running on correct database**</summary>

**Problem:**
Migrations run on wrong database in multi-database setup.

**Solution:**
```python
# Use migrate_to to control where migrations run
databases = {
    "default": DatabaseConfig(...),
    "analytics": DatabaseConfig(
        ...,
        migrate_to="default",  # Migrations run here
    ),
}

# Then run
python manage.py migrate  # Migrates default only
python manage.py migrate_all  # Migrates all with routing
```

:::tip[Multi-Database Migration Control]
The `migrate_to` parameter controls where migrations execute:
- **Not set**: Migrations run on the database itself
- **Set to another db**: Migrations run on the target database
- **Common pattern**: All migrations on `default`, data on separate databases

See [Multi-Database Guide](/guides/multi-database) for detailed patterns.
:::
</details>

## CORS Issues

<details>
<summary>**CORS header 'Access-Control-Allow-Origin' missing**</summary>

**Problem:**
Browser console shows CORS error in production.

**Cause:**
Production requires `security_domains` configuration.

**Solution:**
```python
# Production: Configure security_domains
security_domains = [
    "frontend.example.com",         # ✅ Any format works
    "https://api.example.com",      # ✅ With protocol
    "staging.example.com:3000",     # ✅ With port
]

# Development: No configuration needed!
# debug=True automatically enables CORS_ALLOW_ALL_ORIGINS
```

:::info[Environment-Aware CORS Configuration]
Django-CFG automatically configures CORS based on environment:

**Development Mode** (`debug=True` or no `security_domains`):
- ✅ `CORS_ALLOW_ALL_ORIGINS = True` - Fully open
- ✅ `ALLOWED_HOSTS = ['*']` - All hosts accepted
- ✅ Docker IPs work automatically
- ✅ No configuration needed!

**Production Mode** (when `security_domains` set):
- ✅ `CORS_ALLOWED_ORIGINS` - Generated from security_domains
- ✅ `CORS_ALLOW_CREDENTIALS = True` - Credentials enabled
- ✅ `ALLOWED_HOSTS` - Strict whitelist
- ✅ Auto-normalized from any domain format
- ✅ CORS middleware auto-inserted
:::
</details>

<details>
<summary>**CORS allows all origins in production**</summary>

**Problem:**
`CORS_ALLOW_ALL_ORIGINS = True` in production.

**Cause:**
Not setting `security_domains` in production configuration.

**Solution:**
```python
# REQUIRED in production - set security_domains
security_domains = [
    "example.com",
    "api.example.com",
]

# This automatically switches to strict whitelist mode
```

:::danger[Security Critical: CORS Misconfiguration]
**Django-CFG behavior:**
- ✅ **Development** (`debug=True` or no `security_domains`) → CORS fully open
- 🔒 **Production** (when `security_domains` set) → Strict whitelist only

**Allowing all origins in production is a critical security vulnerability:**
- 🔒 **CSRF attacks** - Any site can make requests to your API
- 🔒 **Data theft** - Malicious sites can steal user data
- 🔒 **Session hijacking** - Attackers can exploit user sessions

**Production checklist:**
- ✅ **REQUIRED**: Set `security_domains` with production domains
- ✅ Use HTTPS domains (handled by reverse proxy)
- ✅ Include only trusted domains
- ✅ Set `debug = False`
- ❌ Never leave `security_domains` empty/None in production

**Example validation:**
```python
if env.env_mode == "production":
    if not config.security_domains:
        raise ValueError("CRITICAL: security_domains required in production!")
```
:::
</details>

## Static Files Issues

<details>
<summary>**Static files not found (404)**</summary>

**Problem:**
Static files return 404 in production.

**Solution:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Ensure WhiteNoise is configured (automatic in django-cfg)
# Check STATIC_ROOT
python manage.py show_config | grep STATIC
```

:::tip[WhiteNoise Auto-Configuration]
Django-CFG automatically configures WhiteNoise for static file serving:
- ✅ **Middleware added** - WhiteNoise middleware inserted
- ✅ **STATIC_ROOT set** - Points to `staticfiles/` directory
- ✅ **Compression enabled** - GZip compression for performance
- ✅ **Caching configured** - Far-future cache headers

**Production checklist:**
1. Run `collectstatic` before deployment
2. Set `STATIC_ROOT` in environment if needed
3. Verify static files exist in `STATIC_ROOT`
:::
</details>

<details>
<summary>**Static files not updating**</summary>

**Problem:**
CSS/JS changes not reflected.

**Solution:**
```bash
# Clear browser cache
# Or bust cache with versioning

# In development, ensure DEBUG=True
debug = True
```

:::info[Cache Busting Strategies]
**Development:**
- Hard refresh browser: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Disable cache in DevTools (Network tab → "Disable cache")
- Set `DEBUG = True` to disable aggressive caching

**Production:**
- Use Django's `ManifestStaticFilesStorage` (automatic with WhiteNoise)
- Files get hash suffix: `style.css` → `style.a4b3c2d1.css`
- Changes create new hash → browser fetches new file
:::
</details>

## Background Tasks Issues

<details>
<summary>**Tasks not being processed**</summary>

**Problem:**
Tasks enqueued but never execute.

**Cause:**
Worker not running.

**Solution:**
```bash
# Start ReArq worker
rearq main:rearq worker

# Or with specific queues
rearq main:rearq worker --queues default high_priority

# Check worker status
rearq main:rearq info
```

:::warning[Worker Must Be Running]
ReArq requires a **separate worker process** to execute tasks:
- ❌ **Common mistake**: Enqueueing tasks without running worker
- ✅ **Development**: Run `rearq main:rearq worker` in separate terminal
- ✅ **Production**: Use process manager (systemd, supervisor, Docker)

**Check if worker is running:**
```bash
ps aux | grep rearq_worker  # Should show running process
```
:::
</details>

<details>
<summary>**Redis connection refused**</summary>

**Problem:**
```python
redis.exceptions.ConnectionError: Error 61 connecting to localhost:6379. Connection refused.
```

**Cause:**
Redis not running.

**Solution:**
```bash
# Start Redis
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis

# Verify connection
redis-cli ping  # Should return PONG
```

:::info[Redis Installation & Setup]
**Install Redis:**
- **macOS**: `brew install redis && brew services start redis`
- **Ubuntu**: `sudo apt install redis-server && sudo systemctl start redis`
- **Docker**: `docker run -d -p 6379:6379 redis`

**Verify Redis:**
```bash
redis-cli ping  # Should return: PONG
redis-cli info | grep uptime  # Show uptime
```

**Configure custom Redis URL:**
```python
# In config.py
tasks: TaskConfig = TaskConfig(
    redis_url="redis://localhost:6379/0",
)
```
:::
</details>

<details>
<summary>**Tasks stuck in queue**</summary>

**Problem:**
Tasks enqueued but status shows "pending" forever.

**Solution:**
```bash
# Check worker logs
rearq main:rearq worker --verbose

# Clear stuck tasks
rearq main:rearq flush

# Restart worker
# Kill existing worker and start fresh
```

:::tip[Debugging Stuck Tasks]
**Common causes of stuck tasks:**
1. **Worker crashed** - Check logs for exceptions
2. **Task timeout** - Increase timeout in task config
3. **Deadlock** - Task waiting for another task
4. **Queue mismatch** - Task sent to queue worker isn't watching

**Debug steps:**
```bash
# 1. Check worker is processing
rearq main:rearq worker --verbose  # Watch logs

# 2. Check Redis has messages
redis-cli LLEN "arq:queue:default"  # Queue length

# 3. Manually retry task
rearq main:rearq retry <task_id>
```
:::
</details>

## Email Issues

<details>
<summary>**Email not sending**</summary>

**Problem:**
Emails not being sent/received.

**Solution:**
```python
# Check email configuration
from django.core.mail import send_mail

send_mail(
    'Test Subject',
    'Test message',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,  # ← Show errors
)

# Or use test command
python manage.py test_email to@example.com
```

:::tip[Email Testing & Debugging]
**Development:**
- Use console backend: `backend="django.core.mail.backends.console.EmailBackend"`
- Emails print to console instead of sending

**Testing:**
```python
# In config.py
email = EmailConfig(
    backend="django.core.mail.backends.console.EmailBackend",  # Development
)

# Or use file backend
email = EmailConfig(
    backend="django.core.mail.backends.filebased.EmailBackend",
    file_path="tmp/emails",  # Emails saved as files
)
```

**Check configuration:**
```bash
python manage.py show_config | grep EMAIL
```
:::
</details>

<details>
<summary>**SMTP authentication failed**</summary>

**Problem:**
```python
SMTPAuthenticationError: (535, b'5.7.8 Authentication failed')
```

**Solution:**
```python
# Verify credentials
email = EmailConfig(
    backend="django.core.mail.backends.smtp.EmailBackend",
    host="smtp.gmail.com",
    port=587,
    use_tls=True,
    user="${EMAIL_USER}",  # Check this
    password="${EMAIL_PASSWORD}",  # Check this
)

# For Gmail, use App Password (not regular password)
```

:::warning[Gmail App Passwords Required]
**Gmail requires App Passwords for SMTP:**
1. Enable 2-Factor Authentication on Google account
2. Go to Google Account → Security → App Passwords
3. Generate new app password for "Mail"
4. Use generated password (16 chars, no spaces)

**Common SMTP configurations:**
```python
# Gmail
email = EmailConfig(
    host="smtp.gmail.com",
    port=587,
    use_tls=True,
)

# Outlook/Office365
email = EmailConfig(
    host="smtp.office365.com",
    port=587,
    use_tls=True,
)

# SendGrid
email = EmailConfig(
    host="smtp.sendgrid.net",
    port=587,
    use_tls=True,
    user="apikey",  # Literal "apikey"
    password="${SENDGRID_API_KEY}",
)
```
:::
</details>

## Ngrok Issues

<details>
<summary>**Ngrok tunnel not starting**</summary>

**Problem:**
`runserver_ngrok` fails to start tunnel.

**Solution:**
```bash
# Install pyngrok
pip install pyngrok

# Set auth token (for custom subdomain)
export NGROK_AUTH_TOKEN=your_token_here

# Or configure in settings
ngrok = NgrokConfig(
    enabled=True,
    auth_token="${NGROK_AUTH_TOKEN}",
)
```

:::info[Ngrok Setup]
**Install pyngrok:**
```bash
pip install pyngrok
```

**Get auth token:**
1. Sign up at https://ngrok.com
2. Go to Dashboard → Auth Token
3. Copy token and set environment variable

**Configure in Django-CFG:**
```python
# config.py
ngrok = NgrokConfig(
    enabled=True,
    auth_token="${NGROK_AUTH_TOKEN}",
    subdomain="myapp",  # Optional: fixed subdomain (requires paid plan)
)
```

**Start server with ngrok:**
```bash
python manage.py runserver_ngrok
# Output: Ngrok tunnel: https://myapp.ngrok.io
```
:::
</details>

<details>
<summary>**Ngrok tunnel URL changes**</summary>

**Problem:**
Tunnel URL changes every restart (random subdomain).

**Solution:**
```python
# Use custom subdomain (requires ngrok auth token)
ngrok = NgrokConfig(
    enabled=True,
    auth_token="${NGROK_AUTH_TOKEN}",
    subdomain="myapp",  # Fixed subdomain
)
```

:::warning[Ngrok Free vs Paid]
**Free plan:**
- ✅ Random subdomain: `https://abc123.ngrok.io`
- ❌ Changes on every restart
- ✅ Good for testing webhooks

**Paid plan ($8/month):**
- ✅ Custom subdomain: `https://myapp.ngrok.io`
- ✅ Persistent URL across restarts
- ✅ Multiple tunnels simultaneously

**Alternatives to paid ngrok:**
- **localtunnel** - Free, but less stable
- **serveo** - Free SSH tunneling
- **pagekite** - Free tier available
:::
</details>

## Payment System Issues

<details>
<summary>**Payment webhook not working**</summary>

**Problem:**
Webhooks not being received/processed.

**Solution:**
```python
# Verify webhook URL is publicly accessible
# Use ngrok for local development
python manage.py runserver_ngrok

# Check webhook secret is correct
payments = PaymentsConfig(
    providers={
        "nowpayments": NowPaymentsConfig(
            ipn_secret="${NOWPAYMENTS_IPN_SECRET}",  # ← Verify this
        ),
    },
)

# Check webhook logs
# Monitor webhook endpoint for incoming requests
```

:::warning[Webhook Requirements]
**Webhooks require publicly accessible URL:**
- ❌ **Won't work**: `localhost`, `127.0.0.1`, private IPs
- ✅ **Will work**: Public domain, ngrok tunnel

**Development setup:**
```bash
# Start ngrok tunnel
python manage.py runserver_ngrok

# Copy ngrok URL from output
# Configure webhook URL in payment provider dashboard
# Example: https://abc123.ngrok.io/payments/webhook/nowpayments/
```

**Verify webhook:**
1. Check webhook URL is registered in provider dashboard
2. Verify IPN secret matches provider settings
3. Monitor webhook logs for incoming requests
4. Test with provider's webhook testing tool
:::
</details>

<details>
<summary>**Payment test mode not working**</summary>

**Problem:**
Test payments fail or use real money.

**Solution:**
```python
# Enable test mode
payments = PaymentsConfig(
    enabled=True,
    test_mode=True,  # ← Ensure this is True
    providers={...},
)

# Use test API keys
# Most providers have separate test/sandbox keys
```

:::danger[Test Mode Critical]
**Always use test mode in development:**
- 🔒 **Prevents real charges** - No actual money transferred
- 🔒 **Use sandbox API keys** - Separate from production
- 🔒 **Test with test cryptocurrencies** - No real crypto needed

**NowPayments test mode:**
```python
payments = PaymentsConfig(
    test_mode=True,  # ✅ Test mode
    providers={
        "nowpayments": NowPaymentsConfig(
            api_key="${NOWPAYMENTS_SANDBOX_API_KEY}",  # Sandbox key
            ipn_secret="${NOWPAYMENTS_SANDBOX_IPN_SECRET}",
        ),
    },
)
```

**Verify test mode:**
```bash
# Check configuration
python manage.py show_config | grep -i test

# Payments should show "sandbox" or "test" in API URLs
```
:::
</details>

## Debug Tools

<details>
<summary>**Using check_settings command**</summary>

```bash
# Validate all Django settings
python manage.py check_settings

# Shows:
# - Required settings present
# - Security issues
# - Configuration warnings
```

:::tip[check_settings Command]
Django-CFG provides `check_settings` command to validate configuration:
- ✅ Checks required settings (SECRET_KEY, DATABASES, etc.)
- ✅ Validates security settings (ALLOWED_HOSTS, CORS, etc.)
- ✅ Warns about common misconfigurations
- ✅ Shows configuration recommendations

**Example output:**
```
✓ SECRET_KEY configured (50+ characters)
✓ Database 'default' configured
✓ ALLOWED_HOSTS configured for production
⚠ DEBUG=True in production (should be False)
```
:::
</details>

<details>
<summary>**Using show_config command**</summary>

```bash
# Display current configuration
python manage.py show_config

# Show specific section
python manage.py show_config --section databases
python manage.py show_config --section security
```

:::info[show_config Options]
**Display modes:**
```bash
# Full configuration
python manage.py show_config

# Specific section
python manage.py show_config --section databases
python manage.py show_config --section security
python manage.py show_config --section middleware

# Sanitized output (hides secrets)
python manage.py show_config --sanitize

# Debug mode (verbose)
python manage.py show_config --debug
```

**Useful for:**
- Verifying configuration values
- Debugging environment variable expansion
- Checking middleware order
- Validating database settings
:::
</details>

<details>
<summary>**Enable Debug Mode**</summary>

```python
# Temporary debug mode
DEBUG = True
startup_info_mode = StartupInfoMode.FULL

# Enables:
# - Detailed error pages
# - Full startup information
# - Template debug
# - SQL query logging
```

:::warning[Debug Mode Settings]
**Development:**
```python
# config.py
debug = True
startup_info_mode = StartupInfoMode.FULL
```

**Production:**
```python
# config.py
debug = False  # ← Must be False
startup_info_mode = StartupInfoMode.NONE
```

**What DEBUG=True enables:**
- Detailed error pages with full traceback
- Template variable inspection
- SQL query logging (performance impact)
- Static file serving (slow, use only in dev)

**Security risk in production:**
- 🔒 Exposes source code paths
- 🔒 Shows environment variables
- 🔒 Reveals database queries
- 🔒 Displays sensitive settings
:::
</details>

<details>
<summary>**Debug Warnings with Traceback**</summary>

**Problem:**
You see RuntimeWarnings like:
```
RuntimeWarning: Accessing the database during app initialization is discouraged.
```

But you don't know WHERE in your code it's happening.

**Solution:**
Enable `debug_warnings` to see full stack traceback:

<Tabs groupId="debug-warnings-method">
<TabItem value="config" label="Via Config (Recommended)">

```python title="config.py"
from django_cfg import DjangoConfig

class MyConfig(DjangoConfig):
    project_name: str = "My Project"

    # Enable warnings traceback in development
    debug_warnings: bool = True  # ← Shows full stack trace
```

</TabItem>
<TabItem value="env" label="Via Environment Variable">

```bash
export DJANGO_CFG_DEBUG_WARNINGS=1
python manage.py runserver
```

</TabItem>
</Tabs>

**Example Output:**
```
================================================================================
⚠️  WARNING TRACEBACK (to help find the source)
================================================================================
  File "/path/to/your/code/apps.py", line 42, in ready
    self.setup_database()
  File "/path/to/your/code/apps.py", line 55, in setup_database
    MyModel.objects.all()  # ← HERE IS THE PROBLEM!
    ^^^^^^^^^^^^^^^^^^^^

--------------------------------------------------------------------------------
⚠️  WARNING MESSAGE:
RuntimeWarning: Accessing the database during app initialization is discouraged.
To fix this warning, avoid executing queries in AppConfig.ready() or when your
app modules are imported.
================================================================================
```

:::tip[Common Issues Found]
**Database access in AppConfig.ready():**
```python
# ❌ Bad - queries during import
def ready(self):
    from .models import MyModel
    MyModel.objects.create(...)

# ✅ Good - use post_migrate signal
def ready(self):
    from django.db.models.signals import post_migrate
    post_migrate.connect(self.setup_data, sender=self)
```

**Model queries at module level:**
```python
# ❌ Bad - runs during import
from .models import MyModel
DEFAULT_SETTINGS = MyModel.objects.first()

# ✅ Good - lazy evaluation
def get_default_settings():
    from .models import MyModel
    return MyModel.objects.first()
```
:::

**What debug_warnings shows:**
- 📍 Full stack trace to the exact line
- 🎯 Which app/file is causing the warning
- 🔍 Complete call chain from Django startup
- ⚡ Works for RuntimeWarning, DeprecationWarning, etc.

</details>

<details>
<summary>**Check Django Configuration**</summary>

```bash
# Run Django system checks
python manage.py check

# Run deployment checks
python manage.py check --deploy

# Check specific tag
python manage.py check --tag security
```

:::tip[Django Check Framework]
**Available check tags:**
```bash
# Security checks
python manage.py check --tag security

# Database checks
python manage.py check --tag database

# Model checks
python manage.py check --tag models

# Compatibility checks
python manage.py check --tag compatibility

# All deployment checks
python manage.py check --deploy
```

**Common issues detected:**
- Missing SECRET_KEY or weak SECRET_KEY
- DEBUG=True in production
- Missing ALLOWED_HOSTS
- Insecure middleware configuration
- Missing staticfiles configuration
:::
</details>

## Performance Issues

<details>
<summary>**Settings generation slow**</summary>

**Problem:**
Application startup is slow.

**Cause:**
Settings generated on every request (should be cached).

**Solution:**
```python
# Settings are cached by default
# Clear cache manually if needed
config.invalidate_cache()

# Or use cached property
@property
def my_settings(self):
    if not hasattr(self, '_my_settings_cache'):
        self._my_settings_cache = expensive_operation()
    return self._my_settings_cache
```

:::tip[Configuration Caching]
Django-CFG automatically caches configuration:
- ✅ **Settings cached** - Generated once per application lifecycle
- ✅ **Environment variables cached** - Expanded once
- ✅ **Model imports cached** - No repeated imports

**Performance benchmarks:**
- First generation: ~50-100ms
- Cached access: &lt;1ms
- No runtime overhead after startup

**When to invalidate cache:**
- Environment variables changed
- Configuration file modified
- Dynamic settings updated
:::
</details>

<details>
<summary>**Database queries slow**</summary>

**Problem:**
Database operations are slow.

**Solution:**
```python
# Enable connection pooling
databases = {
    "default": DatabaseConfig(
        ...,
        conn_max_age=600,  # Connection pooling
        options={
            "connect_timeout": 10,
        },
    ),
}

# Use database indexes
# Use select_related() and prefetch_related()
# Enable query logging to identify slow queries
```

:::info[Database Performance Optimization]
**Connection pooling:**
```python
databases = {
    "default": DatabaseConfig(
        conn_max_age=600,  # Keep connections alive for 10 minutes
        conn_health_checks=True,  # Validate connections before use
    ),
}
```

**Query optimization:**
```python
# N+1 query problem - BAD
for user in User.objects.all():
    print(user.profile.bio)  # Extra query per user

# Optimized with select_related - GOOD
for user in User.objects.select_related('profile'):
    print(user.profile.bio)  # Single JOIN query
```

**Debug slow queries:**
```python
# config.py
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',  # Log all SQL queries
        },
    },
}
```

**Tools for profiling:**
- django-debug-toolbar - Visual query profiler
- django-silk - Request profiling
- nplusone - Detect N+1 queries
:::
</details>

## Getting More Help

### Enable Verbose Logging

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Or configure in LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### Collect Debug Information

When reporting issues, include:

```bash
# Django-cfg version
pip show django-cfg

# Django version
python -m django --version

# Python version
python --version

# Configuration (sanitized)
python manage.py show_config --sanitize

# Django checks
python manage.py check --deploy

# Full traceback
# (Copy entire error with traceback)
```

### Community Support

- **GitHub Issues:** Report bugs
- **Discussions:** Ask questions
- **Stack Overflow:** Tag with `django-cfg`
- **Discord/Slack:** Real-time help

### Professional Support

For enterprise customers:
- Priority bug fixes
- Migration assistance
- Custom feature development
- Architecture review

## Common Patterns

### Development vs Production

```python
# Use environment-specific configuration

# Development
class DevelopmentConfig(DjangoConfig):
    env_mode = EnvironmentMode.DEVELOPMENT
    debug = True
    startup_info_mode = StartupInfoMode.FULL

# Production
class ProductionConfig(DjangoConfig):
    env_mode = EnvironmentMode.PRODUCTION
    debug = False
    startup_info_mode = StartupInfoMode.NONE
    security_domains = ["example.com"]
```

### Testing Configuration

```python
# Test-specific settings
class TestConfig(DjangoConfig):
    env_mode = EnvironmentMode.TEST
    databases = {
        "default": DatabaseConfig(
            engine="django.db.backends.sqlite3",
            name=":memory:",
        )
    }
    email = EmailConfig(
        backend="django.core.mail.backends.locmem.EmailBackend",
    )
```

### Environment Variables

```python
# Load from .env file
from dotenv import load_dotenv
load_dotenv()

# Use in configuration
secret_key = "${SECRET_KEY}"
databases = {
    "default": DatabaseConfig(
        name="${DATABASE_NAME}",
        user="${DATABASE_USER}",
        password="${DATABASE_PASSWORD}",
    )
}
```

## Next Steps

- [Architecture Guide](/fundamentals/core/architecture)
- [Configuration Reference](/fundamentals/configuration)
- [CLI Commands](/cli/commands/quick-reference)
