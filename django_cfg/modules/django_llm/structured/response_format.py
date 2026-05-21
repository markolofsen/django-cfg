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


def to_strict_json_schema(model: type[BaseModel]) -> dict:
    """Convert a Pydantic model to an OpenAI/OpenRouter strict JSON Schema.

    Strict structured outputs require every object to be closed
    (``additionalProperties: false``) with every property listed in
    ``required``. Pydantic's own schema satisfies neither, so the schema
    is walked and rewritten in place.
    """
    schema = model.model_json_schema()
    _strictify(schema)
    return schema


def _strictify(node: object) -> None:
    """Recursively rewrite every object schema to be strict-compatible."""
    if not isinstance(node, dict):
        return

    # `default` is emitted by Pydantic for every optional field and is
    # rejected by strict structured-output validators.
    node.pop("default", None)

    if node.get("type") == "object" and isinstance(node.get("properties"), dict):
        node["additionalProperties"] = False
        node["required"] = list(node["properties"].keys())
        for child in node["properties"].values():
            _strictify(child)

    for container in ("$defs", "definitions"):
        defs = node.get(container)
        if isinstance(defs, dict):
            for child in defs.values():
                _strictify(child)

    for key in ("items", "not", "if", "then", "else"):
        _strictify(node.get(key))

    # A typed `additionalProperties` sub-schema (dict[str, X] fields).
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
