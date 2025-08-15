"""
🚀 Django Config Toolkit - Amazing Configuration Experience

A Python package that makes Django configuration simple, type-safe, and fun!

Features:
- Type-safe configuration with Pydantic 2
- Automatic environment detection
- Smart defaults for Django
- Amazing developer experience
- One-line Django settings integration

Quick Start:
    ```python
    from django_cfg import ConfigToolkit
    
    # One line Django settings
    globals().update(ConfigToolkit.get_django_settings())
    
    # Type-safe access anywhere
    debug = ConfigToolkit.debug
    db_url = ConfigToolkit.database_url
    ```
"""

from .toolkit import ConfigToolkit
from .health import HealthCheckView, SimpleHealthView, get_health_urls
from .models import (
    BaseConfig,
    EnvironmentConfig,
    DatabaseConfig,
    SecurityConfig,
    APIConfig,
    CacheConfig,
    EmailConfig,
    UnfoldConfig,

    ConstanceConfig,
    ConstanceFieldConfig,
    LoggingConfig,
    LoggerConfig,
    HandlerConfig,
    FormatterConfig,
)

__version__ = "1.0.8"
__author__ = "Unrealos Team"

__all__ = [
    # Main interface
    "ConfigToolkit",
    
    # Core configuration models
    "BaseConfig",
    "EnvironmentConfig", 
    "DatabaseConfig",
    "SecurityConfig",
    "APIConfig",
    "CacheConfig",
    "EmailConfig",
    
    # Extended configuration models
    "UnfoldConfig",
 
    "ConstanceConfig",
    "ConstanceFieldConfig",
    "LoggingConfig",
    "LoggerConfig",
    "HandlerConfig",
    "FormatterConfig",
    
    # Health check views
    "HealthCheckView",
    "SimpleHealthView", 
    "get_health_urls",
]

# Show helpful info on import for developers
def _show_welcome_message():
    """Show welcome message for developers."""
    import sys
    if hasattr(sys, 'ps1'):  # Interactive Python
        print("🚀 Django Config Toolkit loaded!")
        print("💡 Use: ConfigToolkit.debug, ConfigToolkit.database_url, etc.")
        print("📚 Docs: https://unrealos.com/")

_show_welcome_message()
