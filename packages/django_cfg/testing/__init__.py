"""
Testing utilities for django-cfg.

Zero-config test runners for automatic test database management.

Usage with Django test:
    # Automatically configured via TEST_RUNNER setting
    python manage.py test

Usage with pytest:
    # pytest-django handles test DB automatically
    # Just use standard pytest-django fixtures (db, django_user_model, etc.)
    pytest

🔥 Generated with django-cfg
"""

from .runners import FastTestRunner, SmartTestRunner

__all__ = [
    "SmartTestRunner",
    "FastTestRunner",
]
