---
title: Core Commands
description: Django-CFG CLI core commands commands. Command-line interface for core commands with examples, options, and production workflows.
sidebar_label: Core Commands
sidebar_position: 2
keywords:
  - django-cfg core commands
  - django-cfg command core commands
  - cli core commands
---

# Core Management Commands

Essential commands for Django-CFG project setup, configuration management, and validation.

## Project Setup

### `django-cfg create-project`

Creates a new Django project with complete Django-CFG setup.

```bash
django-cfg create-project PROJECT_NAME [OPTIONS]
```

**Arguments:**
- `PROJECT_NAME` - Name of the new Django project

**Options:**
- `--path, -p PATH` - Directory where to create the project (default: current directory)
- `--no-deps` - Skip automatic dependency installation
- `--use-pip` - Use pip instead of Poetry for dependency installation
- `--force` - Overwrite existing directory if it exists
- `--no-setup` - Skip automatic project setup (directories, migrations)
- `--no-sample-data` - Skip sample data population (users, posts, products)

**Examples:**

```bash
# Basic project creation
django-cfg create-project "My Awesome Project"

# Create in specific directory
django-cfg create-project "E-Commerce Site" --path ./projects/

# Skip dependency installation
django-cfg create-project "Quick Test" --no-deps

# Use pip instead of Poetry
django-cfg create-project "Legacy Project" --use-pip

# Minimal setup without sample data
django-cfg create-project "Production App" --no-sample-data

# Force overwrite existing directory
django-cfg create-project "My Project" --force

# Complete manual setup
django-cfg create-project "Custom Setup" --no-deps --no-setup
```

**What it creates:**
- ✅ Complete Django project structure
- ✅ Type-safe configuration with Pydantic v2
- ✅ Multi-database setup with routing
- ✅ Modern Unfold admin interface
- ✅ API documentation with Spectacular
- ✅ JWT authentication system
- ✅ Background task processing
- ✅ Docker deployment files
- ✅ Sample applications (blog, shop, profiles)
- ✅ 10 test users, 20 blog posts, 30 products (if not skipped)

---

### `django-cfg info`

Shows Django-CFG installation and system information.

```bash
django-cfg info [OPTIONS]
```

**Options:**
- `--verbose, -v` - Show detailed information including paths

**Examples:**

```bash
# Basic information
django-cfg info

# Detailed information with paths
django-cfg info --verbose
```

**Output includes:**
- Django-CFG version and Python version
- 📋 Project template availability and status
- Core dependencies (Django, Pydantic, Click)
- 🌐 Service integrations (Twilio, SendGrid, OpenAI)
- Admin & UI packages (Unfold, Constance)
- 📊 API & documentation tools (DRF, Spectacular)
- Background processing (Dramatiq, Redis)
- Development tools (Ngrok)

---

## Configuration Management

### `validate_config`

Validates Django-CFG configuration files and settings.

```bash
python manage.py validate_config [OPTIONS]
```

**Options:**
- `--show-details` - Show detailed validation results
- `--check-connections` - Test database and service connections
- `--format [json|yaml|table]` - Output format (default: table)

**Examples:**

```bash
# Basic validation
python manage.py validate_config

# Detailed validation with connection tests
python manage.py validate_config --show-details --check-connections

# JSON output for automation
python manage.py validate_config --format json
```

**Validates:**
- ✅ Pydantic model validation
- ✅ Database connection strings
- ✅ Service API keys and credentials
- ✅ File paths and permissions
- ✅ Environment variable resolution

---

### `show_config`

Displays current Django-CFG configuration.

```bash
python manage.py show_config [OPTIONS]
```

**Options:**
- `--format [json|yaml|table]` - Output format (default: yaml)
- `--include-secrets` - Include sensitive values (use with caution)
- `--section TEXT` - Show specific configuration section

**Examples:**

```bash
# Show all configuration
python manage.py show_config

# JSON format for automation
python manage.py show_config --format json

# Show only database configuration
python manage.py show_config --section database

# Include sensitive values (be careful!)
python manage.py show_config --include-secrets
```

---

### `check_settings`

Comprehensive validation and debugging for Django-CFG configuration.

```bash
python manage.py check_settings [OPTIONS]
```

**Options:**
- `--email-test` - Test email configuration
- `--verbose` - Verbose output with detailed diagnostics

**Examples:**

```bash
# Check all settings
python manage.py check_settings

# Test email configuration
python manage.py check_settings --email-test

# Verbose output with detailed diagnostics
python manage.py check_settings --verbose
```

**Checks:**
- Configuration validity
- Database connections
- Email settings
- Service integrations
- File permissions
- Environment variables

---

## API Endpoints Testing

### `check_endpoints`

Check health and availability of all registered API endpoints.

```bash
python manage.py check_endpoints [OPTIONS]
```

