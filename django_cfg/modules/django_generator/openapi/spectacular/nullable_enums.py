"""Keep `null` on nullable enums.

django-cfg runs drf-spectacular with `ENUM_ADD_EXPLICIT_BLANK_NULL_CHOICE` off, so
`postprocess_schema_enums` lifts a `ChoiceField(allow_null=True)` into a bare
`$ref` and the null is gone. The generated zod schema then rejects every null the
server sends. This hook wraps the stock one and puts the null back as
`oneOf [enum, null]` — blanks stay as they were.
"""

from __future__ import annotations

from typing import Any

from drf_spectacular.hooks import postprocess_schema_enums


def _is_nullable_enum(prop: Any) -> bool:
    if not isinstance(prop, dict) or "enum" not in prop:
        return False
    types = prop.get("type")
    return None in prop["enum"] or prop.get("nullable") is True or (isinstance(types, list) and "null" in types)


def _restore_null(prop: dict[str, Any]) -> None:
    if "$ref" in prop:
        ref = {"$ref": prop.pop("$ref")}
    elif len(prop.get("allOf") or ()) == 1:
        ref = prop.pop("allOf")[0]
    else:
        return  # still inline, or already a oneOf: nothing was dropped
    prop["oneOf"] = [ref, {"type": "null"}]


def postprocess_schema_enums_keep_null(result, generator, **kwargs):
    """`postprocess_schema_enums`, then `oneOf [enum, null]` for every enum that allowed null."""
    schemas = result.get("components", {}).get("schemas", {})
    nullable = [
        (component, name)
        for component, schema in schemas.items()
        for name, prop in (schema.get("properties") or {}).items()
        if _is_nullable_enum(prop)
    ]

    result = postprocess_schema_enums(result, generator, **kwargs)

    schemas = result.get("components", {}).get("schemas", {})
    for component, name in nullable:
        prop = (schemas.get(component, {}).get("properties") or {}).get(name)
        if isinstance(prop, dict):
            _restore_null(prop)
    return result
