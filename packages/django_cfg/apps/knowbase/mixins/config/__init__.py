"""
Configuration utilities for ExternalData.

Parsing and defaults for ExternalDataMeta configuration.
"""

from .defaults import ExternalDataDefaults
from .meta_config import ExternalDataMetaConfig, ExternalDataMetaParser

__all__ = [
    'ExternalDataMetaConfig',
    'ExternalDataMetaParser',
    'ExternalDataDefaults',
]
