"""
Widget registry for declarative admin.

Maps ui_widget names to display utilities.
"""

import logging
from typing import Any, Callable, Dict, Optional

from ..models import (
    DateTimeDisplayConfig,
    MoneyDisplayConfig,
    StatusBadgeConfig,
    UserDisplayConfig,
)
from ..utils import (
    BooleanDisplay,
    CounterBadge,
    DateTimeDisplay,
    MoneyDisplay,
    ProgressBadge,
    StatusBadge,
    UserDisplay,
)

logger = logging.getLogger(__name__)


class WidgetRegistry:
    """
    Widget registry mapping ui_widget names to render functions.

    Maps declarative widget names to actual display utilities.
    """

    _widgets: Dict[str, Callable] = {}

    @classmethod
    def register(cls, name: str, handler: Callable):
        """Register a custom widget."""
        cls._widgets[name] = handler
        logger.debug(f"Registered widget: {name}")

    @classmethod
    def get(cls, name: str) -> Optional[Callable]:
        """Get widget handler by name."""
        return cls._widgets.get(name)

    @classmethod
    def render(cls, widget_name: str, obj: Any, field_name: str, config: Dict[str, Any]):
        """Render field using specified widget."""
        handler = cls.get(widget_name)

        if handler:
            try:
                return handler(obj, field_name, config)
            except Exception as e:
                logger.error(f"Error rendering widget '{widget_name}': {e}")
                return getattr(obj, field_name, "—")

        # Fallback to field value
        logger.warning(f"Widget '{widget_name}' not found, using field value")
        return getattr(obj, field_name, "—")


# Register built-in widgets

# User widgets
WidgetRegistry.register(
    "user_avatar",
    lambda obj, field, cfg: UserDisplay.with_avatar(
        getattr(obj, field),
        UserDisplayConfig(**cfg) if cfg else None
    )
)

WidgetRegistry.register(
    "user_simple",
    lambda obj, field, cfg: UserDisplay.simple(
        getattr(obj, field),
        UserDisplayConfig(**cfg) if cfg else None
    )
)

# Money widgets
WidgetRegistry.register(
    "currency",
    lambda obj, field, cfg: MoneyDisplay.amount(
        getattr(obj, field),
        MoneyDisplayConfig(**cfg) if cfg else None
    )
)

WidgetRegistry.register(
    "money_breakdown",
    lambda obj, field, cfg: MoneyDisplay.with_breakdown(
        getattr(obj, field),
        cfg.get('breakdown_items', []),
        MoneyDisplayConfig(**{k: v for k, v in cfg.items() if k != 'breakdown_items'}) if cfg else None
    )
)

# Badge widgets
WidgetRegistry.register(
    "badge",
    lambda obj, field, cfg: StatusBadge.auto(
        getattr(obj, field),
        StatusBadgeConfig(**cfg) if cfg else None
    )
)

WidgetRegistry.register(
    "progress",
    lambda obj, field, cfg: ProgressBadge.percentage(
        getattr(obj, field)
    )
)

WidgetRegistry.register(
    "counter",
    lambda obj, field, cfg: CounterBadge.simple(
        getattr(obj, field),
        cfg.get('label') if cfg else None
    )
)

# DateTime widgets
WidgetRegistry.register(
    "datetime_relative",
    lambda obj, field, cfg: DateTimeDisplay.relative(
        getattr(obj, field),
        DateTimeDisplayConfig(**cfg) if cfg else None
    )
)

WidgetRegistry.register(
    "datetime_compact",
    lambda obj, field, cfg: DateTimeDisplay.compact(
        getattr(obj, field),
        DateTimeDisplayConfig(**cfg) if cfg else None
    )
)

# Simple widgets
WidgetRegistry.register(
    "text",
    lambda obj, field, cfg: str(getattr(obj, field, ""))
)

WidgetRegistry.register(
    "boolean",
    lambda obj, field, cfg: BooleanDisplay.icon(
        getattr(obj, field, False),
        cfg.get('true_icon') if cfg else None,
        cfg.get('false_icon') if cfg else None
    )
)


