---
title: Implementation Guide
description: Django-CFG implementation feature guide. Production-ready implementation guide with built-in validation, type safety, and seamless Django integration.
sidebar_label: Implementation
sidebar_position: 3
keywords:
  - django-cfg implementation
  - django implementation
  - implementation django-cfg
---

# Implementation Guide

Learn how to implement task queues using Django-CFG's built-in Dramatiq integration. Everything is already configured and ready to use!

## Built-in Features

Django-CFG provides **production-ready Dramatiq integration out of the box**:

✅ **rundramatiq command** - Ready to use, no configuration needed
✅ **Multiple queues** - Create as many queues as you need
✅ **Worker management** - Process/thread configuration
✅ **Redis integration** - Reuses your cache configuration
✅ **Type-safe config** - Pydantic v2 validation

## How It Works

### 1. Zero-Config Setup

The simplest way to get started - just enable tasks:

```python
# config.py
from django_cfg import DjangoConfig, CacheConfig
from django_cfg.models.tasks import TaskConfig

class MyConfig(DjangoConfig):
    project_name: str = "MyApp"

    # Redis configuration
    cache_default: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/0"
    )

    # Enable Dramatiq - that's it!
    tasks: TaskConfig = TaskConfig()

config = MyConfig()
```

**What you get automatically:**
- ✅ `rundramatiq` management command
- ✅ Default queue configured
- ✅ Worker processes and threads set up
- ✅ Retry logic with exponential backoff
- ✅ Database connection management
- ✅ Admin interface (if enabled)

### 2. Start Workers

```bash
# Start with defaults (4 processes, 8 threads, "default" queue)
python manage.py rundramatiq

# That's it! Workers are now processing tasks
```

## Creating Multiple Queues

Need different priority queues? Just configure them:

```python
from django_cfg.models.tasks import TaskConfig, DramatiqConfig

class MyConfig(DjangoConfig):
    # ... other config ...

    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            queues=[
                "critical",    # High-priority tasks
                "default",     # Normal tasks
                "background",  # Low-priority tasks
            ]
        )
    )
```

### Define Tasks for Each Queue

```python
# tasks.py
import dramatiq

# Critical queue - payment processing
@dramatiq.actor(queue_name="critical", max_retries=5)
def process_payment(payment_id: int):
    # Payment processing logic
    pass

# Default queue - email sending
@dramatiq.actor(queue_name="default")
def send_email(user_id: int):
    # Email sending logic
    pass

# Background queue - cleanup tasks
@dramatiq.actor(queue_name="background")
def cleanup_old_files():
    # Cleanup logic
    pass
```

### Run Workers for Specific Queues

```bash
# Process only critical tasks (high-priority workers)
python manage.py rundramatiq --queues critical --processes 8 --threads 16

# Process default and background tasks (lower priority)
python manage.py rundramatiq --queues default,background --processes 4 --threads 8
```

## Practical Implementation Patterns

### Pattern 1: Priority-Based Processing

```python
# config.py
class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            queues=["high", "normal", "low"],
            processes=4,
            threads=8,
        )
    )

# tasks.py
@dramatiq.actor(queue_name="high", max_retries=5, min_backoff=1000)
def critical_task(data_id: int):
    """Tasks that must complete quickly and reliably"""
    pass

@dramatiq.actor(queue_name="normal")
def standard_task(data_id: int):
    """Regular background tasks"""
    pass

@dramatiq.actor(queue_name="low", max_retries=1)
def bulk_operation(batch_ids: list):
    """Large batch operations, low priority"""
    pass
```

**Deployment:**
```bash
# Start 2 worker groups

# High-priority workers (more resources)
nohup python manage.py rundramatiq --queues high --processes 8 --threads 16 > high.log 2>&1 &

# Normal + low priority workers (fewer resources)
nohup python manage.py rundramatiq --queues normal,low --processes 4 --threads 8 > low.log 2>&1 &
```

### Pattern 2: Service-Based Queues

```python
# config.py
class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            queues=[
                "email",      # Email service
                "sms",        # SMS service
                "reports",    # Report generation
                "cleanup",    # Maintenance tasks
            ]
        )
    )

# tasks.py
@dramatiq.actor(queue_name="email")
def send_email(user_id: int, template: str):
    """Email sending tasks"""
    pass

@dramatiq.actor(queue_name="sms")
def send_sms(phone: str, message: str):
    """SMS sending tasks"""
    pass

@dramatiq.actor(queue_name="reports")
def generate_report(user_id: int, report_type: str):
    """Heavy report generation"""
    pass

@dramatiq.actor(queue_name="cleanup")
def cleanup_task(resource_type: str):
    """Cleanup and maintenance"""
    pass
```

