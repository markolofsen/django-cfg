---
title: Commands Overview
description: Django-CFG CLI commands organized by category. Quick access to all 40+ management commands.
sidebar_label: Overview
sidebar_position: 1
keywords:
  - django-cfg commands
  - cli overview
  - management commands
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# CLI Commands Overview

Django-CFG provides **40+ management commands** for development, testing, monitoring, and production operations.

:::tip[Quick Start]
New to Django-CFG? Start with the **[Quick Reference](./quick-reference.md)** for most common commands!
:::

## 📚 Command Categories

<Tabs groupId="command-categories">
  <TabItem value="essential" label="🚀 Essential" default>

### Most Used Commands

```bash
# Check all API endpoints health
python manage.py check_endpoints

# Migrate all databases
python manage.py migrate_all

# Run development server
cli runserver

# Create superuser
cli superuser --email admin@example.com

# Show configuration
python manage.py show_config
```

**[View Quick Reference →](./quick-reference.md)**

  </TabItem>
  <TabItem value="testing" label="🧪 Testing">

### Testing & Monitoring

```bash
# Endpoint health checker (production-ready)
python manage.py check_endpoints --json

# Test email
cli test-email --to admin@test.com

# Test Telegram
cli test-telegram --message "Hello!"

# Test SMS/WhatsApp
python manage.py test_twilio --to "+1234567890"

# Test payment providers
python manage.py test_providers
```

:::info[Feature Highlight]
`check_endpoints` includes:
- Auto-resolves parametrized URLs (`<int:pk>`, `<uuid:id>`)
- JWT auto-authentication
- Multi-database awareness
- REST API for monitoring at `/cfg/endpoints/`
:::

**[View Testing & Monitoring →](./testing-monitoring.md)**

  </TabItem>
  <TabItem value="development" label="🛠️ Development">

### Development Tools

```bash
# Enhanced development server
cli runserver --port 3000

# Run with ngrok tunnel
python manage.py runserver_ngrok

# List all URLs
python manage.py list_urls --pattern "api/"

# Show project structure
python manage.py tree --depth 3

# Run custom script
python manage.py script my_script.py
```

**[View Development Tools →](./development.md)**

  </TabItem>
  <TabItem value="production" label="🚀 Production">

### Production Operations

```bash
# Validate configuration
python manage.py validate_config --check-connections

# Migrate all databases
python manage.py migrate_all

# Process pending payments (cron job)
python manage.py process_pending_payments

# Maintenance mode
python manage.py maintenance enable --cloudflare

# Cleanup expired data
python manage.py cleanup_expired_data --days 30
```

**[View Payments →](./payments.md)** | **[View Maintenance →](./maintenance.md)**

  </TabItem>
</Tabs>

---

## 📋 All Command Categories

<details>
  <summary>

### [🔧 Core Commands](./core-commands.md) — 8 commands

  </summary>

Project setup, configuration validation, and system checks.

| Command | Description |
|---------|-------------|
| `django-cfg create-project` | Create new Django project with full setup |
| `django-cfg info` | Show installation and system information |
| `show_config` | Display current configuration |
| `validate_config` | Validate settings and connections |
| `check_settings` | Comprehensive diagnostics |
| `show_urls` | List all URL patterns |
| `migrate_all` | Migrate all databases |
| `superuser` | Create superuser |

**[Full Documentation →](./core-commands.md)**

</details>

<details>
  <summary>

### [🧪 Testing & Monitoring](./testing-monitoring.md) — 6 commands

  </summary>

Health checks, endpoint validation, and service testing.

| Command | Description |
|---------|-------------|
| `check_endpoints` | **Production-ready endpoint health checker** |
| `test_email` | Test email configuration |
| `test_telegram` | Test Telegram bot |
| `test_twilio` | Test SMS/WhatsApp |
| `test_providers` | Test payment providers |
| `test_otp` | Test OTP authentication |

:::tip[REST API Available]
Access endpoint health via REST API:
```bash
curl http://localhost:8000/cfg/endpoints/
```
:::

**[Full Documentation →](./testing-monitoring.md)**

</details>

<details>
  <summary>

### [🛠️ Development Tools](./development.md) — 8 commands

  </summary>

Development server and productivity tools.

| Command | Description |
|---------|-------------|
| `cli runserver` | Enhanced development server |
| `runserver_ngrok` | Run with ngrok tunnel |
| `script` | Run scripts with Django context |
| `tree` | Show project structure |
| `list_urls` | List all URL patterns |
| `generate` | Generate Django components |
| `create_token` | Create API tokens |
| `clear_constance` | Clear Constance cache |

**[Full Documentation →](./development.md)**

</details>

<details>
  <summary>

### [🤖 AI Agents](./ai-agents.md) — 2 commands

  </summary>

AI agent management and orchestration.

| Command | Description |
|---------|-------------|
| `create_agent` | Create agents from templates |
| `orchestrator_status` | Show orchestrator statistics |

**[Full Documentation →](./ai-agents.md)**

</details>

<details>
  <summary>

### [📚 Knowledge Base](./knowbase.md) — 2 commands

  </summary>

