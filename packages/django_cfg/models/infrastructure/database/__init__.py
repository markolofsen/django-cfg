"""
Database configuration for django_cfg.

Provides type-safe database configuration with:
- Connection string parsing
- Field validation
- Django settings conversion
- Database routing

Organized into focused modules:
- config.py - Main DatabaseConfig class
- validators.py - Field validators
- parsers.py - Connection string parsers
- converters.py - Django settings converters
- routing.py - Database routing utilities
"""

from .config import DatabaseConfig

__all__ = [
    "DatabaseConfig",
]