**Options:**
- `--include-unnamed` - Include unnamed URL patterns in the check
- `--timeout INTEGER` - Request timeout in seconds (default: 5)
- `--json` - Output results as JSON
- `--url TEXT` - Check specific endpoint by URL name
- `--no-auth` - Disable automatic JWT authentication retry (default: enabled)

**Examples:**

```bash
# Check all endpoints (with auto-auth for protected endpoints)
python manage.py check_endpoints

# Include unnamed URL patterns
python manage.py check_endpoints --include-unnamed

# Custom timeout (10 seconds)
python manage.py check_endpoints --timeout 10

# Disable auto-auth (show 401/403 as-is)
python manage.py check_endpoints --no-auth

# JSON output for automation/CI
python manage.py check_endpoints --json

# Check specific endpoint by name
python manage.py check_endpoints --url endpoints_status
```

**Output:**

```bash
❌ Overall Status: UNHEALTHY

📊 Summary:
  Total endpoints: 399
  ✅ Healthy: 0
  ⚠️  Warnings: 0
  ❌ Unhealthy: 69
  ❌ Errors: 90
  ⏭️  Skipped: 240

🔗 Endpoints:
  ✅ endpoints_status
     URL: /cfg/api/endpoints/
     Status: healthy
     Response time: 0.123s

  ✅ api_users_list
     URL: /api/users/
     Status: healthy
     Response time: 0.245s
     🔐 Required JWT authentication

  ❌ api_payments_list
     URL: /api/payments/
     Status: unhealthy
     Error: Database connection failed
```

**JSON Output:**

```json
{
  "status": "unhealthy",
  "timestamp": "2025-10-05T18:00:20.111738+00:00",
  "total_endpoints": 399,
  "healthy": 0,
  "unhealthy": 69,
  "warnings": 0,
  "errors": 90,
  "skipped": 240,
  "endpoints": [
    {
      "url": "/cfg/api/endpoints/",
      "url_name": "endpoints_status",
      "namespace": "",
      "group": "cfg/api/endpoints",
      "view": "EndpointsStatusView",
      "status": "healthy",
      "status_code": 200,
      "response_time_ms": 0.23,
      "is_healthy": true,
      "last_checked": "2025-10-05T18:00:20.111738+00:00",
      "required_auth": false
    },
    {
      "url": "/api/users/",
      "url_name": "api_users_list",
      "namespace": "",
      "group": "api/users",
      "view": "UserViewSet",
      "status": "healthy",
      "status_code": 200,
      "response_time_ms": 0.45,
      "is_healthy": true,
      "last_checked": "2025-10-05T18:00:20.211738+00:00",
      "required_auth": true
    }
  ]
}
```

**What it checks:**

- ✅ All registered URL patterns
- ✅ HTTP status codes (200, 401, 403, etc.)
- ✅ Response times in milliseconds
- ✅ Endpoint availability
- ✅ Error detection and reporting
- ✅ Grouping by URL namespace

**Excluded endpoints:**

- ❌ Admin endpoints (`/admin/`)
- ❌ Static/media files (`/static/`, `/media/`)
- ❌ Health check endpoints (`/cfg/health/`)
- ❌ **Schema/Swagger/Redoc documentation** (`/schema/`)
- ❌ Django debug toolbar (`/__debug__/`, `/__reload__/`)

**Status Categories:**

| Status | Description | HTTP Codes |
|--------|-------------|------------|
| **Healthy** | Endpoint working correctly | 200-299, 301-308, 401, 403, 405 |
| **Warning** | Might be OK (no data) | 404 |
| **Unhealthy** | Endpoint has issues | 400, 500+ |
| **Error** | Exception occurred | Connection errors, timeouts |
| **Skipped** | Requires parameters | URLs with `<pk>`, `<id>` |

**Use Cases:**

**Development:**
```bash
# Quick check during development
python manage.py check_endpoints
```

**CI/CD Pipeline:**
```bash
# Automated testing in GitHub Actions
python manage.py check_endpoints --json > endpoints-report.json
```

**Production Monitoring:**
```bash
# Health check with custom timeout
python manage.py check_endpoints --timeout 10
```

**Debugging:**
```bash
# Check specific problematic endpoint
python manage.py check_endpoints --url api_users_list
```

**Features:**
- ✅ Auto-discovers all registered endpoints
- ✅ **Smart JWT Auto-Authentication** - Automatically retries protected endpoints with JWT token
- ✅ Creates test user `endpoint_test_user` once and reuses token
- ✅ Respects Django Test Client
- ✅ No ALLOWED_HOSTS issues (uses localhost)
- ✅ **Excludes schema/swagger/redoc** (prevents rate limiting issues)
- ✅ Excludes recursive endpoints (health checks)
- ✅ Colored console output with emojis
- ✅ JSON export for automation
- ✅ Response time measurement
- ✅ Indicates which endpoints required authentication (🔐)

