"""
List filters on stock Django pieces.

- ``DropdownFilter``: a ``SimpleListFilter`` rendered as a ``<select>``.
- ``ChoicesDropdownFilter`` / ``RelatedDropdownFilter`` / ``AllValuesDropdownFilter``:
  the stock field filters rendered as a ``<select>``.
- ``AutocompleteFilter``: a foreign key filter on the stock ``AutocompleteSelect``
  widget (select2 and the ``/admin/autocomplete/`` view that ship with
  contrib.admin). The related model's admin needs ``search_fields``.
- ``TextFilter``: a case-insensitive "contains" box for one field.

Ranges come from ``django-admin-rangefilter`` (``rangefilter.filters``).
Import this module only after the app registry is ready (``FilterConfig``
resolves it lazily).
"""

from __future__ import annotations

from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import AutocompleteSelect

_DROPDOWN = "django_admin/filters/dropdown.html"


class DropdownFilter(admin.SimpleListFilter):
    """``SimpleListFilter`` as a dropdown; subclasses define ``lookups()`` and ``queryset()``."""

    template = _DROPDOWN


class ChoicesDropdownFilter(admin.ChoicesFieldListFilter):
    template = _DROPDOWN


class RelatedDropdownFilter(admin.RelatedFieldListFilter):
    template = _DROPDOWN


class AllValuesDropdownFilter(admin.AllValuesFieldListFilter):
    template = _DROPDOWN


class AutocompleteFilter(admin.RelatedFieldListFilter):
    """Foreign key filter with a select2 search box instead of a list of every row."""

    template = "django_admin/filters/autocomplete.html"

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)
        value = self.lookup_val
        if isinstance(value, (list, tuple)):
            value = value[-1] if value else None
        form_field = forms.ModelChoiceField(  # gives the widget its ModelChoiceIterator
            queryset=field.remote_field.model._default_manager.all(),
            required=False,
            widget=AutocompleteSelect(field, model_admin.admin_site),
        )
        self.widget_html = form_field.widget.render(
            self.lookup_kwarg,
            value,
            attrs={"id": f"cfg-filter-{field_path}", "data-cfg-filter": self.lookup_kwarg},
        )

    def field_choices(self, field, request, model_admin):
        return []  # the rows come from the autocomplete view, not from a full query

    def has_output(self):
        return True

    @staticmethod
    def media(admin_site) -> forms.Media:
        """select2 and Django's autocomplete script; ``CfgActionsMixin.media`` adds it once."""
        return AutocompleteSelect(None, admin_site).media


class TextFilter(admin.FieldListFilter):
    """``<field>__icontains`` from a text box."""

    template = "django_admin/filters/text.html"

    def __init__(self, field, request, params, model, model_admin, field_path):
        self.lookup_kwarg = f"{field_path}__icontains"
        super().__init__(field, request, params, model, model_admin, field_path)
        value = self.used_parameters.get(self.lookup_kwarg)
        if isinstance(value, (list, tuple)):
            value = value[-1] if value else ""
        self.value = value or ""

    def expected_parameters(self):
        return [self.lookup_kwarg]

    def has_output(self):
        return True

    def queryset(self, request, queryset):
        if self.value:
            return queryset.filter(**{self.lookup_kwarg: self.value})
        return queryset

    def choices(self, changelist):
        yield {
            "selected": not self.value,
            "query_string": changelist.get_query_string(remove=[self.lookup_kwarg]),
            "display": "All",
        }


__all__ = [
    "DropdownFilter",
    "ChoicesDropdownFilter",
    "RelatedDropdownFilter",
    "AllValuesDropdownFilter",
    "AutocompleteFilter",
    "TextFilter",
]
