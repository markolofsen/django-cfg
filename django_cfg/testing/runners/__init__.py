"""
django-cfg test runners package.

Provides SmartTestRunner and FastTestRunner as drop-in replacements for
Django's default DiscoverRunner.

Usage in settings (auto-configured by django-cfg):
    TEST_RUNNER = 'django_cfg.testing.runners.SmartTestRunner'

Or manually:
    python manage.py test --testrunner=django_cfg.testing.runners.SmartTestRunner
    python manage.py test --testrunner=django_cfg.testing.runners.FastTestRunner
"""

from .fast import FastTestRunner
from .smart import SmartTestRunner

__all__ = [
    "SmartTestRunner",
    "FastTestRunner",
]
