"""
The public ``action`` decorator for admin actions.

Three places an action can appear on a ``PydanticAdmin``:

- bulk: Django's action dropdown over selected rows (``ModelAdmin.actions``);
- changelist: a button above the list (``actions_list``), no selection;
- detail: a button on the change form (``actions_detail``), gets ``object_id``.

Buttons get their own URL (``base.pydantic_admin.hooks.CfgActionsMixin.get_urls``)
named ``<app_label>_<model_name>_<action>`` in the admin namespace, the names
projects already reverse.

Importable without the app registry: ``from django_cfg.modules.django_admin import action``.
"""

from __future__ import annotations

from functools import wraps
from typing import Any, Callable, Iterable, Optional

#: ``ActionConfig.variant`` / ``action(variant=...)`` values; each maps to ``cfg-action-<variant>``.
ACTION_VARIANTS = ("default", "primary", "success", "info", "warning", "danger")

DEFAULT_CONFIRMATION = "Are you sure you want to perform this action?"

#: POST field that marks the second (confirmed) submit of a bulk action: Django's own
#: ``delete_selected`` contract (``post=yes``), so a test or script that already
#: posts it the Django way runs the action.
CONFIRM_FIELD = "post"

#: ``action(method=...)`` values for ``actions_list`` / ``actions_detail`` buttons.
#: ``"post"``: the action changes something; the button is a POST form with the
#: CSRF token and a GET answers 405. ``"get"``: the action is a page (its own form,
#: a preview); the button is a link and the handler takes GET and its own POST.
ACTION_METHODS = ("post", "get")


def action(
    function: Optional[Callable] = None,
    *,
    description: Optional[str] = None,
    permissions: Optional[Iterable[str]] = None,
    url_path: Optional[str] = None,
    icon: Optional[str] = None,
    variant: Optional[str] = None,
    attrs: Optional[dict[str, Any]] = None,
    confirm: Optional[str] = None,
    method: str = "post",
) -> Callable:
    """
    Mark a ModelAdmin method as an admin action.

    Keywords: ``description``, ``permissions``, ``url_path``, ``icon``,
    ``variant``, ``attrs``, ``confirm`` and ``method``. Works for bulk actions
    (``actions``), changelist buttons (``actions_list``) and change form
    buttons (``actions_detail``) of any ``PydanticAdmin``.

    Args:
        description: label in the dropdown or on the button.
        permissions: ``"change"`` checks ``has_change_permission``;
            ``"app.codename"`` checks ``user.has_perm``. A failing check hides
            the button and the URL answers 403.
        url_path: URL segment of a button action (default: the method name).
        icon: Material Symbols name shown on the button.
        variant: one of ``ACTION_VARIANTS``; styles the button.
        attrs: extra HTML attributes of the button.
        confirm: a confirmation text. Buttons ask with ``confirm()`` before
            the POST; bulk actions show an intermediate confirmation page
            first and run on its second POST (``post=yes``, as Django's
            ``delete_selected``).
        method: buttons only. ``"post"`` (default): a POST form with the CSRF
            token, GET answers 405, for an action that changes something.
            ``"get"``: a link, for an action that is a page with its own form
            (the handler checks ``request.method`` itself).

    Usage::

        from django_cfg.modules.django_admin import action

        @action(description="Rebuild", url_path="rebuild", permissions=["change"])
        def rebuild(self, request, object_id):
            ...

        @action(description="Edit names", url_path="names", method="get")
        def edit_names(self, request, object_id):
            form = NamesForm(request.POST or None)
            ...
    """
    variant = getattr(variant, "value", variant)  # ActionVariant enum or plain string
    if variant is not None and str(variant) not in ACTION_VARIANTS:
        raise ValueError(f"action(variant={variant!r}): use one of {ACTION_VARIANTS}")
    if method not in ACTION_METHODS:
        raise ValueError(f"action(method={method!r}): use one of {ACTION_METHODS}")

    def decorator(func: Callable) -> Callable:
        # A fresh wrapper per decoration: one handler shared by two ActionConfigs
        # keeps two sets of attributes.
        func = _require_confirmation(func, confirm) if confirm else _copy(func)
        if permissions is not None:
            func.allowed_permissions = tuple(permissions)
        if description is not None:
            func.short_description = description
        if url_path is not None:
            func.url_path = url_path
        func.icon = icon
        func.variant = None if variant in (None, "default") else str(variant)
        func.attrs = dict(attrs or {})
        func.confirm = confirm
        func.method = method
        return func

    if function is None:
        return decorator
    return decorator(function)


def _copy(func: Callable) -> Callable:
    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    return inner


def _require_confirmation(func: Callable, message: str) -> Callable:
    """
    Bulk actions: the first submit renders a confirmation page, the second runs.

    Button actions (signature ``(self, request)`` or ``(self, request, object_id)``)
    are passed through; their confirmation is the ``confirm()`` dialog on the link.
    """

    @wraps(func)
    def inner(modeladmin, request, *args, **kwargs):
        from django.contrib.admin import helpers
        from django.template.response import TemplateResponse

        queryset = args[0] if args else kwargs.get("queryset")
        if queryset is None or not hasattr(queryset, "model"):
            return func(modeladmin, request, *args, **kwargs)
        if request.POST.get(CONFIRM_FIELD) == "yes":
            return func(modeladmin, request, *args, **kwargs)
        opts = modeladmin.model._meta
        # The name Django knows the action by is what the changelist posted, not
        # func.__name__: register_actions() sets ActionConfig.name on the class,
        # and a handler built by a factory is often called "handler".
        try:
            index = int(request.POST.get("index", 0))
        except ValueError:
            index = 0
        posted = request.POST.getlist("action")
        action_name = posted[index] if index < len(posted) else (posted[0] if posted else func.__name__)
        context = {
            **modeladmin.admin_site.each_context(request),
            "title": getattr(inner, "short_description", func.__name__),
            "message": message,
            "opts": opts,
            "queryset": queryset,
            "action_name": action_name,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "confirm_field": CONFIRM_FIELD,
            "media": modeladmin.media,
        }
        request.current_app = modeladmin.admin_site.name
        return TemplateResponse(request, "django_admin/action_confirmation.html", context)

    return inner


__all__ = ["action", "ACTION_VARIANTS", "ACTION_METHODS", "DEFAULT_CONFIRMATION", "CONFIRM_FIELD"]