def _render_image(obj: Any, field: str, config: Dict[str, Any]) -> str:
    """Render an image from a URL field."""
    # Get image URL - support both direct fields and methods
    value = getattr(obj, field, None)
    if callable(value):
        image_url = value()
    else:
        image_url = value

    if not image_url:
        return config.get('empty_value', "—")

    # Build style attributes
    styles = []
    if config.get('width'):
        styles.append(f"width: {config['width']}")
    if config.get('height'):
        styles.append(f"height: {config['height']}")
    if config.get('max_width'):
        styles.append(f"max-width: {config['max_width']}")
    if config.get('max_height'):
        styles.append(f"max-height: {config['max_height']}")
    if config.get('border_radius'):
        styles.append(f"border-radius: {config['border_radius']}")

    style_attr = f' style="{"; ".join(styles)}"' if styles else ''
    alt_text = config.get('alt_text', 'Image')

    # Build HTML
    html_parts = [f'<img src="{image_url}" alt="{alt_text}"{style_attr}>']

    # Add caption if specified
    caption_text = None
    if config.get('caption'):
        caption_text = config['caption']
    elif config.get('caption_field'):
        caption_text = str(getattr(obj, config['caption_field'], ''))
    elif config.get('caption_template'):
        # Template supports {field_name} placeholders
        template = config['caption_template']
        # Extract field names from template and replace
        import re
        field_names = re.findall(r'\{(\w+)\}', template)
        for field_name in field_names:
            field_value = getattr(obj, field_name, '')
            template = template.replace(f'{{{field_name}}}', str(field_value))
        caption_text = template

    if caption_text:
        html_parts.append(f'<br><small>{caption_text}</small>')

    return ''.join(html_parts)


# Image widget
WidgetRegistry.register("image", _render_image)


def _render_short_uuid(obj: Any, field: str, config: Dict[str, Any]) -> str:
    """Render a shortened UUID with tooltip."""
    from django.utils.safestring import mark_safe

    # Get UUID value
    uuid_value = getattr(obj, field, None)

    if not uuid_value:
        return config.get('empty_value', "—")

    # Convert to string and remove dashes
    uuid_str = str(uuid_value).replace('-', '')

    # Get configuration
    length = config.get('length', 8)
    show_full_on_hover = config.get('show_full_on_hover', True)
    copy_on_click = config.get('copy_on_click', True)

    # Truncate to specified length
    short_uuid = uuid_str[:length]

    # Build HTML
    if show_full_on_hover:
        title_attr = f' title="{uuid_value}"'
    else:
        title_attr = ''

    if copy_on_click:
        # Add click-to-copy functionality
        copy_attr = f' onclick="navigator.clipboard.writeText(\'{uuid_value}\'); this.style.backgroundColor=\'#e8f5e9\'; setTimeout(() => this.style.backgroundColor=\'\', 500);" style="cursor: pointer;"'
    else:
        copy_attr = ''

    html = f'<code{title_attr}{copy_attr}>{short_uuid}</code>'

    return mark_safe(html)


# ShortUUID widget
WidgetRegistry.register("short_uuid", _render_short_uuid)


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
            prestyles="white-space: pre-wrap; word-wrap: break-word; font-size: 0.75rem;",
        )
        return highlight(response, JsonLexer(), formatter)

    # Format JSON with ensure_ascii=False for proper Unicode
    response = json.dumps(json_obj, indent=2, ensure_ascii=False)

    # Return dual-theme HTML (light: colorful, dark: monokai)
    return (
        f'<div class="block dark:hidden">{format_response(response, "colorful")}</div>'
        f'<div class="hidden dark:block">{format_response(response, "monokai")}</div>'
    )


