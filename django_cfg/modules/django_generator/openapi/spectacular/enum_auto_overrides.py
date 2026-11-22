"""Auto-populate ENUM_NAME_OVERRIDES from discovered TextChoices classes.

drf-spectacular's ``postprocess_schema_enums`` generates hash-suffixed
enum names (e.g. ``Status03aEnum``) when multiple serializer fields
share the same choice values. The fix is to provide
``ENUM_NAME_OVERRIDES`` — but maintaining it manually is fragile.

This hook runs **before** ``postprocess_schema_enums`` in the
postprocessing pipeline. It discovers every ``TextChoices`` /
``IntegerChoices`` subclass via ``build_textchoices_index()`` and
injects ``{ClassName}Enum → dotted_path`` entries into
``spectacular_settings.ENUM_NAME_OVERRIDES``.

User-provided overrides always take priority. Ambiguous value-sets
(multiple classes with identical values) are skipped.
"""

from __future__ import annotations

import logging

from .enum_overrides_service import build_textchoices_index

logger = logging.getLogger(__name__)


def _choice_hash(choices):
    """Return drf-spectacular's hash for an override value.

    A project may pin a choice set with a literal list while discovery finds
    the same set through a ``TextChoices`` class (or vice versa). Comparing
    only dotted paths therefore misses duplicate names and makes schema
    generation fail with ``ENUM_NAME_OVERRIDES has duplication issues``.
    Keep this normalization in one place and compare the actual wire choices.
    """
    from enum import Enum

    from drf_spectacular.plumbing import Choices, deep_import_string, list_hash

    try:
        if isinstance(choices, str):
            choices = deep_import_string(choices)
        if isinstance(choices, type) and issubclass(choices, Choices):
            choices = choices.choices
        if isinstance(choices, type) and issubclass(choices, Enum):
            choices = [(choice.value, choice.name) for choice in choices]
        if callable(choices):
            choices = choices()

        normalized = []
        for choice in choices:
            if isinstance(choice, str) or choice is None:
                normalized.append((choice, choice))
            elif isinstance(choice[1], (list, tuple)):
                normalized.extend(choice[1])
            else:
                normalized.append(choice)
        return list_hash([(value, label) for value, label in normalized if value not in ("", None)])
    except (ImportError, AttributeError, TypeError, ValueError):
        # Keep the generator's existing best-effort behaviour for an invalid
        # override. drf-spectacular will emit its normal diagnostic later.
        return None


def auto_populate_enum_overrides(result, generator, **kwargs):
    """drf-spectacular postprocessing hook — inject auto-discovered overrides.

    Must be listed **before** ``postprocess_schema_enums`` in
    ``POSTPROCESSING_HOOKS`` so the overrides are available when that
    hook calls ``load_enum_name_overrides()``.
    """
    from drf_spectacular.plumbing import _load_enum_name_overrides
    from drf_spectacular.settings import spectacular_settings

    choices_index = build_textchoices_index()

    existing = dict(spectacular_settings.ENUM_NAME_OVERRIDES)
    existing_paths = {path for path in existing.values() if isinstance(path, str)}
    existing_hashes = {
        digest for digest in (_choice_hash(choices) for choices in existing.values()) if digest is not None
    }

    enum_suffix = spectacular_settings.ENUM_SUFFIX  # default "Enum"

    auto_overrides = {}
    for _value_set, dotted_paths in choices_index.items():
        if len(dotted_paths) != 1:
            # Ambiguous — multiple classes share the same values.
            # Let the collision detector report it.
            continue
        dotted_path = dotted_paths[0]
        # A project may intentionally pin the same TextChoices class to a
        # context-specific component name (for example a list field whose
        # public name is ``OperatingSystemsEnum``). Do not add a second,
        # auto-derived alias for that class: drf-spectacular treats the two
        # names as a duplicate choice set and aborts schema validation.
        if dotted_path in existing_paths:
            continue
        if (digest := _choice_hash(dotted_path)) in existing_hashes:
            # The project already selected a stable name for this exact wire
            # choice set. Adding an auto-derived alias would make
            # drf-spectacular reject the entire schema as ambiguous.
            continue
        class_name = dotted_path.rsplit(".", 1)[-1]
        # Strip trailing "Choices" if present, then add "Enum".
        # e.g. VehicleStatusChoices → VehicleStatusEnum
        #      CRMClientSource → CRMClientSourceEnum
        base = class_name
        if base.endswith("Choices") and len(base) > len("Choices"):
            base = base[: -len("Choices")]
        enum_name = f"{base}{enum_suffix}"
        if enum_name not in existing:
            auto_overrides[enum_name] = dotted_path
            if digest is not None:
                existing_hashes.add(digest)

    if not auto_overrides:
        return result

    # User overrides take priority over auto-discovered ones.
    merged = {**auto_overrides, **existing}

    # Patch settings in-place so load_enum_name_overrides() picks them up.
    spectacular_settings.ENUM_NAME_OVERRIDES = merged

    # Clear the LRU cache so the next call re-reads patched settings.
    _load_enum_name_overrides.cache_clear()

    logger.debug(
        "Auto-populated %d enum overrides (%d existing, %d auto-discovered)",
        len(merged),
        len(existing),
        len(auto_overrides),
    )

    return result


__all__ = ["auto_populate_enum_overrides"]
