"""
Django-CFG Task Service.

Main DjangoTasks class for Dramatiq integration.
"""

import logging
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from django_cfg.models.django.constance import ConstanceField
from django_cfg.models.tasks import TaskConfig, validate_task_config

from ..base import BaseCfgModule

# Django imports
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

        if dramatiq is None:
            logger.warning("Dramatiq not available")
            return False

        return True

    def get_redis_url(self) -> Optional[str]:
        """Get Redis URL using the same logic as Dramatiq settings generation."""
        if self._redis_url is None:
            config = self.get_config()

            if not config:
                raise RuntimeError("No Django-CFG configuration available")

            # Get Redis URL from cache config
            if hasattr(config, 'cache_default') and config.cache_default:
                self._redis_url = getattr(config.cache_default, 'redis_url', None)
                if self._redis_url:
                    logger.debug(f"Got Redis URL from cache config: {self._redis_url}")
                    return self._redis_url

            # If no cache_default, try Django cache settings
            try:
                from django.conf import settings
                if hasattr(settings, 'CACHES') and 'default' in settings.CACHES:
                    cache_config = settings.CACHES['default']
                    if cache_config.get('BACKEND') == 'django_redis.cache.RedisCache':
                        self._redis_url = cache_config.get('LOCATION')
                        if self._redis_url:
                            logger.debug(f"Got Redis URL from Django cache settings: {self._redis_url}")
                            return self._redis_url
            except Exception as e:
                logger.debug(f"Could not get Redis URL from Django settings: {e}")

            # Try DRAMATIQ_BROKER settings
            try:
                from django.conf import settings
                if hasattr(settings, 'DRAMATIQ_BROKER'):
                    dramatiq_config = settings.DRAMATIQ_BROKER
                    if isinstance(dramatiq_config, dict) and 'OPTIONS' in dramatiq_config:
                        self._redis_url = dramatiq_config['OPTIONS'].get('url')
                        if self._redis_url:
                            logger.debug(f"Got Redis URL from DRAMATIQ_BROKER settings: {self._redis_url}")
                            return self._redis_url
            except Exception as e:
                logger.debug(f"Could not get Redis URL from DRAMATIQ_BROKER settings: {e}")

            raise RuntimeError("No Redis URL found in cache configuration, Django settings, or DRAMATIQ_BROKER")

        return self._redis_url

    def get_redis_client(self):
        """Get Redis client instance."""
        redis_url = self.get_redis_url()
        if not redis_url or redis is None:
            return None

        try:
            parsed = urlparse(redis_url)

            # Extract database from URL path
            db = 1  # Default
            if parsed.path and parsed.path != "/":
                try:
                    db = int(parsed.path.lstrip('/'))
                except ValueError:
                    pass
            elif self.config and self.config.dramatiq:
                db = self.config.dramatiq.redis_db

            logger.debug(f"Using Redis DB: {db} from URL: {redis_url}")

            return redis.Redis(
                host=parsed.hostname or 'localhost',
                port=parsed.port or 6379,
                db=db,
                password=parsed.password,
                socket_timeout=5
            )
        except Exception as e:
            logger.error(f"Failed to create Redis client: {e}")
            return None

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


__all__ = ["DjangoTasks"]