def _render_json_editor(obj: Any, field: str, config: Dict[str, Any]) -> str:
    """
    Render JSON field for display (list view and readonly).

    Uses JSONEditorWidget for consistent rendering across editable and readonly contexts.
    """
    from django.utils.safestring import mark_safe
    import json
    import html as html_lib

    # Get JSON value
    json_value = getattr(obj, field, None)

    if not json_value:
        return config.get('empty_value', "—")

    # Try to format JSON nicely
    try:
        if isinstance(json_value, str):
            json_obj = json.loads(json_value)
        else:
            json_obj = json_value

        # Get configuration
        indent = config.get('indent', 2)
        max_display_length = config.get('max_display_length', 100)
        formatted_json = json.dumps(json_obj, indent=indent, ensure_ascii=False)

        # For compact display (list view or short JSON)
        if len(formatted_json) <= max_display_length:
            # Use Pygments highlighting (no need for wrapper, it has its own styling)
            highlighted_json = _highlight_json(json_obj)
            return mark_safe(highlighted_json)

        # For detailed display - show preview with count
        escaped_json = html_lib.escape(formatted_json)
        if isinstance(json_obj, dict):
            key_count = len(json_obj)
            html = f'<code title="{escaped_json}">{{{key_count} keys}}</code>'
        elif isinstance(json_obj, list):
            item_count = len(json_obj)
            html = f'<code title="{escaped_json}">[{item_count} items]</code>'
        else:
            preview = html_lib.escape(formatted_json[:max_display_length] + "...")
            html = f'<code title="{escaped_json}">{preview}</code>'

        return mark_safe(html)

    except (json.JSONDecodeError, TypeError, ValueError) as e:
        return mark_safe(f"<code>Invalid JSON: {str(json_value)[:100]}</code>")


# JSON Editor widget
WidgetRegistry.register("json_editor", _render_json_editor)


def _render_avatar(obj: Any, field: str, config: Dict[str, Any]) -> str:
    """Render avatar with fallback to initials badge."""
    from django.utils.safestring import mark_safe

    # Validate that the field exists in the model
    if not hasattr(obj, field):
        error_msg = (
            f'<span class="text-red-600 font-bold">⚠️ AvatarField Error: '
            f'Field "{field}" does not exist in model {obj.__class__.__name__}. '
            f'Use a real model field (e.g., "first_name", "username"), not a virtual field!</span>'
        )
        logger.error(f"AvatarField validation error: Field '{field}' not found in {obj.__class__.__name__}")
        return mark_safe(error_msg)

    # Get field configuration
    photo_field = config.get('photo_field')
    name_field = config.get('name_field')
    initials_field = config.get('initials_field')
    subtitle_field = config.get('subtitle_field')

    # Validate required configuration
    if not photo_field or not name_field or not initials_field:
        return mark_safe('<span class="text-gray-500">Avatar config missing (photo_field, name_field, initials_field required)</span>')

    # Get field values from object
    photo = getattr(obj, photo_field, None) if photo_field else None
    name = str(getattr(obj, name_field, '')) if name_field else ''
    initials_source = str(getattr(obj, initials_field, '')) if initials_field else ''
    subtitle = str(getattr(obj, subtitle_field, '')) if subtitle_field else None

    # Get configuration
    avatar_size = config.get('avatar_size', 40)
    show_as_card = config.get('show_as_card', False)
    variant_field = config.get('variant_field')
    variant_map = config.get('variant_map', {})
    default_variant = config.get('default_variant', 'secondary')
    initials_max_length = config.get('initials_max_length', 2)

    # Extract initials
    initials = ''.join([word[0].upper() for word in str(initials_source).split()[:initials_max_length]])
    if not initials:
        initials = str(name)[0].upper() if name else '?'

    # Determine variant for badge fallback
    variant = default_variant
    if variant_field:
        variant_value = getattr(obj, variant_field, None)
        variant = variant_map.get(variant_value, default_variant)

    # If photo exists, show image
    if photo:
        photo_url = photo.url if hasattr(photo, 'url') else str(photo)
        if show_as_card:
            html = f'''
            <div class="flex items-center gap-2">
                <img src="{photo_url}" alt="{name}"
                     class="rounded-full"
                     style="width: {avatar_size}px; height: {avatar_size}px; object-fit: cover;">
                <div>
                    <div class="font-medium">{name}</div>
                    {f'<div class="text-sm text-gray-500">{subtitle}</div>' if subtitle else ''}
                </div>
            </div>
            '''
        else:
            html = f'<img src="{photo_url}" alt="{name}" class="rounded-full" style="width: {avatar_size}px; height: {avatar_size}px; object-fit: cover;">'
    else:
        # Fallback to initials badge
        badge_colors = {
            'primary': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
            'secondary': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
            'success': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
            'danger': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
            'warning': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
            'info': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-300',
        }
        color_class = badge_colors.get(variant, badge_colors['secondary'])

        if show_as_card:
            html = f'''
            <div class="flex items-center gap-2">
                <div class="rounded-full {color_class} flex items-center justify-center font-semibold"
                     style="width: {avatar_size}px; height: {avatar_size}px;">
                    {initials}
                </div>
                <div>
                    <div class="font-medium">{name}</div>
                    {f'<div class="text-sm text-gray-500">{subtitle}</div>' if subtitle else ''}
                </div>
            </div>
            '''
        else:
            html = f'<div class="rounded-full {color_class} flex items-center justify-center font-semibold" style="width: {avatar_size}px; height: {avatar_size}px;">{initials}</div>'

    return mark_safe(html)


