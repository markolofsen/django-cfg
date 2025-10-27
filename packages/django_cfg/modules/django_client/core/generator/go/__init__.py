"""
Go Generator - Generates Go client (net/http).

This generator creates a complete Go API client from IR:
- Go structs (Request/Response/Patch splits)
- Enum types with constants
- net/http client for HTTP requests
- Type-safe operations
- Context-aware requests
"""

from .generator import GoGenerator

__all__ = ['GoGenerator']
