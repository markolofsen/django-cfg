"""
Django-CFG Library Configuration

Configuration settings for the django-cfg library itself.
"""


def is_feature_available(feature: str) -> bool:
    """
    Check if a feature is available (dependencies installed).

    Args:
        feature: Feature name (e.g., 'grpc', 'dramatiq')

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
LIB_SUPPORT_URL = "https://djangocfg.com/demo"
LIB_HEALTH_URL = "/healthz"

# Template configuration for create-project command
TEMPLATE_ARCHIVE_URL = f"{LIB_GITHUB_URL}/archive/refs/heads/main.zip"
TEMPLATE_PATH_IN_ARCHIVE = "solution"  # path inside the archive to extract

def get_maintenance_url(domain: str) -> str:
    """Get the maintenance URL for the current site."""
    # return f"{LIB_SITE_URL}/maintenance/{domain}/"
    return f"{LIB_SITE_URL}/maintenance?site={domain}"