def _render_link(obj: Any, field: str, config: Dict[str, Any]) -> str:
    """Render text with link and optional subtitle."""
    from django.utils.safestring import mark_safe

    # Validate that the field exists in the model
    if not hasattr(obj, field):
        error_msg = (
            f'<span class="text-red-600 font-bold">⚠️ LinkField Error: '
            f'Field "{field}" does not exist in model {obj.__class__.__name__}. '
            f'Use a real model field, not a virtual field!</span>'
        )
        logger.error(f"LinkField validation error: Field '{field}' not found in {obj.__class__.__name__}")
        return mark_safe(error_msg)

    # Get field values
    text = getattr(obj, field, '')
    link_field = config.get('link_field')
    link_url = getattr(obj, link_field, '') if link_field else ''

    if not link_url:
        return str(text)

    # Get configuration
    link_icon = config.get('link_icon')
    link_target = config.get('link_target', '_blank')
    subtitle_field = config.get('subtitle_field')
    subtitle_fields = config.get('subtitle_fields')
    subtitle_template = config.get('subtitle_template')
    subtitle_separator = config.get('subtitle_separator', ' • ')
    subtitle_css_class = config.get('subtitle_css_class', 'text-sm text-gray-500')

    # Build subtitle
    subtitle_text = None
    if subtitle_template:
        # Template with {field_name} placeholders
        import re
        template = subtitle_template
        field_names = re.findall(r'\{(\w+)\}', template)
        for field_name in field_names:
            field_value = getattr(obj, field_name, '')
            template = template.replace(f'{{{field_name}}}', str(field_value))
        subtitle_text = template
    elif subtitle_fields:
        # Multiple fields with separator
        parts = [str(getattr(obj, f, '')) for f in subtitle_fields if getattr(obj, f, '')]
        subtitle_text = subtitle_separator.join(parts) if parts else None
    elif subtitle_field:
        # Single field
        subtitle_text = str(getattr(obj, subtitle_field, ''))

    # Build HTML
    icon_html = f'<span class="material-symbols-outlined" style="font-size: 16px; vertical-align: middle;">{link_icon}</span> ' if link_icon else ''
    link_html = f'<a href="{link_url}" target="{link_target}">{icon_html}{text}</a>'

    if subtitle_text:
        html = f'''
        <div>
            <div>{link_html}</div>
            <div class="{subtitle_css_class}">{subtitle_text}</div>
        </div>
        '''
    else:
        html = link_html

    return mark_safe(html)


def _render_markdown(obj: Any, field: str, config: Dict[str, Any]) -> str:
    """Render markdown content."""
    from django.utils.safestring import mark_safe

    # Get markdown content
    content = getattr(obj, field, '')
    if not content:
        return config.get('empty_value', "—")

    # TODO: Implement markdown rendering with mistune
    # For now, return plain text
    return mark_safe(f'<div class="prose">{content}</div>')


