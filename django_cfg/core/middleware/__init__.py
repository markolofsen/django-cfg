"""
Django-CFG Middleware.

Custom middleware for Django-CFG applications.
"""

from .public_api_cors import PublicAPICORSMiddleware

__all__ = ["PublicAPICORSMiddleware"]
