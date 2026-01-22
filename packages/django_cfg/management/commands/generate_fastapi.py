"""
Django-CFG wrapper for generate_fastapi command.

This is a simple alias for django_fastapi.management.commands.generate_fastapi.
All logic is in django_fastapi module.

Usage:
    python manage.py generate_fastapi
    python manage.py generate_fastapi users products
    python manage.py generate_fastapi --output-dir=api/ --dry-run
    python manage.py generate_fastapi --no-crud --no-schemas
"""

from django_cfg.modules.django_fastapi.management.commands.generate_fastapi import (
    Command as DjangoFastAPICommand,
)


class Command(DjangoFastAPICommand):
    """
    Generate FastAPI ORM from Django models.

    Simply inherits from DjangoFastAPICommand without any changes.
    """
    pass
