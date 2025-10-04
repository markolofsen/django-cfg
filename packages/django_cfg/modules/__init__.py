"""
Django CFG Modules

Auto-configuring utility modules that integrate seamlessly with DjangoConfig.
All modules automatically receive configuration from the DjangoConfig instance
without requiring manual parameter passing.
"""

from .base import BaseCfgModule

# Export the base module
__all__ = ["BaseCfgModule"]
