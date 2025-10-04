"""
Field analysis and detection for ExternalData.

Handles automatic detection of important fields to watch and analyze.
"""

from typing import List


class ExternalDataFieldAnalyzer:
    """
    Analyze model fields for auto-generation and change detection.

    Provides utilities to detect important fields that should be watched
    for changes and included in content generation.
    """

    def __init__(self, model_class):
        """
        Initialize field analyzer for a model class.

        Args:
            model_class: Django model class to analyze
        """
        self.model_class = model_class

    def auto_detect_watch_fields(self) -> List[str]:
        """
        Auto-detect important fields to watch for changes.

        Analyzes model fields and returns list of field names that should
        trigger ExternalData updates when changed.

        Returns:
            List of field names to watch (max 10 fields)
        """
        watch_fields = []

        # Get all model fields
        for field in self.model_class._meta.get_fields():
            if hasattr(field, 'name') and not field.name.startswith('_'):
                field_name = field.name

                # Skip auto-generated and system fields
                skip_fields = {
                    'id', 'pk', 'created_at', 'updated_at', 'external_source_id',
                    '_external_content_hash', 'slug'
                }
                if field_name in skip_fields:
                    continue

                # Skip reverse foreign keys and many-to-many
                if hasattr(field, 'related_model') and field.many_to_many:
                    continue
                if hasattr(field, 'remote_field') and field.remote_field:
                    if hasattr(field.remote_field, 'related_name'):
                        continue

                # Include important field types
                if hasattr(field, '__class__'):
                    field_type = field.__class__.__name__
                    important_types = {
                        'CharField', 'TextField', 'BooleanField', 'IntegerField',
                        'PositiveIntegerField', 'ForeignKey', 'DecimalField', 'FloatField'
                    }
                    if field_type in important_types:
                        watch_fields.append(field_name)

        # If no fields detected, watch all non-system fields
        if not watch_fields:
            for field in self.model_class._meta.get_fields():
                if hasattr(field, 'name') and not field.name.startswith('_'):
                    if field.name not in {'id', 'pk'}:
                        watch_fields.append(field.name)

        return watch_fields[:10]  # Limit to prevent too many triggers
