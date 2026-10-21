"""MCP Server Info View — server metadata and the tool listing.

The listing is a capability map (tool names, descriptions, input schemas), so
it needs the same credential as JSON-RPC on the same profile. There is no
opt-out and no unauthenticated MCP route: anything unauthenticated would
publish what the keyed endpoint withholds.
"""

import logging
from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny

from django_cfg.modules.django_mcp.auth import HEADER, authenticate
from django_cfg.modules.django_mcp.handlers.tools import tool_registry
from django_cfg.modules.django_mcp.throttling import MCPRateThrottle

logger = logging.getLogger(__name__)


@extend_schema(exclude=True)
class MCPInfoView(APIView):
    """
    GET /cfg/mcp/info/

    Returns server metadata and all available tools in one request.
    Faster than JSON-RPC initialize + tools/list (single HTTP GET).

    Response:
    {
        "server": {
            "name": "django-cfg-mcp",
            "version": "1.0.0",
            "protocol": "2025-03-26",
            "description": "..."
        },
        "tools": [
            {
                "name": "get_billing_plans",
                "description": "...",
                "input_schema": {...}
            }
        ],
        "total_tools": 24
    }
    """
    # The VIEW stays reachable without DRF auth: it must be able to answer 401
    # itself. A permission class here would produce DRF's own 403, which tells
    # an MCP client nothing about the header it should have sent.
    permission_classes = [AllowAny]
    # Throttled too: this endpoint walks the tool registry and, on a public
    # profile, is the one an anonymous client hits first.
    throttle_classes = [MCPRateThrottle]

    #: Profile this view serves; see ``MCPView.profile``.
    profile: str | None = None

    def _get_profile(self, mcp_config):
        """The profile answering this request, or ``None``."""
        try:
            profiles = getattr(mcp_config, "profiles", None) or {}
            return profiles.get(self.profile if self.profile is not None else "default")
        except Exception:
            return None

    def _authorized(self, request, mcp_config) -> bool:
        """Same credential check as the JSON-RPC path; never raises."""
        try:
            credentials = self._get_profile(mcp_config) or mcp_config
        except Exception:
            return False
        return authenticate(request.headers.get(HEADER), credentials) is not None

    def get(self, request):
        from django_cfg.core.state import get_current_config
        config = get_current_config()
        mcp_config = config.mcp if config and config.mcp else None

        if not self._authorized(request, mcp_config):
            response = JsonResponse(
                {
                    "detail": (
                        "Unauthorized: a valid X-MCP-Access-Key header is "
                        "required to list this server's tools."
                    )
                },
                status=401,
            )
            # RFC 7235 §3.1 makes the header mandatory on a 401. The scheme is
            # NOT `Bearer`: MCP clients read that as OAuth 2.0 and go fetch
            # `/.well-known/oauth-protected-resource`, which this server does
            # not implement.
            response["WWW-Authenticate"] = (
                'MCPAccessKey realm="mcp", header="X-MCP-Access-Key"'
            )
            return response

        server_info = {
            "name": "django-cfg-mcp",
            "version": "1.0.0",
            "protocol": "2025-03-26",
            "description": (
                "Django-CFG MCP server — AI agents can query models, "
                "execute commands, and introspect the application."
            ),
        }

        if mcp_config:
            server_info["introspection_enabled"] = getattr(
                mcp_config.introspection if hasattr(mcp_config, 'introspection') else {},
                'enabled', False
            )
            server_info["llm_model"] = getattr(mcp_config, 'llm_model', 'openai/gpt-4.1-nano')

        profile = self._get_profile(mcp_config)
        if profile is not None:
            server_info["profile"] = profile.name
            server_info["authentication"] = "access-key"

        tools = []
        for tool in tool_registry.get_all_tools(None, profile=profile):
            tools.append({
                "name": tool.name,
                "description": tool.description,
                # The profile's schema, not the class attribute: a tool whose
                # ceiling differs per profile must advertise the one that
                # applies here, or this listing contradicts the endpoint.
                "input_schema": tool.schema_for(profile) if profile else tool.input_schema,
            })

        return JsonResponse({
            "server": server_info,
            "tools": tools,
            "total_tools": len(tools),
        })