---

## Database Operations

### `migrate_all`

Migrate all databases based on django-cfg configuration.

```bash
python manage.py migrate_all [OPTIONS]
```

**Options:**
- `--dry-run` - Show what would be migrated without executing
- `--skip-makemigrations` - Skip makemigrations step

**Examples:**

```bash
# Migrate all databases
python manage.py migrate_all

# Dry run to see what would happen
python manage.py migrate_all --dry-run

# Skip makemigrations
python manage.py migrate_all --skip-makemigrations
```

**Features:**
- Auto-detects all databases from django-cfg configuration
- Creates migrations for all apps
- Migrates each database based on routing configuration
- Migrates constance separately
- Handles app-specific routing

---

### `migrator`

Interactive database migration tool with automatic database detection and routing support.

```bash
python manage.py migrator [OPTIONS]
```

**Options:**
- `--auto` - Automatic migration mode (no prompts, migrates all databases)
- `--database TEXT` - Target specific database only
- `--app TEXT` - Target specific app only

**Examples:**

```bash
# Interactive mode (default) - shows menu
python manage.py migrator

# Auto-migrate all databases (no prompts)
python manage.py migrator --auto

# Migrate specific database
python manage.py migrator --database blog_db

# Migrate specific app across all databases
python manage.py migrator --app blog

# Migrate specific app on specific database
python manage.py migrator --database blog_db --app blog
```

**Interactive Mode:**

When run without `--auto`, shows an interactive menu:

```
🗄️  Django Database Migrator
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 Current Configuration:
   Databases: default, blog_db, shop_db
   Apps: accounts, blog, shop, profiles

What would you like to do?
> Migrate all databases (recommended)
  Migrate specific database
  Show database status
  View configuration info
  Exit
```

**Auto Mode (`--auto`):**

Runs automatic migration without prompts:

1. **Creates migrations** - Runs `makemigrations` for all apps
2. **Migrates default database** - Migrates main database first
3. **Migrates routed databases** - Migrates blog_db, shop_db based on routing rules
4. **Migrates constance** - Always migrates constance app (required by django-cfg)

**Example Output:**

```bash
$ python manage.py migrator --auto

🚀 Running automatic migration...

📦 Creating migrations for all apps...
✅ Migrations created successfully

🔄 Migrating database: default
  📦 Migrating all apps...
  ✅ Migrations completed for default

🔄 Migrating database: blog_db
  📦 Migrating app: blog
  ✅ Migrations completed for blog_db

🔄 Migrating database: shop_db
  📦 Migrating app: shop
  ✅ Migrations completed for shop_db

✅ Constance migrated successfully
```

**How Routing Works:**

The migrator respects `DATABASE_ROUTING_RULES` from settings:

```python
DATABASE_ROUTING_RULES = {
    'blog': 'blog_db',
    'shop': 'shop_db',
}
```

- Apps listed in routing rules → migrate on their target database only
- Apps NOT listed → migrate on default database
- Constance app → always migrates on default database

**Comparison with migrate_all:**

| Feature | `migrator --auto` | `migrate_all` |
|---------|-------------------|---------------|
| Interactive menu | ✅ Yes (without --auto) | ❌ No |
| Auto makemigrations | ✅ Yes | ✅ Yes (unless --skip-makemigrations) |
| Respects routing rules | ✅ Yes | ✅ Yes |
| Specific database | ✅ --database flag | ❌ Migrates all |
| Specific app | ✅ --app flag | ❌ Migrates all apps |
| Constance handling | ✅ Automatic | ✅ Automatic |
| Best for | Development, targeted migrations | Production, CI/CD |

**Use Cases:**

**Development:**
```bash
# Quick migration during development
python manage.py migrator --auto
```

**Testing specific database:**
```bash
# Test blog database migrations only
python manage.py migrator --database blog_db
```

**Troubleshooting:**
```bash
# Interactive mode to explore database status
python manage.py migrator
# Select "Show database status" from menu
```

**CI/CD Pipeline:**
```bash
# Production deployment - use migrate_all
python manage.py migrate_all
```

**Features:**
- ✅ Automatic database discovery from settings
- ✅ Respects DATABASE_ROUTING_RULES
- ✅ Interactive menu with questionary
- ✅ Progress indicators with emojis
- ✅ Database status checking
- ✅ Configuration info display
- ✅ Constance app auto-migration

---

## Development Server

### `runserver` (Enhanced)

Enhanced development server with better output and options.

```bash
poetry run cli runserver [OPTIONS]
```

**Options:**
- `--port INTEGER` - Port number (default: 8000)
- `--host TEXT` - Host address (default: 127.0.0.1)
- `--debug` - Enable debug mode
- `--no-reload` - Disable auto-reload

