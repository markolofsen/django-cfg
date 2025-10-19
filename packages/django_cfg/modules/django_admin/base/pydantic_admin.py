"""
PydanticAdmin - Declarative admin base class.
"""

import logging
from typing import Any, List, Optional

from django.utils.safestring import mark_safe
from unfold.decorators import action as unfold_action

from ..config import AdminConfig
from ..utils import HtmlBuilder
from ..widgets import WidgetRegistry

logger = logging.getLogger(__name__)


def _get_base_admin_class():
    """
    Get the base admin class with Unfold + Import/Export functionality.

    Since unfold and import_export are always available in django-cfg,
    we always return a combined class that inherits from both.

    MRO (Method Resolution Order):
        UnfoldImportExportModelAdmin
          └─ ImportExportModelAdmin  # Import/Export functionality
          └─ UnfoldModelAdmin        # Unfold UI
               └─ Django ModelAdmin

    This ensures both Unfold UI and Import/Export work together seamlessly.
    """
    from import_export.admin import ImportExportModelAdmin
    from unfold.admin import ModelAdmin as UnfoldModelAdmin

    class UnfoldImportExportModelAdmin(ImportExportModelAdmin, UnfoldModelAdmin):
        """Combined Unfold + Import/Export admin base class."""
        pass

    return UnfoldImportExportModelAdmin


