"""
Django-CFG wrapper for ai_docs command.

This is a simple alias for django_ai.management.commands.ai_docs.
All logic is in django_ai module.

Usage:
    poetry run python manage.py ai_docs search "How to configure database?"
    poetry run python manage.py ai_docs info DatabaseConfig
    poetry run python manage.py ai_docs mcp
    poetry run python manage.py ai_docs hint
"""

from django_cfg.modules.django_ai.management.commands.ai_docs import (
    Command as AiDocsCommand,
)


class Command(AiDocsCommand):
    """
    Alias for ai_docs command.

    Simply inherits from AiDocsCommand without any changes.
    """
    pass
