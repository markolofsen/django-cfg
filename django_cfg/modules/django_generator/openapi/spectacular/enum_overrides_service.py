"""Service: resolve drf-spectacular enum collisions to ENUM_NAME_OVERRIDES.

drf-spectacular's ``ENUM_NAME_OVERRIDES`` is **inverted**: its KEY is
the desired enum name, its VALUE points at the choices set (dotted
path to a TextChoices subclass, or a literal ``[(value, label), ...]``
list). drf-spectacular hashes the choices and substitutes our key
whenever that hash appears.

This service does the resolution end-to-end:

1. Generates the OpenAPI schema and finds hash-suffixed enum names.
2. Walks every loaded Django app for ``models.Choices`` subclasses
   (TextChoices / IntegerChoices), keyed by their value-set.
3. For each collision picks the best match — unique TextChoices
   class → dotted path; multiple matches → best-name heuristic with
   the alternatives reported as ambiguous; no match → literal choices
   fallback.
4. Returns structured suggestions plus a render helper.

Both ``manage.py suggest_enum_overrides`` and the ``auto_fix_enum_names``
postprocessing hook consume this service so output stays consistent.
"""

from __future__ import annotations

import importlib
import logging
import pkgutil
from dataclasses import dataclass, field
from typing import Any

from .enum_naming import _suggest_name, find_enum_collisions

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class ChoiceClassSuggestion:
    """The desired name resolves to a single TextChoices subclass."""

    desired_name: str
    dotted_path: str
    collided_name: str


@dataclass(slots=True, frozen=True)
class ChoiceLiteralSuggestion:
    """No (or ambiguous) TextChoices class — use a literal choices list."""

    desired_name: str
    choices: list[tuple[Any, str]]
    collided_name: str


Suggestion = ChoiceClassSuggestion | ChoiceLiteralSuggestion


@dataclass(slots=True)
class SuggestEnumOverridesResult:
    suggestions: list[Suggestion] = field(default_factory=list)
    ambiguous: list[tuple[str, list[str]]] = field(default_factory=list)

    @property
    def is_empty(self) -> bool:
        return not self.suggestions

    def as_dict(self) -> dict[str, Any]:
        """Render as the JSON-style dict drf-spectacular expects."""
        out: dict[str, Any] = {}
        for s in self.suggestions:
            if isinstance(s, ChoiceClassSuggestion):
                out[s.desired_name] = s.dotted_path
            else:
                out[s.desired_name] = s.choices
        return out

    def render_python_dict(self) -> list[str]:
        """Render as Python source lines (no enclosing dict literal)."""
        lines: list[str] = []
        for s in self.suggestions:
            if isinstance(s, ChoiceClassSuggestion):
                lines.append(f"    {s.desired_name!r}: {s.dotted_path!r},")
            else:
                rendered = ", ".join(f"({v!r}, {label!r})" for v, label in s.choices)
                lines.append(f"    {s.desired_name!r}: [{rendered}],")
        return lines


def suggest_enum_overrides() -> SuggestEnumOverridesResult:
    """Compute ``ENUM_NAME_OVERRIDES`` suggestions for the current schema.

    Requires Django to be set up (``django.setup()``) — both schema
    generation and TextChoices discovery rely on the app registry.
    """
    from drf_spectacular.generators import SchemaGenerator

    schema = SchemaGenerator().get_schema(request=None, public=True)
    schemas = (schema.get("components") or {}).get("schemas") or {}
    return _suggest_from_schemas(schemas)


def _suggest_from_schemas(schemas: dict[str, Any]) -> SuggestEnumOverridesResult:
    collisions = find_enum_collisions(schemas)
    if not collisions:
        return SuggestEnumOverridesResult()

    choices_index = build_textchoices_index()

    result = SuggestEnumOverridesResult()
    for enum_name, sources in collisions:
        primary_model, primary_field, values = sources[0]
        desired = _suggest_name(primary_model, primary_field)

        value_set = frozenset(values)
        matches = choices_index.get(value_set, [])

        if len(matches) == 1:
            result.suggestions.append(
                ChoiceClassSuggestion(desired, matches[0], enum_name)
            )
        elif len(matches) > 1:
            preferred = _pick_best_class(matches, primary_model, primary_field)
            if preferred:
                result.suggestions.append(
                    ChoiceClassSuggestion(desired, preferred, enum_name)
                )
            else:
                result.suggestions.append(
                    ChoiceLiteralSuggestion(
                        desired, [(v, str(v)) for v in values], enum_name
                    )
                )
            result.ambiguous.append((desired, matches))
        else:
            result.suggestions.append(
                ChoiceLiteralSuggestion(
                    desired, [(v, str(v)) for v in values], enum_name
                )
            )

    return result


