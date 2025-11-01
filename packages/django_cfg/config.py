"""
Django-CFG Library Configuration

Configuration settings for the django-cfg library itself.
"""

from typing import List

from .modules.django_admin.icons import Icons
from .modules.django_unfold.models.dropdown import SiteDropdownItem

# Library configuration
LIB_NAME = "django-cfg"
LIB_SITE_URL = "https://djangocfg.com"
LIB_GITHUB_URL = "https://github.com/django-cfg/django-cfg"
LIB_SUPPORT_URL = "https://demo.djangocfg.com"
LIB_HEALTH_URL = "/cfg/health/"

def get_maintenance_url(domain: str) -> str:
    """Get the maintenance URL for the current site."""
    # return f"{LIB_SITE_URL}/maintenance/{domain}/"
    return f"{LIB_SITE_URL}/maintenance?site={domain}"

def get_default_dropdown_items() -> List[SiteDropdownItem]:
    """Get default dropdown menu items for Unfold admin."""
    return [
        SiteDropdownItem(
            title="Documentation",
            icon=Icons.HELP_OUTLINE,
            link=LIB_SITE_URL,
        ),
        SiteDropdownItem(
            title="GitHub",
            icon=Icons.CODE,
            link=LIB_GITHUB_URL,
        ),
        SiteDropdownItem(
            title="Support",
            icon=Icons.SUPPORT_AGENT,
            link=LIB_SUPPORT_URL,
        ),
        SiteDropdownItem(
            title="Django-CFG",
            icon=Icons.HOME,
            link=LIB_SITE_URL,
        ),
    ]


# ==============================================================================
# Feature Detection System
# ==============================================================================

import logging
from typing import Dict, Callable

logger = logging.getLogger(__name__)

# Feature registry
FEATURES: Dict[str, Callable[[], bool]] = {}


def register_feature(name: str, check_func: Callable[[], bool]) -> None:
    """
    Register a feature check function.

    Args:
        name: Feature name (e.g., 'grpc', 'graphql')
        check_func: Function that returns True if feature dependencies are installed

    Example:
        >>> def check_grpc():
        ...     try:
        ...         import grpcio
        ...         return True
        ...     except ImportError:
        ...         return False
        >>> register_feature('grpc', check_grpc)
    """
    FEATURES[name] = check_func
    logger.debug(f"Registered feature: {name}")


def is_feature_available(feature: str) -> bool:
    """
    Check if optional feature is available.

    Args:
        feature: Feature name (e.g., 'grpc', 'graphql')

    Returns:
        True if feature dependencies are installed, False otherwise

    Example:
        >>> if is_feature_available('grpc'):
        ...     from django_cfg.models.api.grpc import GRPCConfig
    """
    check_func = FEATURES.get(feature)
    if not check_func:
        logger.warning(f"Unknown feature: {feature}")
        return False

    try:
        result = check_func()
        logger.debug(f"Feature '{feature}' available: {result}")
        return result
    except Exception as e:
        logger.debug(f"Feature '{feature}' not available: {e}")
        return False


def require_feature(feature: str, error_message: str = None) -> None:
    """
    Require a feature or raise ImportError.

    Args:
        feature: Feature name
        error_message: Custom error message

    Raises:
        ImportError: If feature not available

    Example:
        >>> require_feature('grpc')  # Raises if not installed
        >>> from django_cfg.models.api.grpc import GRPCConfig  # Safe to import
    """
    if not is_feature_available(feature):
        if error_message is None:
            error_message = (
                f"Feature '{feature}' requires additional dependencies. "
                f"Install with: pip install django-cfg[{feature}]"
            )
        raise ImportError(error_message)


# ==============================================================================
# Built-in Feature Checks
# ==============================================================================

def _check_grpc_available() -> bool:
    """Check if gRPC dependencies are installed."""
    try:
        import grpc as _grpc  # noqa: F401
        import grpc_tools as _grpc_tools  # noqa: F401
        import django_grpc_framework as _dgf  # noqa: F401
        import google.protobuf as _protobuf  # noqa: F401
        return True
    except ImportError:
        return False


# Register built-in features
register_feature('grpc', _check_grpc_available)
