---
title: Operations Apps Overview
description: Django-CFG overview feature guide. Production-ready operations apps overview with built-in validation, type safety, and seamless Django integration.
sidebar_label: Overview
sidebar_position: 1
keywords:
  - django-cfg overview
  - django overview
  - overview django-cfg
---

# Operations Apps Overview

Operations apps handle site maintenance, background task processing, and operational automation for your Django-CFG projects.

## Maintenance App

**Simple Cloudflare site maintenance management using Page Rules**

- **🌐 Multi-Site Management** - Manage multiple Cloudflare sites
- **⚡ Page Rules Integration** - Works with Cloudflare Free plan
- **🔄 Bulk Operations** - Enable/disable maintenance for multiple sites
- **📊 Clean Admin Interface** - Unfold styled admin interface
- **📱 CLI Management** - Command-line automation tools

### Key Features

```python
# Simple maintenance control
from django_cfg.apps.maintenance import MaintenanceService

service = MaintenanceService(site)
service.enable_maintenance("Database upgrade")
service.disable_maintenance()
```

### What's New (Simplified)
- ✅ **Page Rules** instead of complex Workers
- ✅ **4 Models** instead of 8+ models  
- ✅ **Cloudflare Free** plan compatible
- ✅ **KISS principle** - Keep It Simple, Stupid

---

## Tasks App

**Asynchronous task processing with Django-RQ**

- **⚡ Background Jobs** - Process tasks asynchronously
- **🔄 Retry Logic** - Automatic retry with exponential backoff
- **📊 Monitoring** - Task status and performance tracking
- **🎯 Priority Queues** - Multiple priority levels
- **📱 Admin Interface** - Task management via Django admin

### Key Features

```python
# Define and run background tasks
from django_cfg.apps.tasks import task

@task()
def send_email_task(user_id, subject, message):
    # Process in background
    pass

# Queue task
send_email_task.delay(user_id=123, subject="Hello", message="World")
```

---

## Best Practices

### 1. **Use Maintenance for Site Operations**
```python
# Scheduled maintenance
service.enable_maintenance("Planned database migration - ETA 30min")
# Perform migration
service.disable_maintenance()
```

### 2. **Use Tasks for Heavy Processing**
```python
@task()
def process_large_dataset(dataset_id):
    # Long-running data processing
    pass
```

### 3. **Monitor Operations**
```python
# Check maintenance logs
logs = MaintenanceLog.objects.filter(status='failed')

# Check task status
from django_cfg.apps.tasks import TaskResult
failed_tasks = TaskResult.objects.filter(status='failed')
```

## See Also

### Operations Apps

**Operations Features:**
- **[Maintenance Documentation](./maintenance)** - Complete maintenance app guide
- **[Tasks Documentation](./tasks)** - Django-RQ task processing guide
- **[Built-in Apps Overview](/features/built-in-apps/overview)** - All available apps

**Background Processing:**
- **[Django-RQ Integration](/features/integrations/django-rq/overview)** - Background tasks framework
- **[Background Task Commands](/features/integrations/django-rq/overview)** - Manage workers via CLI
- **[Production Config](/guides/production-config)** - Production task setup

### Configuration & Setup

**Getting Started:**
- **[Configuration Guide](/getting-started/configuration)** - Enable operations apps
- **[First Project](/getting-started/first-project)** - Quick start tutorial
- **[Installation](/getting-started/installation)** - Install Django-CFG

**Advanced Configuration:**
- **[Configuration Models](/fundamentals/configuration)** - Operations config API
- **[Environment Detection](/fundamentals/configuration/environment)** - Environment-specific setup
- **[Cache Configuration](/fundamentals/configuration/cache)** - Redis setup for tasks

### Tools & Deployment

**CLI Tools:**
- **[CLI Introduction](/cli/introduction)** - Command-line tools overview
- **[Core Commands](/cli/commands/core-commands)** - Essential operations commands
- **[Deployment](/guides/docker/production)** - Production deployment

**Guides:**
- **[Troubleshooting](/guides/troubleshooting)** - Common operations issues
- **[Production Best Practices](/guides/production-config)** - Operational patterns

Operations apps provide the backbone for reliable site operations and background processing! ⚙️