**Examples:**

```bash
# Basic server
poetry run cli runserver

# Custom port and host
poetry run cli runserver --port 3000 --host 0.0.0.0

# Production-like settings
poetry run cli runserver --no-reload --port 8080
```

**Features:**
- Rich colored output
- 📊 Better error formatting
- Faster startup time
- Smart configuration detection

---

## User Management

### `superuser` (Enhanced)

Enhanced superuser creation with better UX.

```bash
poetry run cli superuser [OPTIONS]
```

**Options:**
- `--email TEXT` - Email address for superuser
- `--username TEXT` - Username (optional, defaults to email)
- `--interactive` - Interactive mode (default)
- `--no-input` - Non-interactive mode

**Examples:**

```bash
# Interactive superuser creation
poetry run cli superuser

# Pre-fill email
poetry run cli superuser --email admin@example.com

# Non-interactive (password will be prompted)
poetry run cli superuser --email admin@test.com --no-input
```

---

### `create_token`

Create API tokens for authentication.

```bash
python manage.py create_token USERNAME [OPTIONS]
```

**Arguments:**
- `USERNAME` - Username to create token for

**Options:**
- `--name TEXT` - Token name/description
- `--expires-in INTEGER` - Expiration in days

**Examples:**

```bash
# Create token for user
python manage.py create_token admin

# Create token with specific name
python manage.py create_token admin --name "API Access Token"

# Create token with expiration (30 days)
python manage.py create_token admin --expires-in 30
```

---

## URL Management

### `show_urls` (Enhanced)

Lists all URL patterns in the project.

```bash
poetry run cli show-urls [OPTIONS]
```

**Options:**
- `--format [table|json|list]` - Output format (default: table)
- `--include-admin` - Include admin URLs
- `--pattern TEXT` - Filter URLs by pattern

**Examples:**

```bash
# Show all URLs in table format
poetry run cli show-urls

# JSON format for automation
poetry run cli show-urls --format json

# Filter API URLs only
poetry run cli show-urls --pattern "api/"

# Include admin URLs
poetry run cli show-urls --include-admin
```

---

### `list_urls`

List all URL patterns in the project.

```bash
python manage.py list_urls [OPTIONS]
```

**Options:**
- `--pattern TEXT` - Filter by pattern
- `--names-only` - Show URL names only
- `--output FILE` - Export to file

**Examples:**

```bash
# List all URLs
python manage.py list_urls

# Filter by pattern
python manage.py list_urls --pattern api

# Show URL names only
python manage.py list_urls --names-only

# Export to file
python manage.py list_urls --output urls.txt
```

---

## Utility Commands

### `clear_constance`

Clear Constance dynamic settings cache.

```bash
python manage.py clear_constance [OPTIONS]
```

**Options:**
- `--keys TEXT` - Clear specific keys (comma-separated)
- `--dry-run` - Dry run to see what would be cleared

**Examples:**

```bash
# Clear all constance cache
python manage.py clear_constance

# Clear specific keys
python manage.py clear_constance --keys KEY1,KEY2

# Dry run to see what would be cleared
python manage.py clear_constance --dry-run
```

---

## Best Practices

### 1. Always Validate Before Deploy

```bash
# Validate configuration before deployment
python manage.py validate_config --check-connections
```

### 2. Use Dry Run for Migrations

```bash
# Check what migrations would run
python manage.py migrate_all --dry-run
```

### 3. Check Settings After Configuration Changes

```bash
# Verify settings after changes
python manage.py check_settings --verbose
```

### 4. Create Tokens with Expiration

```bash
# Create tokens with limited lifetime
python manage.py create_token user --expires-in 90
```

### 5. Export Configuration for Documentation

```bash
# Export configuration as YAML
python manage.py show_config --format yaml > docs/config.yaml
```

---

## Command Workflow Examples

### Complete Project Setup

```bash
# Create project and initialize
django-cfg create-project "My Project" && \
cd my_project && \
python manage.py validate_config && \
python manage.py migrate_all && \
python manage.py createsuperuser
```

### Pre-Deployment Checklist

```bash
# Validate everything before deploying
python manage.py validate_config --check-connections && \
python manage.py check_settings --verbose && \
python manage.py migrate_all --dry-run && \
python manage.py collectstatic --noinput --dry-run
```

### Development Startup

```bash
# Quick development environment startup
python manage.py migrate_all && \
python manage.py runserver
```

---

## Related Documentation

- **[Quick Reference](./quick-reference)** - Fast command lookup
- **[AI Agents Commands](./ai-agents)** - Agent management
- **[Background Tasks Commands](./background-tasks)** - Dramatiq workers
- **[Development Commands](./development)** - Development tools

---

**Core commands power your Django-CFG project!** 🚀
