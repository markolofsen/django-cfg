"""
Mixin for automatic ExternalData integration.

This mixin provides automatic integration with knowbase ExternalData system:
- Adds external_source_id field automatically
- Tracks model changes and updates vectorization
- Provides simple configuration interface
- Handles creation, updates, and deletion automatically

Usage:
    class MyModel(ExternalDataMixin, models.Model):
        name = models.CharField(max_length=100)
        description = models.TextField()
        
        class Meta:
            # Standard Django Meta options...
            
        class ExternalDataMeta:
            # Required: fields to watch for changes
            watch_fields = ['name', 'description']
            
            # Optional: similarity threshold (default: 0.5)
            similarity_threshold = 0.4
            
            # Optional: source type (default: ExternalDataType.MODEL)
            source_type = ExternalDataType.CUSTOM
            
            # Optional: enable/disable auto-sync (default: True)
            auto_sync = True
            
            # Optional: make public (default: False)
            is_public = False
        
        # Required: content generation method
        def get_external_content(self):
            return f"# {self.name}\n\n{self.description}"
        
        # Optional: custom title (default: str(instance))
        def get_external_title(self):
            return f"My Model: {self.name}"
        
        # Optional: custom description (default: auto-generated)
        def get_external_description(self):
            return f"Information about {self.name}"
        
        # Optional: metadata (default: basic model info)
        def get_external_metadata(self):
            return {
                'model_type': 'my_model',
                'model_id': str(self.id),
                'name': self.name,
            }
        
        # Optional: tags (default: [model_name.lower()])
        def get_external_tags(self):
            return ['my_model', self.name.lower()]
"""

import logging
import hashlib
from typing import Optional, List, Dict, Any, Type
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType

from ..models.external_data import ExternalData, ExternalDataType, ExternalDataStatus
from .creator import ExternalDataCreator
from .config import ExternalDataConfig

logger = logging.getLogger(__name__)


