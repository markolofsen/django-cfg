"""
Django Logging Modules for django_cfg.

Auto-configuring logging utilities.
"""

from .logger import logger
from .django_logger import DjangoLogger, get_logger

__all__ = [
    "logger",
    "DjangoLogger",
    "get_logger",
]
