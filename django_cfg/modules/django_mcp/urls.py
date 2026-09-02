"""MCP URL Configuration.

**Profiles are mounted by URL, never selected by a header.** A header-selected
profile would let the caller choose their own surface, which makes the public
tool set advisory rather than enforced.

A deployment that declares no profiles gets exactly the paths below, because
the config synthesises a single ``default`` profile at ``endpoint_path`` and
these views resolve to it.
"""

from django.urls import path
from django.urls.resolvers import RegexPattern, URLResolver

from .views import MCPView
from .agents.api.views import MCPAgentChatView, MCPAgentStreamView, MCPAgentHistoryView
from .info_view import MCPInfoView

urlpatterns = [
    path("", MCPView.as_view(), name="mcp-endpoint"),
    path("info/", MCPInfoView.as_view(), name="mcp-info"),
    path("agent/", MCPAgentChatView.as_view(), name="mcp-agent"),
    path("agent/stream/", MCPAgentStreamView.as_view(), name="mcp-agent-stream"),
    path("agent/history/", MCPAgentHistoryView.as_view(), name="mcp-agent-history"),
]


def profile_urlpatterns(config=None) -> list:
    """URL patterns for every declared profile, each at its own path.

    Called by ``django_cfg.apps.urls`` — routing a declared profile is the
    framework's job, not the project's. A profile that exists in the config but
    on no URL is invisible in the worst way: the config reads correct, the tool
    filter works, and the endpoint 404s.

    ``config`` is resolved **lazily**, on the first request, because this module
    is imported while settings are still being built and the MCP config does not
    exist yet. Reading it at import time yields None and silently produces no
    routes — so the patterns below are wrapped in a resolver that runs later.

    **The agent views are deliberately absent.** They spend an LLM budget on the
    deployment's account, so mounting them on an anonymous profile would make it
    a public spending endpoint.
    """
    if config is not None:
        return _patterns_for(config)

    # Django resolves `urlconf_name` on first use, so a module-like object with
    # a lazy `urlpatterns` defers the config read until the app registry is
    # ready. Using the framework's own resolver rather than a hand-written one:
    # a custom object has to reimplement `resolve()`, `reverse_dict`,
    # namespaces and the Resolver404 contract, and getting any of them subtly
    # wrong fails as a 404 on a route that plainly exists.
    return [URLResolver(RegexPattern(r"^"), _LazyProfileURLConf())]


def _patterns_for(config) -> list:
    profiles = getattr(config, "profiles", None) or {}
    # Whatever is already served by `urlpatterns`, wherever the project mounted
    # it. Skipped by PATH rather than by the name "default": a project may name
    # its main surface anything, and mounting it twice would publish the
    # operator endpoint at a second, unintended address.
    mounted = (getattr(config, "endpoint_path", "") or "").strip("/")
    patterns = []
    for name, profile in profiles.items():
        prefix = profile.path.strip("/")
        if prefix == mounted:
            continue
        patterns.append(
            path(f"{prefix}/", MCPView.as_view(profile=name), name=f"mcp-{name}")
        )
        patterns.append(
            path(
                f"{prefix}/info/",
                MCPInfoView.as_view(profile=name),
                name=f"mcp-{name}-info",
            )
        )
    return patterns


class _LazyProfileURLConf:
    """Stands in for a URLconf module, building its patterns on first access.

    ``URLResolver`` reads ``urlconf_name.urlpatterns`` when it first resolves or
    reverses — by then the app registry is ready and the MCP config exists.
    Building them at import time reads a config that is still ``None`` and
    registers nothing, which leaves no trace: an empty list is a valid URLconf,
    so the routes simply are not there.
    """

    @property
    def urlpatterns(self) -> list:
        from django_cfg.core.state import get_current_config

        config = get_current_config()
        mcp = getattr(config, "mcp", None) if config else None
        return _patterns_for(mcp) if mcp is not None else []
