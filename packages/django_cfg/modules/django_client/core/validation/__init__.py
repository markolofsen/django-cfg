"""
OpenAPI Schema Validation Module.

Provides safe validation and fixing of Django REST Framework serializers
to improve OpenAPI schema quality.
"""

from .checker import ValidationChecker
from .fixer import SafeFixer
from .reporter import IssueReporter
from .rules.base import Issue, Severity, ValidationRule
from .safety import SafetyManager

__all__ = [
    'ValidationChecker',
    'SafeFixer',
    'IssueReporter',
    'SafetyManager',
    'Issue',
    'Severity',
    'ValidationRule',
]
