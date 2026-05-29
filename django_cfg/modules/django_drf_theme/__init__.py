"""
Django DRF Tailwind Theme

Lean Tailwind v4 + Alpine.js theme for the Django REST Framework Browsable API.
Zero-build (Tailwind v4 Play CDN); decomposed into small template components.

Features:
- Light / dark / auto theme (class-based, native v4 dark variant)
- Interactive recursive JSON tree (Alpine, collapsible)
- Pretty / Raw / Headers tabs, one-click copy
- Method & status badges, filters, pagination, request forms, toasts
"""

from .renderers import TailwindBrowsableAPIRenderer

__all__ = [
    "TailwindBrowsableAPIRenderer",
]

__version__ = "1.0.0"
