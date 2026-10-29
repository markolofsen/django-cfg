"""URL patterns for the manage API, relative to wherever the project mounts them."""

from __future__ import annotations

from typing import Any

from django.urls import path

from . import views
from .store import load_store


def manage_urlpatterns(store: Any = None) -> list:
    """Routes for keys, connections and usage backed by ``store``.

    ``store`` is a dotted path, a class, an instance, or ``None`` for the
    default store. Mount it anywhere, e.g. ``path("api/mcp/", include(manage_urlpatterns()))``.
    Each route also answers with a trailing slash.
    """
    store = load_store(store)
    routes = [
        ("keys", views.KeysView, "keys"),
        ("keys/<int:pk>", views.KeyView, "key"),
        ("connections", views.ConnectionsView, "connections"),
        ("connections/revoke-all", views.RevokeAllView, "revoke-all"),
        ("connections/<int:pk>", views.ConnectionView, "connection"),
        ("usage", views.UsageView, "usage"),
    ]
    patterns = []
    for route, view, name in routes:
        as_view = view.as_view(store=store)
        patterns.append(path(route, as_view, name=f"mcp-manage-{name}"))
        patterns.append(path(f"{route}/", as_view, name=f"mcp-manage-{name}-slash"))
    return patterns
