---
title: Maintenance App - Simple Cloudflare Site Management
description: Django-CFG maintenance feature guide. Production-ready maintenance app - simple cloudflare site management with built-in validation, type safety, and seamless D
sidebar_label: Maintenance
sidebar_position: 2
keywords:
  - django-cfg maintenance
  - django maintenance
  - maintenance django-cfg
---

# Maintenance App - Simple Cloudflare Site Management

The **Maintenance** app provides a simple, efficient solution for managing maintenance mode across Cloudflare sites using Page Rules. Built with the **KISS principle** (Keep It Simple, Stupid), it focuses on core functionality without unnecessary complexity.

## Overview

The Maintenance app includes:

- **🌐 Multi-Site Management** - Manage Cloudflare sites with simple ORM interface
- **⚡ Page Rules Integration** - Works with Cloudflare Free plan using Page Rules
- **🔄 Bulk Operations** - Enable/disable maintenance for multiple sites simultaneously
- **📊 Clean Admin Interface** - Django admin integration with Unfold styling
- **📱 CLI Management** - Simple management commands for automation
- **📋 Audit Trail** - Operation logging for transparency

## Architecture

### Core Models

```python
# Essential Models (4 total)
CloudflareSite       # Site configuration with custom maintenance URLs
CloudflareApiKey     # API key management with automatic defaults
MaintenanceLog       # Operation audit trail
ScheduledMaintenance # Planned maintenance events
```

### Service Layer

```python
# Core Services (4 total)
MaintenanceService      # Page Rules based maintenance control
SiteSyncService        # Automatic site discovery from Cloudflare
BulkOperationsService  # Multi-site operations
ScheduledMaintenanceService # Maintenance scheduling
```

### Management Commands

```python
# CLI Commands (3 total)
maintenance                   # Site maintenance management
sync_cloudflare              # Site discovery and synchronization
process_scheduled_maintenance # Scheduled maintenance processor
```

## Quick Start

### Enable in Configuration

```python
# config.py
from django_cfg import DjangoConfig

class MyProjectConfig(DjangoConfig):
    # Enable maintenance app
    enable_maintenance: bool = True
```

### Environment Configuration

```yaml
# config.dev.yaml
# No additional configuration needed!
# Just add your Cloudflare API token via admin interface
```

### Run Migrations

```bash
python manage.py migrate
```

### Add Cloudflare API Key

1. Go to Django Admin: `/admin/maintenance/cloudflareapikey/`
2. Add your Cloudflare API token
3. Sites will be auto-discovered and synced

## Site Management

### Simple Interface

```python
from django_cfg.apps.maintenance import CloudflareSite, MaintenanceService

# Get site
site = CloudflareSite.objects.get(domain='example.com')

# Enable maintenance
service = MaintenanceService(site)
log_entry = service.enable_maintenance("Database upgrade")

# Disable maintenance  
log_entry = service.disable_maintenance()

# Check status
is_active = service.get_status()
```

### Custom Maintenance URLs

```python
# Create site with custom maintenance page
site = CloudflareSite.objects.create(
    name="My Site",
    domain="example.com", 
    zone_id="zone_123",
    account_id="account_123",
    api_key=api_key,
    
    # Custom maintenance URL (optional)
    maintenance_url="https://status.mycompany.com/?site=example.com"
)

# If maintenance_url is empty, uses default:
# https://docs.djangocfg.com/maintenance?site=example.com
```

### Subdomain Configuration

```python
# Default: Include ALL subdomains (*.example.com)
site = CloudflareSite.objects.create(
    name="My Site",
    domain="example.com",
    api_key=api_key,
    include_subdomains=True,    # Default: True
    subdomain_list=""           # Default: empty
)

# Custom: Include SPECIFIC subdomains only
site = CloudflareSite.objects.create(
    name="My Site", 
    domain="example.com",
    api_key=api_key,
    include_subdomains=False,   # Disable wildcard
    subdomain_list="api,dashboard,www"  # Specific subdomains
)

# This will create Page Rules for:
# - api.example.com/*
# - dashboard.example.com/* 
# - www.example.com/*
# (root example.com/* is always included)
```

### Bulk Operations

```python
# Enable maintenance for multiple sites
sites = CloudflareSite.objects.filter(is_active=True)
results = CloudflareSite.objects.bulk_sync_all()
print(f"Synced: {results['synced']}, Errors: {results['errors']}")

# Discover new sites
results = CloudflareSite.objects.discover_all_sites()
print(f"Discovered: {results['created']} new sites")
```

## CLI Management

### Basic Commands

```bash
# Enable maintenance for specific domain
python manage.py maintenance enable example.com --reason "Database upgrade"

# Disable maintenance
python manage.py maintenance disable example.com

# Check status
python manage.py maintenance status example.com

# List all sites
python manage.py maintenance list
```

