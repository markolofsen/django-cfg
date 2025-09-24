"""
Task processing configuration models for Django-CFG.

This module provides type-safe Pydantic models for configuring background task
processing with Dramatiq, including worker management, queue configuration,
and monitoring settings.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Literal, Dict, Any
from enum import Enum
import os
import logging
from django_cfg.models.cfg import BaseCfgAutoModule

logger = logging.getLogger(__name__)


class TaskBackend(str, Enum):
    """Supported task backends."""
    DRAMATIQ = "dramatiq"
    # Future: CELERY = "celery"


class QueuePriority(str, Enum):
    """Standard queue priorities."""
    CRITICAL = "critical"
    HIGH = "high"
    DEFAULT = "default"
    LOW = "low"
    BACKGROUND = "background"


class DramatiqConfig(BaseModel):
    """
    Dramatiq-specific configuration with production-ready defaults.
    
    This model provides comprehensive configuration for Dramatiq background
    task processing, including Redis settings, worker configuration, 
    middleware stack, and monitoring options.
    """
    
    # === Redis Configuration ===
    redis_db: int = Field(
        default=1, 
        ge=0, 
        le=15, 
        description="Redis database number for tasks (separate from cache)"
    )
    redis_key_prefix: str = Field(
        default="dramatiq", 
        description="Redis key prefix for task data"
    )
    
    # === Task Configuration ===
    max_retries: int = Field(
        default=3, 
        ge=0, 
        le=10, 
        description="Default maximum retry count for failed tasks"
    )
    default_priority: int = Field(
        default=5, 
        ge=0, 
        le=10, 
        description="Default task priority (0=highest, 10=lowest)"
    )
    max_age_seconds: int = Field(
        default=3600, 
        ge=60, 
        description="Maximum age for tasks before they expire"
    )
    time_limit_seconds: int = Field(
        default=600, 
        ge=30, 
        description="Maximum execution time per task"
    )
    
    # === Worker Configuration ===
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
        description="Number of threads per worker process"
    )
    queues: List[str] = Field(
        default=["default", "high", "low"], 
        description="Available task queues"
    )
    
    # === Middleware Stack ===
    middleware: List[str] = Field(
        default=[
            "dramatiq.middleware.AgeLimit",
            "dramatiq.middleware.TimeLimit", 
            "dramatiq.middleware.Callbacks",
            "dramatiq.middleware.Retries",
            "dramatiq.middleware.Prometheus",
            "django_dramatiq.middleware.AdminMiddleware",
            "django_dramatiq.middleware.DbConnectionsMiddleware",
        ],
        description="Middleware stack for task processing"
    )
    
    # === Monitoring & Admin ===
    prometheus_enabled: bool = Field(
        default=True, 
        description="Enable Prometheus metrics collection"
    )
    admin_enabled: bool = Field(
        default=True, 
        description="Enable Django admin interface integration"
    )
    
    # === Performance Tuning ===
    prefetch_multiplier: int = Field(
        default=2, 
        ge=1, 
        le=10, 
        description="Message prefetch multiplier for workers"
    )
    max_memory_mb: Optional[int] = Field(
        default=512, 
        ge=128, 
        description="Maximum memory usage per worker (MB)"
    )
    
    @field_validator("processes")
    @classmethod
    def validate_processes(cls, v: int) -> int:
        """Ensure reasonable process count based on CPU cores."""
        cpu_count = os.cpu_count() or 4
        max_recommended = cpu_count * 2
        
        if v > max_recommended:
            logger.warning(
                f"Process count ({v}) exceeds recommended maximum ({max_recommended}). "
                f"Consider reducing to avoid resource contention."
            )
        
        return v
    
    @field_validator("queues")
    @classmethod
    def validate_queues(cls, v: List[str]) -> List[str]:
        """Ensure queue names are valid and include default."""
        if not v:
            raise ValueError("At least one queue must be specified")
        
        # Ensure 'default' queue exists
        if "default" not in v:
            v.append("default")
        
        # Validate queue names (alphanumeric + underscore/hyphen)
        import re
        pattern = re.compile(r'^[a-zA-Z0-9_-]+$')
        
        for queue in v:
            if not pattern.match(queue):
                raise ValueError(f"Invalid queue name: {queue}. Use only alphanumeric, underscore, and hyphen.")
        
        return v
    
    @field_validator("middleware")
    @classmethod
    def validate_middleware(cls, v: List[str]) -> List[str]:
        """Ensure essential middleware is included."""
        essential_middleware = [
            "dramatiq.middleware.Retries",
            "django_dramatiq.middleware.DbConnectionsMiddleware",
        ]
        
        for middleware in essential_middleware:
            if middleware not in v:
                logger.warning(f"Adding essential middleware: {middleware}")
                v.append(middleware)
        
        return v


class WorkerConfig(BaseModel):
    """
    Worker process and resource configuration.
    
    Provides fine-grained control over worker behavior, resource limits,
    and health monitoring settings.
    """
    
    # === Process Management ===
    shutdown_timeout: int = Field(
        default=30, 
        ge=5, 
        le=300, 
        description="Graceful shutdown timeout in seconds"
    )
    heartbeat_interval: int = Field(
        default=5, 
        ge=1, 
        le=60, 
        description="Worker heartbeat interval in seconds"
    )
    
    # === Resource Limits ===
    max_memory_mb: Optional[int] = Field(
        default=512, 
        ge=128, 
        description="Maximum memory per worker process (MB)"
    )
    max_cpu_percent: Optional[float] = Field(
        default=80.0, 
        ge=10.0, 
        le=100.0, 
        description="Maximum CPU usage per worker (%)"
    )
    
    # === Health Monitoring ===
    health_check_enabled: bool = Field(
        default=True, 
        description="Enable worker health monitoring"
    )
    restart_on_memory_limit: bool = Field(
        default=True, 
        description="Restart worker if memory limit exceeded"
    )
    
    # === Logging ===
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = Field(
        default="INFO", 
        description="Worker log level"
    )
    log_format: str = Field(
        default="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        description="Log message format"
    )


class TaskConfig(BaseModel, BaseCfgAutoModule):
    """
    High-level task system configuration.
    
    Main entry point for configuring background task processing in Django-CFG.
    Provides environment-aware defaults and automatic Redis integration.
    """
    
    # === Core Settings ===
    enabled: bool = Field(
        default=True, 
        description="Enable background task processing"
    )
    backend: TaskBackend = Field(
        default=TaskBackend.DRAMATIQ, 
        description="Task processing backend"
    )
    
    def __init__(self, **data):
        """Initialize TaskConfig with BaseCfgAutoModule support."""
        super().__init__(**data)
        # Initialize _config attribute for BaseCfgAutoModule
        self._config = None
    
    # === Backend-Specific Configuration ===
    dramatiq: DramatiqConfig = Field(
        default_factory=DramatiqConfig, 
        description="Dramatiq-specific configuration"
    )
    worker: WorkerConfig = Field(
        default_factory=WorkerConfig, 
        description="Worker configuration"
    )
    
    # === Environment-Specific Overrides ===
    dev_processes: Optional[int] = Field(
        default=2, 
        description="Number of processes in development environment"
    )
    prod_processes: Optional[int] = Field(
        default=None, 
        description="Number of processes in production environment"
    )
    
    # === Auto-Configuration ===
    auto_discover_tasks: bool = Field(
        default=True, 
        description="Automatically discover tasks in Django apps"
    )
    task_modules: List[str] = Field(
        default=["tasks"], 
        description="Module names to search for tasks"
    )
    
    @field_validator("enabled")
    @classmethod
    def validate_enabled_with_environment(cls, v: bool) -> bool:
        """Validate task system can be enabled in current environment."""
        if v:
            # Check if we're in a test environment
            if os.getenv("DJANGO_SETTINGS_MODULE", "").endswith("test"):
                logger.info("Task system disabled in test environment")
                return False
            
            # Additional environment checks can be added here
            # For example, checking if Redis is available
        
        return v
    
    def get_effective_processes(self, debug: bool = False) -> int:
        """Get effective number of processes based on environment."""
        if debug and self.dev_processes is not None:
            return self.dev_processes
        elif not debug and self.prod_processes is not None:
            return self.prod_processes
        else:
            return self.dramatiq.processes
    
    def get_effective_queues(self) -> List[str]:
        """Get effective queue configuration."""
        return self.dramatiq.queues
    
    def get_redis_config(self, redis_url: str) -> Dict[str, Any]:
        """Generate Redis configuration for Dramatiq."""
        from urllib.parse import urlparse, parse_qs
        
        # Parse Redis URL
        parsed = urlparse(redis_url)
        
        # Build Redis config
        config = {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 6379,
            "db": self.dramatiq.redis_db,
            "password": parsed.password,
        }
        
        # Add SSL if specified
        if parsed.scheme == "rediss":
            config["ssl"] = True
        
        return config
    
    def get_dramatiq_settings(self, redis_url: str) -> Dict[str, Any]:
        """Generate complete Dramatiq settings for Django."""
        from urllib.parse import urlparse
        
        redis_config = self.get_redis_config(redis_url)
        parsed = urlparse(redis_url)
        
        # Build Redis URL with correct database
        redis_url_with_db = redis_url
        if parsed.path and parsed.path != "/":
            # Replace existing database in URL
            redis_url_with_db = redis_url.replace(parsed.path, f"/{self.dramatiq.redis_db}")
        else:
            # Add database to URL
            redis_url_with_db = f"{redis_url.rstrip('/')}/{self.dramatiq.redis_db}"
        
        return {
            "DRAMATIQ_BROKER": {
                "BROKER": "dramatiq.brokers.redis.RedisBroker",
                "OPTIONS": {
                    "url": redis_url_with_db,
                    **redis_config
                },
            },
            "DRAMATIQ_RESULT_BACKEND": {
                "BACKEND": "dramatiq.results.backends.redis.RedisBackend",
                "BACKEND_OPTIONS": {
                    "url": redis_url_with_db,
                    **redis_config
                },
            },
            "DRAMATIQ_MIDDLEWARE": self.dramatiq.middleware,
            "DRAMATIQ_QUEUES": self.dramatiq.queues,
        }

    def get_smart_defaults(self):
        """Get smart default configuration for this module."""
        config = self.get_config()
        debug = getattr(config, 'debug', False) if config else False
        return get_default_task_config(debug=debug)

    def get_module_config(self):
        """Get the final configuration for this module."""
        return self
    
    @classmethod
    def auto_initialize_if_needed(cls) -> Optional['TaskConfig']:
        """
        Auto-initialize TaskConfig if needed based on config flags.
        
        Returns:
            TaskConfig instance if should be initialized, None otherwise
        """
        # Get config through BaseCfgModule
        from django_cfg.modules import BaseCfgModule
        base_module = BaseCfgModule()
        config = base_module.get_config()
        
        if not config:
            return None
        
        # Check if TaskConfig already exists
        if hasattr(config, 'tasks') and config.tasks is not None:
            # Set config reference and return existing
            config.tasks.set_config(config)
            return config.tasks
        
        # Check if tasks should be enabled
        if config.should_enable_tasks():
            # Auto-initialize with smart defaults
            task_config = cls().get_smart_defaults()
            task_config.set_config(config)
            config.tasks = task_config
            
            import logging
            logger = logging.getLogger(__name__)
            logger.info("🚀 Auto-initialized TaskConfig (enabled by knowbase/agents/tasks flags)")
            
            return task_config
        
        return None


# === Utility Functions ===

def get_smart_queues(debug: bool = False) -> List[str]:
    """
    Get smart default queues based on enabled modules.
    
    Automatically detects which django-cfg modules are enabled and adds
    their corresponding queues to the default queue list.
    
    Args:
        debug: Whether running in debug mode (affects base queues)
        
    Returns:
        List of queue names appropriate for enabled modules
    """
    # Base queues
    if debug:
        base_queues = ["default"]
    else:
        base_queues = ["critical", "high", "default", "low", "background"]
    
    # Try to detect enabled modules and add their queues
    try:
        from django_cfg.modules.base import BaseCfgModule
        base_module = BaseCfgModule()
        
        # Check for knowbase module (requires "knowbase" queue)
        if base_module.is_knowbase_enabled():
            if "knowbase" not in base_queues:
                base_queues.append("knowbase")
                
        # Check for payments module (requires "payments" queue)  
        if base_module.is_payments_enabled():
            if "payments" not in base_queues:
                base_queues.append("payments")
                
        # Check for agents module (may require "agents" queue in future)
        if base_module.is_agents_enabled():
            if "agents" not in base_queues:
                base_queues.append("agents")
                
        logger.info(f"🎯 Smart queue detection: {base_queues}")
        
    except Exception as e:
        logger.warning(f"Failed to auto-detect queues, using defaults: {e}")
    
    return base_queues


def get_default_task_config(debug: bool = False) -> TaskConfig:
    """Get default task configuration based on environment."""
    smart_queues = get_smart_queues(debug)
    
    if debug:
        # Development defaults
        return TaskConfig(
            dramatiq=DramatiqConfig(
                processes=2,
                threads=4,
                prometheus_enabled=False,
                queues=smart_queues,
            ),
            worker=WorkerConfig(
                log_level="DEBUG",
                health_check_enabled=False,
            )
        )
    else:
        # Production defaults
        return TaskConfig(
            dramatiq=DramatiqConfig(
                processes=8,
                threads=16,
                prometheus_enabled=True,
                queues=smart_queues,
            ),
            worker=WorkerConfig(
                log_level="INFO",
                health_check_enabled=True,
                restart_on_memory_limit=True,
            )
        )


def validate_task_config(config: TaskConfig, redis_url: Optional[str] = None) -> bool:
    """Validate task configuration and dependencies."""
    if not config.enabled:
        return True
    
    # Check Redis URL if provided
    if redis_url:
        try:
            from urllib.parse import urlparse
            parsed = urlparse(redis_url)
            if not parsed.scheme.startswith("redis"):
                logger.error(f"Invalid Redis URL scheme: {parsed.scheme}")
                return False
        except Exception as e:
            logger.error(f"Invalid Redis URL: {e}")
            return False
    
    # Check if Dramatiq is available
    try:
        import dramatiq
        import django_dramatiq
    except ImportError as e:
        logger.error(f"Dramatiq dependencies not available: {e}")
        return False
    
    return True


# === Type Exports ===
__all__ = [
    "TaskConfig",
    "DramatiqConfig", 
    "WorkerConfig",
    "TaskBackend",
    "QueuePriority",
    "get_default_task_config",
    "validate_task_config",
]
