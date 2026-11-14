"""``<endpoint>/install.sh`` and ``<endpoint>/SKILL.md``.

Both are served to anyone (an installer has no credential yet) and both hold only
what the caller already knows: the server's name and URL. The tool table and the
server's ``instructions`` of ``SKILL.md`` need a credential the profile accepts,
exactly as ``/info/`` does: see ``auth.py`` (there is no anonymous profile).
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from django.http import HttpResponse, JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from django_cfg.modules.django_mcp.auth import authenticate, presented_credential
from django_cfg.modules.django_mcp.handlers.initialize import resolve_instructions, resolve_server_name
from django_cfg.modules.django_mcp.handlers.tools import tool_registry
from django_cfg.modules.django_mcp.throttling import MCPRateThrottle

from . import script, skill

logger = logging.getLogger(__name__)

#: The script and the anonymous skill hold nothing per-caller, so they may be cached.
_PUBLIC_CACHE = "public, max-age=300"


class _DistributionView(APIView):
    # Reachable without DRF auth on purpose; see the module docstring.
    permission_classes = [AllowAny]
    throttle_classes = [MCPRateThrottle]
    #: Profile this view serves; see ``MCPView.profile``.
    profile: Optional[str] = None

    def _context(self, request) -> Optional[tuple[Any, Any, str, str, str]]:
        """``(mcp_config, profile, name, alias, url)`` or None when MCP is off."""
        from django_cfg.core.state import get_current_config

        config = get_current_config()
        mcp = config.mcp if config and config.mcp else None
        if mcp is None:
            return None
        profiles = getattr(mcp, "profiles", None) or {}
        profile = profiles.get(self.profile if self.profile is not None else "default")
        name = resolve_server_name(getattr(mcp, "server_name", None))
        alias = skill.resolve_alias(mcp, profile, name)
        return mcp, profile, name, alias, self._endpoint_url(request, config, mcp, profile)

    @staticmethod
    def _endpoint_url(request, config: Any, mcp: Any, profile: Any) -> str:
        path = getattr(profile, "path", None) or getattr(mcp, "endpoint_path", "/cfg/mcp/")
        path = "/" + path.strip("/") + "/"
        api_url = (getattr(config, "api_url", None) or "").rstrip("/")
        # The configured public URL first (what `mcp_install` registers); the
        # request's own host otherwise, which ALLOWED_HOSTS has already checked.
        return f"{api_url}{path}" if api_url else request.build_absolute_uri(path)

    @staticmethod
    def _unavailable() -> JsonResponse:
        return JsonResponse({"detail": "Not available."}, status=404)

    @staticmethod
    def _respond(body: str, content_type: str, cache: str, vary: bool = False) -> HttpResponse:
        response = HttpResponse(body, content_type=content_type)
        response["X-Content-Type-Options"] = "nosniff"
        response["Cache-Control"] = cache
        if vary:
            response["Vary"] = "X-MCP-Access-Key, Authorization"
        return response


@extend_schema(exclude=True)
class MCPInstallScriptView(_DistributionView):
    """GET <endpoint>/install.sh"""

    def get(self, request):
        ctx = self._context(request)
        if ctx is None:
            return self._unavailable()
        _, profile, name, alias, url = ctx
        try:
            body = script.render_install_script(
                alias=alias, name=name, url=url, oauth=bool(getattr(profile, "oauth", None))
            )
        except script.UnsafeValue as exc:
            # Refused, not repaired: see script.py.
            logger.error("MCP install.sh not served: %s", exc)
            return self._unavailable()
        return self._respond(body, script.CONTENT_TYPE, _PUBLIC_CACHE)


@extend_schema(exclude=True)
class MCPSkillView(_DistributionView):
    """GET <endpoint>/SKILL.md"""

    def get(self, request):
        ctx = self._context(request)
        if ctx is None:
            return self._unavailable()
        mcp, profile, name, alias, url = ctx
        config = skill.effective_skill(mcp, profile)

        tools = instructions = None
        credentialed = authenticate(presented_credential(request), profile or mcp) is not None
        if credentialed:
            tools = tool_registry.get_all_tools(None, profile=profile)
            instructions = resolve_instructions(mcp, profile)

        body = skill.render_skill(
            alias=alias,
            name=name,
            url=url,
            oauth=bool(getattr(profile, "oauth", None)),
            skill=config,
            tools=tools,
            instructions=instructions,
            file_text=skill.read_skill_file(config),
        )
        # A signed-in reader gets a different document: never stored, never shared.
        cache = "private, no-store" if credentialed else _PUBLIC_CACHE
        return self._respond(body, skill.CONTENT_TYPE, cache, vary=True)
