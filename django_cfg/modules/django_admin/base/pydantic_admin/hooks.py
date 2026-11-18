"""
Changelist and change form extensions on the stock Django admin.

Replaces what the Unfold ModelAdmin base used to give ``PydanticAdmin``:

- ``actions_list``: buttons above the changelist (``action`` decorated methods,
  signature ``(self, request)``); ``action(method="post")`` (the default) renders
  a POST form with the CSRF token and the URL answers 405 to GET,
  ``method="get"`` a link to a page that handles its own form;
- ``actions_detail``: buttons on the change form (``(self, request, object_id)``);
  both entries may be a method name or a group ``{"title": ..., "icon": ...,
  "items": [names]}`` rendered as a dropdown;
- template hooks ``list_before_template``, ``list_after_template``,
  ``change_form_before_template``, ``change_form_after_template``,
  ``change_form_outer_before_template``, ``change_form_outer_after_template``.

Templates: ``django_admin/change_list.html`` (the import/export changelist
plus our blocks) and ``django_admin/change_form.html`` (extends the template
Django would have chosen, passed in as ``cfg_change_form_base``).
"""

from __future__ import annotations

import warnings
from functools import update_wrapper
from typing import Any, Optional

from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.http import HttpResponseNotAllowed
from django.template.loader import select_template
from django.urls import path, reverse

#: Unfold ModelAdmin attributes that have no effect on the stock admin. A
#: project that sets one gets a warning at class creation; delete the line.
DROPPED_UNFOLD_ATTRIBUTES: dict[str, str] = {
    "compressed_fields": "stock fieldsets have one layout",
    "conditional_fields": "no conditional fields on the stock admin; hide fields in get_fieldsets()",
    "warn_unsaved_form": "the stock admin has no unsaved-form warning",
    "readonly_preprocess_fields": "format the value in a display method instead",
    "list_filter_submit": "stock filters apply on click",
    "list_filter_sheet": "stock filters sit in the right column",
    "list_filter_options": "stock filters have no options",
    "list_fullwidth": "the stock changelist width is fixed by Django",
    "list_horizontal_scrollbar_top": "not available on the stock changelist",
    "list_disable_select_all": "not available on the stock changelist",
    "list_sections": "render the extra rows in list_after_template",
    "actions_row": "use actions_detail (a button on the change form)",
    "actions_submit_line": "use actions_detail (a button on the change form)",
    "actions_list_hide_default": "stock object-tools always show Add",
    "actions_detail_hide_default": "stock object-tools always show History",
    "change_form_datasets": "render the data in change_form_after_template",
    "ordering_field": "use list_editable or a custom action",
    "hide_ordering_field": "use list_editable or a custom action",
    "custom_urls": "override get_urls()",
    "show_add_link": "override has_add_permission()",
}


class DroppedUnfoldAttributeWarning(UserWarning):
    """An admin class sets an Unfold-only attribute that the stock admin ignores."""


def warn_dropped_attributes(cls) -> list[str]:
    """Warn for each Unfold-only attribute the class itself sets; return the names."""
    found = [name for name in DROPPED_UNFOLD_ATTRIBUTES if name in cls.__dict__]
    for name in found:
        warnings.warn(
            f"{cls.__module__}.{cls.__qualname__}.{name} is an Unfold attribute and has no effect "
            f"since django-cfg dropped Unfold: {DROPPED_UNFOLD_ATTRIBUTES[name]}. Delete it.",
            DroppedUnfoldAttributeWarning,
            stacklevel=3,
        )
    return found


