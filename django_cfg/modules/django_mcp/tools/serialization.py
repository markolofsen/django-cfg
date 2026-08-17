"""Shared JSON-safe serialization of Django model instances for MCP tools.

This module exists because the same four-branch conversion block was copy-pasted
into three places — ``QueryModelTool.execute``, ``GetObjectTool.execute`` and
``EnhancedQueryTool._serialize_queryset`` — and carried the identical bug in all
three. Any future field type that needs special handling should be taught here
once, not in triplicate.

The bug: Django's ``FieldFile`` (the value behind a ``FileField``/``ImageField``)
defines ``__iter__``, proxying ``File.__iter__`` into ``chunks()``. A generic
``hasattr(value, "__iter__")`` test therefore captured every file field, and
``list(value)`` either raised ``ValueError: The 'x' attribute has no file
associated with it`` (no file set) or silently dumped the file's raw byte chunks
into the JSON payload (file set) — an unbounded blob of exactly the kind the MCP
exposure rules exist to prevent.
"""

from __future__ import annotations

from typing import Any, Dict, Iterable

from django.db import models
from django.db.models.fields.files import FieldFile


def serialize_field_value(value: Any) -> Any:
    """Convert a single model field value into something JSON-safe.

    Anything not handled explicitly is returned untouched and left to
    ``json.dumps(..., default=str)`` at the call site (Decimal, UUID, ...).
    """
    # Related instance -> primary key.
    if isinstance(value, models.Model):
        return value.pk if value else None

    # FILES MUST BE CHECKED BEFORE THE GENERIC __iter__ DUCK-TYPE BELOW.
    # This ordering is the actual fix, and it is load-bearing: FieldFile
    # satisfies both `hasattr(value, "__iter__")` and (via chunks()) iteration,
    # so if the generic branch runs first it wins and we are back to either a
    # ValueError on an empty file or a payload full of file bytes. We return
    # `.name` — the relative storage path — and deliberately NOT `.url`, which
    # raises when no storage URL is configured and would just reintroduce the
    # same class of bug.
    if isinstance(value, FieldFile):
        return value.name or None

    # datetime / date / time.
    if hasattr(value, "isoformat"):
        return value.isoformat()

    # Genuinely iterable, non-file values: JSONField lists, ArrayField, ...
    if hasattr(value, "__iter__") and not isinstance(value, str):
        return list(value)

    return value


def serialize_instance(obj: models.Model, hidden_fields: Iterable[str]) -> Dict[str, Any]:
    """Serialize a model instance's concrete fields, skipping ``hidden_fields``."""
    hidden = set(hidden_fields or ())
    obj_data: Dict[str, Any] = {}
    for field in obj._meta.fields:
        if field.name in hidden:
            continue
        obj_data[field.name] = serialize_field_value(getattr(obj, field.name))
    return obj_data


def serialize_queryset(qs: Iterable[models.Model], hidden_fields: Iterable[str]) -> list[Dict[str, Any]]:
    """Serialize an iterable of model instances into a list of JSON-safe dicts."""
    return [serialize_instance(obj, hidden_fields) for obj in qs]
