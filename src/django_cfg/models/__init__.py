"""
Configuration models for django_cfg.

All models are built using Pydantic v2 for complete type safety and validation.
Following CRITICAL_REQUIREMENTS.md - no raw Dict/Any usage, everything is properly typed.
"""

# This file intentionally left minimal to avoid circular imports
# All models are imported through the main __init__.py lazy loading mechanism

__all__ = []  # All exports handled by parent __init__.py
