"""
FastTestRunner — in-memory SQLite runner for fast unit tests.
"""

import sys

from django.db import connections
from django.test.runner import DiscoverRunner

from .smart import SmartTestRunner


class FastTestRunner(SmartTestRunner):
    """
    Fast test runner using SQLite in-memory.

    Automatically switches all databases to SQLite to speed up unit tests.
    Use for fast tests without complex database features.

    Usage:
        python manage.py test --testrunner=django_cfg.testing.runners.FastTestRunner
    """

    def setup_databases(self, **kwargs) -> list:
        """Override to switch all databases to SQLite in-memory."""
        self._switch_to_sqlite()
        return DiscoverRunner.setup_databases(self, **kwargs)

    def _switch_to_sqlite(self):
        """Switch all databases to SQLite in-memory for speed."""
        for alias in connections:
            connection = connections[alias]
            if not hasattr(connection, '_original_settings'):
                connection._original_settings = connection.settings_dict.copy()
            connection.settings_dict.update({
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            })
            connection.close()

        if self.verbosity >= 1:
            sys.stderr.write("🚀 Switched to SQLite in-memory for fast testing\n")


__all__ = ["FastTestRunner"]
