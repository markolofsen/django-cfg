"""
Widget system for Django Admin.
"""

from .encrypted_field_widget import EncryptedFieldWidget, EncryptedPasswordWidget
from .registry import WidgetRegistry

__all__ = [
    "WidgetRegistry",
    "EncryptedFieldWidget",
    "EncryptedPasswordWidget",
]
