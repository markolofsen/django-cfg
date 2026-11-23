"""Keep `null` and `""` on enums that allow them.

django-cfg runs drf-spectacular with `ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE` off, so
`postprocess_schema_enums` lifts a `ChoiceField(allow_null=True)` or
`ChoiceField(allow_blank=True)` into a bare `$ref`, and both the null and the
blank are gone (`hooks.py` strips `''` and `None` from every component enum). The
generated zod schema then rejects every such value the server sends; e.g. every
`ChatMessage` without an error carries `error_code: ""`. This hook wraps the stock
one and puts them back: `oneOf [enum, {"type": "string", "enum": [""]}, null]`.
"""

from __future__ import annotations

from typing import Any

from drf_spectacular.hooks import postprocess_schema_enums

BLANK = {"type": "string", "enum": [""]}
NULL = {"type": "null"}


def _allows(prop: Any) -> tuple[bool, bool]:
    """(null allowed, blank allowed) for an inline enum property, before the stock hook lifts it."""
    if not isinstance(prop, dict) or "enum" not in prop:
        return False, False
    types = prop.get("type")
    null = None in prop["enum"] or prop.get("nullable") is True or (isinstance(types, list) and "null" in types)
    blank = "" in prop["enum"]
    return null, blank


def _restore(prop: dict[str, Any], *, null: bool, blank: bool) -> None:
    if "$ref" in prop:
        ref = {"$ref": prop.pop("$ref")}
    elif len(prop.get("allOf") or ()) == 1:
        ref = prop.pop("allOf")[0]
    else:
        return  # still inline, or already a oneOf: nothing was dropped
    prop["oneOf"] = [ref] + ([BLANK] if blank else []) + ([NULL] if null else [])


def postprocess_schema_enums_keep_null(result, generator, **kwargs):
    """`postprocess_schema_enums`, then put back `""` and `null` on every enum that allowed them."""
    schemas = result.get("components", {}).get("schemas", {})
    lifted = []
    for component, schema in schemas.items():
        for name, prop in (schema.get("properties") or {}).items():
            null, blank = _allows(prop)
            if null or blank:
                lifted.append((component, name, null, blank))

    result = postprocess_schema_enums(result, generator, **kwargs)

    schemas = result.get("components", {}).get("schemas", {})
    for component, name, null, blank in lifted:
        prop = (schemas.get(component, {}).get("properties") or {}).get(name)
        if isinstance(prop, dict):
            _restore(prop, null=null, blank=blank)
    return result
