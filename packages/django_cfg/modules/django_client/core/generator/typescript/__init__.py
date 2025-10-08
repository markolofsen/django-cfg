"""
TypeScript Generator - Generates TypeScript client (Fetch API).

This generator creates a complete TypeScript API client from IR:
- TypeScript interfaces (Request/Response/Patch splits)
- Enum types from x-enum-varnames
- Fetch API for HTTP
- Django CSRF/session handling
- Type-safe
"""

from .generator import TypeScriptGenerator

__all__ = ['TypeScriptGenerator']
