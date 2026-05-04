"""Per-target spec slicing by OpenAPI tag.

Ported verbatim from cmdop_server/src/devtools/generator/core/slicer.py.

Rules:
  1. Drop operations whose `tags ∩ allowed == ∅` (after normalization —
     ``"API Keys"`` matches ``"api_keys"`` in `Target.groups`).
  2. Walk kept operations, collect transitive `$ref` closure.
  3. Drop `components.schemas.X` not in the closure.
  4. Empty `allowed` → pass-through (return spec unchanged).
"""

from __future__ import annotations

import copy
import json
import re
from typing import Any

_HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
_REF_RE = re.compile(r'"\$ref":\s*"#/components/schemas/([^"]+)"')
_NORMALIZE_RE = re.compile(r"[\s\-–—]+")


def _normalize_tag(tag: str) -> str:
    """Compare-friendly form: lowercase, spaces/dashes → underscore.

    drf-spectacular's tag inference yields a mix of forms — auto path
    tags are snake_case, ``extend_schema(tags=[...])`` often uses
    "Title Case" or "kebab-case". `Target.groups` uses snake_case to
    match Django app names. Normalizing both sides means a group named
    ``"api_keys"`` matches ops tagged ``"API Keys"`` or ``"api-keys"``.
    """
    return _NORMALIZE_RE.sub("_", tag.strip().lower())


def slice_by_tags(spec: dict[str, Any], allowed_tags: set[str]) -> dict[str, Any]:
    if not allowed_tags:
        return spec

    norm_allowed = {_normalize_tag(t) for t in allowed_tags}

    sliced = copy.deepcopy(spec)
    paths: dict[str, Any] = sliced.get("paths", {})

    for path, item in list(paths.items()):
        if not isinstance(item, dict):
            continue
        for method in list(item.keys()):
            if method.lower() not in _HTTP_METHODS:
                continue
            op = item[method]
            if not isinstance(op, dict):
                continue
            op_tags = {_normalize_tag(t) for t in (op.get("tags") or [])}
            if not op_tags & norm_allowed:
                del item[method]
        if not any(m.lower() in _HTTP_METHODS for m in item):
            del paths[path]

    schemas: dict[str, Any] = sliced.get("components", {}).get("schemas", {})
    if schemas:
        kept = _closure(paths, schemas)
        for name in list(schemas.keys()):
            if name not in kept:
                del schemas[name]

    return sliced


def _closure(paths: dict[str, Any], schemas: dict[str, Any]) -> set[str]:
    seeds = _refs_in(paths)
    seen: set[str] = set()
    queue = list(seeds)
    while queue:
        name = queue.pop()
        if name in seen or name not in schemas:
            continue
        seen.add(name)
        queue.extend(_refs_in(schemas[name]))
    return seen


def _refs_in(obj: Any) -> list[str]:
    text = json.dumps(obj, ensure_ascii=False, sort_keys=True)
    return _REF_RE.findall(text)


__all__ = ["slice_by_tags"]
