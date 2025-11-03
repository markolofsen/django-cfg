"""
Mixins for knowbase integration.
"""

from .config import ExternalDataDefaults, ExternalDataMetaConfig, ExternalDataMetaParser
from .creator import ExternalDataCreator
from .external_data_mixin import ExternalDataMixin
from .generators import (
    ExternalDataContentGenerator,
    ExternalDataFieldAnalyzer,
    ExternalDataMetadataGenerator,
)
from .service import ExternalDataService

__all__ = [
    # Core mixin
    'ExternalDataMixin',

    # Configuration
    'ExternalDataMetaConfig',
    'ExternalDataMetaParser',
    'ExternalDataDefaults',

    # Service layer
    'ExternalDataCreator',
    'ExternalDataService',

    # Generators (for advanced usage)
    'ExternalDataContentGenerator',
    'ExternalDataMetadataGenerator',
    'ExternalDataFieldAnalyzer',
]
