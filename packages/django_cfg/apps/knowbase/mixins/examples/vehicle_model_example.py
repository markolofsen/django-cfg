"""
Example of using ExternalDataMixin with VehicleModel.

This shows how to integrate VehicleModel with knowbase using the mixin.
"""

from django.db import models

from django_cfg.apps.knowbase.mixins import ExternalDataMixin
from django_cfg.apps.knowbase.models.external_data import ExternalDataType


class VehicleModelWithMixin(ExternalDataMixin, models.Model):
    """
    Example VehicleModel with ExternalDataMixin integration.
    
    This replaces the manual integration we had before with automatic
    tracking and vectorization.
    """

    # Original VehicleModel fields
    brand = models.ForeignKey('vehicles_data.Brand', on_delete=models.CASCADE)
    code = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    body_type = models.CharField(max_length=20, blank=True)
    segment = models.CharField(max_length=50, blank=True)
    is_active = models.BooleanField(default=True)
    total_vehicles = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True  # This is just an example

    class ExternalDataMeta:
        # Fields to watch for changes - only update when these change
        watch_fields = ['name', 'body_type', 'segment', 'is_active']

        # Lower threshold for multilingual vehicle data
        similarity_threshold = 0.4

        # Vehicle models are model type
        source_type = ExternalDataType.MODEL

        # Enable auto-sync
        auto_sync = True

        # Make public for search
        is_public = True

    # Required: content generation method
    def get_external_content(self):
        """Generate content for vectorization."""
        content_parts = [
            f"# {self.brand.name} {self.name}",
            "",
            "## Basic Information",
            f"- **Brand**: {self.brand.name} ({self.brand.code})",
            f"- **Model**: {self.name} ({self.code})",
        ]

        if self.body_type:
            content_parts.append(f"- **Body Type**: {self.body_type}")

        if self.segment:
            content_parts.append(f"- **Market Segment**: {self.segment}")

        content_parts.extend([
            f"- **Status**: {'Active' if self.is_active else 'Inactive'}",
            "",
            "## Market Statistics",
            f"- **Total Listings**: {self.total_vehicles:,} vehicles available",
        ])

        if hasattr(self, 'vehicles') and self.vehicles.exists():
            # Add some vehicle statistics if available
            vehicles = self.vehicles.filter(is_active=True)
            if vehicles.exists():
                content_parts.extend([
                    "",
                    "## Available Vehicles",
                    f"- **Active Listings**: {vehicles.count():,} vehicles",
                ])

                # Add price range if available
                if hasattr(vehicles.first(), 'price'):
                    prices = vehicles.exclude(price__isnull=True).values_list('price', flat=True)
                    if prices:
                        min_price = min(prices)
                        max_price = max(prices)
                        content_parts.append(f"- **Price Range**: ${min_price:,} - ${max_price:,}")

        content_parts.extend([
            "",
            "## Model History",
            f"- **First Listed**: {self.created_at.strftime('%Y-%m-%d')}",
            f"- **Last Updated**: {self.updated_at.strftime('%Y-%m-%d')}",
        ])

        return "\n".join(content_parts)

    # Optional: custom title
    def get_external_title(self):
        """Generate title for ExternalData."""
        return f"Vehicle Model: {self.brand.name} {self.name}"

    # Optional: custom description
    def get_external_description(self):
        """Generate description for ExternalData."""
        parts = [f"Comprehensive information about {self.brand.name} {self.name}"]

        if self.body_type:
            parts.append(f"({self.body_type})")

        parts.append("including specifications, market data, and vehicle listings.")

        return " ".join(parts)

    # Optional: metadata
    def get_external_metadata(self):
        """Generate metadata for ExternalData."""
        return {
            'vehicle_model_id': str(self.id),
            'brand_code': self.brand.code,
            'brand_name': self.brand.name,
            'model_code': self.code,
            'model_name': self.name,
            'body_type': self.body_type,
            'segment': self.segment,
            'total_vehicles': self.total_vehicles,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'integration_type': 'vehicle_model_mixin_auto'
        }

    # Optional: tags
    def get_external_tags(self):
        """Generate tags for ExternalData."""
        tags = [
            'vehicle',
            'model',
            self.brand.code.lower(),
            self.code.lower(),
            self.brand.name.lower().replace(' ', '_'),
            self.name.lower().replace(' ', '_'),
        ]

        if self.body_type:
            tags.append(self.body_type.lower().replace(' ', '_'))

        if self.segment:
            tags.append(self.segment.lower().replace(' ', '_'))

        return tags

    @property
    def full_name(self):
        """Get full model name with brand."""
        return f"{self.brand.name} {self.name}"

    def __str__(self):
        return self.full_name


# Usage example:
"""
# To use this mixin in your existing VehicleModel:

1. Add the mixin to your model:
   class VehicleModel(ExternalDataMixin, models.Model):
       # ... your existing fields ...
       
       class ExternalDataMeta:
           watch_fields = ['name', 'body_type', 'segment', 'is_active']
           similarity_threshold = 0.4
           source_type = ExternalDataType.MODEL
           auto_sync = True
           is_public = True
       
       def get_external_content(self):
           # ... content generation logic ...
           return content

2. Run migrations to add the mixin fields:
   python manage.py makemigrations
   python manage.py migrate

3. That's it! The mixin will automatically:
   - Create ExternalData when VehicleModel is created
   - Update ExternalData when watched fields change
   - Delete ExternalData when VehicleModel is deleted
   - Handle vectorization and search integration
   
4. Manual operations (if needed):
   vehicle_model.regenerate_external_data()  # Force regeneration
   vehicle_model.delete_external_data()      # Remove integration
   vehicle_model.has_external_data          # Check if linked
   vehicle_model.external_data_status       # Get processing status
"""
