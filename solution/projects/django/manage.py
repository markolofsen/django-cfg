#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # `test` gets api.settings.test (SQLite, fast); everything else gets
    # api.settings.base (Postgres). An explicit DJANGO_SETTINGS_MODULE in the
    # environment still wins, so CI or a deliberate override still works.
    default_settings = (
        'api.settings.test' if len(sys.argv) > 1 and sys.argv[1] == 'test'
        else 'api.settings.base'
    )
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', default_settings)
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
