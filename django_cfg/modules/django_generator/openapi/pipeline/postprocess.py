"""Global-spec postprocessing.

Runs once on the freshly-loaded drf-spectacular spec, before slicing.

  - enforce_tags(spec): every operation must declare ≥1 tag, else PostprocessError.
  - enforce_unique_schemas(spec): detect drf-spectacular auto-rename collisions
    (`UserProfileUpdate`, `UserProfileUpdate2`, …) and abort with a clear
    message pointing at the offending serializer classes.
  - normalize_tags(spec): lowercase + strip; collapse case duplicates.
  - nullable_3_1_to_3_0(spec): rewrite `type: ["string", "null"]` → `type: "string", nullable: true`
    for parameters and schemas. Required by ogen which only supports 3.0.
"""

from __future__ import annotations

import re
from typing import Any

from .errors import PostprocessError

_HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}

# Matches drf-spectacular's auto-rename suffix (`Foo`, `Foo2`, `Foo3`).
# When two serializers share a base name across Django apps, drf-spectacular
# silently appends a digit. We treat that as a hard error.
_AUTORENAME_SUFFIX = re.compile(r"^(?P<base>.+?)(?P<n>\d+)$")


def enforce_unique_schemas(spec: dict[str, Any]) -> None:
    """Abort if drf-spectacular silently renamed colliding schemas.

    Django apps that define serializers with the same class name produce
    `Foo`/`Foo2` pairs in the OpenAPI spec — same shape would suggest
    intentional reuse, different shapes are a project bug. We treat any
    `<Base><digit>` pair where `<Base>` exists as the latter, since
    drf-spectacular only adds the suffix on collision.
    """
    schemas = (spec.get("components") or {}).get("schemas") or {}
    if not isinstance(schemas, dict):
        return

    collisions: dict[str, list[str]] = {}
    names = set(schemas.keys())
    for name in sorted(names):
        m = _AUTORENAME_SUFFIX.match(name)
        if not m:
            continue
        base = m.group("base")
        if base in names:
            collisions.setdefault(base, [base]).append(name)

    if collisions:
        lines = []
        for base, dupes in sorted(collisions.items()):
            lines.append(f"  • {base}: {', '.join(dupes)}")
        raise PostprocessError(
            "Duplicate schema names detected (drf-spectacular auto-renamed):\n"
            + "\n".join(lines)
            + "\n\nFix: rename one of the conflicting serializer classes in your "
              "Django apps so each `components.schemas` entry has a unique name.\n"
              "Tip: search for the base name (e.g. `class UserProfileUpdate` or "
              "`UserProfileUpdateSerializer`) across your apps to find the source."
        )


def enforce_tags(spec: dict[str, Any]) -> None:
    untagged: list[str] = []
    for path, item in (spec.get("paths") or {}).items():
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            if method.lower() not in _HTTP_METHODS or not isinstance(op, dict):
                continue
            if not op.get("tags"):
                untagged.append(f"{method.upper()} {path}")
    if untagged:
        head = ", ".join(untagged[:5])
        more = f" (+{len(untagged) - 5} more)" if len(untagged) > 5 else ""
        raise PostprocessError(f"operations without tags: {head}{more}")


def normalize_tags(spec: dict[str, Any]) -> None:
    for item in (spec.get("paths") or {}).values():
        if not isinstance(item, dict):
            continue
        for method, op in item.items():
            if method.lower() not in _HTTP_METHODS or not isinstance(op, dict):
                continue
            tags = op.get("tags") or []
            if tags:
                cleaned: list[str] = []
                seen: set[str] = set()
                for t in tags:
                    s = str(t).strip()
                    if s and s.lower() not in seen:
                        cleaned.append(s)
                        seen.add(s.lower())
                op["tags"] = cleaned


def nullable_3_1_to_3_0(spec: dict[str, Any]) -> None:
    """Rewrite OpenAPI 3.1 nullable forms into 3.0-compatible shape.

    Walks the entire spec; converts:
      - `type: ["string", "null"]` → `type: "string", nullable: true`
      - parameter schemas with type-array nulls.
    Idempotent.
    """
    _walk(spec)


def _walk(node: Any) -> None:
    if isinstance(node, dict):
        types = node.get("type")
        if isinstance(types, list) and "null" in types:
            non_null = [t for t in types if t != "null"]
            if len(non_null) == 1:
                node["type"] = non_null[0]
                node["nullable"] = True
            else:
                node["type"] = non_null
                node["nullable"] = True
        for v in node.values():
            _walk(v)
    elif isinstance(node, list):
        for v in node:
            _walk(v)


__all__ = [
    "enforce_tags",
    "enforce_unique_schemas",
    "normalize_tags",
    "nullable_3_1_to_3_0",
]
