"""
Custom widget for encrypted fields with copy button.
"""
from typing import Any, Optional

from unfold.widgets import UnfoldAdminPasswordInput, UnfoldAdminTextInputWidget


class EncryptedFieldWidget(UnfoldAdminTextInputWidget):
    """
    Text input widget for encrypted fields with copy-to-clipboard button.

    Extends UnfoldAdminTextInputWidget to add a copy button on the right side.
    """

    template_name = "django_admin/widgets/encrypted_field.html"

    def __init__(self, attrs: Optional[dict[str, Any]] = None, show_copy_button: bool = True) -> None:
        """
        Initialize the widget.

        Args:
            attrs: Widget attributes
            show_copy_button: Whether to show the copy button (default: True)
        """
        self.show_copy_button = show_copy_button
        super().__init__(attrs=attrs)

    def get_context(self, name, value, attrs):
        """Add copy button context."""
        context = super().get_context(name, value, attrs)
        context['widget']['show_copy_button'] = self.show_copy_button
        return context


class EncryptedPasswordWidget(UnfoldAdminPasswordInput):
    """
    Password input widget for encrypted fields with copy button.

    Extends UnfoldAdminPasswordInput to add a copy button on the right side.
    """

    template_name = "django_admin/widgets/encrypted_password.html"

    def __init__(
        self,
        attrs: Optional[dict[str, Any]] = None,
        render_value: bool = False,
        show_copy_button: bool = True
    ) -> None:
        """
        Initialize the widget.

        Args:
            attrs: Widget attributes
            render_value: Whether to render the value (default: False)
            show_copy_button: Whether to show the copy button (default: True)
        """
        self.show_copy_button = show_copy_button
        super().__init__(attrs=attrs, render_value=render_value)

    def get_context(self, name, value, attrs):
        """Add copy button context."""
        context = super().get_context(name, value, attrs)
        context['widget']['show_copy_button'] = self.show_copy_button
        return context
