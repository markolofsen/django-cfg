"""
Django-CFG Task Service Module.

Simplified and focused task service for Dramatiq integration.
Provides essential functionality without unnecessary complexity.
"""

from typing import Optional, Dict, Any, List
import logging
from urllib.parse import urlparse

from . import BaseCfgModule
from django_cfg.models.tasks import TaskConfig, validate_task_config
from django_cfg.models.constance import ConstanceField

# Django imports (will be available when Django is configured)
try:
    from django.apps import apps
except ImportError:
    apps = None

# Optional imports
try:
    import dramatiq
except ImportError:
    dramatiq = None

try:
    import redis
except ImportError:
    redis = None

logger = logging.getLogger(__name__)


class DjangoTasks(BaseCfgModule):
    """
    Simplified Django-CFG task service.
    
    Focuses on essential functionality:
    - Configuration management
    - Task discovery
    - Health checks
    - Constance integration
    """
    
    def __init__(self):
        super().__init__()
        self._config: Optional[TaskConfig] = None
        self._redis_url: Optional[str] = None
    
    @property
    def config(self) -> Optional[TaskConfig]:
        """Get task configuration (lazy-loaded)."""
        if self._config is None:
            try:
                # Get config from django-cfg
                django_config = self.get_config()
                if django_config and hasattr(django_config, 'tasks'):
                    self._config = django_config.tasks
                    logger.debug(f"Loaded TaskConfig: enabled={self._config.enabled if self._config else False}")
                else:
                    # Fallback: try direct import
                    try:
                        from api.config import config as api_config
                        if hasattr(api_config, 'tasks') and api_config.tasks:
                            self._config = api_config.tasks
                            logger.debug(f"Loaded TaskConfig from api.config: enabled={self._config.enabled}")
                    except ImportError:
                        logger.debug("Could not import api.config")
            except Exception as e:
                logger.warning(f"Failed to get task config: {e}")
        
        return self._config
    
    def is_enabled(self) -> bool:
        """Check if task system is enabled and properly configured."""
        if not self.config or not self.config.enabled:
            return False
        
        # Check if required dependencies are available
        if dramatiq is None:
            logger.warning("Dramatiq not available")
            return False
        
        return True
    
    def get_redis_url(self) -> Optional[str]:
        """Get Redis URL from Django-CFG cache configuration."""
        if self._redis_url is None:
            try:
                from django_cfg.core.config import get_current_config
                django_config = get_current_config()
                
                if not django_config:
                    try:
                        from api.config import config
                        django_config = config
                    except ImportError:
                        logger.warning("Could not import config from api.config")
                
                if django_config and hasattr(django_config, 'cache_default') and django_config.cache_default:
                    cache_config = django_config.cache_default
                    if hasattr(cache_config, 'redis_url') and cache_config.redis_url:
                        self._redis_url = cache_config.redis_url
                        logger.debug(f"Got Redis URL: {self._redis_url}")
                    elif hasattr(cache_config, 'location') and cache_config.location:
                        self._redis_url = cache_config.location
                        logger.debug(f"Got Redis URL from location: {self._redis_url}")
            except Exception as e:
                logger.warning(f"Failed to get Redis URL: {e}")
        
        return self._redis_url
    
    def get_redis_client(self):
        """Get Redis client instance."""
        redis_url = self.get_redis_url()
        if not redis_url or redis is None:
            return None
        
        try:
            parsed = urlparse(redis_url)
            return redis.Redis(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 6379,
                db=self.config.dramatiq.redis_db if self.config else 1,
                password=parsed.password,
                socket_timeout=5
            )
        except Exception as e:
            logger.error(f"Failed to create Redis client: {e}")
            return None
    
    def _get_current_timestamp(self) -> str:
        """Get current timestamp in ISO format."""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def check_redis_connection(self) -> bool:
        """Check if Redis connection is available."""
        redis_client = self.get_redis_client()
        if not redis_client:
            return False
        
        try:
            redis_client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis connection failed: {e}")
            return False
    
    def validate_configuration(self) -> bool:
        """Validate complete task system configuration."""
        if not self.config:
            logger.error("Task configuration not available")
            return False
        
        redis_url = self.get_redis_url()
        if not redis_url:
            logger.error("Redis URL not configured")
            return False
        
        return validate_task_config(self.config, redis_url)
    
    def discover_tasks(self) -> List[str]:
        """Discover task modules in Django apps."""
        if not self.config or not self.config.auto_discover_tasks:
            return []
        
        discovered = []
        
        if apps is None:
            logger.warning("Django apps not available")
            return []
        
        try:
            for app_config in apps.get_app_configs():
                for module_name in self.config.task_modules:
                    module_path = f"{app_config.name}.{module_name}"
                    try:
                        __import__(module_path)
                        discovered.append(module_path)
                        logger.debug(f"Discovered task module: {module_path}")
                    except ImportError:
                        # Module doesn't exist, which is fine
                        pass
                    except Exception as e:
                        logger.warning(f"Error importing task module {module_path}: {e}")
        except Exception as e:
            logger.error(f"Task discovery failed: {e}")
        
        return discovered
    
    def get_constance_fields(self) -> List[ConstanceField]:
        """Get Constance fields for Dramatiq configuration."""
        if not self.is_enabled():
            return []
        
        fields = [
            ConstanceField(
                name="DRAMATIQ_WORKER_PROCESSES",
                default=self.config.dramatiq.processes if self.config else 2,
                help_text="Number of worker processes for Dramatiq",
                field_type="int",
                group="Tasks",
            ),
            ConstanceField(
                name="DRAMATIQ_WORKER_THREADS",
                default=self.config.dramatiq.threads if self.config else 4,
                help_text="Number of threads per worker process",
                field_type="int",
                group="Tasks",
            ),
            ConstanceField(
                name="DRAMATIQ_MAX_RETRIES",
                default=3,
                help_text="Maximum number of retries for failed tasks",
                field_type="int",
                group="Tasks",
            ),
            ConstanceField(
                name="DRAMATIQ_TASK_TIMEOUT",
                default=600,
                help_text="Task timeout in seconds (10 minutes default)",
                field_type="int",
                group="Tasks",
            ),
            ConstanceField(
                name="DRAMATIQ_PROMETHEUS_ENABLED",
                default=int(self.config.dramatiq.prometheus_enabled if self.config else False),
                help_text="Enable Prometheus metrics for Dramatiq (0=disabled, 1=enabled)",
                field_type="bool",
                group="Tasks",
                required=False,
            ),
        ]
        
        logger.debug(f"Generated {len(fields)} Constance fields for Dramatiq")
        return fields
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get comprehensive health status of task system."""
        status = {
            "enabled": self.is_enabled(),
            "redis_connection": False,
            "configuration_valid": False,
            "discovered_modules": [],
        }
        
        if self.is_enabled():
            status["redis_connection"] = self.check_redis_connection()
            status["configuration_valid"] = self.validate_configuration()
            status["discovered_modules"] = self.discover_tasks()
        
        return status


# === Service Factory ===

_task_service_instance: Optional[DjangoTasks] = None


def get_task_service() -> DjangoTasks:
    """Get the global task service instance."""
    global _task_service_instance
    
    if _task_service_instance is None:
        _task_service_instance = DjangoTasks()
    
    return _task_service_instance


def reset_task_service():
    """Reset the global task service instance (useful for testing)."""
    global _task_service_instance
    _task_service_instance = None


# === Utility Functions ===

def is_task_system_available() -> bool:
    """Check if task system is available and properly configured."""
    try:
        service = get_task_service()
        return service.is_enabled()
    except Exception:
        return False


def get_task_health() -> Dict[str, Any]:
    """Get task system health status."""
    try:
        service = get_task_service()
        return service.get_health_status()
    except Exception as e:
        return {
            "enabled": False,
            "error": str(e),
            "redis_connection": False,
            "configuration_valid": False,
        }


def initialize_task_system():
    """
    Initialize the task system during Django app startup.
    This function is called from Django AppConfig.ready() method.
    """
    try:
        service = get_task_service()
        
        # Force config reload to ensure we have fresh config
        service._config = None
        config = service.config
        
        if config and config.enabled:
            logger.info("🔧 Initializing Django-CFG task system...")
            
            # Set up Dramatiq broker from Django settings
            try:
                import dramatiq
                from django.conf import settings
                
                # Django-dramatiq automatically configures the broker from DRAMATIQ_BROKER setting
                if hasattr(settings, 'DRAMATIQ_BROKER'):
                    # Configure broker with middleware
                    broker_config = settings.DRAMATIQ_BROKER
                    middleware_list = getattr(settings, 'DRAMATIQ_MIDDLEWARE', [])
                    
                    # Import and instantiate middleware
                    middleware_instances = []
                    for middleware_path in middleware_list:
                        try:
                            module_path, class_name = middleware_path.rsplit('.', 1)
                            module = __import__(module_path, fromlist=[class_name])
                            middleware_class = getattr(module, class_name)
                            middleware_instances.append(middleware_class())
                        except Exception as e:
                            logger.warning(f"Failed to load middleware {middleware_path}: {e}")
                    
                    # Create broker with middleware
                    broker_class_path = broker_config['BROKER']
                    module_path, class_name = broker_class_path.rsplit('.', 1)
                    module = __import__(module_path, fromlist=[class_name])
                    broker_class = getattr(module, class_name)
                    
                    broker_options = broker_config.get('OPTIONS', {})
                    broker = broker_class(middleware=middleware_instances, **broker_options)
                    
                    # Set as default broker
                    dramatiq.set_broker(broker)
                    
                    logger.debug(f"✅ Dramatiq broker configured with {len(middleware_instances)} middleware")
                else:
                    logger.warning("DRAMATIQ_BROKER not found in Django settings")
                    
            except Exception as e:
                logger.warning(f"Failed to configure Dramatiq: {e}")
            
            logger.info("✅ Task system initialized successfully")
            logger.info("💡 To start workers, run: python manage.py rundramatiq")
        else:
            logger.debug(f"Task system not enabled (config: {config}), skipping initialization")
            
    except Exception as e:
        logger.error(f"Failed to initialize task system: {e}")


def generate_dramatiq_settings_from_config(config):
    """
    Generate Dramatiq settings from DjangoConfig instance.
    
    Args:
        config: DjangoConfig instance with tasks configuration
        
    Returns:
        Dict[str, Any]: Dramatiq settings dictionary or empty dict if not enabled
    """
    try:
        if not hasattr(config, "tasks") or not config.tasks or not config.tasks.enabled:
            return {}
            
        # Get Redis URL from cache configuration
        redis_url = None
        if config.cache_default and hasattr(config.cache_default, 'redis_url'):
            redis_url = config.cache_default.redis_url
        elif config.cache_default and hasattr(config.cache_default, 'location'):
            redis_url = config.cache_default.location
        else:
            # Fallback to default Redis URL
            redis_url = "redis://localhost:6379"
        
        if redis_url:
            dramatiq_settings = config.tasks.get_dramatiq_settings(redis_url)
            logger.debug(f"Generated Dramatiq settings with Redis URL: {redis_url}")
            return dramatiq_settings
        else:
            logger.warning("Tasks enabled but no Redis URL available for Dramatiq")
            return {}
            
    except Exception as e:
        logger.error(f"Failed to generate Dramatiq settings: {e}")
        return {}


def extend_constance_config_with_tasks():
    """
    Extend Constance configuration with Dramatiq task fields if tasks are enabled.
    """
    try:
        service = get_task_service()
        if not service.is_enabled():
            logger.debug("Task system not enabled, skipping Constance extension")
            return []
        
        fields = service.get_constance_fields()
        logger.info(f"🔧 Extended Constance with {len(fields)} task configuration fields")
        return fields
        
    except Exception as e:
        logger.error(f"Failed to extend Constance config with tasks: {e}")
        return []


# === Exports ===

def generate_dramatiq_settings_from_config() -> Optional[Dict[str, Any]]:
    """
    Generate Dramatiq settings from auto-discovered DjangoConfig.
    
    Returns:
        Dictionary of Dramatiq settings or None if tasks disabled
    """
    try:
        # Get config through BaseCfgModule
        base_module = BaseCfgModule()
        config = base_module.get_config()
        
        if not config or not hasattr(config, 'tasks') or not config.tasks or not config.tasks.enabled:
            return None
        
        # Get Redis URL from cache config or environment
        redis_url = None
        if hasattr(config, 'cache_default') and config.cache_default:
            redis_url = getattr(config.cache_default, 'redis_url', None)
        
        if not redis_url:
            # Fallback to environment or default
            import os
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/1')
        
        # Generate Dramatiq settings
        dramatiq_settings = config.tasks.get_dramatiq_settings(redis_url)
        
        # Ensure we only use Redis broker (no RabbitMQ)
        if 'DRAMATIQ_BROKER' in dramatiq_settings:
            dramatiq_settings['DRAMATIQ_BROKER']['BROKER'] = 'dramatiq.brokers.redis.RedisBroker'
        
        logger.info(f"✅ Generated Dramatiq settings with Redis broker and {len(config.tasks.dramatiq.queues)} queues")
        return dramatiq_settings
        
    except Exception as e:
        logger.error(f"Failed to generate Dramatiq settings: {e}")
        return None


__all__ = [
    "DjangoTasks",
    "get_task_service",
    "reset_task_service",
    "is_task_system_available",
    "get_task_health",
    "generate_dramatiq_settings_from_config",
    "extend_constance_config_with_tasks",
    "initialize_task_system",
]