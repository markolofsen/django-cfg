"""
Response-format normalization for LLM chat completions.

A caller may ask for structured output in three ways; this module turns
any of them into the dict the OpenAI-compatible API expects:

- ``"json"`` / ``"json_object"``  -> ``{"type": "json_object"}``
- a ready ``dict``                -> passed through unchanged
- a Pydantic ``BaseModel`` class  -> a strict ``json_schema`` block

Strict ``json_schema`` is the only form where the provider *enforces*
the schema during generation (constrained decoding): the model cannot
emit an invalid enum value or omit a required field. Plain
``json_object`` only guarantees syntactically valid JSON.
"""

from __future__ import annotations

from typing import Optional, Union

from pydantic import BaseModel

# What chat_completion() accepts for `response_format`.
ResponseFormat = Union[str, dict, type[BaseModel]]

_JSON_ALIASES = frozenset({"json", "json_object"})

# JSON Schema validation keywords for bounds — validated by Pydantic on the
# Python side after parsing, not needed in the wire schema.
_VALIDATION_BOUNDS = frozenset({
    "minimum", "maximum", "exclusiveMinimum", "exclusiveMaximum",
    "minLength", "maxLength", "minItems", "maxItems", "multipleOf",
})


def to_strict_json_schema(model: type[BaseModel]) -> dict:
    """Convert a Pydantic model to a provider-compatible strict JSON Schema.

    Three transforms applied in order:
    1. Inline $ref/$defs — not all providers support reference resolution.
    2. Strictify — close every object (additionalProperties: false, all
       properties required), remove default values and validation bounds.
    3. anyOf simplification — drop regex-pattern branches (Decimal, date,
       etc.) that exist only for Pydantic coercion; unwrap single survivors.
    """
    schema = model.model_json_schema()
    schema = _inline_refs(schema)
    _strictify(schema)
    return schema


def _inline_refs(schema: dict) -> dict:
    """Replace every $ref with its inlined definition and drop $defs."""
    defs = schema.get("$defs", {})
    result = _resolve(schema, defs)
    if isinstance(result, dict):
        result.pop("$defs", None)
        result.pop("definitions", None)
    return result


def _resolve(node: object, defs: dict) -> object:
    if isinstance(node, list):
        return [_resolve(item, defs) for item in node]
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        ref = node["$ref"]
        if ref.startswith("#/$defs/"):
            name = ref[len("#/$defs/"):]
            if name in defs:
                return _resolve(dict(defs[name]), defs)
        return node
    return {k: _resolve(v, defs) for k, v in node.items() if k not in ("$defs", "definitions")}


def _strictify(node: object) -> None:
    """Recursively rewrite every object schema to be strict-compatible."""
    if not isinstance(node, dict):
        return

    for key in ("default", "title", "description", "examples", "deprecated"):
        node.pop(key, None)
    for key in _VALIDATION_BOUNDS:
        node.pop(key, None)

    # Drop regex-only branches from anyOf (Pydantic emits these for Decimal /
    # date / constrained strings). If a single clean branch remains, unwrap it.
    if "anyOf" in node:
        branches = node["anyOf"]
        if isinstance(branches, list):
            clean = [b for b in branches if not (isinstance(b, dict) and "pattern" in b)]
            if not clean:
                clean = branches
            if len(clean) == 1:
                branch = {k: v for k, v in clean[0].items() if k not in _VALIDATION_BOUNDS}
                del node["anyOf"]
                node.update(branch)
            elif len(clean) < len(branches):
                node["anyOf"] = clean

    if node.get("type") == "object" and isinstance(node.get("properties"), dict):
        node["additionalProperties"] = False
        node["required"] = list(node["properties"].keys())
        for child in node["properties"].values():
            _strictify(child)

    for key in ("items", "not", "if", "then", "else"):
        _strictify(node.get(key))

    if isinstance(node.get("additionalProperties"), dict):
        _strictify(node["additionalProperties"])

    for key in ("anyOf", "oneOf", "allOf", "prefixItems"):
        seq = node.get(key)
        if isinstance(seq, list):
            for child in seq:
                _strictify(child)


def build_response_format(
    response_format: Optional[ResponseFormat],
) -> Optional[dict]:
    """Normalize any accepted ``response_format`` form to the API dict.

    Returns ``None`` when no format is requested. Raises ``TypeError``
    for an unsupported type so a caller mistake fails loudly instead of
    being silently dropped.
    """
    if response_format is None:
        return None

    if isinstance(response_format, dict):
        return response_format

    if isinstance(response_format, str):
        fmt = response_format.strip().lower()
        if fmt in _JSON_ALIASES:
            return {"type": "json_object"}
        return {"type": fmt}

    if isinstance(response_format, type) and issubclass(response_format, BaseModel):
        return {
            "type": "json_schema",
            "json_schema": {
                "name": response_format.__name__,
                "strict": True,
                "schema": to_strict_json_schema(response_format),
            },
        }

    raise TypeError(
        "response_format must be None, a str, a dict, or a Pydantic "
        f"BaseModel subclass — got {type(response_format).__name__}"
    )


def wants_json(response_format: Optional[ResponseFormat]) -> bool:
    """True if the request asked for any JSON output (object or schema)."""
    if isinstance(response_format, str):
        return response_format.strip().lower() in _JSON_ALIASES
    if isinstance(response_format, dict):
        return response_format.get("type") in ("json_object", "json_schema")
    return False