### Site Discovery

```bash
# Sync sites from Cloudflare
python manage.py sync_cloudflare

# Force full sync
python manage.py sync_cloudflare --force

# Sync specific API key
python manage.py sync_cloudflare --api-key "My API Key"
```

## Admin Interface

### Site Management

The admin interface provides:

- **📋 Site List** - Overview with maintenance status badges
- **🔄 Action Buttons** - Individual site actions (sync, enable/disable maintenance)
- **📈 Bulk Actions** - Mass operations from the list view
- **🔍 Filtering** - Filter by maintenance status, API key, activity
- **📝 Logs** - Complete operation history

### Available Actions

#### Individual Site Actions (Detail View)
- **🔄 Sync with Cloudflare** - Update site configuration
- **🔧 Enable Maintenance** - Put site in maintenance mode
- **✅ Disable Maintenance** - Remove maintenance mode

#### Bulk Actions (List View)
- **🔄 Bulk Sync Sites** - Sync multiple sites with Cloudflare
- **🔍 Bulk Discover Sites** - Discover new sites from Cloudflare

### Accessing Admin

```bash
# Navigate to maintenance admin
http://localhost:8000/admin/maintenance/cloudflaresite/

# Individual actions available in site detail view
# Bulk actions available in site list view
```

## How It Works

### Page Rules Technology

The maintenance app uses **Cloudflare Page Rules** instead of Workers, making it compatible with **Cloudflare Free plans**:

1. **Enable Maintenance**: Creates Page Rules that redirect domains to maintenance page
   - **All Subdomains**: `*.domain.com/*` + `domain.com/*` (if `include_subdomains=True`)
   - **Specific Subdomains**: Individual rules for each subdomain (if `include_subdomains=False`)
2. **Disable Maintenance**: Finds and deletes all maintenance Page Rules for the site
3. **Custom URLs**: Supports custom maintenance pages or uses default Django-CFG page
4. **Subdomain Support**: Flexible configuration for subdomain handling

### Automatic Discovery

```python
from django_cfg.apps.maintenance.services import SiteSyncService

# Auto-discover zones from Cloudflare
api_key = CloudflareApiKey.objects.get_default()
sync_service = SiteSyncService(api_key)

# Discover and create/update sites
sites_data = sync_service.sync_zones()
print(f"Processed {len(sites_data)} zones")
```

### What Gets Auto-Configured

1. **Zone Discovery** - Finds all zones in Cloudflare account
2. **Site Creation** - Creates Django models for each zone  
3. **Configuration Sync** - Updates zone_id, account_id automatically
4. **Status Tracking** - Tracks maintenance state and history
5. **Default Subdomain Settings** - New sites include all subdomains by default

> **Important**: Sync operations **preserve** user-configured subdomain settings. Manual changes to `include_subdomains`, `subdomain_list`, and `maintenance_url` are never overwritten by sync operations.

## Event Tracking

### Maintenance Logs

```python
from django_cfg.apps.maintenance.models import MaintenanceLog

# All operations are automatically logged
logs = MaintenanceLog.objects.filter(
    site__domain='example.com'
).order_by('-created_at')

for log in logs:
    print(f"{log.created_at}: {log.action}")
    print(f"  Status: {log.status}")
    print(f"  Duration: {log.duration_seconds}s")
    if log.error_message:
        print(f"  Error: {log.error_message}")
```

### Log Statistics

```python
# Get operation statistics
stats = MaintenanceLog.objects.get_stats(days=30)
print(f"Success rate: {stats['success_rate']:.1f}%")
print(f"Average duration: {stats['avg_duration']:.1f}s")
print(f"Total operations: {stats['total']}")
```

## Configuration

### API Key Management

```python
from django_cfg.apps.maintenance.models import CloudflareApiKey

# Create API key
api_key = CloudflareApiKey.objects.create(
    name="Production Key",
    api_token="your_cloudflare_token_here",
    account_id="auto_discovered",  # Auto-filled on first use
    is_default=True,  # Use as default for new sites
    is_active=True
)

# Multiple API keys supported
api_key2 = CloudflareApiKey.objects.create(
    name="Development Key", 
    api_token="dev_token_here",
    is_active=True
)
```

### Site Configuration

```python
from django_cfg.apps.maintenance.models import CloudflareSite

# Manual site creation
site = CloudflareSite.objects.create(
    name="My Production Site",
    domain="example.com",
    api_key=api_key,
    
    # Optional: auto-discovered if not provided
    zone_id="zone_123",
    account_id="account_123",
    
    # Custom maintenance page
    maintenance_url="https://status.example.com",
    
    # Subdomain configuration (manual)
    include_subdomains=False,              # Don't use wildcard
    subdomain_list="api,dashboard,www",    # Specific subdomains
    
    # Site settings
    is_active=True
)

# User can modify subdomain settings later via admin or code:
site.include_subdomains = True    # Switch to include all subdomains
site.subdomain_list = ""          # Clear specific list
site.save()
```

