"""
Smart defaults for ExternalData configuration.

Provides sensible defaults for ExternalData configuration when not explicitly specified.
"""

from typing import List

from ...models.external_data import ExternalDataType
from ..generators import ExternalDataFieldAnalyzer


class ExternalDataDefaults:
    """
    Provide smart defaults for ExternalData configuration.

    Offers utilities to get sensible defaults when ExternalDataMeta
    is not provided or incomplete.
    """

    @staticmethod
    def get_default_watch_fields(model_class) -> List[str]:
        """
        Get default watch fields for a model class.

        Uses field analyzer to detect important fields.

        Args:
            model_class: Django model class

        Returns:
            List of field names to watch
        """
        analyzer = ExternalDataFieldAnalyzer(model_class)
        return analyzer.auto_detect_watch_fields()

    @staticmethod
    def get_default_source_type() -> ExternalDataType:
        """
        Get default source type.

        Returns:
            ExternalDataType.MODEL as default
        """
        return ExternalDataType.MODEL

    @staticmethod
    def get_default_similarity_threshold() -> float:
        """
        Get default similarity threshold.

        Returns:
            0.5 as balanced default threshold
        """
        return 0.5

    @staticmethod
    def get_default_auto_sync() -> bool:
        """
        Get default auto_sync setting.

        Returns:
            True (enabled by default)
        """
        return True

    @staticmethod
    def get_default_is_public() -> bool:
        """
        Get default is_public setting.

        Returns:
            False (private by default for security)
        """
        return False
