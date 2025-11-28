"""
Crypto app configuration.
"""

from django.apps import AppConfig


class CryptoConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.crypto'
    verbose_name = 'Cryptocurrency Exchange'
