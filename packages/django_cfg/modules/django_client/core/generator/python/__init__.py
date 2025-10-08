"""
Python Generator - Generates Python client (Pydantic 2 + httpx).

This generator creates a complete Python API client from IR:
- Pydantic 2 models (Request/Response/Patch splits)
- Enum classes from x-enum-varnames
- httpx.AsyncClient for async HTTP
- Django CSRF/session handling
- Type-safe (MyPy strict mode compatible)

Reference: https://docs.pydantic.dev/latest/
"""

from .generator import PythonGenerator

__all__ = ['PythonGenerator']
