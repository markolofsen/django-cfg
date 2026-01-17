"""
Display method creators for different field types.

Auto-creates display methods for:
- JSONField - with syntax highlighting
- ImageField/FileField - with preview cards
- MarkdownField - with rendered markdown
"""

import json
import logging
import uuid
from typing import TYPE_CHECKING, Any, Dict, Tuple

from django.utils.safestring import mark_safe

if TYPE_CHECKING:
    from ...config import AdminConfig

logger = logging.getLogger(__name__)


def highlight_json(json_obj: Any) -> str:
    """
    Apply syntax highlighting to JSON using Pygments (Unfold style).

    Returns HTML with Pygments syntax highlighting for light and dark themes.
    """
    try:
        from pygments import highlight
        from pygments.formatters import HtmlFormatter
        from pygments.lexers import JsonLexer
    except ImportError:
        # Fallback to plain JSON if Pygments not available
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


def create_jsonfield_display_methods(cls, config: 'AdminConfig') -> Tuple[list, Dict[str, str]]:
    """
    Auto-create display methods for readonly JSONField fields.

    This ensures proper Unicode display (non-ASCII characters) for readonly JSON fields.
    Django's default display_for_field() uses json.dumps() with ensure_ascii=True,
    which escapes Unicode characters. We override this to use ensure_ascii=False.

    Args:
        cls: The admin class to add methods to
        config: AdminConfig instance

    Returns:
        Tuple of (updated_readonly_fields, jsonfield_replacements_dict)
    """
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
                            highlighted_json = highlight_json(json_obj)

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


def create_imagefield_display_methods(cls, readonly_fields: list, config: 'AdminConfig') -> Tuple[list, Dict[str, str], bool]:
    """
    Auto-create display methods for readonly ImageField/FileField fields.

    Uses ImagePreviewDisplay for image fields to show clickable thumbnails
    with modal preview.

    Args:
        cls: The admin class to add methods to
        readonly_fields: Current readonly_fields list
        config: AdminConfig instance

    Returns:
        Tuple of (updated_readonly_fields, imagefield_replacements_dict, has_image_preview)
    """
    from ...utils import ImagePreviewDisplay

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


def create_markdownfield_display_methods(cls, readonly_fields: list, config: 'AdminConfig') -> Tuple[list, Dict[str, str]]:
    """
    Auto-create display methods for fields with MarkdownField config.

    Scans display_fields for MarkdownField configs, and if the field
    is in readonly_fields, creates a display method that renders markdown.

    Args:
        cls: The admin class to add methods to
        readonly_fields: Current readonly_fields list
        config: AdminConfig instance

    Returns:
        Tuple of (updated_readonly_fields, markdownfield_replacements_dict)
    """
    from ...utils.html.markdown_integration import MarkdownIntegration
    from ...config.field_config.markdown import MarkdownField

    if not config.display_fields:
        return readonly_fields, {}

    updated_readonly_fields = list(readonly_fields)
    markdownfield_replacements = {}

    # Find MarkdownField configs in display_fields
    for field_config in config.display_fields:
        if not isinstance(field_config, MarkdownField):
            continue

        field_name = field_config.name
        if field_name not in readonly_fields:
            continue

        # Create display method name
        method_name = f'{field_name}_md_display'

        # Get config options
        collapsible = field_config.collapsible
        default_open = field_config.default_open
        max_height = field_config.max_height
        title = field_config.title or field_name.replace('_', ' ').title()
        icon = field_config.header_icon
        enable_plugins = field_config.enable_plugins
        full_width = field_config.full_width

        # Create display method
        def create_method(fname, ftitle, fcollapsible, fdefault_open, fmax_height, ficon, fenable_plugins, ffull_width):
            def display_method(self, obj):
                value = getattr(obj, fname, None)
                if not value:
                    return mark_safe('<span class="text-gray-400 italic">—</span>')

                content = MarkdownIntegration.markdown_docs(
                    content=value,
                    collapsible=fcollapsible,
                    title=ftitle,
                    icon=ficon or 'description',
                    max_height=fmax_height,
                    enable_plugins=fenable_plugins,
                    default_open=fdefault_open,
                )

                # Wrap in full-width container if enabled
                if ffull_width:
                    # Use unique ID for targeting
                    uid = str(uuid.uuid4())[:8]
                    return mark_safe(
                        f'<div id="md-{uid}" class="markdown-full-width">'
                        f'{content}'
                        f'</div>'
                        f'<style>'
                        f'/* Override Unfold max-w-2xl on readonly container */'
                        f'.readonly:has(#md-{uid}) {{'
                        f'  max-width: none !important;'
                        f'  width: 100% !important;'
                        f'}}'
                        f'/* Ensure markdown content takes full width */'
                        f'#md-{uid} {{'
                        f'  width: 100% !important;'
                        f'}}'
                        f'</style>'
                    )
                return content
            display_method.short_description = ftitle
            return display_method

        method = create_method(field_name, title, collapsible, default_open, max_height, icon, enable_plugins, full_width)
        setattr(cls, method_name, method)

        # Track replacement
        markdownfield_replacements[field_name] = method_name

        # Replace in updated list
        try:
            idx = updated_readonly_fields.index(field_name)
            updated_readonly_fields[idx] = method_name
        except ValueError:
            pass

        logger.debug(f"Created markdown display method '{method_name}' for field '{field_name}'")

    return updated_readonly_fields, markdownfield_replacements


def apply_replacements_to_fieldsets(fieldsets, replacements: Dict[str, str]):
    """
    Apply field replacements to fieldsets.

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
