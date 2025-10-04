"""
Configuration utilities for ExternalData.

Parsing and defaults for ExternalDataMeta configuration.
"""

from .meta_config import ExternalDataMetaConfig, ExternalDataMetaParser
from .defaults import ExternalDataDefaults

__all__ = [
    'ExternalDataMetaConfig',
    'ExternalDataMetaParser',
    'ExternalDataDefaults',
]
