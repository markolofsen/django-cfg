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

    enum_suffix = spectacular_settings.ENUM_SUFFIX  # default "Enum"

    auto_overrides = {}
    for _value_set, dotted_paths in choices_index.items():
        if len(dotted_paths) != 1:
            # Ambiguous — multiple classes share the same values.
            # Let the collision detector report it.
            continue
        dotted_path = dotted_paths[0]
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
