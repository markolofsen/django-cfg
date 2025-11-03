"""
ExternalDataMeta configuration parser.

Handles parsing and processing of ExternalDataMeta configuration from model classes.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ...models.external_data import ExternalDataType
from ..generators import ExternalDataFieldAnalyzer


@dataclass
class ExternalDataMetaConfig:
    """
    Configuration from ExternalDataMeta class.

    Attributes:
        watch_fields: List of field names to watch for changes
        similarity_threshold: Threshold for similarity search (0.0-1.0)
        source_type: Type of external data source
        auto_sync: Whether to automatically sync on changes
        is_public: Whether data is public
        title: Title for the external data (for create_from_config)
        description: Description for the external data
        content: Content for the external data
        source_identifier: Source identifier
        is_active: Whether the data is active
        metadata: Additional metadata
        tags: List of tags
        source_config: Source configuration dict
    """
    # Core configuration fields
    watch_fields: List[str] = field(default_factory=list)
    similarity_threshold: float = 0.5
    source_type: ExternalDataType = ExternalDataType.MODEL
    auto_sync: bool = True
    is_public: bool = False

    # ExternalData creation fields (used by ExternalDataCreator)
    title: str = ""
    description: str = ""
    content: str = ""
    source_identifier: str = ""
    is_active: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    source_config: Dict[str, Any] = field(default_factory=dict)


class ExternalDataMetaParser:
    """
    Parse ExternalDataMeta from model class.

    Extracts configuration from model's ExternalDataMeta inner class
    and applies smart defaults where needed.
    """

    @staticmethod
    def parse(model_class) -> Dict[str, Any]:
        """
        Parse ExternalDataMeta configuration from model class.

        Args:
            model_class: Django model class with optional ExternalDataMeta

        Returns:
            Dictionary with parsed configuration and smart defaults
        """
        config = {}

        # If ExternalDataMeta exists, use it
        if hasattr(model_class, 'ExternalDataMeta'):
            meta_class = model_class.ExternalDataMeta
            # Extract configuration from ExternalDataMeta
            for attr in dir(meta_class):
                if not attr.startswith('_'):
                    value = getattr(meta_class, attr)
                    if not callable(value):  # Only properties, not methods
                        config[attr] = value

        # Smart defaults based on model analysis
        if 'watch_fields' not in config:
            analyzer = ExternalDataFieldAnalyzer(model_class)
            config['watch_fields'] = analyzer.auto_detect_watch_fields()

        if 'similarity_threshold' not in config:
            config['similarity_threshold'] = 0.5  # Balanced default

        if 'source_type' not in config:
            config['source_type'] = ExternalDataType.MODEL  # Smart default

        if 'auto_sync' not in config:
            config['auto_sync'] = True  # Enable by default

        if 'is_public' not in config:
            config['is_public'] = False  # Private by default for security

        return config

    @staticmethod
    def to_dataclass(model_class) -> ExternalDataMetaConfig:
        """
        Parse configuration and return as dataclass.

        Args:
            model_class: Django model class

        Returns:
            ExternalDataMetaConfig dataclass instance
        """
        config_dict = ExternalDataMetaParser.parse(model_class)
        return ExternalDataMetaConfig(
            watch_fields=config_dict.get('watch_fields', []),
            similarity_threshold=config_dict.get('similarity_threshold', 0.5),
            source_type=config_dict.get('source_type', ExternalDataType.MODEL),
            auto_sync=config_dict.get('auto_sync', True),
            is_public=config_dict.get('is_public', False),
        )