**Deployment:**
```bash
# Dedicated worker for each service type
python manage.py rundramatiq --queues email --processes 2 --threads 8 &
python manage.py rundramatiq --queues sms --processes 2 --threads 4 &
python manage.py rundramatiq --queues reports --processes 4 --threads 16 &
python manage.py rundramatiq --queues cleanup --processes 1 --threads 2 &
```

### Pattern 3: Environment-Based Configuration

```python
# config.py
from .environment import env

class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            # Development: Fewer resources, simple queues
            queues=["default"] if env.environment == "development" else [
                "critical", "default", "background"
            ],

            # Production: More resources
            processes=8 if env.environment == "production" else 2,
            threads=16 if env.environment == "production" else 4,

            # Production: More retries
            max_retries=5 if env.environment == "production" else 2,
        )
    )
```

## Using rundramatiq Command

### Basic Usage

```bash
# Start with all default settings
python manage.py rundramatiq

# Equivalent to:
# --processes 4
# --threads 8
# --queues default
```

### Advanced Usage

```bash
# Custom process and thread count
python manage.py rundramatiq --processes 8 --threads 16

# Specific queues
python manage.py rundramatiq --queues critical,default

# With verbose logging
python manage.py rundramatiq --log-level debug

# Combine options
python manage.py rundramatiq \
    --queues critical,default \
    --processes 6 \
    --threads 12 \
    --log-level info
```

### Production Deployment

```bash
# Using systemd service
# /etc/systemd/system/dramatiq-workers.service

[Unit]
Description=Dramatiq Workers
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/app
Environment="DJANGO_SETTINGS_MODULE=myproject.settings"
ExecStart=/app/venv/bin/python manage.py rundramatiq --queues critical,default --processes 8 --threads 16
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Start service
sudo systemctl start dramatiq-workers
sudo systemctl enable dramatiq-workers  # Auto-start on boot

# Monitor service
sudo systemctl status dramatiq-workers
sudo journalctl -u dramatiq-workers -f  # Follow logs
```

## Task Execution Flow

Understanding how tasks are executed:

```
1. Task Definition
   @dramatiq.actor(queue_name="default")
   def my_task(data): ...
   ↓
2. Task Enqueued
   my_task.send(data)
   ↓
3. Redis Queue
   Task message stored in Redis
   ↓
4. Worker Picks Up Task
   rundramatiq worker reads from queue
   ↓
5. Task Executed
   Worker executes task function
   ↓
6. Result/Retry
   Success → Done
   Failure → Retry (if retries remain)
```

## Built-in Middleware

Django-CFG configures these middleware automatically:

```python
# Automatically configured - no action needed
DRAMATIQ_BROKER = {
    "MIDDLEWARE": [
        "dramatiq.middleware.AgeLimit",           # Discard old tasks
        "dramatiq.middleware.TimeLimit",          # Timeout protection
        "dramatiq.middleware.Callbacks",          # Task callbacks
        "dramatiq.middleware.Retries",            # Retry logic
        "django_dramatiq.middleware.AdminMiddleware",        # Admin interface
        "django_dramatiq.middleware.DbConnectionsMiddleware", # DB connections
    ]
}
```

**What each middleware does:**
- **AgeLimit**: Discards tasks older than max_age
- **TimeLimit**: Kills tasks that run too long
- **Callbacks**: Execute callbacks after task completion
- **Retries**: Implements exponential backoff retry logic
- **AdminMiddleware**: Enables task monitoring in Django admin
- **DbConnectionsMiddleware**: Manages Django DB connections properly

## Queue Management

### Checking Queue Status

```bash
# Get queue statistics
python manage.py dramatiq_status

# Output:
# Queue: critical (5 pending, 2 processing)
# Queue: default (12 pending, 4 processing)
# Queue: background (100 pending, 8 processing)
```

### Clearing Failed Tasks

```bash
# Clear all failed tasks
python manage.py dramatiq_clear_failed

# Retry specific failed tasks
python manage.py dramatiq_retry_failed --queue critical
```

## Resource Optimization

### CPU-Bound Tasks

```python
# config.py - For CPU-heavy tasks
class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            processes=8,  # Match CPU cores
            threads=2,    # Minimal threads
        )
    )
```

### I/O-Bound Tasks

