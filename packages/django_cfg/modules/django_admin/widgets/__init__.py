"""
Widget system for Django Admin.

NOTE: EncryptedFieldWidget and EncryptedPasswordWidget are lazily imported
to avoid circular import issues with unfold.widgets which accesses settings.DEBUG
at module level.
"""

from .registry import WidgetRegistry

__all__ = [
    "WidgetRegistry",
    "EncryptedFieldWidget",
    "EncryptedPasswordWidget",
]


def __getattr__(name):
    """
    Lazy import for EncryptedFieldWidget and EncryptedPasswordWidget.

    These widgets depend on unfold.widgets which accesses settings.DEBUG
    at import time, causing ImproperlyConfigured errors when importing
    django_cfg outside of Django runtime (e.g., in api/config.py).

    Using PEP 562 lazy imports allows these widgets to be imported only
    when actually needed (i.e., when Django is properly configured).
    """
    if name == "EncryptedFieldWidget":
        from .encrypted_field_widget import EncryptedFieldWidget
        return EncryptedFieldWidget
    elif name == "EncryptedPasswordWidget":
        from .encrypted_field_widget import EncryptedPasswordWidget
        return EncryptedPasswordWidget
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