Vector search and knowledge management.

| Command | Description |
|---------|-------------|
| `setup_knowbase` | Setup pgvector extension |
| `knowbase_stats` | Show knowledge base statistics |

**[Full Documentation →](./knowbase.md)**

</details>

<details>
  <summary>

### 🔄 Background Tasks — Django-RQ Integration

  </summary>

Django-RQ worker management via native CLI.

| Command | Description |
|---------|-------------|
| `rearq main:rearq worker` | Start background workers |
| `rearq main:rearq timer` | Start cron task scheduler |
| `rearq main:rearq server` | Start monitoring server |
| `test_tasks` | Test task processing |

**[Full Documentation →](/features/integrations/django-rq/overview)**

</details>

<details>
  <summary>

### [🔧 Maintenance Mode](./maintenance.md) — 3 commands

  </summary>

Maintenance mode and Cloudflare integration.

| Command | Description |
|---------|-------------|
| `maintenance` | Enable/disable maintenance mode |
| `sync_cloudflare` | Sync with Cloudflare |
| `process_scheduled_maintenance` | Process scheduled windows |

**[Full Documentation →](./maintenance.md)**

</details>

<details>
  <summary>

### [💳 Payments](./payments.md) — 6 commands

  </summary>

Payment system management.

| Command | Description |
|---------|-------------|
| `currency_stats` | Currency statistics |
| `manage_currencies` | Manage currencies |
| `manage_providers` | Manage payment providers |
| `test_providers` | Test provider integrations |
| `process_pending_payments` | Process pending payments |
| `cleanup_expired_data` | Cleanup old payment data |

**[Full Documentation →](./payments.md)**

</details>

---

## 🎯 Common Workflows

### Initial Project Setup

```bash
# 1. Create project
django-cfg create-project "My Project"
cd my_project

# 2. Validate configuration
python manage.py validate_config --check-connections

# 3. Migrate databases
python manage.py migrate_all

# 4. Create superuser
cli superuser --email admin@example.com

# 5. Check endpoint health
python manage.py check_endpoints

# 6. Run server
cli runserver
```

### Pre-Deployment Checklist

```bash
# 1. Validate configuration
python manage.py validate_config --check-connections

# 2. Check endpoint health
python manage.py check_endpoints

# 3. Test integrations
cli test-email --to admin@example.com
python manage.py test_providers

# 4. Run migrations
python manage.py migrate_all

# 5. Collect static files
python manage.py collectstatic --noinput
```

### CI/CD Integration

```bash
# Health check in pipeline
python manage.py check_endpoints --json | jq '.errors'

# Exit if unhealthy
test $(python manage.py check_endpoints --json | jq '.errors') -eq 0
```

:::warning[Production Tip]
Add endpoint health checks to your monitoring:
```bash
# Cron job - every 5 minutes
*/5 * * * * python manage.py check_endpoints --json > /var/log/health.json
```
:::

---

## 💡 Best Practices

<Tabs>
  <TabItem value="isolation" label="Isolation" default>

### Use Poetry for Isolation

```bash
# Recommended
poetry run cli runserver
poetry run python manage.py check_endpoints

# Also works but less isolated
python manage.py runserver
```

  </TabItem>
  <TabItem value="validation" label="Validation">

### Always Validate

```bash
# Before deployment
poetry run cli validate-config --check-connections

# Before migrations
python manage.py migrate_all --dry-run

# Before cleanup
python manage.py cleanup_expired_data --dry-run
```

  </TabItem>
  <TabItem value="testing" label="Testing">

### Test After Changes

```bash
# Test email
cli test-email --to admin@test.com

# Test messaging
cli test-telegram --message "Deploy successful"

# Test payments
python manage.py test_providers

# Test endpoints
python manage.py check_endpoints
```

  </TabItem>
  <TabItem value="monitoring" label="Monitoring">

### Continuous Monitoring

```bash
# Endpoint health check
curl http://localhost:8000/cfg/endpoints/ | jq

# System stats
python manage.py orchestrator_status --detailed

# Currency stats
python manage.py currency_stats --format json
```

  </TabItem>
</Tabs>

---

## 🔗 Quick Navigation

| I want to... | Go to... |
|-------------|----------|
| Find a command quickly | **[Quick Reference](./quick-reference.md)** |
| Set up a new project | **[Core Commands](./core-commands.md)** |
| Monitor API health | **[Testing & Monitoring](./testing-monitoring.md)** |
| Start development | **[Development Tools](./development.md)** |
| Manage payments | **[Payments](./payments.md)** |
| Use AI agents | **[AI Agents](./ai-agents.md)** |
| Configure maintenance | **[Maintenance](./maintenance.md)** |

---

:::info[Next Steps]
- 📖 **New to Django-CFG?** Start with [Quick Reference](./quick-reference.md)
- 🧪 **Need monitoring?** See [Testing & Monitoring](./testing-monitoring.md)
- 🚀 **Ready to deploy?** Check [Core Commands](./core-commands.md)
:::

**40+ commands. One powerful CLI.** 🚀