def _render_status_badges(obj: Any, field: str, config: Dict[str, Any]) -> str:
    """Render multiple conditional status badges."""
    from django.utils.safestring import mark_safe

    # Validate that the field exists in the model (though it's not directly used, it's in list_display)
    if not hasattr(obj, field):
        error_msg = (
            f'<span class="text-red-600 font-bold">⚠️ StatusBadgesField Error: '
            f'Field "{field}" does not exist in model {obj.__class__.__name__}. '
            f'Use a real model field!</span>'
        )
        logger.error(f"StatusBadgesField validation error: Field '{field}' not found in {obj.__class__.__name__}")
        return mark_safe(error_msg)

    badge_rules = config.get('badge_rules', [])
    separator = config.get('separator', ' ')
    empty_text = config.get('empty_text')
    empty_variant = config.get('empty_variant', 'secondary')

    # Check each rule and collect matching badges
    badges = []
    for rule in badge_rules:
        condition_field = rule.get('condition_field')
        condition_value = rule.get('condition_value', True)
        label = rule.get('label', '')
        variant = rule.get('variant', 'secondary')
        icon = rule.get('icon')

        # Check if condition matches
        field_value = getattr(obj, condition_field, None)
        if field_value == condition_value:
            # Build badge
            badge_colors = {
                'primary': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
                'secondary': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
                'success': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
                'danger': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
                'warning': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
                'info': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-300',
            }
            color_class = badge_colors.get(variant, badge_colors['secondary'])
            icon_html = f'<span class="material-symbols-outlined" style="font-size: 16px; vertical-align: middle;">{icon}</span> ' if icon else ''
            badge_html = f'<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium {color_class}">{icon_html}{label}</span>'
            badges.append(badge_html)

    # If no badges match, show empty state
    if not badges and empty_text:
        badge_colors = {
            'secondary': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
        }
        color_class = badge_colors.get(empty_variant, badge_colors['secondary'])
        return mark_safe(f'<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium {color_class}">{empty_text}</span>')

    return mark_safe(separator.join(badges)) if badges else "—"


def _render_counter_badge(obj: Any, field: str, config: Dict[str, Any]) -> str:
    """Render counter badge with optional link."""
    from django.utils.safestring import mark_safe

    # Validate that the field exists in the model
    if not hasattr(obj, field):
        error_msg = (
            f'<span class="text-red-600 font-bold">⚠️ CounterBadgeField Error: '
            f'Field "{field}" does not exist in model {obj.__class__.__name__}. '
            f'Use a real model field!</span>'
        )
        logger.error(f"CounterBadgeField validation error: Field '{field}' not found in {obj.__class__.__name__}")
        return mark_safe(error_msg)

    count_field = config.get('count_field')
    count = getattr(obj, count_field, 0) if count_field else 0

    variant = config.get('variant', 'primary')
    icon = config.get('icon')
    link_url_template = config.get('link_url_template')
    link_target = config.get('link_target', '_self')
    format_thousands = config.get('format_thousands', True)
    hide_on_zero = config.get('hide_on_zero', False)
    empty_display = config.get('empty_display', False)
    empty_text = config.get('empty_text', '-')

    # Handle zero count
    if count == 0:
        if hide_on_zero:
            return ""
        if empty_display:
            count_display = empty_text
        else:
            count_display = "0"
    else:
        # Format number
        count_display = f"{count:,}" if format_thousands else str(count)

    # Build badge
    badge_colors = {
        'primary': 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
        'secondary': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
        'success': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
        'danger': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300',
        'warning': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
        'info': 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900 dark:text-cyan-300',
    }
    color_class = badge_colors.get(variant, badge_colors['primary'])
    icon_html = f'<span class="material-symbols-outlined" style="font-size: 16px; vertical-align: middle;">{icon}</span> ' if icon else ''
    badge_html = f'<span class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium {color_class}">{icon_html}{count_display}</span>'

    # Wrap in link if template provided
    if link_url_template and count > 0:
        # Replace {obj.field} placeholders
        import re
        link_url = link_url_template
        placeholders = re.findall(r'\{obj\.(\w+)\}', link_url)
        for placeholder in placeholders:
            value = getattr(obj, placeholder, '')
            link_url = link_url.replace(f'{{obj.{placeholder}}}', str(value))
        badge_html = f'<a href="{link_url}" target="{link_target}">{badge_html}</a>'

    return mark_safe(badge_html)


# Register new widgets
WidgetRegistry.register("avatar", _render_avatar)
WidgetRegistry.register("link", _render_link)
WidgetRegistry.register("markdown", _render_markdown)
WidgetRegistry.register("status_badges", _render_status_badges)
WidgetRegistry.register("counter_badge", _render_counter_badge)
