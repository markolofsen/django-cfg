> **📚 Part of**: [ReArq Integration](/features/integrations/rearq/overview) - Return to ReArq overview

# ReArq Configuration Guide

**Status**: Production Ready
**Author**: Django-CFG Team
**Date**: 2025-10-30
**Version**: 2.0

---

## Overview

Complete configuration reference for ReArq task system integration in django-cfg. This guide covers all configuration options, environment-specific settings, and production deployment patterns.

**Key Features**:
- Zero-configuration defaults for quick setup
- Comprehensive field validation with Pydantic
- Environment-aware smart defaults
- Production-ready configuration patterns
- Redis Sentinel and cluster support

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [Configuration Models](#configuration-models)
3. [Basic Configuration](#basic-configuration)
4. [Environment-Specific Configuration](#environment-specific-configuration)
5. [Advanced Configuration](#advanced-configuration)
6. [Worker Configuration](#worker-configuration)
7. [Queue Configuration](#queue-configuration)
8. [Redis Configuration](#redis-configuration)
9. [Database Configuration](#database-configuration)
10. [Configuration Validation](#configuration-validation)
11. [Best Practices](#best-practices)

---

## Quick Start

### Zero-Config Example

The simplest way to enable ReArq tasks with all defaults:

```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.models.tasks import TaskConfig

class Config(DjangoConfig):
    project_name = "My Project"

    # Enable tasks with all defaults
    tasks = TaskConfig(enabled=True)

config = Config()
```

**What you get**:
- Redis URL: `redis://localhost:6379/0`
- Database URL: `sqlite://./rearq.db`
- Max jobs: `10`
- Job timeout: `300` seconds (5 minutes)
- Retry count: `3`
- Auto task discovery enabled

### Minimal Production Config

```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.models.tasks import TaskConfig, RearqConfig

class Config(DjangoConfig):
    project_name = "My Project"

    tasks = TaskConfig(
        enabled=True,
        rearq=RearqConfig(
            redis_url="redis://localhost:6379/0",
            db_url="postgresql://user:pass@localhost/myproject",
        )
    )

config = Config()
```

---

## Configuration Models

### TaskConfig (Main Entry Point)

**Location**: `/Users/markinmatrix/Documents/htdocs/@CARAPIS/encar_parser_new/@projects/django-cfg/projects/django-cfg-dev/src/django_cfg/models/tasks/config.py`

```python
from django_cfg.models.tasks import TaskConfig, TaskBackend, RearqConfig

config = TaskConfig(
    # === Core Settings ===
    enabled=True,                      # Enable background task processing
    backend=TaskBackend.REARQ,         # Task processing backend (only ReArq supported)

    # === Backend Configuration ===
    rearq=RearqConfig(...),            # ReArq-specific settings (see below)

    # === Auto-Discovery ===
    auto_discover_tasks=True,          # Auto-discover tasks in Django apps
    task_modules=["tasks"],            # Module names to search for tasks

    # === Environment Overrides ===
    dev_processes=2,                   # Processes in development
    prod_processes=None,               # Processes in production (None = auto)
)
```

**Field Details**:

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `enabled` | `bool` | `True` | Master switch for entire task system |
| `backend` | `TaskBackend` | `REARQ` | Task backend (only ReArq supported) |
| `rearq` | `RearqConfig` | Auto-initialized | ReArq-specific configuration |
| `auto_discover_tasks` | `bool` | `True` | Auto-discover task modules in Django apps |
| `task_modules` | `List[str]` | `["tasks"]` | Module names to search (e.g., "tasks", "background") |
| `dev_processes` | `int` | `2` | Number of processes in development |
| `prod_processes` | `int` | `None` | Number of processes in production |

### RearqConfig (Backend Settings)

**Location**: `/Users/markinmatrix/Documents/htdocs/@CARAPIS/encar_parser_new/@projects/django-cfg/projects/django-cfg-dev/src/django_cfg/models/tasks/backends.py`

```python
from django_cfg.models.tasks import RearqConfig

rearq = RearqConfig(
    # === Core Settings ===
    redis_url="redis://localhost:6379/0",
    db_url="sqlite://./rearq.db",

    # === Worker Settings ===
    max_jobs=10,                       # Max concurrent jobs per worker
    job_timeout=300,                   # Default job timeout (seconds)
    job_retry=3,                       # Default retry count
    job_retry_after=60,                # Retry delay (seconds)

    # === Cleanup Settings ===
    keep_job_days=7,                   # Days to keep job history (None = forever)
)
```

**All Fields**:

| Field | Type | Range | Default | Description |
|-------|------|-------|---------|-------------|
| `redis_url` | `str` | - | `"redis://localhost:6379/0"` | Redis connection URL |
| `db_url` | `str` | - | `"sqlite://./rearq.db"` | Database URL (Tortoise ORM) |
| `max_jobs` | `int` | 1-100 | `10` | Max concurrent jobs per worker |
| `job_timeout` | `int` | 30-3600 | `300` | Default job timeout (seconds) |
| `job_retry` | `int` | 0-10 | `3` | Default retry count for failed jobs |
| `job_retry_after` | `int` | ≥1 | `60` | Delay before retrying (seconds) |
| `keep_job_days` | `int` | ≥1 or None | `7` | Days to keep job history |

---

## Basic Configuration

### Development Configuration

**Optimized for**: Local development, debugging, fast iteration

```python
# config.py
from django_cfg import DjangoConfig
from django_cfg.models.tasks import TaskConfig, RearqConfig

class DevConfig(DjangoConfig):
    debug = True

    tasks = TaskConfig(
        enabled=True,
        rearq=RearqConfig(
            # Local Redis
            redis_url="redis://localhost:6379/0",

            # Local SQLite (fast, no setup needed)
            db_url="sqlite://./rearq.db",

            # Lower resource usage
            max_jobs=5,              # Fewer concurrent jobs
            job_timeout=300,         # 5 minutes
            job_retry=3,             # Standard retry
            job_retry_after=60,      # 1 minute retry delay

            # Keep less history
            keep_job_days=3,         # Only 3 days of history
        )
    )

config = DevConfig()
```

**Benefits**:
- Fast startup with SQLite
- Lower memory footprint
- Easier to debug
- No external database required

### Staging Configuration

**Optimized for**: Pre-production testing, QA

```python
# config.py
class StagingConfig(DjangoConfig):
    debug = False

    tasks = TaskConfig(
        enabled=True,
        rearq=RearqConfig(
            # Staging Redis (may be shared)
            redis_url="redis://staging-redis:6379/1",

            # Staging PostgreSQL
            db_url="postgresql://rearq_user:password@staging-db:5432/rearq",

            # Production-like settings
            max_jobs=10,
            job_timeout=600,         # 10 minutes
            job_retry=5,             # More retries
            job_retry_after=120,     # 2 minute retry delay

            # Keep more history for debugging
            keep_job_days=14,
        )
    )

config = StagingConfig()
```

### Production Configuration

**Optimized for**: High performance, reliability, scalability

```python
# config.py
import os

class ProductionConfig(DjangoConfig):
    debug = False

    tasks = TaskConfig(
        enabled=True,
        rearq=RearqConfig(
            # Production Redis with password
            redis_url=os.getenv(
                "REDIS_URL",
                "redis://:strong-password@prod-redis:6379/0"
            ),

            # Production PostgreSQL with connection pool
            db_url=os.getenv(
                "REARQ_DB_URL",
                "postgresql://rearq_user:password@prod-db:5432/rearq"
            ),

            # High performance settings
            max_jobs=20,             # More concurrent jobs
            job_timeout=600,         # 10 minutes
            job_retry=5,             # More retries
            job_retry_after=120,     # 2 minute retry delay

            # Keep longer history
            keep_job_days=30,        # 30 days
        )
    )

config = ProductionConfig()
```

---

## Environment-Specific Configuration

### Using Environment Variables

**Recommended approach** for production deployments:

```python
# config.py
import os
from django_cfg import DjangoConfig
from django_cfg.models.tasks import TaskConfig, RearqConfig

class Config(DjangoConfig):
    # Detect environment
    debug = os.getenv("DEBUG", "False").lower() == "true"

    tasks = TaskConfig(
        enabled=os.getenv("TASKS_ENABLED", "True").lower() == "true",
        rearq=RearqConfig(
            redis_url=os.getenv(
                "REDIS_URL",
                "redis://localhost:6379/0"
            ),
            db_url=os.getenv(
                "REARQ_DB_URL",
                "sqlite://./rearq.db" if debug else "postgresql://localhost/rearq"
            ),
            max_jobs=int(os.getenv("REARQ_MAX_JOBS", "10")),
            job_timeout=int(os.getenv("REARQ_JOB_TIMEOUT", "300")),
            job_retry=int(os.getenv("REARQ_JOB_RETRY", "3")),
            job_retry_after=int(os.getenv("REARQ_JOB_RETRY_AFTER", "60")),
            keep_job_days=int(os.getenv("REARQ_KEEP_JOB_DAYS", "7")),
        )
    )

config = Config()
```

**.env file** (development):

```bash
# .env
DEBUG=True
TASKS_ENABLED=True
REDIS_URL=redis://localhost:6379/0
REARQ_DB_URL=sqlite://./rearq.db
REARQ_MAX_JOBS=5
REARQ_JOB_TIMEOUT=300
REARQ_JOB_RETRY=3
REARQ_JOB_RETRY_AFTER=60
REARQ_KEEP_JOB_DAYS=3
```

**.env file** (production):

```bash
# .env.production
DEBUG=False
TASKS_ENABLED=True
REDIS_URL=redis://:StrongPassword123@redis.internal:6379/0
REARQ_DB_URL=postgresql://rearq_user:SecurePass@db.internal:5432/rearq
REARQ_MAX_JOBS=20
REARQ_JOB_TIMEOUT=600
REARQ_JOB_RETRY=5
REARQ_JOB_RETRY_AFTER=120
REARQ_KEEP_JOB_DAYS=30
```

### Smart Defaults Based on Environment

ReArq automatically adapts to your environment:

```python
from django_cfg.models.tasks import get_default_task_config

# Automatically detects debug mode from config
config = get_default_task_config(debug=True)   # Development defaults
config = get_default_task_config(debug=False)  # Production defaults
```

**Development defaults**:
- `max_jobs`: 5
- `db_url`: `sqlite://./rearq.db`
- `job_timeout`: 300 seconds

**Production defaults**:
- `max_jobs`: 20
- `db_url`: `postgresql://localhost/rearq`
- `job_timeout`: 600 seconds

---

## Advanced Configuration

### Complete Configuration with All Options

```python
from django_cfg import DjangoConfig
from django_cfg.models.tasks import TaskConfig, RearqConfig

class AdvancedConfig(DjangoConfig):
    project_name = "Advanced Project"

    tasks = TaskConfig(
        # === Core ===
        enabled=True,
        backend=TaskBackend.REARQ,

        # === Auto-Discovery ===
        auto_discover_tasks=True,
        task_modules=["tasks", "background", "jobs"],  # Multiple modules

        # === Environment Overrides ===
        dev_processes=2,
        prod_processes=4,

        # === ReArq Configuration ===
        rearq=RearqConfig(
            # === Connection ===
            redis_url="redis://:password@redis-master:6379/0",
            db_url="postgresql://user:pass@db:5432/rearq?sslmode=require",

            # === Worker Performance ===
            max_jobs=25,                 # High concurrency
            job_timeout=900,             # 15 minutes max
            job_retry=5,                 # Retry up to 5 times
            job_retry_after=180,         # 3 minute retry delay

            # === Data Retention ===
            keep_job_days=60,            # Keep 2 months of history
        )
    )

config = AdvancedConfig()
```

### Redis URL Formats

**Standard Redis**:
```python
redis_url="redis://localhost:6379/0"
redis_url="redis://:password@localhost:6379/0"
redis_url="rediss://localhost:6380/0"  # SSL/TLS
```

**Redis with authentication**:
```python
redis_url="redis://:MyPassword123@redis.internal:6379/0"
```

**Redis Sentinel** (High Availability):
```python
# Note: ReArq supports Redis Sentinel through connection string
redis_url="redis+sentinel://sentinel1:26379,sentinel2:26379,sentinel3:26379/mymaster/0"
```

**Redis Cluster**:
```python
# Note: Check ReArq documentation for cluster support
redis_url="redis://node1:6379,node2:6379,node3:6379/0"
```

### Database URL Formats

**SQLite** (Development):
```python
db_url="sqlite://./rearq.db"              # Relative path
db_url="sqlite:///tmp/rearq.db"           # Absolute path
db_url="sqlite:///:memory:"               # In-memory (testing)
```

**PostgreSQL** (Production):
```python
db_url="postgresql://user:pass@localhost/rearq"
db_url="postgresql://user:pass@localhost:5432/rearq"
db_url="postgresql://user:pass@localhost/rearq?sslmode=require"
db_url="postgres://user:pass@localhost/rearq"  # Also valid
```

**MySQL**:
```python
db_url="mysql://user:pass@localhost/rearq"
db_url="mysql://user:pass@localhost:3306/rearq?charset=utf8mb4"
```

---

## Worker Configuration

### Max Jobs (Concurrency)

Controls how many jobs can run simultaneously per worker:

```python
rearq = RearqConfig(
    max_jobs=10,  # 10 concurrent jobs per worker
)
```

**Guidelines**:

| Environment | Recommended | Reasoning |
|-------------|-------------|-----------|
| Development | 5-10 | Lower resource usage, easier debugging |
| Staging | 10-15 | Test production load |
| Production (small) | 10-20 | Balance between throughput and stability |
| Production (large) | 20-50 | High throughput, requires monitoring |

**Calculation**:
```
Total Concurrent Jobs = max_jobs × number_of_workers
```

Example:
- 3 workers × 20 max_jobs = 60 total concurrent jobs

### Job Timeout

Maximum time a job can run before being terminated:

```python
rearq = RearqConfig(
    job_timeout=300,  # 5 minutes (seconds)
)
```

**Common Values**:

| Task Type | Timeout | Example |
|-----------|---------|---------|
| Quick API calls | 30-60s | Send email, webhook |
| Data processing | 300-600s | Process CSV, generate report |
| Long operations | 900-1800s | Video encoding, ML training |
| Background sync | 1800-3600s | Full database sync |

**Per-Task Override**:
```python
from django_cfg.apps.tasks import task

@task(job_timeout=60)  # Override default, 1 minute max
async def quick_task():
    pass

@task(job_timeout=1800)  # 30 minutes for long task
async def long_task():
    pass
```

### Job Retry Settings

Configure automatic retry behavior:

```python
rearq = RearqConfig(
    job_retry=3,           # Retry up to 3 times
    job_retry_after=60,    # Wait 60 seconds between retries
)
```

**Retry Strategies**:

**Conservative** (critical tasks):
```python
job_retry=5              # More attempts
job_retry_after=300      # Longer delay (5 minutes)
```

**Aggressive** (quick recovery):
```python
job_retry=3              # Standard attempts
job_retry_after=30       # Short delay (30 seconds)
```

**Exponential Backoff** (per-task):
```python
@task(job_retry=5)
async def smart_retry_task():
    # Implements exponential backoff internally
    # Retry delays: 1m, 2m, 4m, 8m, 16m
    pass
```

**Disable Retries**:
```python
job_retry=0  # No automatic retries
```

### Multiple Workers

**Systemd** approach:
```bash
# Start multiple workers on different queues
# Note: Requires main.py that imports Django and ReArq client
rearq main:rearq worker --queue default &
rearq main:rearq worker --queue high &
rearq main:rearq worker --queue low &
```

**Docker Compose** approach:
```yaml
services:
  worker-default:
    command: rearq main:rearq worker --queue default
    deploy:
      replicas: 3  # 3 workers for default queue

  worker-high:
    command: rearq main:rearq worker --queue high
    deploy:
      replicas: 2  # 2 workers for high priority
```

**Create main.py** (required for ReArq CLI):
```python
# main.py - Entry point for ReArq CLI
import django
from django.conf import settings

# Configure Django
django.setup()

# Import and expose ReArq client
from django_cfg.apps.tasks import get_rearq_client

# Create rearq instance for CLI
rearq = get_rearq_client()
```

---

## Queue Configuration

### Smart Queue Detection

ReArq automatically detects required queues based on enabled modules:

```python
from django_cfg.models.tasks import get_smart_queues

# Automatically includes queues for enabled modules
queues = get_smart_queues(debug=False)
# Returns: ["critical", "high", "default", "low", "background"]

# In debug mode (simplified)
queues = get_smart_queues(debug=True)
# Returns: ["default"]
```

### Module-Specific Queues

Different django-cfg modules add their own queues:

| Module | Queue Name | Purpose |
|--------|-----------|---------|
| Base | `default` | General tasks |
| Base | `high`, `low` | Priority levels |
| Knowbase | `knowbase` | Document processing, embeddings |
| Payments | `payments` | Payment processing |
| Agents | `agents` | AI agent tasks |

**Auto-detection in action**:
```python
from django_cfg import DjangoConfig

class Config(DjangoConfig):
    # Enable knowbase module
    knowbase = KnowbaseConfig(enabled=True)

    # Tasks auto-detect and add "knowbase" queue
    tasks = TaskConfig(enabled=True)

# Result: queues = ["default", "high", "low", "knowbase"]
```

### Custom Queue Configuration

**Define custom queues**:
```python
# myapp/tasks.py
from django_cfg.apps.tasks import task

@task(queue="emails")
async def send_email(to: str, subject: str):
    pass

@task(queue="reports")
async def generate_report(report_id: int):
    pass

@task(queue="critical")
async def urgent_task():
    pass
```

**Run workers for specific queues** (using native ReArq CLI):
```bash
# Worker for emails only
rearq main:rearq worker --queue emails

# Worker for multiple queues
rearq main:rearq worker --queue default --queue high --queue emails

# Worker for all queues
rearq main:rearq worker --queue default --queue high --queue low --queue emails --queue reports
```

### Queue Priority Strategy

**Recommended setup**:

```
critical (2 workers)    → Payment processing, security alerts
high (3 workers)        → User-facing tasks, notifications
default (5 workers)     → General background tasks
low (2 workers)         → Data cleanup, reporting
background (1 worker)   → Scheduled maintenance
```

---

## Redis Configuration

### Basic Redis Setup

**Standard connection**:
```python
rearq = RearqConfig(
    redis_url="redis://localhost:6379/0"
)
```

**With authentication**:
```python
rearq = RearqConfig(
    redis_url="redis://:MySecurePassword@localhost:6379/0"
)
```

**SSL/TLS connection**:
```python
rearq = RearqConfig(
    redis_url="rediss://localhost:6380/0"  # Note: rediss:// (double 's')
)
```

### Redis Database Selection

**Recommendation**: Use dedicated database for ReArq

```python
# Cache uses DB 0
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
    }
}

# ReArq uses DB 1 (separate namespace)
rearq = RearqConfig(
    redis_url="redis://localhost:6379/1"  # Different DB
)
```

### Redis Sentinel (High Availability)

For production systems requiring Redis HA:

```python
# Sentinel configuration
rearq = RearqConfig(
    redis_url="redis+sentinel://sentinel1:26379,sentinel2:26379,sentinel3:26379/mymaster/0"
)
```

**Sentinel setup** (redis.conf):
```conf
# /etc/redis/sentinel.conf
port 26379
sentinel monitor mymaster 127.0.0.1 6379 2
sentinel auth-pass mymaster YourRedisPassword
sentinel down-after-milliseconds mymaster 5000
sentinel parallel-syncs mymaster 1
sentinel failover-timeout mymaster 10000
```

### Redis Connection Pooling

**Default connection pooling** (handled by ReArq):
```python
# ReArq manages connection pool automatically
rearq = RearqConfig(
    redis_url="redis://localhost:6379/0"
    # Connection pool created automatically
)
```

**Custom pool settings** (via URL parameters):
```python
rearq = RearqConfig(
    redis_url="redis://localhost:6379/0?max_connections=50&socket_timeout=5"
)
```

### Redis Security

**Production security checklist**:

```conf
# /etc/redis/redis.conf

# 1. Bind to specific interface
bind 127.0.0.1

# 2. Require password
requirepass YourVeryStrongPasswordHere

# 3. Enable protected mode
protected-mode yes

# 4. Disable dangerous commands
rename-command FLUSHDB ""
rename-command FLUSHALL ""
rename-command CONFIG ""

# 5. Use TLS/SSL (optional but recommended)
tls-port 6380
tls-cert-file /path/to/redis.crt
tls-key-file /path/to/redis.key
tls-ca-cert-file /path/to/ca.crt
```

**Corresponding ReArq config**:
```python
rearq = RearqConfig(
    redis_url="rediss://:YourVeryStrongPasswordHere@localhost:6380/0"
)
```

---

## Database Configuration

### SQLite (Development)

**Best for**: Development, testing, single-server deployments

```python
rearq = RearqConfig(
    db_url="sqlite://./rearq.db"  # File in current directory
)
```

**Advantages**:
- Zero setup required
- Fast for development
- Easy to delete/reset
- No external dependencies

**Limitations**:
- Not recommended for production
- No concurrent write support
- Limited scalability

### PostgreSQL (Production)

**Best for**: Production, high availability, scalability

```python
rearq = RearqConfig(
    db_url="postgresql://rearq_user:password@localhost:5432/rearq"
)
```

**Create database**:
```sql
-- Create user
CREATE USER rearq_user WITH PASSWORD 'SecurePassword123';

-- Create database
CREATE DATABASE rearq
    OWNER rearq_user
    ENCODING 'UTF8'
    LC_COLLATE 'en_US.UTF-8'
    LC_CTYPE 'en_US.UTF-8';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE rearq TO rearq_user;
```

**With SSL**:
```python
rearq = RearqConfig(
    db_url="postgresql://rearq_user:password@localhost:5432/rearq?sslmode=require"
)
```

**Connection pooling** (pgbouncer):
```python
# Connect through pgbouncer (port 6432)
rearq = RearqConfig(
    db_url="postgresql://rearq_user:password@localhost:6432/rearq"
)
```

### MySQL

**Alternative** to PostgreSQL:

```python
rearq = RearqConfig(
    db_url="mysql://rearq_user:password@localhost:3306/rearq?charset=utf8mb4"
)
```

**Create database**:
```sql
CREATE DATABASE rearq CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'rearq_user'@'localhost' IDENTIFIED BY 'SecurePassword123';
GRANT ALL PRIVILEGES ON rearq.* TO 'rearq_user'@'localhost';
FLUSH PRIVILEGES;
```

### Database Migrations

**Initialize database** (first time):
```bash
# ReArq automatically creates tables on first run
# Start a worker using native ReArq CLI (requires main.py)
rearq main:rearq worker --queue default

# This will automatically create the necessary tables:
# - rearq_job
# - rearq_job_result
# - rearq_scheduled_job
```

**Database tables created**:
- `rearq_job` - Job metadata
- `rearq_job_result` - Job results
- `rearq_scheduled_job` - Scheduled/cron jobs

### Cleanup Configuration

**Automatic cleanup** of old jobs:

```python
rearq = RearqConfig(
    keep_job_days=7  # Delete jobs older than 7 days
)
```

**Keep forever**:
```python
rearq = RearqConfig(
    keep_job_days=None  # Never delete
)
```

**Manual cleanup**:
```bash
# ReArq manages cleanup via the worker with timer support
# Start a worker with timer to handle cleanup tasks
rearq main:rearq worker --with-timer

# This will automatically clean up jobs older than keep_job_days
# based on your RearqConfig settings
```

---

## Configuration Validation

### Automatic Validation

ReArq configuration is validated automatically using Pydantic:

```python
from django_cfg.models.tasks import RearqConfig
from pydantic import ValidationError

try:
    config = RearqConfig(
        redis_url="invalid://url",  # Invalid scheme
        max_jobs=200,               # Out of range (max 100)
        job_timeout=10,             # Too low (min 30)
    )
except ValidationError as e:
    print(e)
    # ValidationError: 3 validation errors
```

### Validation Rules

**Redis URL**:
```python
@field_validator("redis_url")
def validate_redis_url(cls, v: str) -> str:
    if not v.startswith(("redis://", "rediss://")):
        raise ValueError("Redis URL must start with redis:// or rediss://")
    return v
```

**Database URL**:
```python
@field_validator("db_url")
def validate_db_url(cls, v: str) -> str:
    valid_schemes = ("sqlite://", "postgres://", "postgresql://", "mysql://")
    if not v.startswith(valid_schemes):
        raise ValueError(f"Database URL must start with one of: {valid_schemes}")
    return v
```

**Field Ranges**:

| Field | Minimum | Maximum | Error |
|-------|---------|---------|-------|
| `max_jobs` | 1 | 100 | "max_jobs must be between 1 and 100" |
| `job_timeout` | 30 | 3600 | "job_timeout must be between 30 and 3600" |
| `job_retry` | 0 | 10 | "job_retry must be between 0 and 10" |
| `job_retry_after` | 1 | ∞ | "job_retry_after must be >= 1" |
| `keep_job_days` | 1 | ∞ or None | "keep_job_days must be >= 1" |

### Configuration Check

**Check configuration** before starting workers:

```python
from django_cfg.models.tasks import validate_task_config, get_default_task_config

config = get_default_task_config(debug=False)

if validate_task_config(config, redis_url="redis://localhost:6379/0"):
    print("✅ Configuration is valid")
else:
    print("❌ Configuration is invalid")
```

**Management command**:
```bash
# Check task configuration
python manage.py check_tasks

# Output:
# ✅ Task system configuration is valid
# ✅ Redis connection is working
# ✅ Database is accessible
# Discovered task modules: ['myapp.tasks', 'otherapp.tasks']
```

---

## Best Practices

### 1. Environment Separation

**DO**: Use different Redis databases/instances per environment

```python
# Development
redis_url="redis://localhost:6379/0"

# Staging
redis_url="redis://staging-redis:6379/1"

# Production
redis_url="redis://prod-redis:6379/0"
```

**DON'T**: Share Redis instance between environments
```python
# BAD - All environments use same Redis
redis_url="redis://shared-redis:6379/0"
```

### 2. Use Environment Variables

**DO**: Externalize configuration

```python
import os

rearq = RearqConfig(
    redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
    db_url=os.getenv("REARQ_DB_URL", "sqlite://./rearq.db"),
)
```

**DON'T**: Hardcode credentials
```python
# BAD - Credentials in code
rearq = RearqConfig(
    redis_url="redis://:MyPassword123@redis:6379/0",
    db_url="postgresql://user:password@db:5432/rearq",
)
```

### 3. Resource Planning

**Calculate resources** before deployment:

```
Memory per worker ≈ 50-100 MB base + (max_jobs × 10 MB per job)

Example:
- Worker: 50 MB base
- Max jobs: 20
- Per job: 10 MB
- Total: 50 + (20 × 10) = 250 MB per worker

For 4 workers: 4 × 250 MB = 1 GB total
```

**CPU allocation**:
```
Recommended: 1 worker per CPU core
Example: 4 CPU cores = 4 workers max
```

### 4. Monitoring Setup

**Always enable** monitoring in production:

```python
# Production config
class ProductionConfig(DjangoConfig):
    tasks = TaskConfig(
        enabled=True,
        rearq=RearqConfig(
            redis_url=os.getenv("REDIS_URL"),
            db_url=os.getenv("REARQ_DB_URL"),

            # Production settings
            max_jobs=20,
            job_timeout=600,
            keep_job_days=30,  # Keep history for analysis
        )
    )
```

**Set up monitoring**:
- Job success/failure rates
- Queue depths
- Worker health
- Task execution times

### 5. Graceful Degradation

**Handle task failures** gracefully:

```python
from django_cfg.apps.tasks import task

@task(job_retry=3, job_retry_after=60)
async def resilient_task(user_id: int):
    """Task that fails gracefully."""
    try:
        result = await external_api_call(user_id)
        return {"success": True, "result": result}
    except TemporaryError:
        # Will retry automatically
        raise
    except PermanentError as e:
        # Log and return failure (don't retry)
        logger.error(f"Permanent error for user {user_id}: {e}")
        return {"success": False, "error": str(e)}
```

### 6. Testing Configuration

**Separate test config**:

```python
# Test config
class TestConfig(DjangoConfig):
    tasks = TaskConfig(
        enabled=True,
        rearq=RearqConfig(
            redis_url="redis://localhost:6379/15",  # Different DB
            db_url="sqlite:///:memory:",             # In-memory
            max_jobs=1,                              # Single job
            job_timeout=30,                          # Short timeout
            keep_job_days=1,                         # Minimal history
        )
    )
```

### 7. Secrets Management

**DO**: Use secret managers

```python
# AWS Secrets Manager
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

secrets = get_secret('prod/rearq')

rearq = RearqConfig(
    redis_url=secrets['redis_url'],
    db_url=secrets['db_url'],
)
```

**DON'T**: Commit secrets to git
```python
# BAD - Secret in code/config file
redis_url="redis://:SuperSecretPassword@redis:6379/0"
```

### 8. Configuration Versioning

**Track configuration changes**:

```python
# config.py
class Config(DjangoConfig):
    """
    ReArq Configuration v2.0

    Changes:
    - 2025-10-30: Increased max_jobs from 10 to 20
    - 2025-10-29: Changed retry delay from 60s to 120s
    - 2025-10-28: Migrated from SQLite to PostgreSQL
    """
    tasks = TaskConfig(...)
```

### 9. Documentation

**Document your configuration**:

```python
# config.py
class ProductionConfig(DjangoConfig):
    tasks = TaskConfig(
        enabled=True,
        rearq=RearqConfig(
            # Redis master with password authentication
            # Failover handled by Redis Sentinel (3 nodes)
            redis_url=os.getenv("REDIS_URL"),

            # PostgreSQL with connection pooling via pgbouncer
            # Daily backups at 2 AM UTC
            db_url=os.getenv("REARQ_DB_URL"),

            # Tuned for 4-core server, 8GB RAM
            # Allows 20 concurrent jobs per worker
            max_jobs=20,

            # 10 minute timeout for ML model inference tasks
            job_timeout=600,
        )
    )
```

### 10. Health Checks

**Implement health checks**:

```python
from django.http import JsonResponse
from django_cfg.apps.tasks import get_rearq_client

async def tasks_health(request):
    """Health check endpoint for load balancers."""
    try:
        client = get_rearq_client()

        # Check Redis
        await client.redis.ping()

        # Check workers
        workers_info = await client.redis.hgetall("rearq:workers")

        return JsonResponse({
            "status": "healthy",
            "redis": "connected",
            "workers": len(workers_info),
        })
    except Exception as e:
        return JsonResponse({
            "status": "unhealthy",
            "error": str(e)
        }, status=503)
```

---

## Common Mistakes

### ❌ Wrong Database for Environment

```python
# DON'T: SQLite in production
rearq = RearqConfig(
    db_url="sqlite://./rearq.db"  # BAD for production!
)

# DO: PostgreSQL in production
rearq = RearqConfig(
    db_url="postgresql://user:pass@db:5432/rearq"
)
```

### ❌ Same Redis DB as Cache

```python
# DON'T: Share Redis DB
CACHES = {'default': {'LOCATION': 'redis://localhost:6379/0'}}
rearq = RearqConfig(redis_url="redis://localhost:6379/0")  # Conflict!

# DO: Separate Redis DBs
CACHES = {'default': {'LOCATION': 'redis://localhost:6379/0'}}
rearq = RearqConfig(redis_url="redis://localhost:6379/1")  # Separate
```

### ❌ Too Many Concurrent Jobs

```python
# DON'T: Overload system
rearq = RearqConfig(
    max_jobs=100  # Too many for most systems
)

# DO: Start conservative
rearq = RearqConfig(
    max_jobs=10   # Scale up as needed
)
```

### ❌ Timeout Too Short

```python
# DON'T: Timeout too short for task
rearq = RearqConfig(
    job_timeout=30  # ML task needs 10 minutes!
)

@task()  # Uses default 30s timeout - will fail!
async def ml_inference():
    result = await run_ml_model()  # Takes 5 minutes
    return result

# DO: Set appropriate timeout
rearq = RearqConfig(
    job_timeout=600  # 10 minutes default
)

@task(job_timeout=900)  # Or per-task override (15 min)
async def ml_inference():
    result = await run_ml_model()
    return result
```

### ❌ No Retry for Network Tasks

```python
# DON'T: No retry for external API
rearq = RearqConfig(
    job_retry=0  # No retries!
)

@task()
async def call_external_api():
    # Network can fail - should retry
    pass

# DO: Enable retries for network tasks
rearq = RearqConfig(
    job_retry=3,
    job_retry_after=60
)
```

---

## Summary

### Quick Reference

**Minimal Config**:
```python
tasks = TaskConfig(enabled=True)
```

**Production Config**:
```python
tasks = TaskConfig(
    enabled=True,
    rearq=RearqConfig(
        redis_url=os.getenv("REDIS_URL"),
        db_url=os.getenv("REARQ_DB_URL"),
        max_jobs=20,
        job_timeout=600,
        job_retry=5,
        keep_job_days=30,
    )
)
```

### Django Settings Generated

When you configure ReArq, the following Django settings are automatically generated:

```python
# Generated by to_django_settings()
REARQ_REDIS_URL = "redis://localhost:6379/0"
REARQ_DB_URL = "postgresql://user:pass@localhost/rearq"
REARQ_MAX_JOBS = 20
REARQ_JOB_TIMEOUT = 600
REARQ_JOB_RETRY = 5
REARQ_JOB_RETRY_AFTER = 120
REARQ_KEEP_JOB_DAYS = 30
```

### Related Documentation

- **API Reference**: See `03_API_REFERENCE.md` for task decorators and functions
- **Usage Examples**: See `04_USAGE_EXAMPLES.md` for practical examples
- **Deployment**: See `05_DEPLOYMENT.md` for production deployment guide
- **Architecture**: See `02_ARCHITECTURE.md` for system design

---

## See Also

### Configuration Guides
- **[Configuration Fundamentals](/fundamentals/configuration)** - Core configuration patterns
- **[Environment Variables](/fundamentals/configuration/environment)** - Managing secrets
- **[Production Configuration](/guides/production-config)** - Production deployment settings

### Related Modules
- **[Database Configuration](/fundamentals/configuration/database)** - Database setup

### Deployment
- **[Docker Production](/guides/docker/production)** - Docker deployment with ReArq
- **[Deployment Overview](/deployment/overview)** - All deployment options

### Built-in Apps
- **[AI Knowledge Base](/features/built-in-apps/ai-knowledge/knowbase-configuration)** - Knowbase task configuration

---

**End of Configuration Guide**
