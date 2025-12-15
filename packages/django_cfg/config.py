"""
Django-CFG Library Configuration

Configuration settings for the django-cfg library itself.
"""

from typing import List

from .modules.django_admin.icons import Icons
from .modules.django_unfold.models.dropdown import SiteDropdownItem


def is_feature_available(feature: str) -> bool:
    """
    Check if a feature is available (dependencies installed).

    Args:
        feature: Feature name (e.g., 'grpc', 'centrifugo', 'webpush', 'dramatiq')

    Returns:
        True if feature dependencies are available
    """
    if feature == "grpc":
        try:
            import grpc  # noqa
            import grpc_reflection  # noqa
            return True
        except ImportError:
            return False
    elif feature == "centrifugo":
        try:
            import cent  # noqa
            return True
        except ImportError:
            return False
    elif feature == "webpush":
        try:
            import pywebpush  # noqa
            return True
        except ImportError:
            return False
    elif feature == "dramatiq":
        try:
            import dramatiq  # noqa
            return True
        except ImportError:
            return False

    return False

# Library configuration
LIB_NAME = "django-cfg"
LIB_SITE_URL = "https://djangocfg.com"
LIB_GITHUB_URL = "https://github.com/markolofsen/django-cfg"
LIB_GITHUB_RAW_URL = "https://github.com/markolofsen/django-cfg/raw/refs/heads/main"
LIB_SUPPORT_URL = "https://djangocfg.com/demo"
LIB_HEALTH_URL = "/cfg/health/"

# Template configuration for create-project command
TEMPLATE_ARCHIVE_URL = f"{LIB_GITHUB_URL}/archive/refs/heads/main.zip"
TEMPLATE_PATH_IN_ARCHIVE = "solution"  # path inside the archive to extract

# Frontend assets configuration (for auto-download when not bundled in PyPI package)
FRONTEND_ASSETS = {
    "admin": {
        "filename": "admin.zip",
        "download_url": f"{LIB_GITHUB_RAW_URL}/packages/django_cfg/static/frontend/admin.zip",
        "relative_path": "static/frontend",
    },
}


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

