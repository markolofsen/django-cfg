---
title: Cache Models
description: CacheConfig model for Redis, LocMem, and Dummy cache backends
sidebar_label: Cache Models
sidebar_position: 5
---

import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

# Cache Models

:::tip[Automatic Backend Selection]
Django-CFG automatically selects the **best cache backend** based on your environment and configuration - Redis for production, LocMem for development, DummyCache as safe fallback.
:::

Django-CFG provides `CacheConfig` model for type-safe cache configuration with automatic backend selection.

## CacheConfig

Type-safe cache backend configuration with environment-aware smart defaults.

### Complete Model

```python
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any

class CacheConfig(BaseModel):
    """Cache backend configuration"""

    redis_url: Optional[str] = Field(
        default=None,
        description="Redis connection URL"
    )
    timeout: int = Field(
        default=300,
        description="Default timeout in seconds",
        ge=0
    )
    max_connections: int = Field(
        default=50,
        description="Maximum Redis connections",
        ge=1
    )
    key_prefix: str = Field(
        default="",
        description="Cache key prefix"
    )
    version: int = Field(
        default=1,
        description="Cache key version",
        ge=1
    )

    # Advanced Redis settings
    connection_pool_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Redis connection pool parameters"
    )

    @field_validator('redis_url')
    @classmethod
    def validate_redis_url(cls, v):
        """Validate Redis URL format"""
        if v and not v.startswith(('redis://', 'rediss://')):
            raise ValueError("Redis URL must start with redis:// or rediss://")
        return v

    def to_django_config(self, environment: str, debug: bool) -> Dict[str, Any]:
        """Convert to Django cache configuration"""
        from django_cfg.utils.smart_defaults import SmartDefaults

        backend = SmartDefaults.get_cache_backend(
            debug=debug,
            redis_url=self.redis_url,
            environment=environment
        )

        config = {
            'BACKEND': backend,
            'TIMEOUT': self.timeout,
            'KEY_PREFIX': self.key_prefix,
            'VERSION': self.version,
        }

        if backend == 'django_redis.cache.RedisCache' and self.redis_url:
            config['LOCATION'] = self.redis_url
            config['OPTIONS'] = {
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': self.max_connections,
                    **self.connection_pool_kwargs
                }
            }
        elif backend == 'django.core.cache.backends.locmem.LocMemCache':
            config['LOCATION'] = f'{self.key_prefix}-{id(self)}'

        return config
```

## Smart Backend Selection

Django-CFG automatically selects the best cache backend based on environment and configuration:

| Scenario | Backend | Reason |
|----------|---------|--------|
| Production + Redis URL | **RedisCache** | Production-ready, distributed |
| Staging + Redis URL | **RedisCache** | Production-like testing |
| Development + Redis URL | **RedisCache** | Local Redis for testing |
| Development + No Redis | **LocMemCache** | Fast in-memory cache |
| Production + No Redis | **DummyCache** | No cache (safe fallback) |

## Usage Examples

<Tabs>
  <TabItem value="redis" label="Redis (Production)" default>

```python title="config.py"
from django_cfg import DjangoConfig
from django_cfg.models import CacheConfig

class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    cache_default: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/0",
        timeout=300,  # 5 minutes
        key_prefix="myapp",
        max_connections=50
    )
```

**Generated Django settings:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
        'TIMEOUT': 300,
        'KEY_PREFIX': 'myapp',
        'VERSION': 1,
        'OPTIONS': {
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50
            }
        }
    }
}
```

:::info[Redis Benefits]
Redis cache provides:
- **Distributed caching** across multiple servers
- **Persistence** options for cache data
- **High performance** with sub-millisecond latency
- **Advanced features** like pub/sub, transactions
:::

  </TabItem>
  <TabItem value="redis-ssl" label="Redis SSL">

```python title="config.py (Production SSL)"
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    cache_default: CacheConfig = CacheConfig(
        redis_url="rediss://cache.example.com:6380/0",  # SSL (note: rediss://)
        timeout=600,
        key_prefix="myapp_prod",
        max_connections=100,
        connection_pool_kwargs={
            'ssl_cert_reqs': 'required',
            'ssl_ca_certs': '/path/to/ca-cert.pem'
        }
    )
