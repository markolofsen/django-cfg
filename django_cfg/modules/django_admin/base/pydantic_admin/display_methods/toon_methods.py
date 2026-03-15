"""
Auto-display methods for ToonField (readonly_fields on change form).

Renders JSON field values as a full TOON/JSON collapsible viewer using
ToonDisplay.from_field().
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any, Dict, Tuple

from django.utils.safestring import SafeString

if TYPE_CHECKING:
    from ....config import AdminConfig

logger = logging.getLogger(__name__)


def create_toonfield_display_methods(
    cls: Any,
    readonly_fields: list[str],
    config: AdminConfig,
) -> Tuple[list[str], Dict[str, str]]:
    """
    Auto-create display methods for fields with ToonField config.

    Scans display_fields for ToonField entries that are also in readonly_fields
    and creates a display method rendering the full TOON/JSON form viewer.

    Returns:
        (updated_readonly_fields, {field_name: method_name})
    """
    from ....config.field_config.toon import ToonField

    if not config.display_fields:
        return list(readonly_fields), {}

    updated = list(readonly_fields)
    replacements: Dict[str, str] = {}

    for field_config in config.display_fields:
        if not isinstance(field_config, ToonField):
            continue

        field_name = field_config.name
        if field_name not in readonly_fields:
            continue

        method_name = f"{field_name}_toon_display"
        widget_config = field_config.get_widget_config()

        method = _make_toon_method(field_name, widget_config)
        setattr(cls, method_name, method)
        replacements[field_name] = method_name

        try:
            updated[updated.index(field_name)] = method_name
        except ValueError:
            pass

        logger.debug("Created toon display method '%s' for '%s'", method_name, field_name)

    return updated, replacements


def _make_toon_method(fname: str, widget_config: Dict[str, Any]) -> Any:
    from ....utils.displays.toon_display import ToonDisplay

    label = widget_config.get("label") or fname.replace("_", " ").title()

    def display_method(self: Any, obj: Any) -> SafeString:
        return ToonDisplay.from_field(obj, fname, widget_config)

    display_method.short_description = label  # type: ignore[attr-defined]
    return display_method
