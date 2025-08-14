"""
Cache Configuration Model

Django cache settings with Pydantic 2.
"""

from typing import Dict, Any, Optional
from pydantic import Field, field_validator
from .base import BaseConfig


class CacheConfig(BaseConfig):
    """
    💾 Cache Configuration - Django cache settings
    
    Supports Redis, Memcached, and database caching with
    smart defaults and environment-aware configuration.
    """
    
    # Cache backend
    backend: str = Field(
        default="memory",
        description="Cache backend (redis/memory/database/memcached)"
    )
    
    # Redis settings
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis URL (redis://localhost:6379/0)"
    )
    
    # Default cache settings
    default_timeout: int = Field(
        default=300,
        ge=0,
        description="Default cache timeout in seconds"
    )
    
    key_prefix: str = Field(
        default="django_cache",
        description="Cache key prefix"
    )
    
    # Cache versioning
    version: int = Field(
        default=1,
        ge=1,
        description="Cache version"
    )
    
    # Memory cache settings
    max_entries: int = Field(
        default=1000,
        ge=1,
        description="Maximum entries for memory cache"
    )
    
    @field_validator('backend')
    @classmethod
    def validate_backend(cls, v: str) -> str:
        """Validate cache backend."""
        valid_backends = ['redis', 'memory', 'database', 'memcached', 'dummy']
        if v not in valid_backends:
            raise ValueError(f"Cache backend must be one of: {valid_backends}")
        return v
    
    @field_validator('redis_url')
    @classmethod
    def validate_redis_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate Redis URL if provided."""
        if v and not v.startswith('redis://'):
            raise ValueError("Redis URL must start with redis://")
        return v
    
    def to_django_settings(self) -> Dict[str, Any]:
        """Convert to Django CACHES setting."""
        if self.backend == 'redis':
            if not self.redis_url:
                raise ValueError("Redis URL is required when using Redis backend")
            
            cache_config = {
                'BACKEND': 'django.core.cache.backends.redis.RedisCache',
                'LOCATION': self.redis_url,
                'OPTIONS': {
                    'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                },
            }
        
        elif self.backend == 'memory':
            cache_config = {
                'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
                'OPTIONS': {
                    'MAX_ENTRIES': self.max_entries,
                },
            }
        
        elif self.backend == 'database':
            cache_config = {
                'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
                'LOCATION': 'cache_table',
            }
        
        elif self.backend == 'memcached':
            cache_config = {
                'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache',
                'LOCATION': '127.0.0.1:11211',
            }
        
        elif self.backend == 'dummy':
            cache_config = {
                'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
            }
        
        else:
            raise ValueError(f"Unsupported cache backend: {self.backend}")
        
        # Add common settings
        cache_config.update({
            'TIMEOUT': self.default_timeout,
            'KEY_PREFIX': self.key_prefix,
            'VERSION': self.version,
        })
        
        return {
            'CACHES': {
                'default': cache_config
            }
        }
