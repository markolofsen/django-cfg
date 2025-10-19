---
title: Dramatiq Configuration
description: Django-CFG configuration feature guide. Production-ready dramatiq configuration with built-in validation, type safety, and seamless Django integration.
sidebar_label: Configuration
sidebar_position: 2
keywords:
  - django-cfg configuration
  - django configuration
  - configuration django-cfg
---

# Configuration Patterns

Complete guide to configuring Dramatiq with Django-CFG using type-safe Pydantic models.

## Basic Configuration

### Zero-Config Setup

The simplest configuration - uses intelligent defaults:

```python
# config.py
from django_cfg import DjangoConfig, CacheConfig
from django_cfg.models.tasks import TaskConfig

class MyConfig(DjangoConfig):
    project_name: str = "MyApp"

    # Redis for cache + tasks
    cache_default: CacheConfig = CacheConfig(redis_url="redis://localhost:6379/0")

    # Enable tasks with zero configuration
    tasks: TaskConfig = TaskConfig()  # Uses intelligent defaults!

config = MyConfig()
```

**What you get:**
- ✅ Redis message broker (reuses cache configuration)
- ✅ Default middleware stack (retries, callbacks, db connections)
- ✅ Sensible worker defaults (processes=4, threads=8)
- ✅ Default queue ("default")

## Environment-Specific Configuration

### Development vs Production

```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.models.tasks import TaskConfig, DramatiqConfig
from .environment import env

class DevConfig(DjangoConfig):
    debug: bool = True

    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            processes=2,  # Fewer processes for development
            threads=4,    # Fewer threads for development
            prometheus_enabled=False,  # Disable monitoring in dev
        )
    )

class ProdConfig(DjangoConfig):
    debug: bool = False

    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            processes=8,   # More processes for production
            threads=16,    # More threads for production
            max_retries=5, # More retries in production
            queues=["critical", "default", "background"],
            prometheus_enabled=True,   # Enable monitoring
            admin_enabled=True,        # Enable admin interface
        )
    )

# Environment detection
config = ProdConfig() if env.environment == "production" else DevConfig()
```

## Advanced Configuration

### Custom Redis Configuration

```python
from django_cfg.models.tasks import TaskConfig

class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        broker_url="redis://redis-tasks.example.com:6379/0",  # Custom Redis instance
        result_backend="redis://redis-tasks.example.com:6379/1",  # Separate DB for results
    )
```

### Custom Middleware Stack

```python
from django_cfg.models.tasks import DramatiqConfig

class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            middleware=[
                "dramatiq.middleware.AgeLimit",
                "dramatiq.middleware.TimeLimit",
                "dramatiq.middleware.Callbacks",
                "dramatiq.middleware.Retries",
                "myapp.middleware.TaskTimingMiddleware",  # Custom middleware
                "django_dramatiq.middleware.AdminMiddleware",
                "django_dramatiq.middleware.DbConnectionsMiddleware",
            ]
        )
    )
```

### Multi-Queue Setup

```python
from django_cfg.models.tasks import DramatiqConfig

class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            queues=[
                "critical",    # High-priority tasks
                "default",     # Normal tasks
                "background",  # Low-priority background tasks
                "scheduled",   # Scheduled/cron tasks
            ],
            # Queue-specific worker configuration
            processes=8,
            threads=16,
        )
    )
```

## Worker Configuration

### Process and Thread Count

```python
from django_cfg.models.tasks import DramatiqConfig

class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            processes=4,   # Number of worker processes
            threads=8,     # Threads per process
            # Total concurrency: 4 * 8 = 32 tasks
        )
    )
```

**Guidelines:**
- **CPU-bound tasks:** `processes = CPU cores`, `threads = 1-2`
- **I/O-bound tasks:** `processes = 2-4`, `threads = 8-16`
- **Mixed workload:** `processes = 4`, `threads = 8` (default)

### Retry Configuration

```python
from django_cfg.models.tasks import DramatiqConfig

class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            max_retries=5,         # Maximum retry attempts
            min_backoff=1000,      # 1 second minimum backoff
            max_backoff=60000,     # 60 seconds maximum backoff
            max_age=3600000,       # 1 hour max task age (milliseconds)
        )
    )
```

## TaskConfig Reference

Complete reference for `TaskConfig` Pydantic model:

```python
from django_cfg.models.tasks import TaskConfig
from typing import Optional

class TaskConfig(BaseModel):
    """
    Dramatiq task queue configuration.

    Validates task settings and generates Django settings for Dramatiq.
    """

    # Required
    broker_url: str = Field(
        default="",  # Auto-detected from cache_default if empty
        description="Redis URL for message broker"
    )

    # Optional
    result_backend: Optional[str] = Field(
        default=None,
        description="Redis URL for result storage (uses broker_url if not set)"
    )

    enabled: bool = Field(
        default=True,
        description="Enable/disable task processing"
    )

    dramatiq: Optional[DramatiqConfig] = Field(
        default_factory=DramatiqConfig,
        description="Dramatiq-specific configuration"
    )

    def to_django_config(self) -> Dict[str, Any]:
        """Convert to Django settings dict"""
        # Implementation details...
```

## DramatiqConfig Reference

Complete reference for `DramatiqConfig` Pydantic model:

