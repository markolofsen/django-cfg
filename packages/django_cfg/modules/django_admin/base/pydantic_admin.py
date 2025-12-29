"""
PydanticAdmin - Declarative admin base class.
"""

import logging
from pathlib import Path
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
          └─ UnfoldModelAdmin        # Unfold UI (first for template priority)
          └─ ImportExportMixin       # Import/Export functionality (django_cfg custom)
               └─ Django ModelAdmin

    This ensures both Unfold UI and Import/Export work together seamlessly.

    Uses django_cfg's custom ImportExportMixin which includes:
    - Custom templates for proper Unfold styling
    - Unfold forms (ImportForm, ExportForm)
    - Properly styled import/export buttons
    """
    # Use original ImportExportModelAdmin with Unfold
    from import_export.admin import ImportExportModelAdmin as BaseImportExportModelAdmin
    from unfold.admin import ModelAdmin as UnfoldModelAdmin

    class UnfoldImportExportModelAdmin(BaseImportExportModelAdmin, UnfoldModelAdmin):
        """Combined Import/Export + Unfold admin base class."""
        # Import/Export should come FIRST in MRO to get its get_urls() method
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

    @staticmethod
    def _highlight_json(json_obj: Any) -> str:
        """
        Apply syntax highlighting to JSON using Pygments (Unfold style).

        Returns HTML with Pygments syntax highlighting for light and dark themes.
        """
        try:
            from pygments import highlight
            from pygments.formatters import HtmlFormatter
            from pygments.lexers import JsonLexer
            import json
        except ImportError:
            # Fallback to plain JSON if Pygments not available
            import json
            import html as html_lib
            formatted_json = json.dumps(json_obj, indent=2, ensure_ascii=False)
            return html_lib.escape(formatted_json)

        def format_response(response: str, theme: str) -> str:
            formatter = HtmlFormatter(
                style=theme,
                noclasses=True,
                nobackground=True,
                prestyles="white-space: pre-wrap; word-wrap: break-word;",
            )
            return highlight(response, JsonLexer(), formatter)

        # Format JSON with ensure_ascii=False for proper Unicode
        response = json.dumps(json_obj, indent=2, ensure_ascii=False)

        # Return dual-theme HTML (light: colorful, dark: monokai)
        return (
            f'<div class="block dark:hidden">{format_response(response, "colorful")}</div>'
            f'<div class="hidden dark:block">{format_response(response, "monokai")}</div>'
        )

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

        # Auto-create display methods for readonly JSONField fields
        # This modifies readonly_fields to use custom display methods and returns mapping
        cls.readonly_fields, jsonfield_replacements = cls._create_jsonfield_display_methods(config)

        # Auto-create display methods for readonly ImageField/FileField fields
        cls.readonly_fields, imagefield_replacements, has_image_preview = cls._create_imagefield_display_methods(
            cls.readonly_fields, config
        )
        cls._has_image_preview = has_image_preview

        # List display options
        # Rename list_display_links to match display method names (field -> field_display)
        if config.list_display_links:
            cls.list_display_links = cls._build_list_display_links(config)
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

        # Combine all field replacements
        all_replacements = {**jsonfield_replacements, **imagefield_replacements}

        # Fieldsets - apply field replacements
        if config.fieldsets:
            cls.fieldsets = config.to_django_fieldsets()
            # Apply replacements to fieldsets
            if all_replacements:
                cls.fieldsets = cls._apply_jsonfield_replacements_to_fieldsets(cls.fieldsets, all_replacements)
        # Also convert fieldsets if they're defined directly in the class as FieldsetConfig objects
        elif hasattr(cls, 'fieldsets') and isinstance(cls.fieldsets, list):
            from ..config import FieldsetConfig
            if cls.fieldsets and isinstance(cls.fieldsets[0], FieldsetConfig):
                cls.fieldsets = tuple(fs.to_django_fieldset() for fs in cls.fieldsets)
                # Apply replacements to fieldsets
                if all_replacements:
                    cls.fieldsets = cls._apply_jsonfield_replacements_to_fieldsets(cls.fieldsets, all_replacements)

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
            cls._register_actions(config)

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
                cls.resource_class = cls._generate_resource_class(config)

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

    def _get_app_path(self) -> Optional[Path]:
        """
        Detect the app path for relative file resolution.

        Returns:
            Path to the app directory or None
        """
        if not self.model:
            return None

        try:
            # Get app label from model
            app_label = self.model._meta.app_label

            # Try to get app config
            from django.apps import apps
            app_config = apps.get_app_config(app_label)

            if app_config and hasattr(app_config, 'path'):
                return Path(app_config.path)
        except Exception as e:
            logger.warning(f"Could not detect app path for {self.model}: {e}")

        return None

    @classmethod
    def _create_jsonfield_display_methods(cls, config: AdminConfig):
        """
        Auto-create display methods for readonly JSONField fields.

        This ensures proper Unicode display (non-ASCII characters) for readonly JSON fields.
        Django's default display_for_field() uses json.dumps() with ensure_ascii=True,
        which escapes Unicode characters. We override this to use ensure_ascii=False.

        Returns:
            Tuple of (updated_readonly_fields, jsonfield_replacements_dict)
        """
        import json
        import html as html_lib
        from django.utils.safestring import mark_safe

        # Get model
        model = config.model
        if not model:
            return config.readonly_fields, {}

        # Track which fields should be replaced
        updated_readonly_fields = []
        jsonfield_replacements = {}

        # Find JSONField fields in readonly_fields
        for field_name in config.readonly_fields:
            try:
                # Get the model field
                field = model._meta.get_field(field_name)
                field_class_name = field.__class__.__name__

                # Check if it's a JSONField
                if field_class_name == 'JSONField':
                    # Create a custom display method for this field
                    def make_json_display_method(fname, field_obj):
                        def json_display_method(self, obj):
                            """Display JSONField with proper Unicode support."""
                            json_value = getattr(obj, fname, None)

                            if not json_value:
                                return "—"

                            try:
                                # Parse JSON if it's a string
                                if isinstance(json_value, str):
                                    json_obj = json.loads(json_value)
                                else:
                                    json_obj = json_value

                                # Syntax highlight JSON using Pygments (Unfold style)
                                highlighted_json = self._highlight_json(json_obj)

                                # Return formatted HTML (Pygments adds its own styling)
                                return mark_safe(highlighted_json)

                            except (json.JSONDecodeError, TypeError, ValueError):
                                return mark_safe(f"<code>Invalid JSON: {str(json_value)[:100]}</code>")

                        # Set method attributes for Django admin
                        json_display_method.short_description = field_obj.verbose_name or fname.replace('_', ' ').title()
                        return json_display_method

                    # Create method name
                    method_name = f'_auto_display_{field_name}'

                    # Add method to class
                    setattr(cls, method_name, make_json_display_method(field_name, field))
                    logger.debug(f"Created auto-display method '{method_name}' for JSONField '{field_name}'")

                    # Track replacement
                    jsonfield_replacements[field_name] = method_name
                    updated_readonly_fields.append(method_name)
                else:
                    # Not a JSONField, keep original
                    updated_readonly_fields.append(field_name)

            except Exception as e:
                # Field might not exist or be a property - keep original
                logger.debug(f"Skipped creating display method for '{field_name}': {e}")
                updated_readonly_fields.append(field_name)

        return updated_readonly_fields, jsonfield_replacements

    @classmethod
    def _create_imagefield_display_methods(cls, readonly_fields: list, config: AdminConfig):
        """
        Auto-create display methods for readonly ImageField/FileField fields.

        Uses ImagePreviewDisplay for image fields to show clickable thumbnails
        with modal preview.

        Returns:
            Tuple of (updated_readonly_fields, imagefield_replacements_dict, has_image_preview)
        """
        from django.utils.safestring import mark_safe
        from ..utils import ImagePreviewDisplay

        # Get model
        model = config.model
        if not model:
            return readonly_fields, {}, False

        # Track which fields should be replaced
        updated_readonly_fields = list(readonly_fields)
        imagefield_replacements = {}
        has_image_preview = False

        # Find ImageField/FileField fields in readonly_fields
        for field_name in readonly_fields:
            try:
                # Get the model field
                field = model._meta.get_field(field_name)
                field_class_name = field.__class__.__name__

                # Check if it's an ImageField or FileField
                if field_class_name in ('ImageField', 'FileField'):
                    # Create a custom display method for this field
                    def make_image_display_method(fname, field_obj):
                        def image_display_method(self, obj):
                            """Display ImageField with preview card."""
                            value = getattr(obj, fname, None)

                            if not value:
                                return "—"

                            # Get URL from field
                            if hasattr(value, 'url'):
                                image_url = value.url
                            else:
                                image_url = str(value)

                            if not image_url:
                                return "—"

                            # Check if it's actually an image
                            is_image = field_obj.__class__.__name__ == 'ImageField'
                            ext = image_url.lower().split('?')[0].split('.')[-1]
                            if not is_image:
                                # Check by file extension
                                is_image = ext in ('jpg', 'jpeg', 'png', 'gif', 'webp', 'svg', 'bmp', 'avif', 'ico')

                            if is_image:
                                # Try to get file info from model
                                file_size = None
                                dimensions = None

                                # Try common field names for file size
                                for size_field in ('file_size', 'size', f'{fname}_size'):
                                    size_val = getattr(obj, size_field, None)
                                    if size_val:
                                        # Format size
                                        if isinstance(size_val, (int, float)):
                                            if size_val >= 1024 * 1024:
                                                file_size = f"{size_val / (1024 * 1024):.1f} MB"
                                            elif size_val >= 1024:
                                                file_size = f"{size_val / 1024:.1f} KB"
                                            else:
                                                file_size = f"{size_val} B"
                                        else:
                                            file_size = str(size_val)
                                        break

                                # Try to get dimensions
                                width = getattr(obj, 'width', None) or getattr(obj, f'{fname}_width', None)
                                height = getattr(obj, 'height', None) or getattr(obj, f'{fname}_height', None)
                                if width and height:
                                    dimensions = f"{width}×{height}"

                                return mark_safe(ImagePreviewDisplay.render_card(
                                    image_url,
                                    config={
                                        'thumbnail_width': '120px',
                                        'thumbnail_height': '120px',
                                        'show_info': True,
                                        'zoom_enabled': True,
                                        'file_size': file_size,
                                        'dimensions': dimensions,
                                    }
                                ))
                            else:
                                # Not an image - show link
                                filename = image_url.split('/')[-1].split('?')[0]
                                return mark_safe(
                                    f'<a href="{image_url}" target="_blank" '
                                    f'class="inline-flex items-center gap-1 text-primary-600 dark:text-primary-400 hover:underline">'
                                    f'<span class="material-symbols-outlined text-sm">attachment</span>'
                                    f'{filename}</a>'
                                )

                        # Set method attributes for Django admin
                        image_display_method.short_description = field_obj.verbose_name or fname.replace('_', ' ').title()
                        return image_display_method

                    # Create method name
                    method_name = f'_auto_display_{field_name}'

                    # Add method to class
                    setattr(cls, method_name, make_image_display_method(field_name, field))
                    logger.debug(f"Created auto-display method '{method_name}' for ImageField '{field_name}'")

                    # Track replacement
                    imagefield_replacements[field_name] = method_name
                    has_image_preview = True

                    # Replace in updated list
                    try:
                        idx = updated_readonly_fields.index(field_name)
                        updated_readonly_fields[idx] = method_name
                    except ValueError:
                        pass

            except Exception as e:
                # Field might not exist or be a property - keep original
                logger.debug(f"Skipped creating image display method for '{field_name}': {e}")

        return updated_readonly_fields, imagefield_replacements, has_image_preview

    @classmethod
    def _apply_jsonfield_replacements_to_fieldsets(cls, fieldsets, replacements):
        """
        Apply JSONField replacements to fieldsets.

        Args:
            fieldsets: Django fieldsets tuple
            replacements: Dict mapping original field names to replacement method names

        Returns:
            Updated fieldsets tuple
        """
        if not replacements:
            return fieldsets

        updated_fieldsets = []
        for fieldset in fieldsets:
            title, options = fieldset
            fields = list(options.get('fields', []))

            # Replace field names in fields list
            updated_fields = []
            for field in fields:
                if isinstance(field, (list, tuple)):
                    # Handle multi-column fieldsets
                    updated_field = [replacements.get(f, f) for f in field]
                    updated_fields.append(tuple(updated_field))
                else:
                    # Single field
                    updated_fields.append(replacements.get(field, field))

            # Create updated options dict
            updated_options = options.copy()
            updated_options['fields'] = tuple(updated_fields)

            updated_fieldsets.append((title, updated_options))

        return tuple(updated_fieldsets)

    @classmethod
    def _generate_resource_class(cls, config: AdminConfig):
        """
        Auto-generate a ModelResource class for import/export.

        Uses ResourceConfig if provided, otherwise generates basic Resource.
        """
        from import_export import resources

        target_model = config.model
        resource_config = config.resource_config

        # Determine fields to include
        if resource_config and resource_config.fields:
            # Use explicitly specified fields
            model_fields = resource_config.fields
        else:
            # Auto-detect fields from model
            model_fields = []
            for field in target_model._meta.get_fields():
                # Skip relations and auto fields that shouldn't be imported
                if field.concrete and not field.many_to_many:
                    # Skip password fields for security
                    if 'password' not in field.name.lower():
                        model_fields.append(field.name)

        # Apply exclusions if specified
        if resource_config and resource_config.exclude:
            model_fields = [f for f in model_fields if f not in resource_config.exclude]

        # Build Meta attributes
        meta_attrs = {
            'model': target_model,
            'fields': tuple(model_fields),
        }

        # Add ResourceConfig settings
        if resource_config:
            meta_attrs['import_id_fields'] = resource_config.import_id_fields
            meta_attrs['skip_unchanged'] = resource_config.skip_unchanged
            meta_attrs['report_skipped'] = resource_config.report_skipped
            meta_attrs['use_transactions'] = resource_config.use_transactions

            if resource_config.export_order:
                meta_attrs['export_order'] = tuple(resource_config.export_order)
        else:
            # Default settings
            meta_attrs['import_id_fields'] = ['id'] if 'id' in model_fields else []
            meta_attrs['skip_unchanged'] = True
            meta_attrs['report_skipped'] = True

        # Create Meta class
        ResourceMeta = type('Meta', (), meta_attrs)

        # Build Resource class attributes (methods + Meta)
        resource_attrs = {'Meta': ResourceMeta}

        # Add hooks from ResourceConfig
        if resource_config:
            # before_import hook
            if resource_config.before_import:
                hook = resource_config.get_callable('before_import')
                if hook:
                    resource_attrs['before_import'] = hook

            # after_import hook
            if resource_config.after_import:
                hook = resource_config.get_callable('after_import')
                if hook:
                    resource_attrs['after_import'] = hook

            # before_import_row hook
            if resource_config.before_import_row:
                hook = resource_config.get_callable('before_import_row')
                if hook:
                    resource_attrs['before_import_row'] = hook

            # after_import_row hook
            if resource_config.after_import_row:
                hook = resource_config.get_callable('after_import_row')
                if hook:
                    resource_attrs['after_import_row'] = hook

        # Create Resource class
        AutoGeneratedResource = type(
            f'{target_model.__name__}Resource',
            (resources.ModelResource,),
            resource_attrs
        )

        return AutoGeneratedResource

    @classmethod
    def _build_list_display(cls, config: AdminConfig) -> List[str]:
        """Build list_display with generated display methods."""
        result = []
        # Get list_display_links for detecting link fields
        link_fields = config.list_display_links or []

        for field_name in config.list_display:
            # Check if we have a FieldConfig for this field
            field_config = config.get_display_field_config(field_name)

            if field_config and field_config.ui_widget:
                # Check if this field is a link field
                is_link = field_name in link_fields
                # Generate display method for this field
                method_name = f"{field_name}_display"
                display_method = cls._generate_display_method(field_config, is_link=is_link)
                setattr(cls, method_name, display_method)
                result.append(method_name)
            else:
                # Use field as-is
                result.append(field_name)

        return result

    @classmethod
    def _build_list_display_links(cls, config: AdminConfig) -> List[str]:
        """
        Build list_display_links with correct field names.

        If a field has a display_field config with ui_widget, it will be renamed
        to {field_name}_display in list_display. We need to apply the same
        transformation to list_display_links so Django can find the matching field.
        """
        result = []

        for field_name in config.list_display_links:
            # Check if we have a FieldConfig for this field
            field_config = config.get_display_field_config(field_name)

            if field_config and field_config.ui_widget:
                # Field was renamed to {field_name}_display
                result.append(f"{field_name}_display")
            else:
                # Use field as-is
                result.append(field_name)

        return result

    @classmethod
    def _generate_display_method(cls, field_config, is_link: bool = False):
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
                # Add is_link flag for link styling
                widget_config['is_link'] = is_link
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
        """
        Register actions from ActionConfig with Unfold decorator support.

        Supports two types of actions:
        - bulk: Traditional bulk actions (require selected items)
        - changelist: Buttons above the listing (no selection required)
        """
        bulk_action_functions = []
        changelist_action_functions = []

        for action_config in config.actions:
            # Get handler function
            handler = action_config.get_handler_function()

            # Build decorator kwargs
            decorator_kwargs = {
                'description': action_config.description,
            }

            # Add URL path for changelist actions
            if action_config.action_type == 'changelist':
                url_path = action_config.url_path or action_config.name.replace('_', '-')
                decorator_kwargs['url_path'] = url_path

            # Add variant (Unfold uses ActionVariant enum, but we accept strings)
            if action_config.variant and action_config.variant != 'default':
                decorator_kwargs['attrs'] = decorator_kwargs.get('attrs', {})
                decorator_kwargs['attrs']['class'] = f'button-{action_config.variant}'

            # Add icon if specified
            if action_config.icon:
                decorator_kwargs['icon'] = action_config.icon

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

            # Add to appropriate list
            if action_config.action_type == 'changelist':
                changelist_action_functions.append(action_name)
            else:  # bulk
                bulk_action_functions.append(action_name)

        # Set bulk actions list
        if bulk_action_functions:
            if hasattr(cls, 'actions') and cls.actions:
                cls.actions = list(cls.actions) + bulk_action_functions
            else:
                cls.actions = bulk_action_functions

        # Set changelist actions list (Unfold's actions_list)
        if changelist_action_functions:
            if hasattr(cls, 'actions_list') and cls.actions_list:
                cls.actions_list = list(cls.actions_list) + changelist_action_functions
            else:
                cls.actions_list = changelist_action_functions

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

    def changelist_view(self, request, extra_context=None):
        """Override to add documentation context to changelist."""
        if extra_context is None:
            extra_context = {}

        # Add documentation context if configured
        if hasattr(self, 'documentation_config') and self.documentation_config:
            doc_config = self.documentation_config
            app_path = self._get_app_path()

            if doc_config.show_on_changelist:
                extra_context['documentation_config'] = doc_config
                extra_context['documentation_sections'] = doc_config.get_sections(app_path)

                # Add tree structure for modal view
                import json
                tree_structure = doc_config.get_tree_structure(app_path)
                extra_context['documentation_tree'] = mark_safe(json.dumps(tree_structure))
                extra_context['documentation_sections_count'] = len(doc_config.get_sections(app_path))

                # Add management commands if enabled
                if doc_config.show_management_commands:
                    extra_context['management_commands'] = doc_config._discover_management_commands(app_path)

                # Add Mermaid resources if plugins enabled
                if doc_config.enable_plugins:
                    from django_cfg.modules.django_admin.utils.markdown.mermaid_plugin import get_mermaid_resources
                    extra_context['mermaid_resources'] = get_mermaid_resources()

        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Override to add documentation context to changeform."""
        if extra_context is None:
            extra_context = {}

        # Add documentation context if configured
        if hasattr(self, 'documentation_config') and self.documentation_config:
            doc_config = self.documentation_config
            app_path = self._get_app_path()

            if doc_config.show_on_changeform:
                extra_context['documentation_config'] = doc_config
                extra_context['documentation_sections'] = doc_config.get_sections(app_path)

                # Add tree structure for modal view
                import json
                tree_structure = doc_config.get_tree_structure(app_path)
                extra_context['documentation_tree'] = mark_safe(json.dumps(tree_structure))
                extra_context['documentation_sections_count'] = len(doc_config.get_sections(app_path))

                # Add management commands if enabled
                if doc_config.show_management_commands:
                    extra_context['management_commands'] = doc_config._discover_management_commands(app_path)

                # Add Mermaid resources if plugins enabled
                if doc_config.enable_plugins:
                    from django_cfg.modules.django_admin.utils.markdown.mermaid_plugin import get_mermaid_resources
                    extra_context['mermaid_resources'] = get_mermaid_resources()

        return super().changeform_view(request, object_id, form_url, extra_context)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        """
        Override form field for specific database field types.

        Automatically detects and customizes:
        - JSON fields (applies django-json-widget for editable fields only)
        - Encrypted fields from django-crypto-fields

        Respects the show_encrypted_fields_as_plain_text setting from AdminConfig.
        Uses custom widgets with copy-to-clipboard functionality.
        """
        field_class_name = db_field.__class__.__name__

        # Auto-apply JSONEditorWidget for editable JSON fields (not readonly)
        if field_class_name == 'JSONField':
            # Check if field is editable (not in readonly_fields)
            is_readonly = db_field.name in self.readonly_fields

            # Only apply for editable fields
            if not is_readonly:
                try:
                    # Use our custom JSONEditorWidget with Unfold theme support
                    from ..widgets import JSONEditorWidget

                    # Get field-specific config from AdminConfig.widgets
                    field_widget_config = getattr(self.__class__, '_field_widget_configs', {}).get(db_field.name, {})

                    # Default widget settings with Unfold theme support
                    widget_kwargs = {
                        'mode': 'code',
                        'height': '400px',
                        'options': {
                            'modes': ['code', 'tree', 'view'],
                            # Unfold dark theme colors
                            'mainMenuBar': True,
                            'navigationBar': False,
                        }
                    }

                    # Override with field-specific config
                    if field_widget_config:
                        widget_kwargs.update(field_widget_config)
                        logger.debug(f"Applied custom JSONWidget config for '{db_field.name}': {field_widget_config}")

                    # Apply JSONEditorWidget (overrides Unfold's UnfoldAdminTextareaWidget)
                    kwargs['widget'] = JSONEditorWidget(**widget_kwargs)
                    logger.debug(f"Auto-applied JSONEditorWidget to editable field '{db_field.name}'")
                except ImportError:
                    logger.warning("django-json-widget not available, using default textarea")

        # Check if this is an EncryptedTextField or EncryptedCharField
        if 'Encrypted' in field_class_name and ('TextField' in field_class_name or 'CharField' in field_class_name):
            from django import forms
            from ..widgets import EncryptedFieldWidget, EncryptedPasswordWidget

            # Determine placeholder based on field name
            placeholder = "Enter value"
            if 'key' in db_field.name.lower():
                placeholder = "Enter API Key"
            elif 'secret' in db_field.name.lower():
                placeholder = "Enter API Secret"
            elif 'passphrase' in db_field.name.lower():
                placeholder = "Enter Passphrase (if required)"

            # Widget attributes
            widget_attrs = {
                'placeholder': placeholder,
            }

            # Decide widget based on config
            show_plain_text = getattr(self.config, 'show_encrypted_fields_as_plain_text', False)

            if show_plain_text:
                # Show as plain text with copy button
                widget = EncryptedFieldWidget(attrs=widget_attrs, show_copy_button=True)
            else:
                # Show as password (masked) with copy button
                # render_value=True shows masked value (••••••) after save
                widget = EncryptedPasswordWidget(attrs=widget_attrs, render_value=True, show_copy_button=True)

            # Return CharField with appropriate widget
            return forms.CharField(
                widget=widget,
                required=not db_field.blank and not db_field.null,
                help_text=db_field.help_text or "This field is encrypted at rest",
                label=db_field.verbose_name if hasattr(db_field, 'verbose_name') else db_field.name.replace('_', ' ').title()
            )

        # Fall back to default Django behavior
        return super().formfield_for_dbfield(db_field, request, **kwargs)


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
