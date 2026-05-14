from django.contrib.admin.views.decorators import staff_member_required
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from ..registry import TabRegistry


def _get_dashboard_config():
    from django_cfg.core.config import get_current_config
    config = get_current_config()
    return getattr(config, "dashboard", None)


@staff_member_required
def dashboard_index(request: HttpRequest) -> HttpResponse:
    """Redirect to the first tab the user has access to."""
    config = _get_dashboard_config()
    if not config or not config.tabs:
        raise Http404
    registry = TabRegistry()
    visible = [t for t in config.tabs if registry.has_permission(t, request)]
    if not visible:
        raise PermissionDenied
    default_slug = config.get_default_slug()
    slug = default_slug if any(t.slug == default_slug for t in visible) else visible[0].slug
    return redirect("django_cfg_dashboard_tab", slug=slug)


@staff_member_required
def dashboard_tab(request: HttpRequest, slug: str) -> HttpResponse:
    config = _get_dashboard_config()
    if not config:
        raise Http404

    tab = config.get_tab(slug)
    if tab is None:
        raise Http404

    registry = TabRegistry()
    if not registry.has_permission(tab, request):
        raise PermissionDenied

    extra_context = registry.get_context(tab, request)
    is_iframe = request.GET.get("iframe") == "1"
    visible_tabs = [t for t in config.tabs if registry.has_permission(t, request)]
    context = {
        **extra_context,
        "current_tab": tab,
        "all_tabs": visible_tabs,
        "dashboard_config": config,
        "title": tab.title,
        "is_iframe": is_iframe,
        # tell user templates which base to extend
        "dashboard_base": "django_dashboard/base_iframe.html" if is_iframe else "django_dashboard/base.html",
    }

    template = tab.template or "django_dashboard/tab_empty.html"
    return render(request, template, context)
