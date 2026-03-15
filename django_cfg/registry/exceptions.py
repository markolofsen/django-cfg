"""
Django-CFG exceptions registry.
"""

EXCEPTIONS_REGISTRY = {
    # Core exceptions
    "DjangoCfgException": ("django_cfg.core.exceptions", "DjangoCfgException"),
    "ConfigurationError": ("django_cfg.core.exceptions", "ConfigurationError"),
    "ValidationError": ("django_cfg.core.exceptions", "ValidationError"),
    "EnvironmentError": ("django_cfg.core.exceptions", "EnvironmentError"),
}
