"""Detect ``requestBody`` shapes that crash generated clients.

django-cfg already sets ``DEFAULT_PARSER_CLASSES = [JSONParser]``
globally, so 95% of operations end up with a single ``application/json``
content-type and never trigger this audit. When this audit DOES fire,
the cause is one of:

1. **View-level override** — a ViewSet/APIView explicitly declared
   ``parser_classes = [...]`` with multipart/form parsers (often copied
   from a tutorial). Find it with::

       grep -rn 'parser_classes' apps/<app>/api/views/

2. **Serializer with FileField/ImageField/Base64ImageField** — DRF
   auto-attaches ``MultiPartParser`` for serializers that have binary
   fields, and drf-spectacular reflects that as ``multipart/form-data``.
   This is intentional for upload endpoints.

3. **``@extend_schema(request=...)`` with multiple media types** —
   explicit OpenAPI override on the operation.

4. **DRF generic action** (e.g. ``DjangoFilterBackend`` form rendering
   on browsable API) leaking parsers into schema generation.

Two failure modes we lint for:

1. **Multi content-type with nested objects** (WARNING) — multipart/form
   encoding cannot represent nested objects. ``openapi-python-client``
   generates three ``if isinstance`` branches, the multipart one wins
   at runtime, and ``httpx`` multipart encoder rejects the nested dict
   with ``Expected primitive type, got <class 'dict'>``. Real crash —
   FIX REQUIRED.

2. **Multi content-type without binary upload** (INFO) — three
   content-types declared but no FileField/ImageField found. Usually
   leftover from a view-level override. SDK still works, types are
   just wider than they need to be.

The audit walks ``paths.<url>.<method>.requestBody.content`` and
returns one human-readable line per finding. ``severity`` is either
``"warning"`` (real crash) or ``"info"`` (cosmetic). The caller
decides how to surface them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Multipart and form encoding cannot represent nested objects without
# special encoding, which most clients don't generate. We treat both
# as "non-JSON" for the audit.
_NON_JSON_CTS = ("multipart/form-data", "application/x-www-form-urlencoded")
_HTTP_METHODS = ("post", "put", "patch", "delete")


@dataclass(slots=True)
class Finding:
    severity: str  # "warning" | "info"
    path: str
    method: str
    message: str

    def format(self) -> str:
        # One line, easy to grep, matches the existing
        # ``Inline schema (no $ref)`` warning style.
        prefix = "⚠️  WARNING" if self.severity == "warning" else "ℹ️  INFO"
        return f"{prefix} {self.method.upper()} {self.path} — {self.message}"


def audit_requestbody_content_types(spec: dict[str, Any]) -> list[Finding]:
    """Lint every POST/PUT/PATCH/DELETE for risky requestBody shapes."""
    findings: list[Finding] = []
    components = (spec.get("components") or {}).get("schemas") or {}

    for path, methods in (spec.get("paths") or {}).items():
        if not isinstance(methods, dict):
            continue
        for method, op in methods.items():
            if method.lower() not in _HTTP_METHODS:
                continue
            if not isinstance(op, dict):
                continue
            content = ((op.get("requestBody") or {}).get("content")) or {}
            if not isinstance(content, dict) or len(content) <= 1:
                continue

            non_json_cts = [ct for ct in content if ct in _NON_JSON_CTS]
            if not non_json_cts:
                continue

            # Resolve the nested-object risk for the non-JSON entries.
            has_nested_obj = any(
                _schema_has_nested_object(content[ct].get("schema") or {}, components)
                for ct in non_json_cts
            )

            # File-upload endpoints intentionally need multipart and
            # don't have nested object payloads — skip them.
            has_file = any(
                _schema_has_binary(content[ct].get("schema") or {}, components)
                for ct in non_json_cts
            )

            if has_nested_obj and not has_file:
                findings.append(Finding(
                    severity="warning",
                    path=path,
                    method=method,
                    message=(
                        f"requestBody declares {', '.join(sorted(content))} "
                        "and the schema has nested objects — generated "
                        "Python clients will crash at runtime (httpx "
                        "multipart encoder: 'Expected primitive type, got "
                        "dict'). The global `DEFAULT_PARSER_CLASSES = "
                        "[JSONParser]` is set, so something is overriding "
                        "it for THIS operation. Check (in order): "
                        "(1) view-level `parser_classes = [...]` on the "
                        "ViewSet/APIView, (2) `@extend_schema(request=...)` "
                        "with explicit media types, (3) the serializer for "
                        "FileField/ImageField that auto-attaches "
                        "MultiPartParser. Remove the override or split "
                        "uploads into a dedicated endpoint."
                    ),
                ))
            elif not has_file:
                findings.append(Finding(
                    severity="info",
                    path=path,
                    method=method,
                    message=(
                        f"requestBody declares {len(content)} content-types "
                        f"({', '.join(sorted(content))}) but no binary fields. "
                        "Global `DEFAULT_PARSER_CLASSES = [JSONParser]` is set, "
                        "so this is a per-operation override leaking through. "
                        "Likely sources: view-level `parser_classes = [...]`, "
                        "`@extend_schema(request=...)`, or a Base64-style "
                        "serializer field. SDK still works (types are wider "
                        "than needed); fix only if it bothers you."
                    ),
                ))

    return findings


def _resolve_ref(schema: dict[str, Any], components: dict[str, Any]) -> dict[str, Any]:
    ref = schema.get("$ref")
    if not isinstance(ref, str):
        return schema
    # Only resolve in-document component refs — anything else (e.g.
    # external file refs) we treat as opaque.
    prefix = "#/components/schemas/"
    if not ref.startswith(prefix):
        return schema
    name = ref[len(prefix):]
    return components.get(name) or {}


def _schema_has_nested_object(
    schema: dict[str, Any], components: dict[str, Any], depth: int = 0
) -> bool:
    """``True`` if any property is itself an object or array of objects.

    Bounded recursion — most specs are shallow, but ``allOf`` / ``$ref``
    chains can loop. ``depth=8`` is enough for real APIs.
    """
    if depth > 8 or not isinstance(schema, dict):
        return False
    schema = _resolve_ref(schema, components)

    for combinator in ("allOf", "oneOf", "anyOf"):
        for sub in schema.get(combinator) or []:
            if _schema_has_nested_object(sub, components, depth + 1):
                return True

    props = schema.get("properties") or {}
    if not isinstance(props, dict):
        return False
    for prop in props.values():
        prop = _resolve_ref(prop, components)
        t = prop.get("type")
        if t == "object" or "properties" in prop:
            return True
        if t == "array":
            items = _resolve_ref(prop.get("items") or {}, components)
            if items.get("type") == "object" or "properties" in items:
                return True
        for combinator in ("allOf", "oneOf", "anyOf"):
            for sub in prop.get(combinator) or []:
                if _schema_has_nested_object(sub, components, depth + 1):
                    return True
    return False


def _schema_has_binary(
    schema: dict[str, Any], components: dict[str, Any], depth: int = 0
) -> bool:
    """``True`` if any property is a binary upload (real file field)."""
    if depth > 8 or not isinstance(schema, dict):
        return False
    schema = _resolve_ref(schema, components)
    if schema.get("format") == "binary":
        return True
    props = schema.get("properties") or {}
    if isinstance(props, dict):
        for prop in props.values():
            prop = _resolve_ref(prop, components)
            if prop.get("format") == "binary":
                return True
            if prop.get("type") == "array":
                items = _resolve_ref(prop.get("items") or {}, components)
                if items.get("format") == "binary":
                    return True
    return False


__all__ = ["Finding", "audit_requestbody_content_types"]
