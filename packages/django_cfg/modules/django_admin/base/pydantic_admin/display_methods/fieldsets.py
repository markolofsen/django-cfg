"""
Fieldset utilities — apply field-name replacements to Django fieldsets.
"""
from __future__ import annotations

from typing import Any, Dict


def apply_replacements_to_fieldsets(
    fieldsets: Any,
    replacements: Dict[str, str],
) -> tuple[Any, ...]:
    """
    Rewrite fieldsets, substituting original field names with display-method names.

    Args:
        fieldsets:    Django fieldsets tuple  ((title, {fields: [...]}), ...)
        replacements: Mapping of {original_field_name: display_method_name}

    Returns:
        Updated fieldsets tuple with replaced names.
    """
    if not replacements:
        return fieldsets

    result = []
    for title, options in fieldsets:
        updated_fields = []
        for field in options.get("fields", []):
            if isinstance(field, (list, tuple)):
                updated_fields.append(tuple(replacements.get(f, f) for f in field))
            else:
                updated_fields.append(replacements.get(field, field))

        updated_options = {**options, "fields": tuple(updated_fields)}
        result.append((title, updated_options))

    return tuple(result)