```

:::warning[Production Redis]
Always use SSL (`rediss://`) for Redis connections in production to encrypt cache data in transit.
:::

  </TabItem>
  <TabItem value="locmem" label="LocMem (Development)">

```python title="config.py (Development)"
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = True

    cache_default: CacheConfig = CacheConfig(
        # No redis_url - auto-selects LocMemCache in debug mode
        timeout=300,
        key_prefix="myapp_dev"
    )
```

**Generated Django settings:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'myapp_dev-140123456789',
        'TIMEOUT': 300,
        'KEY_PREFIX': 'myapp_dev',
        'VERSION': 1,
    }
}
```

:::note[LocMem Use Case]
LocMem cache is ideal for:
- **Development** - No Redis setup required
- **Testing** - Fast, isolated cache per process
- **Single-server** deployments with low traffic

**Not suitable for:**
- ❌ Multi-server deployments
- ❌ Persistent cache needs
- ❌ High-traffic production
:::

  </TabItem>
  <TabItem value="dummy" label="Dummy (Disabled)">

```python title="config.py (No Caching)"
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    # No cache_default - DummyCache used as safe fallback
```

**Generated Django settings:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
```

:::warning[Dummy Cache]
DummyCache **doesn't cache anything** - all cache operations are no-ops. Used as safe fallback when:
- No Redis URL provided in production
- Cache explicitly disabled for testing
- Troubleshooting cache-related issues
:::

  </TabItem>
</Tabs>

## Multiple Cache Backends

### Default + Sessions Cache

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    # Default cache for application data
    cache_default: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/0",
        timeout=300,
        key_prefix="myapp"
    )

    # Separate cache for sessions
    cache_sessions: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/1",  # Different DB
        timeout=86400,  # 24 hours
        key_prefix="sessions"
    )
```

**Generated Django settings:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/0',
        'TIMEOUT': 300,
        'KEY_PREFIX': 'myapp',
        'VERSION': 1,
        'OPTIONS': {
            'CONNECTION_POOL_KWARGS': {'max_connections': 50}
        }
    },
    'sessions': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'TIMEOUT': 86400,
        'KEY_PREFIX': 'sessions',
        'VERSION': 1,
        'OPTIONS': {
            'CONNECTION_POOL_KWARGS': {'max_connections': 50}
        }
    }
}

# Sessions backend
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'sessions'
```

## Advanced Redis Configuration

### Connection Pool Settings

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    cache_default: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/0",
        max_connections=100,
        connection_pool_kwargs={
            'socket_connect_timeout': 5,
            'socket_timeout': 5,
            'retry_on_timeout': True,
            'max_connections': 100,
            'socket_keepalive': True,
            'socket_keepalive_options': {
                1: 1,  # TCP_KEEPIDLE
                2: 1,  # TCP_KEEPINTVL
                3: 3,  # TCP_KEEPCNT
            }
        }
    )
```

### Redis Sentinel

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    cache_default: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/0",
        connection_pool_kwargs={
            'sentinels': [
                ('sentinel1.example.com', 26379),
                ('sentinel2.example.com', 26379),
                ('sentinel3.example.com', 26379),
            ],
            'service_name': 'mymaster',
            'sentinel_kwargs': {'password': 'sentinel_password'},
        }
    )
```

### Redis Cluster

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    cache_default: CacheConfig = CacheConfig(
        redis_url="redis://node1:6379/0",
        connection_pool_kwargs={
            'startup_nodes': [
                {'host': 'node1.example.com', 'port': 6379},
                {'host': 'node2.example.com', 'port': 6379},
                {'host': 'node3.example.com', 'port': 6379},
            ],
            'skip_full_coverage_check': True,
        }
    )