class ExternalDataMixin(models.Model):
    """
    Mixin that automatically integrates models with knowbase ExternalData system.
    
    Provides:
    - Automatic external_source_id field
    - Change tracking and vectorization
    - Simple configuration interface
    - Automatic cleanup on deletion
    """
    
    # Automatically added field for linking to ExternalData
    external_source_id = models.UUIDField(
        null=True, 
        blank=True, 
        db_index=True,
        help_text="UUID of the linked ExternalData object in knowbase",
        verbose_name="External Source ID"
    )
    
    # Track content hash for change detection
    _external_content_hash = models.CharField(
        max_length=64,
        blank=True,
        help_text="SHA256 hash of content for change detection",
        verbose_name="Content Hash"
    )
    
    class Meta:
        abstract = True
    
    def __init_subclass__(cls, **kwargs):
        """Register signal handlers for each subclass."""
        super().__init_subclass__(**kwargs)
        
        # Register signals for this specific model class
        post_save.connect(
            cls._external_data_post_save_handler,
            sender=cls,
            dispatch_uid=f"external_data_mixin_{cls.__name__}"
        )
        
        post_delete.connect(
            cls._external_data_post_delete_handler,
            sender=cls,
            dispatch_uid=f"external_data_mixin_delete_{cls.__name__}"
        )
    
    @classmethod
    def _external_data_post_save_handler(cls, sender, instance, created, **kwargs):
        """Handle post_save signal for ExternalData integration."""
        try:
            meta_config = cls._get_external_data_meta()
            if not meta_config or not meta_config.get('auto_sync', True):
                return
            
            # Check if we should process this save (only if watched fields changed)
            if not created and not cls._should_update_external_data(instance, kwargs):
                logger.debug(f"📊 No relevant field changes for {cls.__name__}: {instance}")
                return
            
            # Check if content changed
            current_content = cls._get_content_for_instance(instance)
            current_hash = cls._calculate_content_hash(current_content)
            
            if created:
                # New instance - create ExternalData
                logger.info(f"🔗 Creating ExternalData for new {cls.__name__}: {instance}")
                instance._external_content_hash = current_hash
                instance.save(update_fields=['_external_content_hash'])
                cls._create_external_data(instance)
                
            elif instance._external_content_hash != current_hash:
                # Content changed - update ExternalData
                logger.info(f"🔮 Content changed for {cls.__name__}: {instance}, updating ExternalData")
                instance._external_content_hash = current_hash
                instance.save(update_fields=['_external_content_hash'])
                
                if instance.external_source_id:
                    cls._update_external_data(instance)
                else:
                    cls._create_external_data(instance)
            else:
                logger.debug(f"📊 No content changes for {cls.__name__}: {instance}")
                
        except Exception as e:
            logger.error(f"❌ Error in ExternalData post_save handler for {cls.__name__}: {e}")
    
    @classmethod
    def _external_data_post_delete_handler(cls, sender, instance, **kwargs):
        """Handle post_delete signal for ExternalData cleanup."""
        try:
            if instance.external_source_id:
                logger.info(f"🗑️ Cleaning up ExternalData for deleted {cls.__name__}: {instance}")
                ExternalData.objects.filter(id=instance.external_source_id).delete()
        except Exception as e:
            logger.error(f"❌ Error cleaning up ExternalData for {cls.__name__}: {e}")
    
    @classmethod
    def _get_external_data_meta(cls) -> Dict[str, Any]:
        """Get ExternalDataMeta configuration from the model or auto-generate smart defaults."""
        config = {}
        
        # If ExternalDataMeta exists, use it
        if hasattr(cls, 'ExternalDataMeta'):
            meta_class = cls.ExternalDataMeta
            # Extract configuration from ExternalDataMeta
            for attr in dir(meta_class):
                if not attr.startswith('_'):
                    value = getattr(meta_class, attr)
                    if not callable(value):  # Only properties, not methods
                        config[attr] = value
        
        # Smart defaults based on model analysis
        if 'watch_fields' not in config:
            config['watch_fields'] = cls._auto_detect_watch_fields()
        
        if 'similarity_threshold' not in config:
            config['similarity_threshold'] = 0.5  # Balanced default
        
        if 'source_type' not in config:
            from ..models.external_data import ExternalDataType
            config['source_type'] = ExternalDataType.MODEL  # Smart default
        
        if 'auto_sync' not in config:
            config['auto_sync'] = True  # Enable by default
        
        if 'is_public' not in config:
            config['is_public'] = False  # Private by default for security
        
        return config
    
    @classmethod
    def _should_update_external_data(cls, instance, save_kwargs) -> bool:
        """Check if we should update ExternalData based on changed fields."""
        meta_config = cls._get_external_data_meta()
        if not meta_config:
            return True  # No config = update always
        
        watch_fields = meta_config.get('watch_fields', [])
        if not watch_fields:
            return True  # No watch fields = update always
        
        # Check if update_fields was used in save()
        update_fields = save_kwargs.get('update_fields')
        if update_fields is not None:
            # Only update if any watched field was updated
            return any(field in update_fields for field in watch_fields)
        
        # If no update_fields specified, assume all fields might have changed
        return True
    
    @classmethod
    def _get_content_for_instance(cls, instance) -> str:
        """Get content string for the instance."""
        if hasattr(instance, 'get_external_content'):
            try:
                return str(instance.get_external_content())
            except Exception as e:
                logger.warning(f"Error calling get_external_content on {cls.__name__}: {e}")
        
        # Smart auto-generation based on model fields
        return cls._auto_generate_content(instance)
    
    @classmethod
    def _get_title_for_instance(cls, instance) -> str:
        """Get title for the instance."""
        if hasattr(instance, 'get_external_title'):
            try:
                return str(instance.get_external_title())
            except Exception as e:
                logger.warning(f"Error calling get_external_title on {cls.__name__}: {e}")
        
        # Smart auto-generation based on model fields
        return cls._auto_generate_title(instance)
    
    @classmethod
    def _get_description_for_instance(cls, instance) -> str:
        """Get description for the instance."""
        if hasattr(instance, 'get_external_description'):
            try:
                return str(instance.get_external_description())
            except Exception as e:
                logger.warning(f"Error calling get_external_description on {cls.__name__}: {e}")
        
        # Smart auto-generation based on model fields
        return cls._auto_generate_description(instance)
    
    @classmethod
    def _get_tags_for_instance(cls, instance) -> List[str]:
        """Get tags for the instance."""
        if hasattr(instance, 'get_external_tags'):
            try:
                tags = instance.get_external_tags()
                if isinstance(tags, (list, tuple)):
                    return list(tags)
                return [str(tags)]
            except Exception as e:
                logger.warning(f"Error calling get_external_tags on {cls.__name__}: {e}")
        
        # Smart auto-generation based on model fields
        return cls._auto_generate_tags(instance)
    
    @classmethod
    def _calculate_content_hash(cls, content: str) -> str:
        """Calculate SHA256 hash of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    @classmethod
    def _create_external_data(cls, instance):
        """Create ExternalData for the instance."""
        try:
            meta_config = cls._get_external_data_meta()
            if not meta_config:
                logger.warning(f"No ExternalDataMeta found for {cls.__name__}")
                return
            
            # Get user (try to find from instance or use superuser)
            user = cls._get_user_for_instance(instance)
            
            # Build ExternalDataConfig
            external_config = ExternalDataConfig(
                title=cls._get_title_for_instance(instance),
                description=cls._get_description_for_instance(instance),
                source_type=meta_config.get('source_type', ExternalDataType.MODEL),
                source_identifier=f"{cls._meta.label_lower}_{instance.pk}",
                content=cls._get_content_for_instance(instance),
                similarity_threshold=meta_config.get('similarity_threshold', 0.5),
                is_active=True,
                is_public=meta_config.get('is_public', False),
                metadata=cls._build_metadata(instance, meta_config),
                tags=cls._get_tags_for_instance(instance),
                source_config={
                    'model': cls._meta.label_lower,
                    'pk': str(instance.pk),
                    'auto_sync': meta_config.get('auto_sync', True),
                    'watch_fields': meta_config.get('watch_fields', []),
                }
            )
            
            # Create ExternalData
            creator = ExternalDataCreator(user)
            result = creator.create_from_config(external_config)
            
            if result['success']:
                external_data = result['external_data']
                instance.external_source_id = external_data.id
                instance.save(update_fields=['external_source_id'])
                logger.info(f"✅ Created ExternalData {external_data.id} for {cls.__name__}: {instance}")
            else:
                logger.error(f"❌ Failed to create ExternalData for {cls.__name__}: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"❌ Error creating ExternalData for {cls.__name__}: {e}")
    
    @classmethod
    def _update_external_data(cls, instance):
        """Update existing ExternalData for the instance."""
        try:
            if not instance.external_source_id:
                return
            
            external_data = ExternalData.objects.get(id=instance.external_source_id)
            meta_config = cls._get_external_data_meta() or {}
            
            # Update fields using the same methods as creation
            external_data.title = cls._get_title_for_instance(instance)
            external_data.description = cls._get_description_for_instance(instance)
            external_data.content = cls._get_content_for_instance(instance)
            external_data.metadata = cls._build_metadata(instance, meta_config)
            external_data.tags = cls._get_tags_for_instance(instance)
            external_data.similarity_threshold = meta_config.get('similarity_threshold', 0.5)
            external_data.status = ExternalDataStatus.PENDING  # Mark for reprocessing
            
            external_data.save()
            logger.info(f"✅ Updated ExternalData {external_data.id} for {cls.__name__}: {instance}")
            
        except ExternalData.DoesNotExist:
            logger.warning(f"ExternalData {instance.external_source_id} not found, creating new one")
            cls._create_external_data(instance)
        except Exception as e:
            logger.error(f"❌ Error updating ExternalData for {cls.__name__}: {e}")
    
    @classmethod
    def _build_metadata(cls, instance, config: Dict[str, Any]) -> Dict[str, Any]:
        """Build metadata dictionary for ExternalData."""
        metadata = {
            'model': cls._meta.label_lower,
            'model_name': cls.__name__,
            'pk': str(instance.pk),
            'app_label': cls._meta.app_label,
            'created_at': getattr(instance, 'created_at', None),
            'updated_at': getattr(instance, 'updated_at', None),
        }
        
        # Add custom metadata if method exists
        if hasattr(instance, 'get_external_metadata'):
            try:
                custom_metadata = instance.get_external_metadata()
                if isinstance(custom_metadata, dict):
                    metadata.update(custom_metadata)
            except Exception as e:
                logger.warning(f"Error calling get_external_metadata on {cls.__name__}: {e}")
        
        # Convert datetime objects to strings
        for key, value in metadata.items():
            if hasattr(value, 'isoformat'):
                metadata[key] = value.isoformat()
        
        return metadata
    
    @classmethod
    def _get_user_for_instance(cls, instance):
        """Get user for ExternalData ownership."""
        # Try to get user from instance
        if hasattr(instance, 'user'):
            return instance.user
        if hasattr(instance, 'created_by'):
            return instance.created_by
        if hasattr(instance, 'owner'):
            return instance.owner
        
        # Fallback to superuser
        from django.contrib.auth import get_user_model
        User = get_user_model()
        superuser = User.objects.filter(is_superuser=True).first()
        if superuser:
            return superuser
        
        raise ValueError("No user found for ExternalData ownership")
    
    def regenerate_external_data(self):
        """Manually regenerate ExternalData for this instance."""
        if self.external_source_id:
            self._update_external_data(self)
        else:
            self._create_external_data(self)
    
    def create_external_data(self, user=None):
        """Create ExternalData for this instance if it doesn't exist."""
        if self.external_source_id:
            return {
                'success': False,
                'error': f'External data already exists: {self.external_source_id}',
                'external_data': None
            }
        
        try:
            self._create_external_data(self)
            if self.external_source_id:
                return {
                    'success': True,
                    'message': f'External data created for {self}',
                    'external_data': self.external_source_id
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to create external data for {self}',
                    'external_data': None
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Error creating external data: {str(e)}',
                'external_data': None
            }
    
    def delete_external_data(self):
        """Manually delete ExternalData for this instance."""
        if self.external_source_id:
            try:
                ExternalData.objects.filter(id=self.external_source_id).delete()
                self.external_source_id = None
                self.save(update_fields=['external_source_id'])
                logger.info(f"🗑️ Deleted ExternalData for {self.__class__.__name__}: {self}")
            except Exception as e:
                logger.error(f"❌ Error deleting ExternalData: {e}")
    
    @property
    def has_external_data(self) -> bool:
        """Check if this instance has linked ExternalData."""
        return bool(self.external_source_id)
    
    @property
    def external_data_status(self) -> Optional[str]:
        """Get status of linked ExternalData."""
        if not self.external_source_id:
            return None
        
        try:
            external_data = ExternalData.objects.get(id=self.external_source_id)
            return external_data.status
        except ExternalData.DoesNotExist:
            return None
    
    # ==========================================
    # SMART AUTO-GENERATION METHODS
    # ==========================================
    
    @classmethod
    def _auto_generate_title(cls, instance) -> str:
        """Auto-generate title based on model fields."""
        # Try common title fields first
        title_fields = ['title', 'name', 'full_name', 'display_name', 'label']
        
        for field_name in title_fields:
            if hasattr(instance, field_name):
                value = getattr(instance, field_name, None)
                if value and str(value).strip():
                    # Add model context for clarity
                    model_name = cls._meta.verbose_name or cls.__name__
                    return f"{model_name}: {value}"
        
        # Fallback: use string representation with model name
        model_name = cls._meta.verbose_name or cls.__name__
        return f"{model_name}: {instance}"
    
    @classmethod
    def _auto_generate_description(cls, instance) -> str:
        """Auto-generate description based on model fields."""
        model_name = cls._meta.verbose_name or cls.__name__
        
        # Try common description fields
        desc_fields = ['description', 'summary', 'about', 'details', 'info']
        for field_name in desc_fields:
            if hasattr(instance, field_name):
                value = getattr(instance, field_name, None)
                if value and str(value).strip():
                    return f"{model_name} information: {value}"
        
        # Build description from key fields
        key_info = []
        
        # Add primary identifier
        if hasattr(instance, 'name') and instance.name:
            key_info.append(f"Name: {instance.name}")
        elif hasattr(instance, 'title') and instance.title:
            key_info.append(f"Title: {instance.title}")
        
        # Add status if available
        if hasattr(instance, 'is_active'):
            status = "Active" if instance.is_active else "Inactive"
            key_info.append(f"Status: {status}")
        
        # Add creation date if available
        if hasattr(instance, 'created_at') and instance.created_at:
            key_info.append(f"Created: {instance.created_at.strftime('%Y-%m-%d')}")
        
        if key_info:
            return f"Comprehensive information about this {model_name.lower()}. {', '.join(key_info)}."
        
        return f"Auto-generated information from {model_name} model."
    
    @classmethod
    def _auto_generate_tags(cls, instance) -> List[str]:
        """Auto-generate tags based on model fields and metadata."""
        tags = []
        
        # Add model-based tags
        tags.append(cls.__name__.lower())
        if cls._meta.verbose_name:
            tags.append(cls._meta.verbose_name.lower().replace(' ', '_'))
        
        # Add app label
        tags.append(cls._meta.app_label)
        
        # Add field-based tags
        tag_fields = ['category', 'type', 'kind', 'status', 'brand', 'model']
        for field_name in tag_fields:
            if hasattr(instance, field_name):
                value = getattr(instance, field_name, None)
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
            if hasattr(instance, field_name):
                value = getattr(instance, field_name, None)
                if value is True:
                    tags.append(field_name.replace('is_', ''))
        
        # Clean and deduplicate tags
        clean_tags = []
        for tag in tags:
            clean_tag = str(tag).lower().strip().replace(' ', '_')
            if clean_tag and clean_tag not in clean_tags:
                clean_tags.append(clean_tag)
        
        return clean_tags[:10]  # Limit to 10 tags
    
    @classmethod
    def _auto_generate_content(cls, instance) -> str:
        """Auto-generate comprehensive content based on model fields."""
        content_parts = []
        
        # Header with title
        title = cls._auto_generate_title(instance)
        content_parts.append(f"# {title}")
        content_parts.append("")
        
        # Basic Information section
        content_parts.append("## Basic Information")
        
        # Add key fields
        key_fields = cls._get_content_fields(instance)
        for field_name, field_value, field_label in key_fields:
            if field_value is not None and str(field_value).strip():
                content_parts.append(f"- **{field_label}**: {field_value}")
        
        content_parts.append("")
        
        # Add relationships section if any
        relationships = cls._get_relationship_info(instance)
        if relationships:
            content_parts.append("## Related Information")
            for rel_name, rel_info in relationships.items():
                content_parts.append(f"- **{rel_name}**: {rel_info}")
            content_parts.append("")
        
        # Add statistics if available
        stats = cls._get_statistics_info(instance)
        if stats:
            content_parts.append("## Statistics")
            for stat_name, stat_value in stats.items():
                content_parts.append(f"- **{stat_name}**: {stat_value}")
            content_parts.append("")
        
        # Add metadata section
        content_parts.append("## Technical Information")
        content_parts.append(f"This data is automatically synchronized from the {cls.__name__} model using ExternalDataMixin.")
        content_parts.append(f"")
        content_parts.append(f"**Model**: {cls._meta.label}")
        content_parts.append(f"**ID**: {instance.pk}")
        if hasattr(instance, 'created_at') and instance.created_at:
            content_parts.append(f"**Created**: {instance.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        if hasattr(instance, 'updated_at') and instance.updated_at:
            content_parts.append(f"**Updated**: {instance.updated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(content_parts)
    
    @classmethod
    def _get_content_fields(cls, instance) -> List[tuple]:
        """Get fields to include in content generation."""
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
            if hasattr(instance, field_name):
                value = getattr(instance, field_name, None)
                if value is not None:
                    # Format boolean fields
                    if isinstance(value, bool):
                        value = "Yes" if value else "No"
                    # Format choice fields
                    elif hasattr(instance, f'get_{field_name}_display'):
                        display_value = getattr(instance, f'get_{field_name}_display')()
                        if display_value:
                            value = display_value
                    # Format foreign key relationships
                    elif hasattr(value, '__str__'):
                        value = str(value)
                    
                    fields_info.append((field_name, value, field_label))
        
        return fields_info
    
    @classmethod
    def _get_relationship_info(cls, instance) -> Dict[str, str]:
        """Get relationship information for content."""
        relationships = {}
        
        # Common relationship field names
        rel_fields = ['brand', 'category', 'parent', 'owner', 'user', 'created_by']
        
        for field_name in rel_fields:
            if hasattr(instance, field_name):
                value = getattr(instance, field_name, None)
                if value:
                    relationships[field_name.replace('_', ' ').title()] = str(value)
        
        return relationships
    
    @classmethod
    def _get_statistics_info(cls, instance) -> Dict[str, Any]:
        """Get statistics information for content."""
        stats = {}
        
        # Common statistics field names
        stat_fields = ['total_vehicles', 'total_models', 'total_items', 'count', 'views', 'likes']
        
        for field_name in stat_fields:
            if hasattr(instance, field_name):
                value = getattr(instance, field_name, None)
                if value is not None and (isinstance(value, (int, float)) and value > 0):
                    label = field_name.replace('_', ' ').title()
                    if isinstance(value, float):
                        stats[label] = f"{value:,.2f}"
                    else:
                        stats[label] = f"{value:,}"
        
        return stats
    
    @classmethod
    def _auto_detect_watch_fields(cls) -> List[str]:
        """Auto-detect important fields to watch for changes."""
        watch_fields = []
        
        # Get all model fields
        for field in cls._meta.get_fields():
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
                if hasattr(field, 'remote_field') and field.remote_field and hasattr(field.remote_field, 'related_name'):
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
            for field in cls._meta.get_fields():
                if hasattr(field, 'name') and not field.name.startswith('_') and field.name not in {'id', 'pk'}:
                    watch_fields.append(field.name)
        
        return watch_fields[:10]  # Limit to prevent too many triggers
    
    # ==========================================
    # MANAGER-LEVEL METHODS (CLASS METHODS)
    # ==========================================
    
    @classmethod
    def with_external_data(cls):
        """Return queryset of instances that have external data."""
        return cls.objects.filter(external_source_id__isnull=False)
    
    @classmethod
    def without_external_data(cls):
        """Return queryset of instances that don't have external data."""
        return cls.objects.filter(external_source_id__isnull=True)
    
    @classmethod
    def sync_all_external_data(cls, limit=None):
        """Sync external data for all instances that have it."""
        instances_with_data = cls.with_external_data()
        
        if limit:
            instances_with_data = instances_with_data[:limit]
        
        results = {
            'total_processed': 0,
            'successful_updates': 0,
            'failed_updates': 0,
            'errors': []
        }
        
        for instance in instances_with_data:
            try:
                instance.regenerate_external_data()
                results['successful_updates'] += 1
                results['total_processed'] += 1
            except Exception as e:
                results['failed_updates'] += 1
                results['errors'].append(f"{instance}: {str(e)}")
        
        return results
    
    @classmethod
    def create_external_data_for_all(cls, limit=None):
        """Create external data for all instances that don't have it."""
        instances_without_data = cls.without_external_data()
        
        if limit:
            instances_without_data = instances_without_data[:limit]
        
        results = {
            'total_processed': 0,
            'successful_creates': 0,
            'failed_creates': 0,
            'errors': []
        }
        
        for instance in instances_without_data:
            try:
                result = instance.create_external_data()
                if result['success']:
                    results['successful_creates'] += 1
                else:
                    results['failed_creates'] += 1
                    results['errors'].append(f"{instance}: {result['error']}")
                results['total_processed'] += 1
            except Exception as e:
                results['failed_creates'] += 1
                results['errors'].append(f"{instance}: {str(e)}")
        
        return results