## 🧪 Testing

### Simple Tests

```python
from django.test import TestCase
from django_cfg.apps.maintenance import CloudflareSite, MaintenanceService

class MaintenanceTest(TestCase):
    def setUp(self):
        self.api_key = CloudflareApiKey.objects.create(
            name="Test Key",
            api_token="test_token",
            is_default=True
        )
        self.site = CloudflareSite.objects.create(
            name="Test Site",
            domain="test.example.com",
            api_key=self.api_key
        )
    
    def test_maintenance_cycle(self):
        service = MaintenanceService(self.site)
        
        # Test enable
        log = service.enable_maintenance("Test reason")
        self.assertEqual(log.status, 'success')
        
        # Test status
        self.assertTrue(service.get_status())
        
        # Test disable
        log = service.disable_maintenance()
        self.assertEqual(log.status, 'success')
        self.assertFalse(service.get_status())
```

### Test Coverage

Current test coverage includes:
- **✅ Models** - All model methods and managers
- **✅ Services** - Core maintenance operations  
- **✅ Utils** - Retry logic and error handling
- **✅ Commands** - CLI command functionality

## 🔒 Security Features

### Access Control
- **API Token Security** - Tokens stored securely in database
- **Permission Validation** - All operations validate API permissions
- **Error Handling** - Safe error messages without sensitive data exposure

### Input Validation
- **Domain Validation** - Ensures valid domain formats
- **API Response Validation** - Validates Cloudflare API responses
- **URL Validation** - Validates custom maintenance URLs

## Performance

### Optimizations
- **Lazy Imports** - Models and services loaded on demand
- **Retry Logic** - Exponential backoff for API failures
- **JSON Serialization** - Safe handling of datetime objects in logs
- **Efficient Queries** - Custom managers with optimized querysets

### Rate Limiting
```python
# Built-in retry with exponential backoff
@retry_on_failure(max_retries=3, base_delay=1.0)
def _create_maintenance_page_rule(self):
    # Handles API rate limits automatically
    return self.client.page_rules.create(...)
```

## Best Practices

### 1. Use Descriptive Reasons

```python
# Good: Specific and informative
service.enable_maintenance("Database migration v2.1 - ETA 30 minutes")

# Avoid: Vague messages  
service.enable_maintenance("Maintenance")
```

### 2. Set Custom Maintenance URLs

```python
# Branded maintenance page
site.maintenance_url = "https://status.yourcompany.com/?site=example.com"
site.save()
```

### 3. Configure Subdomains Appropriately

```python
# For most sites: Include all subdomains (default)
site.include_subdomains = True
site.subdomain_list = ""

# For specific control: List only critical subdomains
site.include_subdomains = False
site.subdomain_list = "api,dashboard,www"  # Skip dev/test subdomains

# Mixed approach: Add specific subdomains to wildcard
# (not supported - use one approach or the other)
```

### 4. Monitor Logs

```python
# Check for errors regularly
failed_logs = MaintenanceLog.objects.filter(
    status='failed',
    created_at__gte=timezone.now() - timedelta(days=1)
)

if failed_logs.exists():
    # Alert administrators
    send_alert_email(failed_logs)
```

### 5. Test in Development

```bash
# Always test maintenance flow
python manage.py maintenance enable dev.example.com --reason "Testing"
# Verify maintenance page loads
python manage.py maintenance disable dev.example.com
```

## 🆚 Migration from Complex Version

If migrating from the old complex maintenance app:

### What's Removed
- ❌ **Workers Support** - Now uses Page Rules only
- ❌ **Monitoring System** - External monitoring removed
- ❌ **Site Groups** - Simplified to direct site management
- ❌ **User Ownership** - Sites are global, not user-specific
- ❌ **Complex Templates** - Uses simple URL redirects
- ❌ **API Endpoints** - Admin and CLI only

### What's Simplified
- ✅ **4 Models** instead of 8+ models
- ✅ **Page Rules** instead of Worker deployment
- ✅ **Simple CLI** instead of complex filtering
- ✅ **Direct Operations** instead of async processing
- ✅ **Cloudflare Free** compatible

### Migration Steps
1. Export site data from old app
2. Install new maintenance app
3. Create API keys in admin
4. Import/recreate sites
5. Test maintenance operations

## Related Documentation

- [**Configuration Guide**](/fundamentals/configuration) - Basic Django-CFG setup
- [**CLI Tools**](/cli/introduction) - Command-line usage
- [**Deployment Guide**](/deployment/environment-setup) - Production setup
- [**Admin Interface**](/features/modules/unfold/overview) - Unfold admin styling

The simplified Maintenance app provides efficient site maintenance management with minimal complexity! 🌐
