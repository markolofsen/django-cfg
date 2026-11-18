"""Mounted at ``cfg/admin/overview/`` by ``django_cfg.apps.urls``. POST only; no key in any URL."""

from django.urls import path

from .views import create_credential, reveal_credential

urlpatterns = [
    path("mcp/<slug:profile>/credential/", reveal_credential, name="django_cfg_overview_mcp_reveal"),
    path("mcp/<slug:profile>/credential/create/", create_credential, name="django_cfg_overview_mcp_create"),
]
