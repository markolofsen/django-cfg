"""
Frontend App Setup Helpers

Provides utilities to automatically configure Django to serve Next.js static builds.
"""

from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.conf import Settings


def setup_frontend_serving(settings: 'Settings' = None) -> dict:
    """
    Configure Django to serve Next.js static builds.

    This function returns configuration that should be added to Django settings.

    Usage in settings.py:
    ```python
    from django_cfg.apps.system.frontend.setup import setup_frontend_serving

    # Apply frontend configuration
    frontend_config = setup_frontend_serving()
    INSTALLED_APPS += frontend_config['INSTALLED_APPS']
    ```

    Args:
        settings: Django settings module (optional)

    Returns:
        dict: Configuration to merge into settings
    """
    import django_cfg

    config = {
        'INSTALLED_APPS': [
            'django_cfg.apps.system.frontend',
        ],
    }

    return config


def get_frontend_path(app_name: str = 'admin') -> Path:
    """
    Get the path to a frontend app's static build.

    Args:
        app_name: Name of the frontend app (e.g., 'admin')

    Returns:
        Path: Absolute path to the frontend build directory

    Example:
        >>> from django_cfg.apps.system.frontend.setup import get_frontend_path
        >>> admin_path = get_frontend_path('admin')
        >>> print(admin_path)
        /path/to/django_cfg/static/frontend/admin
    """
    import django_cfg
    return Path(django_cfg.__file__).parent / 'static' / 'frontend' / app_name


def is_frontend_built(app_name: str = 'admin') -> bool:
    """
    Check if a frontend app has been built.

    Args:
        app_name: Name of the frontend app

    Returns:
        bool: True if the build exists, False otherwise
    """
    path = get_frontend_path(app_name)
    index_html = path / 'index.html'
    return index_html.exists()


def get_frontend_urls():
    """
    Get URL patterns for frontend apps.

    Usage in urls.py:
    ```python
    from django_cfg.apps.system.frontend.setup import get_frontend_urls

    urlpatterns = [
        # Your URLs here
        ...
    ]

    # Add frontend URLs
    urlpatterns += get_frontend_urls()
    ```

    Returns:
        list: URL patterns for frontend apps
    """
    from django.urls import path, include

    return [
        path('', include('django_cfg.apps.system.frontend.urls', namespace='frontend')),
    ]