```python
# config.py - For I/O-heavy tasks (API calls, file operations)
class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            processes=4,   # Fewer processes
            threads=16,    # More threads
        )
    )
```

### Mixed Workload

```python
# config.py - Balanced configuration (default)
class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            processes=4,
            threads=8,
        )
    )
```

## Monitoring Workers

### Check Running Workers

```bash
# List all workers
ps aux | grep rundramatiq

# Count running workers
pgrep -f rundramatiq | wc -l

# Detailed worker info
python manage.py dramatiq_workers
```

### Worker Metrics

```python
# Add to your monitoring/metrics endpoint
from django_cfg.modules.django_tasks import get_task_service

def get_worker_stats():
    task_service = get_task_service()

    return {
        "workers": task_service.get_worker_stats(),
        "queues": task_service.get_queue_stats(),
        "redis_connection": task_service.check_redis_connection()
    }
```

## Best Practices

### 1. Queue Organization
✅ Separate queues by priority or service
✅ Use descriptive queue names
✅ Monitor queue depths regularly

### 2. Worker Configuration
✅ Start with defaults, optimize based on metrics
✅ CPU-bound: More processes, fewer threads
✅ I/O-bound: Fewer processes, more threads

### 3. Task Design
✅ Keep tasks idempotent (safe to retry)
✅ Use appropriate queue for each task
✅ Set reasonable max_retries
✅ Add proper error handling

### 4. Production Deployment
✅ Use systemd or supervisor for workers
✅ Enable automatic restart on failure
✅ Monitor worker health
✅ Log to centralized logging system

## Troubleshooting

### Workers Not Starting

```bash
# Check Redis connection
redis-cli ping

# Check Django settings
python manage.py check

# Try manual start with debug logging
python manage.py rundramatiq --log-level debug
```

### Tasks Not Processing

```bash
# Check queue depth
python manage.py dramatiq_status

# Verify workers are running
pgrep -af rundramatiq

# Check Redis for messages
redis-cli
> LLEN "default.DQ"  # Check default queue length
```

### High Memory Usage

```python
# Reduce worker count
tasks: TaskConfig = TaskConfig(
    dramatiq=DramatiqConfig(
        processes=2,  # Reduce processes
        threads=4,    # Reduce threads
    )
)
```

## See Also

### Dramatiq Integration

**Core Documentation:**
- [**Dramatiq Overview**](./overview) - Background task processing introduction
- [**Configuration Guide**](./configuration) - Advanced configuration patterns
- [**Task Examples**](./examples) - Real-world implementation examples
- [**Monitoring Guide**](./monitoring) - Performance tracking and observability
- [**Testing Tasks**](./testing) - Test background tasks

### Implementation Guides

**Practical Guides:**
- [**Sample Project Guide**](/guides/sample-project/overview) - Production example
- [**Examples Overview**](/guides/examples) - More implementation patterns
- [**Production Config**](/guides/production-config) - Production task setup
- [**Troubleshooting**](/guides/troubleshooting) - Common implementation issues

**Related Features:**
- [**Operations Apps**](/features/built-in-apps/operations/overview) - Operational features
- [**Tasks App**](/features/built-in-apps/operations/tasks) - Task management
- [**Email Module**](/features/modules/email/overview) - Background email sending

### Configuration & Infrastructure

**Setup:**
- [**Installation**](/getting-started/installation) - Install Django-CFG with Dramatiq
- [**Configuration Guide**](/getting-started/configuration) - Enable background tasks
- [**First Project**](/getting-started/first-project) - Quick start tutorial

**Infrastructure:**
- [**Redis Configuration**](/fundamentals/configuration/cache) - Redis as message broker
- [**Environment Variables**](/fundamentals/configuration/environment) - Broker credentials
- [**Environment Detection**](/fundamentals/configuration/environment) - Environment-specific setup

**Apps Using Tasks:**
- [**AI Knowledge Base**](/features/built-in-apps/ai-knowledge/overview) - Document processing
- [**Payments System**](/features/built-in-apps/payments/overview) - Async payments
- [**Newsletter App**](/features/built-in-apps/user-management/newsletter) - Bulk emails

### Tools & Deployment

**CLI & Management:**
- [**Background Task Commands**](/cli/commands/background-tasks) - Manage workers
- [**CLI Tools**](/cli/introduction) - Command-line interface

**Production:**
- [**Docker Deployment**](/guides/docker/production) - Containerized workers
- [**Logging**](/deployment/logging) - Task execution logging
