"""
Cache configuration models for django_cfg.

Following CRITICAL_REQUIREMENTS.md:
- No raw Dict/Any usage - everything through Pydantic models
- Proper type annotations for all fields
- No mutable default arguments
- Environment-aware backend selection
"""

from typing import Dict, Optional, Any, Literal, Union
from pydantic import BaseModel, Field, field_validator, model_validator
from urllib.parse import urlparse

from django_cfg.core.exceptions import CacheError, ValidationError


class CacheConfig(BaseModel):
    """
    Type-safe cache backend configuration.
    
    Automatically selects appropriate backend based on environment:
    - Production: Redis (if redis_url provided)
    - Development: Local memory cache
    - Testing: Dummy cache with short timeouts
    """
    
    model_config = {
        "str_strip_whitespace": True,
        "validate_assignment": True,
        "extra": "forbid",
    }
    
    # Redis configuration
    redis_url: Optional[str] = Field(
        default=None,
        description="Redis connection URL (redis://host:port/db)",
    )
    
    # Timeout settings
    timeout: int = Field(
        default=300,
        description="Default cache timeout in seconds",
        ge=0,  # Allow 0 for no timeout
        le=86400 * 7,  # Max 7 days
    )
    
    # Connection settings
    max_connections: int = Field(
        default=50,
        description="Maximum Redis connections in pool",
        ge=1,
        le=1000,
    )
    
    # Cache key settings
    key_prefix: str = Field(
        default="",
        description="Prefix for all cache keys",
        max_length=100,
    )
    
    version: int = Field(
        default=1,
        description="Cache key version for invalidation",
        ge=1,
    )
    
    # Redis-specific settings
    connection_pool_kwargs: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional Redis connection pool parameters",
    )
    
    # Compression settings
    compress: bool = Field(
        default=False,
        description="Enable cache value compression",
    )
    
    # Serialization settings
    serializer: Literal["json", "pickle", "msgpack"] = Field(
        default="pickle",
        description="Cache value serializer",
    )
    
    # Backend override (for testing)
    backend_override: Optional[str] = Field(
        default=None,
        description="Override automatic backend selection",
        exclude=True,
    )
    
    @field_validator('redis_url')
    @classmethod
    def validate_redis_url(cls, v: Optional[str]) -> Optional[str]:
        """Validate Redis URL format."""
        if v is None:
            return v
        
        if not v.startswith(('redis://', 'rediss://')):
            raise ValueError(
                "Redis URL must start with 'redis://' or 'rediss://' "
                f"(got: '{v}')"
            )
        
        try:
            parsed = urlparse(v)
            
            # Validate components
            if not parsed.hostname:
                raise ValueError("Redis URL must include hostname")
            
            if parsed.port and (parsed.port < 1 or parsed.port > 65535):
                raise ValueError(f"Invalid Redis port: {parsed.port}")
            
            # Validate database number if present
            if parsed.path and parsed.path != '/':
                db_path = parsed.path.lstrip('/')
                if db_path:
                    try:
                        db_num = int(db_path)
                        if db_num < 0 or db_num > 15:  # Redis default max 16 databases
                            raise ValueError(f"Redis database number must be 0-15 (got: {db_num})")
                    except ValueError as e:
                        if "invalid literal" in str(e):
                            raise ValueError(f"Invalid Redis database path: {parsed.path}")
                        raise
            
            return v
            
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Invalid Redis URL format: {e}") from e
    
    @field_validator('key_prefix')
    @classmethod
    def validate_key_prefix(cls, v: str) -> str:
        """Validate cache key prefix."""
        if v and not v.replace('_', '').replace('-', '').replace(':', '').isalnum():
            raise ValueError(
                "Cache key prefix must contain only alphanumeric characters, "
                "underscores, hyphens, and colons"
            )
        
        return v
    
    @field_validator('serializer')
    @classmethod
    def validate_serializer(cls, v: str) -> str:
        """Validate serializer choice."""
        valid_serializers = {"json", "pickle", "msgpack"}
        if v not in valid_serializers:
            raise ValueError(
                f"Invalid serializer '{v}'. "
                f"Valid options: {', '.join(sorted(valid_serializers))}"
            )
        
        return v
    
    @model_validator(mode='after')
    def validate_configuration_consistency(self) -> 'CacheConfig':
        """Validate cache configuration consistency."""
        # Warn about compression with JSON serializer
        if self.compress and self.serializer == "json":
            # JSON is already compact, compression might not help much
            pass  # Just a note, not an error
        
        # Validate connection pool kwargs
        if self.connection_pool_kwargs:
            invalid_keys = set(self.connection_pool_kwargs.keys()) - {
                'retry_on_timeout', 'health_check_interval', 'socket_timeout',
                'socket_connect_timeout', 'socket_keepalive', 'socket_keepalive_options',
                'encoding', 'encoding_errors', 'decode_responses'
            }
            if invalid_keys:
                raise ValueError(
                    f"Invalid connection pool parameters: {', '.join(invalid_keys)}"
                )
        
        return self
    
    def get_backend_type(self, environment: str, debug: bool) -> str:
        """
        Determine appropriate cache backend based on environment.
        
        Args:
            environment: Current environment (development, production, etc.)
            debug: Django DEBUG setting
            
        Returns:
            Django cache backend class path
        """
        # Allow manual override for testing
        if self.backend_override:
            return self.backend_override
        
        # Environment-based backend selection
        if environment == "testing":
            return "django.core.cache.backends.dummy.DummyCache"
        
        elif environment == "development" or debug:
            # Use Redis if available, otherwise memory cache
            if self.redis_url:
                return "django_redis.cache.RedisCache"
            else:
                return "django.core.cache.backends.locmem.LocMemCache"
        
        elif environment in ("production", "staging"):
            # Production should use Redis
            if self.redis_url:
                return "django_redis.cache.RedisCache"
            else:
                # Fallback to file cache for production without Redis
                return "django.core.cache.backends.filebased.FileBasedCache"
        
        else:
            # Unknown environment - use Redis if available
            if self.redis_url:
                return "django_redis.cache.RedisCache"
            else:
                return "django.core.cache.backends.locmem.LocMemCache"
    
    def to_django_config(self, environment: str, debug: bool, cache_alias: str = "default") -> Dict[str, Any]:
        """
        Convert to Django cache configuration format.
        
        Args:
            environment: Current environment
            debug: Django DEBUG setting
            cache_alias: Cache alias name for unique location generation
            
        Returns:
            Django-compatible cache configuration
            
        Raises:
            CacheError: If configuration cannot be converted
        """
        try:
            backend = self.get_backend_type(environment, debug)
            
            config = {
                'BACKEND': backend,
                'TIMEOUT': self.timeout,
                'KEY_PREFIX': self.key_prefix,
                'VERSION': self.version,
            }
            
            # Backend-specific configuration
            if backend == "django_redis.cache.RedisCache":
                if not self.redis_url:
                    raise CacheError(
                        "Redis URL is required for Redis cache backend",
                        cache_alias=cache_alias,
                        backend_type="redis"
                    )
                
                config['LOCATION'] = self.redis_url
                config['OPTIONS'] = {
                    'CONNECTION_POOL_KWARGS': {
                        'max_connections': self.max_connections,
                        **self.connection_pool_kwargs,
                    }
                }
                
                # Add compression if enabled
                if self.compress:
                    config['OPTIONS']['COMPRESSOR'] = 'django_redis.compressors.zlib.ZlibCompressor'
                
                # Add serializer configuration
                if self.serializer == "json":
                    config['OPTIONS']['SERIALIZER'] = 'django_redis.serializers.json.JSONSerializer'
                elif self.serializer == "msgpack":
                    config['OPTIONS']['SERIALIZER'] = 'django_redis.serializers.msgpack.MSGPackSerializer'
                # pickle is default, no need to specify
            
            elif backend == "django.core.cache.backends.locmem.LocMemCache":
                # Use unique location for each cache alias to avoid conflicts
                config['LOCATION'] = f'{self.key_prefix or "django_cfg"}_{cache_alias}_{id(self)}'
                config['OPTIONS'] = {
                    'MAX_ENTRIES': min(self.max_connections * 100, 10000),  # Reasonable default
                }
            
            elif backend == "django.core.cache.backends.filebased.FileBasedCache":
                from pathlib import Path
                cache_dir = Path("tmp") / "django_cache" / f"{self.key_prefix or 'default'}_{cache_alias}"
                config['LOCATION'] = str(cache_dir)
                config['OPTIONS'] = {
                    'MAX_ENTRIES': 1000,
                }
            
            elif backend == "django.core.cache.backends.dummy.DummyCache":
                # Dummy cache for testing - no additional options needed
                config['OPTIONS'] = {}
            
            return config
            
        except Exception as e:
            raise CacheError(
                f"Failed to convert cache configuration: {e}",
                cache_alias=cache_alias,
                backend_type=backend if 'backend' in locals() else 'unknown',
                context={
                    'environment': environment,
                    'debug': debug,
                    'config': self.model_dump(exclude={'backend_override'})
                }
            ) from e
    
    def test_connection(self) -> bool:
        """
        Test cache connection (placeholder for future implementation).
        
        Returns:
            True if connection successful, False otherwise
        """
        # TODO: Implement actual connection testing
        # This would require the cache backend to be configured
        return True
    
    def get_memory_estimate_mb(self) -> float:
        """
        Estimate memory usage for this cache configuration.
        
        Returns:
            Estimated memory usage in MB
        """
        if self.redis_url:
            # Redis connection overhead
            return self.max_connections * 0.1  # ~100KB per connection
        else:
            # Local memory cache estimate
            return min(self.max_connections * 0.5, 50)  # Up to 50MB


# Export all models
__all__ = [
    "CacheConfig",
]