```python
from django_cfg.models.tasks import DramatiqConfig
from typing import List, Optional

class DramatiqConfig(BaseModel):
    """
    Dramatiq worker configuration.
    """

    processes: int = Field(
        default=4,
        ge=1,
        le=32,
        description="Number of worker processes"
    )

    threads: int = Field(
        default=8,
        ge=1,
        le=64,
        description="Threads per process"
    )

    queues: List[str] = Field(
        default_factory=lambda: ["default"],
        description="Queue names to process"
    )

    max_retries: int = Field(
        default=3,
        ge=0,
        description="Maximum retry attempts for failed tasks"
    )

    min_backoff: int = Field(
        default=1000,
        ge=100,
        description="Minimum backoff in milliseconds"
    )

    max_backoff: int = Field(
        default=30000,
        ge=1000,
        description="Maximum backoff in milliseconds"
    )

    max_age: Optional[int] = Field(
        default=None,
        ge=1000,
        description="Maximum task age in milliseconds"
    )

    prometheus_enabled: bool = Field(
        default=False,
        description="Enable Prometheus metrics"
    )

    admin_enabled: bool = Field(
        default=False,
        description="Enable admin interface integration"
    )

    middleware: List[str] = Field(
        default_factory=lambda: [
            "dramatiq.middleware.AgeLimit",
            "dramatiq.middleware.TimeLimit",
            "dramatiq.middleware.Callbacks",
            "dramatiq.middleware.Retries",
            "django_dramatiq.middleware.AdminMiddleware",
            "django_dramatiq.middleware.DbConnectionsMiddleware",
        ],
        description="Middleware stack (order matters!)"
    )
```

## Configuration Best Practices

### 1. Separate Redis Databases

```python
class MyConfig(DjangoConfig):
    # Cache on DB 0
    cache_default: CacheConfig = CacheConfig(redis_url="redis://localhost:6379/0")

    # Tasks on DB 1 (separate from cache)
    tasks: TaskConfig = TaskConfig(
        broker_url="redis://localhost:6379/1",
        result_backend="redis://localhost:6379/2",  # Results on DB 2
    )
```

### 2. Environment Variables

```python
from .environment import env

class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        broker_url=env.redis.tasks_url,  # From YAML config
        dramatiq=DramatiqConfig(
            processes=env.dramatiq.processes,  # From environment
            threads=env.dramatiq.threads,
        )
    )
```

### 3. Conditional Features

```python
class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            # Enable monitoring only in production
            prometheus_enabled=(env.environment == "production"),
            admin_enabled=(env.environment == "production"),

            # More resources in production
            processes=8 if env.environment == "production" else 2,
            threads=16 if env.environment == "production" else 4,
        )
    )
```

## Validation and Type Safety

Django-CFG validates configuration at startup:

```python
# This will FAIL at startup (before Django loads)
class MyConfig(DjangoConfig):
    tasks: TaskConfig = TaskConfig(
        dramatiq=DramatiqConfig(
            processes=100,  # ❌ ValidationError: Must be <= 32
            threads=0,      # ❌ ValidationError: Must be >= 1
            max_retries=-1, # ❌ ValidationError: Must be >= 0
        )
    )
```

**Benefits:**
- ✅ Errors caught at startup, not in production
- ✅ IDE autocomplete for all fields
- ✅ Type hints with field descriptions
- ✅ Clear validation error messages

## See Also

### Dramatiq Integration

**Core Documentation:**
- [**Dramatiq Overview**](./overview) - Background task processing introduction
- [**Implementation Guide**](./implementation) - Implementation roadmap and details
- [**Task Examples**](./examples) - Real-world task patterns
- [**Monitoring Guide**](./monitoring) - Observability and performance tracking
- [**Testing Tasks**](./testing) - Test background tasks

### Configuration & Setup

**Infrastructure:**
- [**Redis Configuration**](/fundamentals/configuration/cache) - Redis as message broker
- [**Configuration Models**](/fundamentals/configuration) - Complete Dramatiq config API
- [**Environment Detection**](/fundamentals/configuration/environment) - Environment-specific workers
- [**Environment Variables**](/fundamentals/configuration/environment) - Secure broker credentials

**Getting Started:**
- [**Installation**](/getting-started/installation) - Install Django-CFG with Dramatiq
- [**Configuration Guide**](/getting-started/configuration) - Enable background tasks
- [**First Project**](/getting-started/first-project) - Quick start tutorial

### Related Features

**Apps Using Dramatiq:**
- [**Operations Apps**](/features/built-in-apps/operations/overview) - Maintenance and tasks
- [**Tasks App**](/features/built-in-apps/operations/tasks) - Built-in task management
- [**AI Knowledge Base**](/features/built-in-apps/ai-knowledge/overview) - Document processing
- [**Payments System**](/features/built-in-apps/payments/overview) - Async payment processing
- [**Newsletter App**](/features/built-in-apps/user-management/newsletter) - Bulk email campaigns

**Integrations:**
- [**Ngrok Integration**](/features/integrations/ngrok/overview) - Webhook task triggers
- [**Integrations Overview**](/features/integrations/overview) - All integrations

### Tools & Deployment

**CLI & Management:**
- [**Background Task Commands**](/cli/commands/background-tasks) - Manage workers via CLI
- [**CLI Tools**](/cli/introduction) - Command-line interface
- [**Core Commands**](/cli/commands/core-commands) - Essential management

**Production:**
- [**Docker Deployment**](/guides/docker/production) - Containerized workers
- [**Production Config**](/guides/production-config) - Production task queue setup
- [**Logging**](/deployment/logging) - Task execution logging
- [**Troubleshooting**](/guides/troubleshooting) - Common task issues
