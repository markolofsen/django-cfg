"""
Custom JSON editor widget with copy button.

Extends django-json-widget's JSONEditorWidget to add copy-to-clipboard functionality.
"""
from typing import Any, Optional

try:
    from django_json_widget.widgets import JSONEditorWidget as BaseJSONEditorWidget
except ImportError:
    # Fallback to Django's default widget if django-json-widget is not installed
    from django.forms import Textarea as BaseJSONEditorWidget


class JSONEditorWidget(BaseJSONEditorWidget):
    """
    JSON editor widget with copy-to-clipboard button and Unfold theme support.

    Extends django-json-widget's JSONEditorWidget to add:
    - Copy button with visual feedback
    - Automatic Unfold dark/light theme switching
    - Enhanced styling for Unfold integration

    Features:
    - Rich JSON editor (tree/code/view modes)
    - Syntax highlighting
    - Copy button with visual feedback
    - Automatic theme switching (light/dark)
    - Validation
    """

    template_name = "django_admin/widgets/json_editor.html"

    class Media:
        css = {
            'all': ('django_admin/css/json_editor_theme.css',)
        }

    def __init__(
        self,
        attrs: Optional[dict[str, Any]] = None,
        mode: str = "tree",
        options: Optional[dict[str, Any]] = None,
        width: Optional[str] = None,
        height: Optional[str] = "400px",
        show_copy_button: bool = True,
    ) -> None:
        """
        Initialize the JSON editor widget.

        Args:
            attrs: Widget attributes
            mode: Editor mode - 'tree', 'code', or 'view' (default: 'tree')
            options: Additional JSONEditor options
            width: Editor width (default: '100%')
            height: Editor height (default: '400px')
            show_copy_button: Whether to show the copy button (default: True)
        """
        self.show_copy_button = show_copy_button

        # Prepare options for django-json-widget
        if options is None:
            options = {}

        # Set default mode
        options.setdefault('mode', mode)
        options.setdefault('modes', ['tree', 'code', 'view'])

        # Prepare attrs
        if attrs is None:
            attrs = {}

        # Set dimensions
        style_parts = []
        if width:
            style_parts.append(f'width: {width}')
        if height:
            style_parts.append(f'height: {height}')

        if style_parts:
            existing_style = attrs.get('style', '')
            attrs['style'] = '; '.join(style_parts + ([existing_style] if existing_style else []))

        # Initialize parent
        super().__init__(attrs=attrs, options=options)

    def get_context(self, name, value, attrs):
        """Add copy button context."""
        context = super().get_context(name, value, attrs)
        context['widget']['show_copy_button'] = self.show_copy_button
        return context
