"""
Widget system for Django Admin.

NOTE: EncryptedFieldWidget, EncryptedPasswordWidget, and JSONEditorWidget are lazily imported
to avoid circular import issues with unfold.widgets and django-json-widget which access settings
at module level.
"""

from .registry import WidgetRegistry

__all__ = [
    "WidgetRegistry",
    "EncryptedFieldWidget",
    "EncryptedPasswordWidget",
    "JSONEditorWidget",
    "MoneyFieldWidget",
    "MoneyFieldFormField",
    # Geo widgets
    "CountrySelectWidget",
    "CitySelectWidget",
    "LocationSelectWidget",
]


def __getattr__(name):
    """
    Lazy import for widgets that depend on Django settings.

    These widgets depend on libraries that access settings.DEBUG or other Django settings
    at import time, causing ImproperlyConfigured errors when importing django_cfg
    outside of Django runtime (e.g., in api/config.py).

    Using PEP 562 lazy imports allows these widgets to be imported only
    when actually needed (i.e., when Django is properly configured).
    """
    if name == "EncryptedFieldWidget":
        from .encrypted_field_widget import EncryptedFieldWidget
        return EncryptedFieldWidget
    elif name == "EncryptedPasswordWidget":
        from .encrypted_field_widget import EncryptedPasswordWidget
        return EncryptedPasswordWidget
    elif name == "JSONEditorWidget":
        from .json_editor_widget import JSONEditorWidget
        return JSONEditorWidget
    elif name == "MoneyFieldWidget":
        from .money_widget import MoneyFieldWidget
        return MoneyFieldWidget
    elif name == "MoneyFieldFormField":
        from .money_widget import MoneyFieldFormField
        return MoneyFieldFormField
    elif name == "CountrySelectWidget":
        from .location_widget import CountrySelectWidget
        return CountrySelectWidget
    elif name == "CitySelectWidget":
        from .location_widget import CitySelectWidget
        return CitySelectWidget
    elif name == "LocationSelectWidget":
        from .location_widget import LocationSelectWidget
        return LocationSelectWidget
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
