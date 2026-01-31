"""
Django-CFG: Developer-First Django Configuration with Pydantic v2

A revolutionary Django configuration system that provides type-safe, intelligent,
and zero-boilerplate configuration management through Pydantic v2 models.

Key Features:
- 90% reduction in settings.py boilerplate
- 100% type safety with Pydantic v2 models
- Environment-aware smart defaults
- Seamless third-party integrations
- Zero raw dictionary usage

Example:
    ```python
    from django_cfg import DjangoConfig, DatabaseConfig
    
    class MyConfig(DjangoConfig):
        project_name: str = "My Project"
        databases: Dict[str, DatabaseConfig] = {
            "default": DatabaseConfig(
                engine="django.db.backends.postgresql",
                name="${DATABASE_URL:mydb}",
            )
        }
    
    config = MyConfig()
    ```
"""

# Configure Django app
default_app_config = "django_cfg.apps.DjangoCfgConfig"

# Version information
__version__ = "1.5.212"
__license__ = "MIT"

# Setup warnings debug early (checks env var only at this point)
# Will also check config.debug_warnings later when config is loaded
from .core.debug import setup_warnings_debug
setup_warnings_debug()

# Start Django startup timer early (at module import time)
try:
    from .core.integration.timing import start_django_timer, get_django_timer
    if not get_django_timer():
        start_django_timer()
except ImportError:
    pass

# Import registry for organized lazy loading
from .config import LIB_NAME
from .registry import DJANGO_CFG_REGISTRY

# Get author from library config
__author__ = LIB_NAME


def __getattr__(name: str):
    """Lazy import mechanism using registry pattern."""
    if name in DJANGO_CFG_REGISTRY:
        module_path, class_name = DJANGO_CFG_REGISTRY[name]

        import importlib
        module = importlib.import_module(module_path)
        return getattr(module, class_name)

    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")


# Export all registered components
__all__ = list(DJANGO_CFG_REGISTRY.keys())
