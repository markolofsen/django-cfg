"""
Task service factory and utilities.

Provides singleton instance and utility functions.
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Lazy import to avoid circular dependency
_task_service_instance = None


def get_task_service():
    """Get the global task service instance."""
    global _task_service_instance

    if _task_service_instance is None:
        from .service import DjangoTasks
        _task_service_instance = DjangoTasks()

    return _task_service_instance


def reset_task_service():
    """Reset the global task service instance (useful for testing)."""
    global _task_service_instance
    _task_service_instance = None


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


__all__ = [
    "get_task_service",
    "reset_task_service",
    "is_task_system_available",
    "get_task_health",
    "initialize_task_system",
]
