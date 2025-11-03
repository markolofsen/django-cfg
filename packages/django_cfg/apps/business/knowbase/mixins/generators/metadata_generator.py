"""
Metadata and tags generation for ExternalData.

Handles automatic generation of descriptions, tags, and metadata from model instances.
"""

from typing import List


class ExternalDataMetadataGenerator:
    """
    Generate metadata, tags, and descriptions for model instances.

    Provides smart auto-generation based on model fields and relationships.
    """

    def __init__(self, instance):
        """
        Initialize metadata generator for a model instance.

        Args:
            instance: Django model instance to generate metadata for
        """
        self.instance = instance
        self.model_class = instance.__class__

    def generate_description(self) -> str:
        """
        Auto-generate description based on model fields.

        Tries common description fields first, then builds description
        from key fields (name, status, dates).

        Returns:
            Generated description string
        """
        model_name = self.model_class._meta.verbose_name or self.model_class.__name__

        # Try common description fields
        desc_fields = ['description', 'summary', 'about', 'details', 'info']
        for field_name in desc_fields:
            if hasattr(self.instance, field_name):
                value = getattr(self.instance, field_name, None)
                if value and str(value).strip():
                    return f"{model_name} information: {value}"

        # Build description from key fields
        key_info = []

        # Add primary identifier
        if hasattr(self.instance, 'name') and self.instance.name:
            key_info.append(f"Name: {self.instance.name}")
        elif hasattr(self.instance, 'title') and self.instance.title:
            key_info.append(f"Title: {self.instance.title}")

        # Add status if available
        if hasattr(self.instance, 'is_active'):
            status = "Active" if self.instance.is_active else "Inactive"
            key_info.append(f"Status: {status}")

        # Add creation date if available
        if hasattr(self.instance, 'created_at') and self.instance.created_at:
            created_str = self.instance.created_at.strftime('%Y-%m-%d')
            key_info.append(f"Created: {created_str}")

        if key_info:
            return (f"Comprehensive information about this {model_name.lower()}. "
                    f"{', '.join(key_info)}.")

        return f"Auto-generated information from {model_name} model."

    def generate_tags(self) -> List[str]:
        """
        Auto-generate tags based on model fields and metadata.

        Generates tags from:
        - Model name and verbose name
        - App label
        - Field values (category, type, status, etc.)
        - Boolean field values

        Returns:
            List of tags (max 10), cleaned and deduplicated
        """
        tags = []

        # Add model-based tags
        tags.append(self.model_class.__name__.lower())
        if self.model_class._meta.verbose_name:
            tags.append(self.model_class._meta.verbose_name.lower().replace(' ', '_'))

        # Add app label
        tags.append(self.model_class._meta.app_label)

        # Add field-based tags
        tag_fields = ['category', 'type', 'kind', 'status', 'brand', 'model']
        for field_name in tag_fields:
            if hasattr(self.instance, field_name):
                value = getattr(self.instance, field_name, None)
                if value:
                    # Handle foreign key relationships
                    if hasattr(value, 'name'):
                        tags.append(str(value.name).lower())
                    elif hasattr(value, 'code'):
                        tags.append(str(value.code).lower())
                    else:
                        tags.append(str(value).lower())

        # Add boolean field tags
        bool_fields = ['is_active', 'is_public', 'is_featured', 'is_published']
        for field_name in bool_fields:
            if hasattr(self.instance, field_name):
                value = getattr(self.instance, field_name, None)
                if value is True:
                    tags.append(field_name.replace('is_', ''))

        # Clean and deduplicate tags
        clean_tags = []
        for tag in tags:
            clean_tag = str(tag).lower().strip().replace(' ', '_')
            if clean_tag and clean_tag not in clean_tags:
                clean_tags.append(clean_tag)

        return clean_tags[:10]  # Limit to 10 tags
