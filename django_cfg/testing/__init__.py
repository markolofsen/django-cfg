"""
Testing utilities for django-cfg.

Zero-config test runners for automatic test database management.

Usage with Django test:
    # Automatically configured via TEST_RUNNER setting
    python manage.py test

Usage with pytest:
    # Add to your project's conftest.py:
    pytest_plugins = ["django_cfg.testing.pytest_plugin"]

🔥 Generated with django-cfg
"""

from .runners import FastTestRunner, SmartTestRunner
from .runners.utils import install_all_extensions

__all__ = [
    "SmartTestRunner",
    "FastTestRunner",
    "install_all_extensions",
]