class PydanticAdminMixin:
    """
    Mixin providing Pydantic config processing for ModelAdmin.

    Use this with your preferred ModelAdmin base class.
    """

    config: AdminConfig
    _config_processed = False

    @property
    def html(self):
        """Universal HTML builder for display methods."""
        return HtmlBuilder

    def __init__(self, *args, **kwargs):
        """Process config on first instantiation."""
        # Process config once when first admin instance is created
        if hasattr(self.__class__, '_config_needs_processing') and self.__class__._config_needs_processing:
            self.__class__._build_from_config()
            self.__class__._config_needs_processing = False
            self.__class__._config_processed = True

        super().__init__(*args, **kwargs)

    def __init_subclass__(cls, **kwargs):
        """Mark class as needing config processing, but defer actual processing."""
        super().__init_subclass__(**kwargs)

        if hasattr(cls, 'config') and isinstance(cls.config, AdminConfig):
            cls._config_needs_processing = True

    @classmethod
    def _build_from_config(cls):
        """Convert AdminConfig to ModelAdmin attributes."""
        config = cls.config

        # Basic list display
        cls.list_display = cls._build_list_display(config)
        cls.list_filter = config.list_filter
        cls.search_fields = config.search_fields
        cls.ordering = config.ordering if config.ordering else []
        cls.readonly_fields = config.readonly_fields

        # List display options
        cls.list_display_links = config.list_display_links or getattr(cls, 'list_display_links', None)

        # Pagination
        cls.list_per_page = config.list_per_page
        cls.list_max_show_all = config.list_max_show_all

        # Form options
        cls.autocomplete_fields = config.autocomplete_fields or getattr(cls, 'autocomplete_fields', [])
        cls.raw_id_fields = config.raw_id_fields or getattr(cls, 'raw_id_fields', [])
        cls.prepopulated_fields = config.prepopulated_fields or getattr(cls, 'prepopulated_fields', {})
        cls.formfield_overrides = config.formfield_overrides or getattr(cls, 'formfield_overrides', {})

        # Inlines
        cls.inlines = config.inlines or getattr(cls, 'inlines', [])

        # Fieldsets
        if config.fieldsets:
            cls.fieldsets = config.to_django_fieldsets()

        # Also convert fieldsets if they're defined directly in the class as FieldsetConfig objects
        elif hasattr(cls, 'fieldsets') and isinstance(cls.fieldsets, list):
            from ..config import FieldsetConfig
            if cls.fieldsets and isinstance(cls.fieldsets[0], FieldsetConfig):
                cls.fieldsets = tuple(fs.to_django_fieldset() for fs in cls.fieldsets)

        # Actions
        if config.actions:
            cls._register_actions(config)

        # Extra options
        if config.date_hierarchy:
            cls.date_hierarchy = config.date_hierarchy
        cls.save_on_top = config.save_on_top
        cls.save_as = config.save_as
        cls.preserve_filters = config.preserve_filters

        # Import/Export configuration
        if config.import_export_enabled and config.resource_class:
            cls.resource_class = config.resource_class

    @classmethod
    def _build_list_display(cls, config: AdminConfig) -> List[str]:
        """Build list_display with generated display methods."""
        result = []

        for field_name in config.list_display:
            # Check if we have a FieldConfig for this field
            field_config = config.get_display_field_config(field_name)

            if field_config and field_config.ui_widget:
                # Generate display method for this field
                method_name = f"{field_name}_display"
                display_method = cls._generate_display_method(field_config)
                setattr(cls, method_name, display_method)
                result.append(method_name)
            else:
                # Use field as-is
                result.append(field_name)

        return result

    @classmethod
    def _generate_display_method(cls, field_config):
        """Generate display method from FieldConfig."""

        def display_method(self, obj):
            # Get field value
            value = getattr(obj, field_config.name, None)

            if value is None:
                empty = field_config.empty_value
                # For header fields, return tuple format
                if field_config.header:
                    return (empty, [])
                return empty

            # Render using widget
            if field_config.ui_widget:
                widget_config = field_config.get_widget_config()
                rendered = WidgetRegistry.render(
                    field_config.ui_widget,
                    obj,
                    field_config.name,
                    widget_config
                )

                # Widget returns the result - could be string, list, or tuple
                # For header widgets (user_avatar), they return list format directly
                # For other widgets, wrap in safe string
                if rendered is None:
                    rendered = field_config.empty_value

                # If it's already a list or tuple (e.g., from user_avatar widget), return as-is
                if isinstance(rendered, (list, tuple)):
                    return rendered

                # Otherwise mark as safe and return
                result = mark_safe(rendered)

                # For non-list header fields, wrap in tuple format
                if field_config.header:
                    return (result, [])
                return result

            # Fallback to simple value
            if field_config.header:
                return (value, [])
            return value

        # Set display method attributes
        display_method.short_description = field_config.title or field_config.name.replace('_', ' ').title()

        if field_config.ordering:
            display_method.admin_order_field = field_config.ordering

        # Check if field has boolean attribute (only for BooleanField or base FieldConfig)
        if hasattr(field_config, 'boolean') and field_config.boolean:
            display_method.boolean = True

        if field_config.header:
            # For header display (user with avatar)
            display_method.header = True

        return display_method

    @classmethod
    def _register_actions(cls, config: AdminConfig):
        """Register actions from ActionConfig with Unfold decorator support."""
        action_functions = []

        for action_config in config.actions:
            # Get handler function
            handler = action_config.get_handler_function()

            # Build decorator kwargs
            decorator_kwargs = {
                'description': action_config.description,
            }

            # Add variant if specified
            if action_config.variant and action_config.variant != 'default':
                decorator_kwargs['attrs'] = decorator_kwargs.get('attrs', {})
                decorator_kwargs['attrs']['class'] = f'button-{action_config.variant}'

            # Add icon if specified
            if action_config.icon:
                decorator_kwargs['attrs'] = decorator_kwargs.get('attrs', {})
                decorator_kwargs['attrs']['data-icon'] = action_config.icon

            # Add confirmation if enabled
            if action_config.confirmation:
                decorator_kwargs['attrs'] = decorator_kwargs.get('attrs', {})
                decorator_kwargs['attrs']['data-confirm'] = 'Are you sure you want to perform this action?'

            # Add permissions if specified
            if action_config.permissions:
                decorator_kwargs['permissions'] = action_config.permissions

            # Apply Unfold decorator
            decorated_handler = unfold_action(**decorator_kwargs)(handler)

            # Store for later registration
            action_name = action_config.name
            setattr(cls, action_name, decorated_handler)
            action_functions.append(action_name)

        # Set actions list
        if hasattr(cls, 'actions') and cls.actions:
            cls.actions = list(cls.actions) + action_functions
        else:
            cls.actions = action_functions

    def get_queryset(self, request):
        """Apply select_related, prefetch_related, and annotations from config."""
        qs = super().get_queryset(request)

        # Auto-apply optimizations from config
        if self.config.select_related:
            qs = qs.select_related(*self.config.select_related)

        if self.config.prefetch_related:
            qs = qs.prefetch_related(*self.config.prefetch_related)

        # Auto-apply annotations from config
        if self.config.annotations:
            qs = qs.annotate(**self.config.annotations)

        return qs

    def get_fieldsets(self, request, obj=None):
        """
        Return fieldsets, filtering out non-editable fields from add form.

        For add form (obj=None), we exclude fields that are:
        - auto_now_add=True (created_at, etc)
        - auto_now=True (updated_at, etc)
        - auto-generated (id, uuid, etc)
        - methods (not actual model fields)

        For change form (obj exists), we show all fieldsets as-is.
        """
        fieldsets = super().get_fieldsets(request, obj)

        # For change form, return fieldsets as-is (readonly fields will be shown)
        if obj is not None:
            return fieldsets

        # For add form, filter out non-editable fields
        if not fieldsets:
            return fieldsets

        # Get all actual model field names
        model_field_names = set()
        for field in self.model._meta.get_fields():
            model_field_names.add(field.name)

        # Get non-editable field names
        non_editable_fields = set()
        for field in self.model._meta.get_fields():
            if hasattr(field, 'editable') and not field.editable:
                non_editable_fields.add(field.name)
            # Also check for auto_now and auto_now_add
            if hasattr(field, 'auto_now') and field.auto_now:
                non_editable_fields.add(field.name)
            if hasattr(field, 'auto_now_add') and field.auto_now_add:
                non_editable_fields.add(field.name)

        # Filter fieldsets
        filtered_fieldsets = []
        for name, options in fieldsets:
            if 'fields' in options:
                # Filter out non-editable fields and non-model fields from this fieldset
                filtered_fields = [
                    f for f in options['fields']
                    if f in model_field_names and f not in non_editable_fields
                ]

                # Only include fieldset if it has remaining fields
                if filtered_fields:
                    filtered_options = options.copy()
                    filtered_options['fields'] = tuple(filtered_fields)
                    filtered_fieldsets.append((name, filtered_options))
            else:
                # Keep fieldsets without 'fields' key as-is
                filtered_fieldsets.append((name, options))

        return tuple(filtered_fieldsets)


class PydanticAdmin(PydanticAdminMixin, _get_base_admin_class()):
    """
    Pydantic-driven admin base class with Unfold UI and Import/Export support.

    Inherits from UnfoldImportExportModelAdmin which combines:
    - ImportExportModelAdmin: Import/Export functionality
    - UnfoldModelAdmin: Modern Unfold UI
    - Django ModelAdmin: Base Django admin

    Both Unfold UI and Import/Export are always available.
    Enable import/export functionality via config:
        import_export_enabled=True
        resource_class=YourResourceClass

    Usage:
        from django_cfg.modules.django_admin import AdminConfig
        from django_cfg.modules.django_admin.base import PydanticAdmin

        # Simple admin (Unfold UI enabled by default)
        config = AdminConfig(
            model=MyModel,
            list_display=["name", "status"],
            ...
        )

        @admin.register(MyModel)
        class MyModelAdmin(PydanticAdmin):
            config = config

        # With Import/Export
        config = AdminConfig(
            model=MyModel,
            import_export_enabled=True,
            resource_class=MyModelResource,
            list_display=["name", "status"],
            ...
        )

        @admin.register(MyModel)
        class MyModelAdmin(PydanticAdmin):
            config = config
    """
    pass