class CfgActionsMixin:
    """``actions_list`` / ``actions_detail`` buttons and the template hooks."""

    actions_list: tuple | list = ()
    actions_detail: tuple | list = ()

    list_before_template: Optional[str] = None
    list_after_template: Optional[str] = None
    change_form_before_template: Optional[str] = None
    change_form_after_template: Optional[str] = None
    change_form_outer_before_template: Optional[str] = None
    change_form_outer_after_template: Optional[str] = None

    #: The leaf changelist template; import_export puts a project's own
    #: ``change_list_template`` underneath it (``ie_base_change_list_template``).
    import_export_change_list_template = "django_admin/change_list.html"
    change_form_template = "django_admin/change_form.html"
    #: A project's own ``change_form_template`` moves here (see ``__init_subclass__``).
    cfg_base_change_form_template: Optional[str] = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        own = cls.__dict__.get("change_form_template")
        if own and own != CfgActionsMixin.change_form_template:
            cls.cfg_base_change_form_template = own
            cls.change_form_template = CfgActionsMixin.change_form_template
        warn_dropped_attributes(cls)

    # ------------------------------------------------------------------ names

    @staticmethod
    def _cfg_action_names(entries) -> list[str]:
        names: list[str] = []
        for entry in entries or ():
            if isinstance(entry, str):
                names.append(entry)
            elif isinstance(entry, dict) and "items" in entry:
                names.extend(entry["items"])
            else:
                raise ImproperlyConfigured(
                    f"actions_list / actions_detail entries are method names or "
                    f"{{'title': ..., 'items': [...]}} groups, got {entry!r}"
                )
        return names

    def _cfg_url_name(self, name: str) -> str:
        opts = self.model._meta
        return f"{opts.app_label}_{opts.model_name}_{name}"

    def _cfg_method(self, name: str):
        method = getattr(self, name, None)
        if method is None or not callable(method):
            raise ImproperlyConfigured(f"{type(self).__name__}: action {name!r} is not a method")
        return method

    # ------------------------------------------------------------------- URLs

    def get_urls(self):
        urls = super().get_urls()

        def wrap(view, detail: bool):
            def wrapper(request, *args, **kwargs):
                # An action that changes something runs on POST only (a GET link
                # is a CSRF hole: <img src=".../purge/"> on any page would run it).
                if getattr(view, "method", "post") == "post" and request.method != "POST":
                    return HttpResponseNotAllowed(["POST"])
                if not self._cfg_action_allowed(request, view, kwargs.get("object_id") if detail else None):
                    raise PermissionDenied
                return view(request, *args, **kwargs)

            wrapper = update_wrapper(wrapper, view)
            wrapper.model_admin = self
            return self.admin_site.admin_view(wrapper)

        extra = []
        for name in self._cfg_action_names(self.actions_list):
            method = self._cfg_method(name)
            segment = getattr(method, "url_path", name).strip("/")
            extra.append(path(f"{segment}/", wrap(method, False), name=self._cfg_url_name(name)))
        for name in self._cfg_action_names(self.actions_detail):
            method = self._cfg_method(name)
            segment = getattr(method, "url_path", name).strip("/")
            extra.append(
                path(f"<path:object_id>/{segment}/", wrap(method, True), name=self._cfg_url_name(name))
            )
        return extra + urls

    # ------------------------------------------------------------ permissions

    def _cfg_action_allowed(self, request, method, object_id=None) -> bool:
        for permission in getattr(method, "allowed_permissions", None) or ():
            if "." in permission:
                if not request.user.has_perm(permission):
                    return False
                continue
            check = getattr(self, f"has_{permission}_permission", None)
            if check is None:
                raise ImproperlyConfigured(
                    f"{type(self).__name__}: action permission {permission!r} needs a "
                    f"has_{permission}_permission() method"
                )
            if not (check(request, object_id) if object_id is not None else check(request)):
                return False
        return True

    # ------------------------------------------------------------------ media

    @property
    def media(self):
        """Stock media, plus select2 once when a list filter is an ``AutocompleteFilter``."""
        from ...filters import AutocompleteFilter

        media = super().media
        for entry in getattr(self, "list_filter", None) or ():
            cls = entry[1] if isinstance(entry, (tuple, list)) and len(entry) == 2 else entry
            if isinstance(cls, type) and issubclass(cls, AutocompleteFilter):
                return media + AutocompleteFilter.media(self.admin_site)
        return media

    # ---------------------------------------------------------------- context

    def _cfg_action_item(self, request, name: str, object_id=None) -> Optional[dict[str, Any]]:
        method = self._cfg_method(name)
        if not self._cfg_action_allowed(request, method, object_id):
            return None
        url_name = f"{self.admin_site.name}:{self._cfg_url_name(name)}"
        return {
            "title": getattr(method, "short_description", None) or name.replace("_", " ").capitalize(),
            "icon": getattr(method, "icon", None),
            "variant": getattr(method, "variant", None),
            "attrs": getattr(method, "attrs", None) or {},
            "confirm": getattr(method, "confirm", None),
            "method": getattr(method, "method", "post"),
            "path": reverse(url_name, args=(object_id,)) if object_id is not None else reverse(url_name),
        }

    def _cfg_actions_navigation(self, request, entries, object_id=None) -> list[dict[str, Any]]:
        navigation = []
        for entry in entries or ():
            if isinstance(entry, str):
                item = self._cfg_action_item(request, entry, object_id)
                if item:
                    navigation.append(item)
            else:
                items = [
                    item for item in (
                        self._cfg_action_item(request, name, object_id) for name in entry["items"]
                    ) if item
                ]
                if items:
                    navigation.append({
                        "title": entry.get("title", ""),
                        "icon": entry.get("icon"),
                        "variant": None if entry.get("variant") in (None, "default") else entry.get("variant"),
                        "children": items,  # not "items": a template reads dict.items as the method
                    })
        return navigation

    def changelist_view(self, request, extra_context=None):
        extra_context = dict(extra_context or {})
        extra_context["cfg_actions_list"] = self._cfg_actions_navigation(request, self.actions_list)
        return super().changelist_view(request, extra_context)

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        extra_context = dict(extra_context or {})
        if object_id:
            extra_context["cfg_actions_detail"] = self._cfg_actions_navigation(
                request, self.actions_detail, object_id
            )
        return super().changeform_view(request, object_id, form_url, extra_context)

    def render_change_form(self, request, context, add=False, change=False, form_url="", obj=None):
        opts = self.model._meta
        names = (
            [self.cfg_base_change_form_template]
            if self.cfg_base_change_form_template
            else [
                f"admin/{opts.app_label}/{opts.model_name}/change_form.html",
                f"admin/{opts.app_label}/change_form.html",
                "admin/change_form.html",
            ]
        )
        context["cfg_change_form_base"] = select_template(names)
        return super().render_change_form(request, context, add, change, form_url, obj)
