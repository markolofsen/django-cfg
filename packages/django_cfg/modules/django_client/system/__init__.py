"""
MJS Client Generation System for django-cfg

This module provides a modular system for generating JavaScript ES modules
with JSDoc type annotations from OpenAPI schemas.

Components:
- base_generator: Base class with common utilities
- schema_parser: OpenAPI schema parsing and type extraction
- mjs_generator: Main generator for MJS clients
- templates/: Jinja2 templates for code generation
"""

from .base_generator import BaseGenerator
from .mjs_generator import MJSGenerator
from .schema_parser import SchemaParser

__all__ = [
    'BaseGenerator',
    'SchemaParser',
    'MJSGenerator'
]

__version__ = '1.0.0'
