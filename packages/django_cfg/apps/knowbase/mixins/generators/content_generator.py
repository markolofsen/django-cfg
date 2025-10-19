"""
Content and title generation for ExternalData.

Handles automatic generation of titles and markdown content from model instances.
"""

from typing import Any, Dict, List, Tuple


class ExternalDataContentGenerator:
    """
    Generate content and titles for model instances.

    Provides smart auto-generation of titles and comprehensive markdown content
    based on model fields and metadata.
    """

    def __init__(self, instance):
        """
        Initialize content generator for a model instance.

        Args:
            instance: Django model instance to generate content for
        """
        self.instance = instance
        self.model_class = instance.__class__

    def generate_title(self) -> str:
        """
        Auto-generate title based on model fields.

        Tries common title fields first (title, name, etc.), then falls back
        to string representation with model name.

        Returns:
            Generated title string (e.g., "Product: iPhone 15")
        """
        # Try common title fields first
        title_fields = ['title', 'name', 'full_name', 'display_name', 'label']

        for field_name in title_fields:
            if hasattr(self.instance, field_name):
                value = getattr(self.instance, field_name, None)
                if value and str(value).strip():
                    # Add model context for clarity
                    model_name = self.model_class._meta.verbose_name or self.model_class.__name__
                    return f"{model_name}: {value}"

        # Fallback: use string representation with model name
        model_name = self.model_class._meta.verbose_name or self.model_class.__name__
        return f"{model_name}: {self.instance}"

    def generate_content(self) -> str:
        """
        Auto-generate comprehensive markdown content.

        Generates structured markdown content with:
        - Header with title
        - Basic Information section with key fields
        - Related Information section with relationships
        - Statistics section if available
        - Technical Information section with metadata

        Returns:
            Generated markdown content as string
        """
        content_parts = []

        # Header with title
        title = self.generate_title()
        content_parts.append(f"# {title}")
        content_parts.append("")

        # Basic Information section
        content_parts.append("## Basic Information")

        # Add key fields
        key_fields = self._get_content_fields()
        for field_name, field_value, field_label in key_fields:
            if field_value is not None and str(field_value).strip():
                content_parts.append(f"- **{field_label}**: {field_value}")

        content_parts.append("")

        # Add relationships section if any
        relationships = self._get_relationship_info()
        if relationships:
            content_parts.append("## Related Information")
            for rel_name, rel_info in relationships.items():
                content_parts.append(f"- **{rel_name}**: {rel_info}")
            content_parts.append("")

        # Add statistics if available
        stats = self._get_statistics_info()
        if stats:
            content_parts.append("## Statistics")
            for stat_name, stat_value in stats.items():
                content_parts.append(f"- **{stat_name}**: {stat_value}")
            content_parts.append("")

        # Add metadata section
        content_parts.append("## Technical Information")
        content_parts.append(
            f"This data is automatically synchronized from the {self.model_class.__name__} "
            f"model using ExternalDataMixin."
        )
        content_parts.append("")
        content_parts.append(f"**Model**: {self.model_class._meta.label}")
        content_parts.append(f"**ID**: {self.instance.pk}")

        if hasattr(self.instance, 'created_at') and self.instance.created_at:
            created_str = self.instance.created_at.strftime('%Y-%m-%d %H:%M:%S')
            content_parts.append(f"**Created**: {created_str}")

        if hasattr(self.instance, 'updated_at') and self.instance.updated_at:
            updated_str = self.instance.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            content_parts.append(f"**Updated**: {updated_str}")

        return "\n".join(content_parts)

    def _get_content_fields(self) -> List[Tuple[str, Any, str]]:
        """
        Get fields to include in content generation.

        Returns priority fields with their values and labels.

        Returns:
            List of tuples: (field_name, field_value, field_label)
        """
        fields_info = []

        # Define field priority and labels
        priority_fields = {
            'name': 'Name',
            'title': 'Title',
            'code': 'Code',
            'description': 'Description',
            'summary': 'Summary',
            'body_type': 'Body Type',
            'segment': 'Segment',
            'category': 'Category',
            'type': 'Type',
            'status': 'Status',
            'is_active': 'Active',
            'is_public': 'Public',
            'price': 'Price',
            'year': 'Year',
            'fuel_type': 'Fuel Type',
        }

        # Add priority fields first
        for field_name, field_label in priority_fields.items():
            if hasattr(self.instance, field_name):
                value = getattr(self.instance, field_name, None)
                if value is not None:
                    # Format boolean fields
                    if isinstance(value, bool):
                        value = "Yes" if value else "No"
                    # Format choice fields
                    elif hasattr(self.instance, f'get_{field_name}_display'):
                        display_value = getattr(self.instance, f'get_{field_name}_display')()
                        if display_value:
                            value = display_value
                    # Format foreign key relationships
                    elif hasattr(value, '__str__'):
                        value = str(value)

                    fields_info.append((field_name, value, field_label))

        return fields_info

    def _get_relationship_info(self) -> Dict[str, str]:
        """
        Get relationship information for content.

        Extracts foreign key relationships from common field names.

        Returns:
            Dictionary mapping relationship names to string values
        """
        relationships = {}

        # Common relationship field names
        rel_fields = ['brand', 'category', 'parent', 'owner', 'user', 'created_by']

        for field_name in rel_fields:
            if hasattr(self.instance, field_name):
                value = getattr(self.instance, field_name, None)
                if value:
                    relationships[field_name.replace('_', ' ').title()] = str(value)

        return relationships

    def _get_statistics_info(self) -> Dict[str, Any]:
        """
        Get statistics information for content.

        Extracts numeric statistics from common field names.

        Returns:
            Dictionary mapping statistic names to formatted values
        """
        stats = {}

        # Common statistics field names
        stat_fields = ['total_vehicles', 'total_models', 'total_items', 'count', 'views', 'likes']

        for field_name in stat_fields:
            if hasattr(self.instance, field_name):
                value = getattr(self.instance, field_name, None)
                if value is not None and (isinstance(value, (int, float)) and value > 0):
                    label = field_name.replace('_', ' ').title()
                    if isinstance(value, float):
                        stats[label] = f"{value:,.2f}"
                    else:
                        stats[label] = f"{value:,}"

        return stats
