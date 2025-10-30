---
title: Quick Reference
description: Django-CFG CLI quick reference commands. Command-line interface for quick reference with examples, options, and production workflows.
sidebar_label: Quick Reference
sidebar_position: 1
keywords:
  - django-cfg quick reference
  - django-cfg command quick reference
  - cli quick reference
---

# CLI Commands Quick Reference

Fast reference guide for all Django-CFG management commands. Perfect for quick lookups!

## 🚀 Project Setup

```bash
# Create new project
django-cfg create-project "My Project"

# Show Django-CFG info
django-cfg info --verbose

# Validate configuration
python manage.py validate_config --check-connections

# Show current configuration
python manage.py show_config --format yaml
```

## 🗄️ Database Operations

```bash
# Migrate all databases (recommended)
python manage.py migrate_all

# Smart migration with auto-detection
python manage.py migrator --auto

# Dry run to preview migrations
python manage.py migrate_all --dry-run

# Migrate specific database
python manage.py migrator --database analytics_db
```

## 🏃 Development Server

```bash
# Enhanced development server
cli runserver

# With ngrok tunnel (for webhooks)
python manage.py runserver_ngrok

# Custom port and host
cli runserver --port 3000 --host 0.0.0.0
```

## 👤 User Management

```bash
# Create superuser (enhanced)
cli superuser --email admin@example.com

# Standard Django way
python manage.py createsuperuser

# Test OTP authentication
python manage.py test_otp --email user@test.com
python manage.py test_otp --phone "+1234567890"
```

## 🧪 Testing & Monitoring

```bash
# Check all API endpoints health (auto-resolves parametrized URLs)
python manage.py check_endpoints

# Check with JSON output for CI/CD
python manage.py check_endpoints --json

# Check without automatic JWT authentication
python manage.py check_endpoints --no-auth

# Check specific endpoint
python manage.py check_endpoints --url endpoints_status

# API endpoint for monitoring
curl http://localhost:8000/cfg/endpoints/

# Test email
cli test-email --to admin@test.com

# Test Telegram
cli test-telegram --message "Hello!"

# Test Twilio SMS
python manage.py test_twilio --to "+1234567890"

# Test Twilio WhatsApp
python manage.py test_twilio --to "+1234567890" --whatsapp

# Test payment providers
python manage.py test_providers

# Test newsletter
python manage.py test_newsletter --email test@test.com
```

## 🤖 AI Agents

```bash
# List available templates
python manage.py create_agent --list

# Load all templates
python manage.py create_agent --load-all

# Create custom agent
python manage.py create_agent "analyzer" \
  "Analyze content for sentiment and topics" \
  --category content --public

# Show orchestrator status
python manage.py orchestrator_status --detailed

# Agent stats for last 48 hours
python manage.py orchestrator_status --agents --recent 48
```

## 📚 Knowledge Base

```bash
# Setup Knowledge Base (first time)
python manage.py setup_knowbase

# Show statistics
python manage.py knowbase_stats

# Detailed stats as JSON
python manage.py knowbase_stats --detailed --format json
```

## 🔧 Maintenance Mode

```bash
# Enable maintenance mode
python manage.py maintenance enable

# Enable with Cloudflare sync
python manage.py maintenance enable --cloudflare

# Disable maintenance mode
python manage.py maintenance disable

# Check status
python manage.py maintenance status

# Sync with Cloudflare
python manage.py sync_cloudflare --enable
python manage.py sync_cloudflare --disable
```

## 💳 Payments Management

```bash
# Currency operations
python manage.py currency_stats
python manage.py manage_currencies list
python manage.py manage_currencies add --code BTC --name Bitcoin

# Provider management
python manage.py manage_providers list
python manage.py manage_providers add --name NowPayments --type crypto

# Process pending payments
python manage.py process_pending_payments --limit 100

# Cleanup old data
python manage.py cleanup_expired_data --days 30
```

## 🔄 Background Tasks (ReArq)

```bash
# Start async worker
rearq main:rearq worker

# Start cron task scheduler
rearq main:rearq timer

# Start monitoring web interface
rearq main:rearq server

# Start worker with specific queues
rearq main:rearq worker --queues default,high,low

# Show task status
python manage.py task_status

# Test task processing
python manage.py test_tasks
```

