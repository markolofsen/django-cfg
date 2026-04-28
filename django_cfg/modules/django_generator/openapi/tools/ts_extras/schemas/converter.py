"""OpenAPI schema dict → Zod TS expression (string).

Entry point: `to_zod(schema, *, lookup) -> str`.

Rules:
    $ref          → "<Name>Schema"
    enum          → z.enum([...]) for strings, z.union(...) for mixed
    type=string   → z.string() + .min/.max/.regex/format
    type=integer  → z.number().int() + min/max
    type=number   → z.number()
    type=boolean  → z.boolean()
    type=array    → z.array(<inner>)
    type=object   → z.object({...}) with required/optional
    anyOf/oneOf   → z.union([...]) (Optional[T] flattened to .nullable())
    allOf         → merged into a single z.object
    no type       → z.unknown()

`lookup(name) -> bool` is asked whether a referenced schema exists. Missing
refs become z.unknown() with a comment, so the generated file still parses.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from ..naming import schema_constant
from .format_map import ZOD_FORMAT_MAP


def to_zod(schema: Any, *, lookup: Callable[[str], bool]) -> str:
    if not isinstance(schema, dict):
        return "z.unknown()"

    ref = schema.get("$ref")
    if isinstance(ref, str):
        return _ref_to_const(ref, lookup)

    if "enum" in schema:
        return _enum(schema)

    branches = schema.get("anyOf") or schema.get("oneOf")
    if isinstance(branches, list):
        return _union(branches, lookup=lookup)

    all_of = schema.get("allOf")
    if isinstance(all_of, list) and all_of:
        return _all_of(all_of, lookup=lookup)

    t = schema.get("type")
    if isinstance(t, list):
        # Modern 3.1 style: ["string", "null"]
        return _union(
            [{**schema, "type": v} if v != "null" else {"type": "null"} for v in t],
            lookup=lookup,
        )

    if t == "string":
        return _string(schema)
    if t == "integer":
        return _integer(schema)
    if t == "number":
        return _number(schema)
    if t == "boolean":
        return "z.boolean()"
    if t == "array":
        return _array(schema, lookup=lookup)
    if t == "object" or "properties" in schema:
        return _object(schema, lookup=lookup)
    if t == "null":
        return "z.null()"

    return "z.unknown()"


def _ref_to_const(ref: str, lookup: Callable[[str], bool]) -> str:
    prefix = "#/components/schemas/"
    if not ref.startswith(prefix):
        return "z.unknown()"
    name = ref[len(prefix):]
    if not lookup(name):
        return f"z.unknown() /* missing $ref: {name} */"
    return schema_constant(name)


def _enum(schema: dict[str, Any]) -> str:
    values = schema.get("enum") or []
    if all(isinstance(v, str) for v in values):
        items = ", ".join(f'"{v}"' for v in values)
        return f"z.enum([{items}])"
    # Mixed — fall back to a literal union.
    items = ", ".join(_literal(v) for v in values)
    return f"z.union([{items}])"


def _literal(v: Any) -> str:
    if isinstance(v, str):
        return f'z.literal("{v}")'
    if isinstance(v, bool):
        return f"z.literal({'true' if v else 'false'})"
    if isinstance(v, (int, float)):
        return f"z.literal({v})"
    return "z.unknown()"


def _string(schema: dict[str, Any]) -> str:
    fmt = schema.get("format")
    if isinstance(fmt, str) and fmt in ZOD_FORMAT_MAP:
        return ZOD_FORMAT_MAP[fmt]
    parts = ["z.string()"]
    if isinstance(schema.get("minLength"), int):
        parts.append(f".min({schema['minLength']})")
    if isinstance(schema.get("maxLength"), int):
        parts.append(f".max({schema['maxLength']})")
    if isinstance(schema.get("pattern"), str):
        parts.append(f".regex(/{schema['pattern']}/)")
    return "".join(parts)


def _integer(schema: dict[str, Any]) -> str:
    parts = ["z.number().int()"]
    if isinstance(schema.get("minimum"), (int, float)):
        parts.append(f".min({schema['minimum']})")
    if isinstance(schema.get("maximum"), (int, float)):
        parts.append(f".max({schema['maximum']})")
    return "".join(parts)


def _number(schema: dict[str, Any]) -> str:
    parts = ["z.number()"]
    if isinstance(schema.get("minimum"), (int, float)):
        parts.append(f".min({schema['minimum']})")
    if isinstance(schema.get("maximum"), (int, float)):
        parts.append(f".max({schema['maximum']})")
    return "".join(parts)


def _array(schema: dict[str, Any], *, lookup: Callable[[str], bool]) -> str:
    items = schema.get("items")
    inner = to_zod(items, lookup=lookup) if isinstance(items, dict) else "z.unknown()"
    return f"z.array({inner})"


def _object(schema: dict[str, Any], *, lookup: Callable[[str], bool]) -> str:
    props = schema.get("properties") or {}
    required = set(schema.get("required") or [])
    if not props:
        return "z.object({})"
    lines = ["z.object({"]
    for key, sub in props.items():
        expr = to_zod(sub, lookup=lookup)
        if key not in required:
            expr = f"{expr}.optional()"
        lines.append(f"  {_safe_key(key)}: {expr},")
    lines.append("})")
    return "\n".join(lines)


def _union(branches: list[Any], *, lookup: Callable[[str], bool]) -> str:
    # Flatten Optional[T] (`anyOf: [T, null]`) into `T.nullable()`.
    non_null = [b for b in branches if not (isinstance(b, dict) and b.get("type") == "null")]
    has_null = len(non_null) != len(branches)
    if len(non_null) == 1:
        expr = to_zod(non_null[0], lookup=lookup)
        return f"{expr}.nullable()" if has_null else expr
    parts = [to_zod(b, lookup=lookup) for b in non_null]
    inner = "z.union([" + ", ".join(parts) + "])"
    return f"{inner}.nullable()" if has_null else inner


def _all_of(parts: list[Any], *, lookup: Callable[[str], bool]) -> str:
    """Use z.intersection chain — Zod doesn't have native allOf merge."""
    rendered = [to_zod(p, lookup=lookup) for p in parts]
    if len(rendered) == 1:
        return rendered[0]
    expr = rendered[0]
    for r in rendered[1:]:
        expr = f"z.intersection({expr}, {r})"
    return expr


_VALID_JS_KEY = __import__("re").compile(r"^[A-Za-z_$][A-Za-z0-9_$]*$")


def _safe_key(key: str) -> str:
    """JS object key — bare ident or quoted."""
    if _VALID_JS_KEY.match(key):
        return key
    return f'"{key}"'
