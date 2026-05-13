"""drf-spectacular postprocessing hooks for django_generator.

Verbatim copy from django_client_old/spectacular/. Path strings referenced
from `SPECTACULAR_SETTINGS["POSTPROCESSING_HOOKS"]` must use the constants
below — never raw strings.
"""

from .async_detection import (
    mark_async_operations,
)
from .enum_auto_overrides import (
    auto_populate_enum_overrides,
)
from .enum_naming import (
    EnumCollisionError,
    auto_fix_enum_names,
    find_enum_collisions,
)
from .enum_overrides_service import (
    ChoiceClassSuggestion,
    ChoiceLiteralSuggestion,
    SuggestEnumOverridesResult,
    suggest_enum_overrides,
)
from .schema import PathBasedAutoSchema

POSTPROCESSING_HOOKS = (
    "django_cfg.modules.django_generator.openapi.spectacular.enum_auto_overrides.auto_populate_enum_overrides",
    "django_cfg.modules.django_generator.openapi.spectacular.async_detection.mark_async_operations",
    "django_cfg.modules.django_generator.openapi.spectacular.enum_naming.auto_fix_enum_names",
)

DEFAULT_SCHEMA_CLASS = (
    "django_cfg.modules.django_generator.openapi.spectacular.schema.PathBasedAutoSchema"
)


__all__ = [
    "auto_populate_enum_overrides",
    "auto_fix_enum_names",
    "EnumCollisionError",
    "find_enum_collisions",
    "ChoiceClassSuggestion",
    "ChoiceLiteralSuggestion",
    "SuggestEnumOverridesResult",
    "suggest_enum_overrides",
    "mark_async_operations",
    "PathBasedAutoSchema",
    "POSTPROCESSING_HOOKS",
    "DEFAULT_SCHEMA_CLASS",
]
