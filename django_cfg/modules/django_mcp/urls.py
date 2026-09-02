"""MCP URL Configuration.

**Profiles are mounted by URL, never selected by a header.** A header-selected
profile would let the caller choose their own surface, which makes the public
tool set advisory rather than enforced.

A deployment that declares no profiles gets exactly the paths below, because
the config synthesises a single ``default`` profile at ``endpoint_path`` and
these views resolve to it.
"""

from django.urls import path

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


def profile_urlpatterns(config) -> list:
    """URL patterns for every declared profile, each at its own path.

    Returned rather than appended to ``urlpatterns`` so the project decides
    where to include them — the paths are absolute (``/mcp/``), not relative to
    wherever this module is mounted.

    **The agent views are deliberately absent.** They consume an LLM budget on
    the deployment's account, so mounting them on an anonymous profile would
    turn a public endpoint into a public spending endpoint.
    """
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