def build_textchoices_index() -> dict[frozenset, list[str]]:
    """Walk every loaded Django app and collect ``models.Choices``
    subclasses (``TextChoices`` / ``IntegerChoices``), keyed by the
    frozenset of their values. Multiple classes can share a value-set
    — that's why values are lists.

    Two passes: model attributes (nested classes inside ``class Meta``)
    and submodule scan (top-level classes in ``apps/<x>/models/choices.py``).
    """
    from django.apps import apps
    from django.db import models

    index: dict[frozenset, list[str]] = {}
    seen: set[str] = set()

    def _record(cls: type) -> None:
        if not isinstance(cls, type):
            return
        if not issubclass(cls, models.Choices):
            return
        if cls in (models.Choices, models.TextChoices, models.IntegerChoices):
            return
        try:
            value_set = frozenset(member.value for member in cls)
        except Exception:
            return
        if not value_set:
            return
        dotted = f"{cls.__module__}.{cls.__qualname__}"
        if dotted in seen:
            return
        seen.add(dotted)
        index.setdefault(value_set, []).append(dotted)

    # Pass 1: model attributes.
    for model in apps.get_models():
        for attr_name in dir(model):
            try:
                attr = getattr(model, attr_name)
            except Exception:
                continue
            _record(attr)

    # Pass 2: walk every app's submodules. TextChoices defined at module
    # scope (apps/catalog/models/choices.py) are missed by pass 1.
    for app_config in apps.get_app_configs():
        for submod in iter_app_modules(app_config.name):
            for attr_name in dir(submod):
                try:
                    attr = getattr(submod, attr_name)
                except Exception:
                    continue
                _record(attr)

    return index


# Never imported by the scan: frozen history, tests, and modules whose import
# has side effects (admin.site.register, signal wiring, URL routing).
_SKIP_PARTS = frozenset({"migrations", "tests", "admin", "signals", "urls"})


def _is_app_package(path: str) -> bool:
    """A directory with its own ``apps.py`` is a Django app."""
    import os

    return os.path.isfile(os.path.join(path, "apps.py"))


def iter_app_modules(package_name: str):
    """Yield the imported submodules of one installed app package.

    Unlike ``pkgutil.walk_packages`` it decides before importing: a nested
    package that is a Django app of its own (has ``apps.py``) is not entered.
    If that app is installed it gets its own walk; if not, nothing of it is
    imported. ``django_cfg`` is an installed app, and walking it whole used to
    import ``django_cfg.apps.payments.admin`` and register the payments admin
    in projects without payments.
    """
    import os

    try:
        module = importlib.import_module(package_name)
    except ImportError:
        return
    if not hasattr(module, "__path__"):
        return

    stack: list[tuple[list[str], str]] = [(list(module.__path__), package_name)]
    while stack:
        paths, prefix = stack.pop()
        for info in pkgutil.iter_modules(paths):
            name = info.name
            if name in _SKIP_PARTS or name.startswith("test_"):
                continue
            dotted = f"{prefix}.{name}"
            if info.ispkg:
                pkg_dir = os.path.join(getattr(info.module_finder, "path", ""), name)
                if _is_app_package(pkg_dir):
                    continue
            try:
                submod = importlib.import_module(dotted)
            # BaseException, not Exception: pytest.importorskip raises Skipped
            # (an OutcomeException → BaseException) at module scope, which would
            # otherwise abort the entire schema build.
            except BaseException:
                continue
            yield submod
            if info.ispkg and hasattr(submod, "__path__"):
                stack.append((list(submod.__path__), dotted))


def _pick_best_class(paths: list[str], model: str, field: str) -> str | None:
    """Pick the TextChoices class whose name best matches the
    ``model + field`` string. Tie-broken by stability of input order."""
    needle = (model + field).lower()
    best: tuple[int, str] | None = None
    for path in paths:
        cls_name = path.rsplit(".", 1)[-1].lower()
        score = sum(1 for ch in cls_name if ch in needle)
        if best is None or score > best[0]:
            best = (score, path)
    return best[1] if best else None


__all__ = [
    "ChoiceClassSuggestion",
    "ChoiceLiteralSuggestion",
    "Suggestion",
    "SuggestEnumOverridesResult",
    "build_textchoices_index",
    "suggest_enum_overrides",
]