## 🌐 URLs & Routing

```bash
# Show all URLs (enhanced)
cli show-urls

# Filter URLs
cli show-urls --pattern "api/"

# Include admin URLs
cli show-urls --include-admin

# List URLs (alternative)
python manage.py list_urls --output urls.txt
```

## 🛠️ Development Tools

```bash
# Run script with Django context
python manage.py script my_script.py

# Show project structure
python manage.py tree --depth 3

# Generate components
python manage.py generate model Product name:str price:decimal

# Create API token
python manage.py create_token username --expires-in 30

# Check settings
python manage.py check_settings --verbose

# Clear Constance cache
python manage.py clear_constance
```

## 📊 Statistics & Monitoring

```bash
# Support tickets
python manage.py support_stats --format json

# Newsletter campaigns
python manage.py newsletter_stats --subscribers

# Lead conversion
python manage.py leads_stats --funnel

# Orchestrator metrics
python manage.py orchestrator_status --detailed

# Knowledge base metrics
python manage.py knowbase_stats --detailed
```

## ⏰ Cron Jobs

Commonly used commands in cron:

```bash
# Process pending payments every 5 minutes
*/5 * * * * cd /path/to/project && python manage.py process_pending_payments

# Process scheduled maintenance every 5 minutes
*/5 * * * * cd /path/to/project && python manage.py process_scheduled_maintenance

# Cleanup expired data daily at 3 AM
0 3 * * * cd /path/to/project && python manage.py cleanup_expired_data

# Update currency rates every hour
0 * * * * cd /path/to/project && python manage.py update_currency_rates
```

## 🔗 Command Chaining

Useful command combinations:

```bash
# Complete project setup
django-cfg create-project "My Project" && \
cd my_project && \
python manage.py migrate_all && \
python manage.py createsuperuser

# Validate and migrate
python manage.py validate_config && \
python manage.py migrate_all

# Deploy workflow
python manage.py validate_config --check-connections && \
python manage.py migrate_all && \
python manage.py collectstatic --noinput && \
python manage.py test_email --to admin@example.com

# Development startup
python manage.py migrate_all && \
python manage.py runserver_ngrok
```

## 📋 Command Categories

| Category | Command Count | Main Purpose |
|----------|--------------|--------------|
| **Core** | 8 | Project setup, configuration, validation |
| **Database** | 3 | Migrations, database management |
| **AI Agents** | 2 | Agent creation, orchestrator management |
| **Knowledge Base** | 2 | Vector search setup, statistics |
| **Maintenance** | 3 | Maintenance mode, Cloudflare sync |
| **Payments** | 6 | Currency, provider, payment management |
| **Accounts** | 1 | OTP authentication testing |
| **Background Tasks** | 4 | ReArq worker management |
| **Development** | 8 | Server, ngrok, scripts, testing |
| **Built-in Apps** | 4 | Support, newsletter, leads stats |

## 💡 Tips

### Use Poetry for Project Commands

```bash
# Recommended
poetry run cli runserver

# Also works
python manage.py runserver
```

### Always Validate Before Deploy

```bash
poetry run cli validate-config --check-connections
```

### Use Dry Run for Safety

```bash
python manage.py migrate_all --dry-run
python manage.py cleanup_expired_data --dry-run
```

### Test Integrations After Configuration

```bash
poetry run cli test-email --to admin@test.com
poetry run cli test-telegram --message "Deploy successful"
python manage.py test_twilio --to "+1234567890"
```

## 🔍 Find More Information

- **[Core Commands](./core-commands)** - Project setup, configuration
- **[AI Agents](./ai-agents)** - Agent management commands
- **[Knowledge Base](./knowbase)** - Vector search commands
- **[Maintenance](./maintenance)** - Maintenance mode commands
- **[Payments](./payments)** - Payment management commands
- **[Background Tasks](/features/integrations/rearq/overview)** - ReArq commands
- **[Development](./development)** - Development tools

---

**Quick, focused, practical.** Bookmark this page! 🚀
