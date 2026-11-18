"""
Declarative filter configuration for Django Admin list_filter.

Provides FilterConfig — a Pydantic model that converts a (field, type) declaration
into the Django-compatible entry that list_filter expects:
- ('field', FilterClass)  for FieldListFilter-based types
- A dynamic SimpleListFilter subclass  for 'dropdown' / 'dropdown_multiple'

The filter classes are stock Django, ``django_cfg.modules.django_admin.filters``
and ``rangefilter``; imports are deferred inside to_list_filter_entry() to avoid
AppRegistryNotReady errors at import time.
"""
import importlib
import warnings
from typing import Annotated, Any, Literal, Optional, Type, Union

from pydantic import BaseModel, ConfigDict, Field, SkipValidation

FilterType = Literal[
    # --- SimpleListFilter-based (dropdown UI, custom queryset) ---
    "dropdown",
    "dropdown_multiple",
    # --- FieldListFilter-based (bound to a model field) ---
    "choices_dropdown",
    "choices_dropdown_multiple",
    "choices_checkbox",
    "choices_radio",
    "boolean",
    "related_dropdown",
    "related_dropdown_multiple",
    "related_checkbox",
    "autocomplete",
    "autocomplete_multiple",
    "range_numeric",
    "slider",
    "range_date",
    "range_datetime",
    "text",
]

_F = "django_cfg.modules.django_admin.filters"
_RANGE = "rangefilter.filters"

# Dotted import paths, resolved lazily at to_list_filter_entry() call time.
# Each entry: (path, note). A note means the kind has no exact stock
# equivalent: the nearest filter is used and a FilterFallbackWarning says so.
_FILTER_TYPE_TO_PATH: dict[str, tuple[str, str]] = {
    # SimpleListFilter subclasses
    "dropdown":                  (f"{_F}.DropdownFilter", ""),
    "dropdown_multiple":         (f"{_F}.DropdownFilter", "single choice, no multi-select"),
    # FieldListFilter subclasses
    "choices_dropdown":          (f"{_F}.ChoicesDropdownFilter", ""),
    "choices_dropdown_multiple": (f"{_F}.ChoicesDropdownFilter", "single choice, no multi-select"),
    "choices_checkbox":          ("django.contrib.admin.ChoicesFieldListFilter", "a link list, single choice"),
    "choices_radio":             ("django.contrib.admin.ChoicesFieldListFilter", ""),
    "boolean":                   ("django.contrib.admin.BooleanFieldListFilter", ""),
    "related_dropdown":          (f"{_F}.RelatedDropdownFilter", ""),
    "related_dropdown_multiple": (f"{_F}.RelatedDropdownFilter", "single choice, no multi-select"),
    "related_checkbox":          ("django.contrib.admin.RelatedFieldListFilter", "a link list, single choice"),
    "autocomplete":              (f"{_F}.AutocompleteFilter", ""),
    "autocomplete_multiple":     (f"{_F}.AutocompleteFilter", "single choice, no multi-select"),
    "range_numeric":             (f"{_RANGE}.NumericRangeFilter", ""),
    "slider":                    (f"{_RANGE}.NumericRangeFilter", "two number boxes, no slider"),
    "range_date":                (f"{_RANGE}.DateRangeFilter", ""),
    "range_datetime":            (f"{_RANGE}.DateTimeRangeFilter", ""),
    "text":                      (f"{_F}.TextFilter", ""),
}

# These require a dynamic SimpleListFilter subclass (not a tuple)
_SIMPLE_LIST_FILTER_TYPES: frozenset[str] = frozenset({"dropdown", "dropdown_multiple"})


class FilterFallbackWarning(UserWarning):
    """A FilterConfig type was mapped to the nearest stock filter."""


def _import_class(dotted_path: str) -> type:
    module_path, _, class_name = dotted_path.rpartition(".")
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


class FilterConfig(BaseModel):
    """
    Declarative configuration for a single list_filter entry.

    Converts to the Django-compatible form that list_filter expects.
    Mix freely with raw strings, classes, and tuples in the same list_filter.

    Examples::

        config = AdminConfig(
            list_filter=[
                FilterConfig(field='status', type='choices_dropdown'),
                FilterConfig(field='amount', type='range_numeric'),
                FilterConfig(field='created_at', type='range_date'),
                FilterConfig(field='user', type='autocomplete'),
                FilterConfig(field='brand', type='related_dropdown'),
                FilterConfig(field='is_active', type='boolean'),
                # Raw entries still work:
                'source',
                ('price', MyCustomFilter),
            ],
        )

    Notes:
        - ``autocomplete`` / ``autocomplete_multiple`` require the related model's
          admin to define ``search_fields``.
        - ``dropdown`` / ``dropdown_multiple`` are ``SimpleListFilter``-based and
          need Django's ``queryset()`` and ``lookups()`` logic — for pure field
          filtering prefer ``choices_dropdown`` or ``related_dropdown``.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    field: str = Field(..., description="Model field name to filter on")
    type: Union[FilterType, None] = Field(
        default=None,
        description="Filter type. Required unless filter_class is set.",
    )
    filter_class: Annotated[Optional[Type[Any]], SkipValidation] = Field(
        None,
        description="Raw Django filter class. Bypasses type lookup.",
    )
    title: Optional[str] = Field(
        None,
        description="Human-readable filter title (only used for SimpleListFilter types).",
    )

    def to_list_filter_entry(self) -> Any:
        """
        Convert to a Django-compatible list_filter entry.

        Returns:
            - A dynamic SimpleListFilter subclass for 'dropdown' / 'dropdown_multiple'
            - A ('field', FilterClass) tuple for all FieldListFilter-based types
            - The raw filter_class (or tuple) when filter_class is explicitly set
        """
        if self.filter_class is not None:
            from django.contrib.admin import SimpleListFilter
            if issubclass(self.filter_class, SimpleListFilter):
                return self.filter_class
            return (self.field, self.filter_class)

        if self.type is None:
            raise ValueError(
                f"FilterConfig for field '{self.field}' must set either 'type' or 'filter_class'."
            )

        dotted, note = _FILTER_TYPE_TO_PATH[self.type]
        if note:
            warnings.warn(
                f"FilterConfig(field={self.field!r}, type={self.type!r}) renders as {dotted.rsplit('.', 1)[-1]}: "
                f"{note}. Pick a type without a fallback to silence this.",
                FilterFallbackWarning,
                stacklevel=2,
            )
        cls = _import_class(dotted)

        if self.type in _SIMPLE_LIST_FILTER_TYPES:
            # SimpleListFilter subclasses require title + parameter_name on the class.
            # Create a minimal dynamic subclass — the standard Django pattern.
            _title = self.title or self.field.replace("_", " ").title()
            return type(
                f"{self.field}_filter",
                (cls,),
                {"title": _title, "parameter_name": self.field},
            )

        # FieldListFilter-based: standard ('field', FilterClass) tuple
        return (self.field, cls)


__all__ = ["FilterType", "FilterConfig", "FilterFallbackWarning"]
