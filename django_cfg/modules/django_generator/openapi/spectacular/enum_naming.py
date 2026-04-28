"""Enum collision detector + reporter for drf-spectacular.

drf-spectacular suffixes enum component names with a hash (e.g.
``StatusA98Enum``) when two unrelated serializers expose the same
field name with *different* choices. The hash is unstable across
schema regenerations and produces noisy diffs in generated SDKs.

This hook does **not** rename — silent rename either drops the hash
(and reintroduces the underlying collision under one shared name) or
duplicates the schema under two new names (which fragments a real
shared type). Both make the SDK lie about the API.

Instead, the hook surfaces the collision so the backend author can fix
it at the source. Two fixes work:

* Define a named ``models.TextChoices`` subclass — drf-spectacular uses
  the class name and the hash disappears.
* Add an explicit entry to ``SpectacularConfig.enum_name_overrides``
  — turns into ``ENUM_NAME_OVERRIDES`` for drf-spectacular.

Behaviour is controlled by ``SpectacularConfig.enum_collision_policy``:

* ``"ignore"`` — no output (legacy behaviour).
* ``"warn"``   — log a structured report (default).
* ``"error"``  — log the report and raise ``EnumCollisionError`` so CI
  blocks the regeneration until the source is fixed.

The companion ``manage.py suggest_enum_overrides`` command prints a
ready-to-copy ``ENUM_NAME_OVERRIDES`` dict derived from the current
schema, so existing collisions can be locked down without touching
serializer code.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


_RE_HASH_SUFFIX = re.compile(r"^(?P<base>[A-Za-z][A-Za-z0-9]*?)(?P<hash>[0-9a-fA-F]{3,})Enum$")


class EnumCollisionError(RuntimeError):
    """Raised when ``enum_collision_policy='error'`` and collisions exist."""


def auto_fix_enum_names(result: Dict[str, Any], generator, request, public) -> Dict[str, Any]:
    """drf-spectacular postprocessing hook — collision detector + reporter.

    Name kept for backward compatibility with existing
    ``POSTPROCESSING_HOOKS`` entries; behaviour is detect-only now.
    """

    schemas = (result.get("components") or {}).get("schemas") or {}
    if not schemas:
        return result

    collisions = _find_collisions(schemas)
    if not collisions:
        return result

    policy = _resolve_policy()
    if policy == "ignore":
        return result

    report = _format_report(collisions)
    logger.warning("\n%s", report)

    if policy == "error":
        raise EnumCollisionError(
            f"{len(collisions)} enum naming collision(s) detected — see warning above. "
            "Fix at source (named TextChoices subclass) or pin via "
            "SpectacularConfig.enum_name_overrides."
        )

    return result


def find_enum_collisions(schemas: Dict[str, Any]) -> List[Tuple[str, List[Tuple[str, str, List[Any]]]]]:
    """Public helper used by the ``suggest_enum_overrides`` command.

    Returns a list of ``(enum_name, [(model, field, choices), ...])``
    entries — one per collided enum, sorted by name.
    """
    return _find_collisions(schemas)


def _find_collisions(
    schemas: Dict[str, Any],
) -> List[Tuple[str, List[Tuple[str, str, List[Any]]]]]:
    """Scan ``components.schemas`` for hash-suffixed enums and collect
    every ``(model, field)`` that references each of them."""
    refs: Dict[str, List[Tuple[str, str]]] = {}

    for schema_name, schema in schemas.items():
        if not isinstance(schema, dict):
            continue
        if schema.get("type") != "object":
            continue
        properties = schema.get("properties") or {}
        if not isinstance(properties, dict):
            continue

        model_name = _extract_model_name(schema_name)
        for field_name, field_schema in properties.items():
            enum_name = _ref_to_enum_name(field_schema)
            if enum_name is None:
                continue
            refs.setdefault(enum_name, []).append((model_name, field_name))

    out: List[Tuple[str, List[Tuple[str, str, List[Any]]]]] = []
    for enum_name, sources in sorted(refs.items()):
        if not _is_hash_suffixed(enum_name):
            continue
        enriched = [
            (model, field, _enum_values(schemas.get(enum_name)))
            for model, field in sources
        ]
        out.append((enum_name, enriched))
    return out


def _ref_to_enum_name(field_schema: Any) -> str | None:
    """Extract an enum component name from a property schema.

    Supports direct ``$ref`` references and the
    ``component_split_request=True`` pattern where a property is wrapped
    as ``{"allOf": [{"$ref": ...}], ...}``.
    """
    if not isinstance(field_schema, dict):
        return None

    ref = field_schema.get("$ref")
    if isinstance(ref, str) and "#/components/schemas/" in ref:
        return ref.rsplit("/", 1)[-1]

    all_of = field_schema.get("allOf")
    if isinstance(all_of, list):
        for item in all_of:
            if not isinstance(item, dict):
                continue
            inner = item.get("$ref")
            if isinstance(inner, str) and "#/components/schemas/" in inner:
                return inner.rsplit("/", 1)[-1]

    return None


def _is_hash_suffixed(enum_name: str) -> bool:
    """True for drf-spectacular's collision-mangled names like
    ``StatusA98Enum`` or ``Status50eEnum`` — base word + 3+ hex chars +
    ``Enum``. Short single-word names like ``StatusEnum`` are *not*
    flagged: those are stable and likely intentional."""
    match = _RE_HASH_SUFFIX.match(enum_name)
    if match is None:
        return False
    hash_part = match.group("hash")
    # Must contain at least one digit AND at least one alpha to count as
    # a hex hash (otherwise `Status123` could be a real model name).
    has_digit = any(c.isdigit() for c in hash_part)
    has_alpha = any(c.isalpha() for c in hash_part)
    return has_digit and has_alpha


def _extract_model_name(schema_name: str) -> str:
    name = schema_name
    if name.startswith("Paginated") and name.endswith("List"):
        name = name[len("Paginated") : -len("List")]
    for suffix in ("Request", "Response", "Detail", "List", "Create", "Update", "Serializer"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name or schema_name


def _enum_values(schema: Any) -> List[Any]:
    if not isinstance(schema, dict):
        return []
    values = schema.get("enum")
    if isinstance(values, list):
        return list(values)
    return []


def _format_report(
    collisions: List[Tuple[str, List[Tuple[str, str, List[Any]]]]],
) -> str:
    # Suggested canonical name per collision — informational only.
    # Concrete dotted-path / literal-choices values are produced by
    # `manage.py suggest_enum_overrides` (it has access to TextChoices
    # subclasses; this hook only sees the rendered schema).
    suggested_names: dict[str, str] = {}
    for enum_name, sources in collisions:
        primary_model, primary_field, _ = sources[0]
        suggested_names[enum_name] = _suggest_name(primary_model, primary_field)

    lines = [
        f"⚠ drf-spectacular: {len(collisions)} enum naming collision(s) detected.",
        "  Hash suffixes (e.g. 'Status50eEnum') are unstable across regenerations",
        "  and produce noisy diffs in generated SDKs on every backend change.",
        "",
        "  Recommended fix — pin via SpectacularConfig.enum_name_overrides:",
        "",
        "    1. Generate a copy-paste-ready dict:",
        "         python manage.py suggest_enum_overrides",
        "",
        "    2. Paste it into your DjangoConfig:",
        "",
        "         from django_cfg.models.api.drf import SpectacularConfig",
        "",
        "         config = DjangoConfig(",
        "             ...",
        "             spectacular=SpectacularConfig(",
        "                 enum_name_overrides={ ... },  # output from step 1",
        "             ),",
        "         )",
        "",
        "  drf-spectacular's ENUM_NAME_OVERRIDES is INVERTED — its KEY is the",
        "  desired enum name, and its VALUE is a dotted path to a TextChoices",
        "  subclass (or a literal choices list). The suggest command resolves",
        "  TextChoices classes by matching their values to each collision and",
        "  picks dotted paths automatically.",
        "",
        "  Alternative — rename at source: define a named `models.TextChoices`",
        "  subclass (e.g. `class SystemHealthStatus(models.TextChoices): ...`)",
        "  per usage. drf-spectacular picks the class name and the hash",
        "  disappears.",
        "",
        "  Per-collision detail:",
    ]
    for enum_name, sources in collisions:
        lines.append(f"  • {enum_name}  →  suggest naming as `{suggested_names[enum_name]}`")
        for model, field, values in sources:
            preview = ", ".join(map(str, values[:6]))
            if len(values) > 6:
                preview += ", …"
            lines.append(f"      ↳ {model}.{field}  choices=[{preview}]")
        lines.append("")
    return "\n".join(lines)


def _suggest_name(model: str, field: str) -> str:
    """Build a deterministic enum name from a model + field pair."""
    return f"{model}{field.title().replace('_', '')}Enum"


def _resolve_policy() -> str:
    """Read collision policy from settings, falling back to env, then ``warn``."""
    policy = os.environ.get("DJANGO_CFG_ENUM_COLLISION_POLICY")
    if policy:
        return policy.strip().lower()
    try:
        from django.conf import settings  # local import — Django may not be ready
    except Exception:
        return "warn"
    value = getattr(settings, "DJANGO_CFG_ENUM_COLLISION_POLICY", None)
    if isinstance(value, str) and value:
        return value.strip().lower()
    return "warn"


__all__ = [
    "auto_fix_enum_names",
    "find_enum_collisions",
    "EnumCollisionError",
]