```

## Environment-Specific Configuration

### Using Properties

```python
import os

class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"

    @property
    def cache_default(self) -> Optional[CacheConfig]:
        if self._environment == "production":
            return CacheConfig(
                redis_url=os.getenv('REDIS_URL'),
                timeout=600,
                key_prefix="prod",
                max_connections=200
            )
        elif self._environment == "development":
            return CacheConfig(
                # No redis_url - uses LocMemCache
                timeout=60,
                key_prefix="dev"
            )
        return None  # Dummy cache
```

### Using YAML

```yaml
# config.production.yaml
cache_default:
  redis_url: "redis://prod-cache.example.com:6379/0"
  timeout: 600
  key_prefix: "prod"
  max_connections: 200

# config.development.yaml
cache_default:
  timeout: 60
  key_prefix: "dev"
  # No redis_url - auto-selects LocMemCache
```

## Cache Key Versioning

```python
class MyConfig(DjangoConfig):
    secret_key: str = "your-secret-key"
    debug: bool = False

    cache_default: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/0",
        key_prefix="myapp",
        version=2  # Increment when cache schema changes
    )
```

**Usage:**

```python
from django.core.cache import cache

# Set with version
cache.set('my_key', 'value', version=2)

# Get with version
value = cache.get('my_key', version=2)

# Different version = cache miss
value = cache.get('my_key', version=1)  # None
```

## Performance Tuning

### Timeout Settings

```python
class MyConfig(DjangoConfig):
    cache_default: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/0",
        timeout=300,  # 5 minutes default
    )
```

**Common timeouts:**

- **60s** - Frequently changing data
- **300s (5m)** - Default for most data
- **3600s (1h)** - Semi-static data
- **86400s (24h)** - Very static data

### Connection Pool Size

```python
class MyConfig(DjangoConfig):
    cache_default: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/0",
        max_connections=50,  # Adjust based on load
    )
```

**Guidelines:**

- **10-20** - Low traffic (< 1000 req/min)
- **50-100** - Medium traffic (1000-10000 req/min)
- **100-200** - High traffic (> 10000 req/min)

## Security Best Practices

### 1. Use Environment Variables

```python
import os

class MyConfig(DjangoConfig):
    cache_default: CacheConfig = CacheConfig(
        redis_url=os.getenv('REDIS_URL'),
        key_prefix=os.getenv('CACHE_PREFIX', 'myapp')
    )
```

### 2. Enable SSL/TLS

```python
class MyConfig(DjangoConfig):
    cache_default: CacheConfig = CacheConfig(
        redis_url="rediss://cache.example.com:6380/0",  # SSL
        connection_pool_kwargs={
            'ssl_cert_reqs': 'required'
        }
    )
```

### 3. Use Different Databases

```python
class MyConfig(DjangoConfig):
    cache_default: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/0"  # DB 0 for cache
    )

    cache_sessions: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/1"  # DB 1 for sessions
    )
```

## Troubleshooting

### Redis Connection Errors

**Error:**
```
ConnectionError: Error connecting to Redis
```

**Solution:**
```python
class MyConfig(DjangoConfig):
    cache_default: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/0",
        connection_pool_kwargs={
            'socket_connect_timeout': 10,
            'retry_on_timeout': True
        }
    )
```

### Cache Key Too Long

**Error:**
```
ValueError: Cache key too long (max 250 chars)
```

**Solution:**
```python
class MyConfig(DjangoConfig):
    cache_default: CacheConfig = CacheConfig(
        redis_url="redis://localhost:6379/0",
        key_prefix="short"  # Use shorter prefix
    )
```

## See Also

- [**DjangoConfig**](./django-settings) - Base configuration class
- [**Configuration Overview**](./) - Configuration system overview
