"""
PydanticAdminMixin - Core mixin providing Pydantic config processing.

This is the main orchestrator that coordinates all the decomposed modules.
"""

import logging
from typing import Any

from ...config import AdminConfig
from ...utils import HtmlBuilder
from .display_methods import (
    apply_replacements_to_fieldsets,
    create_imagefield_display_methods,
    create_jsonfield_display_methods,
    create_markdownfield_display_methods,
    highlight_json,
)
from .list_display import build_list_display, build_list_display_links
from .actions import register_actions
from .import_export import generate_resource_class
from .views import ViewMixin

logger = logging.getLogger(__name__)


class PydanticAdminMixin(ViewMixin):
    """
    Mixin providing Pydantic config processing for ModelAdmin.

    Use this with your preferred ModelAdmin base class.

    Inherits from ViewMixin which provides:
    - changelist_view, changeform_view overrides
    - get_fieldsets, get_queryset overrides
    - formfield_for_dbfield override
    """

    config: AdminConfig
    _config_processed = False

    @property
    def html(self):
        """Universal HTML builder for display methods."""
        return HtmlBuilder

    @staticmethod
    def _highlight_json(json_obj: Any) -> str:
        """
        Apply syntax highlighting to JSON using Pygments (Unfold style).

        Returns HTML with Pygments syntax highlighting for light and dark themes.
        """
        return highlight_json(json_obj)

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
        cls.list_display = build_list_display(cls, config)
        cls.list_filter = config.list_filter
        cls.search_fields = config.search_fields
        cls.ordering = config.ordering if config.ordering else []

        # Auto-create display methods for readonly JSONField fields
        # This modifies readonly_fields to use custom display methods and returns mapping
        cls.readonly_fields, jsonfield_replacements = create_jsonfield_display_methods(cls, config)

        # Auto-create display methods for readonly ImageField/FileField fields
        cls.readonly_fields, imagefield_replacements, has_image_preview = create_imagefield_display_methods(
            cls, cls.readonly_fields, config
        )
        cls._has_image_preview = has_image_preview

        # Auto-create display methods for MarkdownField configs
        cls.readonly_fields, markdownfield_replacements = create_markdownfield_display_methods(
            cls, cls.readonly_fields, config
        )

        # List display options
        # Rename list_display_links to match display method names (field -> field_display)
        if config.list_display_links:
            cls.list_display_links = build_list_display_links(config)
        else:
            cls.list_display_links = getattr(cls, 'list_display_links', None)

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

        # Combine field replacements for fieldsets
        fieldset_replacements = {
            **jsonfield_replacements,
            **imagefield_replacements,
            **markdownfield_replacements,
        }

        # Fieldsets - apply field replacements
        if config.fieldsets:
            cls.fieldsets = config.to_django_fieldsets()
            # Apply replacements to fieldsets
            if fieldset_replacements:
                cls.fieldsets = apply_replacements_to_fieldsets(cls.fieldsets, fieldset_replacements)
        # Also convert fieldsets if they're defined directly in the class as FieldsetConfig objects
        elif hasattr(cls, 'fieldsets') and isinstance(cls.fieldsets, list):
            from ...config import FieldsetConfig
            if cls.fieldsets and isinstance(cls.fieldsets[0], FieldsetConfig):
                cls.fieldsets = tuple(fs.to_django_fieldset() for fs in cls.fieldsets)
                # Apply replacements to fieldsets
                if fieldset_replacements:
                    cls.fieldsets = apply_replacements_to_fieldsets(cls.fieldsets, fieldset_replacements)

        # Collect widget configurations from AdminConfig.widgets for custom JSON widget configs
        cls._field_widget_configs = {}
        if config.widgets:
            for widget_config in config.widgets:
                if hasattr(widget_config, 'field') and hasattr(widget_config, 'to_widget_kwargs'):
                    field_name = widget_config.field
                    cls._field_widget_configs[field_name] = widget_config.to_widget_kwargs()
                    logger.debug(f"Registered widget config for field '{field_name}' from AdminConfig.widgets")
                else:
                    logger.warning(f"Invalid widget config in AdminConfig.widgets: {widget_config}")

        # Actions
        if config.actions:
            register_actions(cls, config)

        # Extra options
        if config.date_hierarchy:
            cls.date_hierarchy = config.date_hierarchy
        cls.save_on_top = config.save_on_top
        cls.save_as = config.save_as
        cls.preserve_filters = config.preserve_filters

        # Import/Export configuration
        if config.import_export_enabled:
            # Set import/export template
            cls.change_list_template = 'admin/import_export/change_list_import_export.html'

            if config.resource_class:
                # Use provided resource class
                cls.resource_class = config.resource_class
            else:
                # Auto-generate resource class
                cls.resource_class = generate_resource_class(config)

            # Override changelist_view to add import/export context
            original_changelist_view = cls.changelist_view

            def changelist_view_with_import_export(self, request, extra_context=None):
                if extra_context is None:
                    extra_context = {}
                extra_context['has_import_permission'] = self.has_import_permission(request)
                extra_context['has_export_permission'] = self.has_export_permission(request)
                return original_changelist_view(self, request, extra_context)

            cls.changelist_view = changelist_view_with_import_export

        # Documentation configuration
        if config.documentation:
            cls._setup_documentation(config)

        # Image preview modal (include once if image_preview widget is used)
        cls._setup_image_preview_modal(config)

    @classmethod
    def _setup_documentation(cls, config: AdminConfig):
        """
        Setup documentation using unfold's template hooks.

        Uses unfold's built-in hooks:
        - list_before_template: Shows documentation before changelist table
        - change_form_before_template: Shows documentation before fieldsets
        """
        doc_config = config.documentation

        # Set unfold template hooks
        if doc_config.show_on_changelist:
            cls.list_before_template = "django_admin/documentation_block.html"

        if doc_config.show_on_changeform:
            cls.change_form_before_template = "django_admin/documentation_block.html"

        # Store documentation config for access in views
        cls.documentation_config = doc_config

    @classmethod
    def _setup_image_preview_modal(cls, config: AdminConfig):
        """
        Setup global image preview modal if image_preview widget is used.

        Uses unfold's template hooks to include modal once per page:
        - list_after_template: for changelist page
        - change_form_after_template: for change form page
        """
        # Check if any display_fields use image_preview widget
        has_image_preview = getattr(cls, '_has_image_preview', False)

        if not has_image_preview and config.display_fields:
            for field_config in config.display_fields:
                if hasattr(field_config, 'ui_widget') and field_config.ui_widget == 'image_preview':
                    has_image_preview = True
                    break

        if has_image_preview:
            cls.list_after_template = "django_admin/widgets/image_preview_modal.html"
            cls.change_form_after_template = "django_admin/widgets/image_preview_modal.html"

    # Legacy method aliases for backward compatibility
    @classmethod
    def _create_jsonfield_display_methods(cls, config: AdminConfig):
        """Legacy alias for backward compatibility."""
        return create_jsonfield_display_methods(cls, config)

    @classmethod
    def _create_imagefield_display_methods(cls, readonly_fields: list, config: AdminConfig):
        """Legacy alias for backward compatibility."""
        return create_imagefield_display_methods(cls, readonly_fields, config)

    @classmethod
    def _create_markdownfield_display_methods(cls, readonly_fields: list, config: AdminConfig):
        """Legacy alias for backward compatibility."""
        return create_markdownfield_display_methods(cls, readonly_fields, config)

    @classmethod
    def _apply_jsonfield_replacements_to_fieldsets(cls, fieldsets, replacements):
        """Legacy alias for backward compatibility."""
        return apply_replacements_to_fieldsets(fieldsets, replacements)

    @classmethod
    def _generate_resource_class(cls, config: AdminConfig):
        """Legacy alias for backward compatibility."""
        return generate_resource_class(config)

    @classmethod
    def _build_list_display(cls, config: AdminConfig):
        """Legacy alias for backward compatibility."""
        return build_list_display(cls, config)

    @classmethod
    def _build_list_display_links(cls, config: AdminConfig):
        """Legacy alias for backward compatibility."""
        return build_list_display_links(config)

    @classmethod
    def _register_actions(cls, config: AdminConfig):
        """Legacy alias for backward compatibility."""
        return register_actions(cls, config)
