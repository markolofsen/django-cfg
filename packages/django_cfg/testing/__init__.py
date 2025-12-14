"""
Testing utilities for django-cfg.

Zero-config test runners и utilities для автоматического управления тестовыми БД.

🔥 Generated with django-cfg
"""

from .runners import FastTestRunner, SmartTestRunner

__all__ = [
    'SmartTestRunner',
    'FastTestRunner',
]
