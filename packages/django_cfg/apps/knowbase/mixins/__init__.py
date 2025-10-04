"""
Mixins for knowbase integration.
"""

from .external_data_mixin import ExternalDataMixin
from .config import ExternalDataMetaConfig, ExternalDataMetaParser, ExternalDataDefaults
from .creator import ExternalDataCreator
from .service import ExternalDataService
from .generators import (
    ExternalDataContentGenerator,
    ExternalDataMetadataGenerator,
    ExternalDataFieldAnalyzer,
)

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
