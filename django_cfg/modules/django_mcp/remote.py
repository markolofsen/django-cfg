"""Tools, resources and prompts served by another app (e.g. a Next.js frontend).

The app publishes ``GET <base>/mcp-manifest.json`` and accepts
``POST <base>/mcp-call``; both carry a 60 s HS256 bearer signed with a shared
secret. Contract: ``@docs/remote-frontend.md``.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit

import jwt
import requests

from django_cfg.modules.django_mcp.registries import Prompt, Resource, prompt_registry, resource_registry
from django_cfg.modules.django_mcp.services.context import MCPContext
from django_cfg.modules.django_mcp.tools.base import MCPTool, tool_registry
from django_cfg.modules.django_mcp.tools.results import BLOCK_TYPES, ToolResult

logger = logging.getLogger(__name__)

#: A failed fetch is retried after this long, not after the full TTL.
RETRY_AFTER = 30.0


def sign_bearer(secret: str, url: str, sub: str = "django-cfg", ttl: int = 60) -> str:
    """HS256 JWT for ``url``: iss=django-cfg, aud=<origin of url>, exp=now+ttl."""
    parts = urlsplit(url)
    now = int(time.time())
    claims = {"iss": "django-cfg", "aud": f"{parts.scheme}://{parts.netloc}", "sub": sub, "iat": now, "exp": now + ttl}
    return jwt.encode(claims, secret, algorithm="HS256")


def _user_id(context: Optional[MCPContext]) -> Optional[str]:
    user = getattr(context, "user", None)
    if user is not None and getattr(user, "is_authenticated", False):
        return str(user.pk)
    return None


class ProxyTool(MCPTool):
    """A tool whose execution is a POST to the remote app."""

    def __init__(self, source: "RemoteSource", entry: Dict[str, Any]):
        self.source = source
        self.remote_name = entry["name"]
        self.name = f"{source.prefix}{self.remote_name}"
        self.description = entry.get("description", "")
        self.input_schema = entry.get("inputSchema") or {"type": "object", "properties": {}}
        self.public = bool(entry.get("public", source.public))
        hints = entry.get("annotations") or {}
        self.title = hints.get("title", "")
        self.read_only = bool(hints.get("readOnlyHint", False))
        self.destructive = hints.get("destructiveHint")
        self.idempotent = hints.get("idempotentHint")
        self.open_world = bool(hints.get("openWorldHint", False))

    def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> ToolResult:
        user_id = _user_id(context)
        url = f"{self.source.base}/mcp-call"
        payload = {"tool": self.remote_name, "arguments": arguments, "user_id": user_id}
        try:
            response = requests.post(
                url,
                json=payload,
                headers={"Authorization": f"Bearer {sign_bearer(self.source.secret, url, user_id or 'anonymous')}"},
                timeout=self.source.timeout,
            )
            response.raise_for_status()
            body = response.json()
        except (requests.RequestException, ValueError) as exc:
            logger.warning("mcp.remote call tool=%s failed: %s", self.name, type(exc).__name__)
            return ToolResult(f"The {self.remote_name} tool is unavailable: {type(exc).__name__}.", is_error=True)
        return _to_result(body)


def _to_result(body: Any) -> ToolResult:
    """``{"content": [blocks], "isError": bool}`` to a ToolResult."""
    blocks = (body.get("content") if isinstance(body, dict) else None) or []
    text = "\n".join(b.get("text", "") for b in blocks if b.get("type") == "text")
    extra = [b for b in blocks if b.get("type") in BLOCK_TYPES and b.get("type") != "text"]
    return ToolResult(text, extra, is_error=bool(isinstance(body, dict) and body.get("isError")))


class RemoteSource:
    """One remote app: a cached manifest and the registry entries built from it."""

    def __init__(self, url: str, secret: str, *, prefix: str = "", public: bool = False,
                 ttl: float = 300, timeout: float = 60):
        self.base = url.rstrip("/")
        self.secret = secret
        self.prefix = prefix
        self.public = public
        self.ttl = ttl
        self.timeout = timeout
        self._manifest: Dict[str, Any] = {}
        self._tools: List[ProxyTool] = []
        self._expires = 0.0
        self._lock = threading.Lock()

    def __repr__(self) -> str:  # never print the secret
        return f"RemoteSource({self.base!r})"

    def register(self) -> None:
        """Attach to the tool, resource and prompt registries (idempotent per base URL)."""
        for old in [s for s in _sources if s.base == self.base]:
            old.unregister()
        _sources.append(self)
        tool_registry.add_provider(self.tools)
        resource_registry.add_source(self.resources)
        prompt_registry.add_source(self.prompts)

    def unregister(self) -> None:
        if self in _sources:
            _sources.remove(self)
        tool_registry.remove_provider(self.tools)
        resource_registry.remove_source(self.resources)
        prompt_registry.remove_source(self.prompts)

    def manifest(self) -> Dict[str, Any]:
        """The cached manifest; refetched after the TTL. Failure keeps the last good copy."""
        with self._lock:
            if time.monotonic() < self._expires:
                return self._manifest
            url = f"{self.base}/mcp-manifest.json"
            try:
                response = requests.get(url, headers=self._headers(url), timeout=self.timeout)
                response.raise_for_status()
                data = response.json()
                if not isinstance(data, dict):
                    raise ValueError("manifest is not an object")
                self._manifest = data
                self._tools = [ProxyTool(self, t) for t in data.get("tools", []) if t.get("name")]
                self._expires = time.monotonic() + self.ttl
            except (requests.RequestException, ValueError) as exc:
                logger.warning("mcp.remote manifest %s unavailable: %s", url, type(exc).__name__)
                self._expires = time.monotonic() + RETRY_AFTER
            return self._manifest

    def _headers(self, url: str, sub: str = "django-cfg") -> Dict[str, str]:
        return {"Authorization": f"Bearer {sign_bearer(self.secret, url, sub)}"}

    @property
    def instructions(self) -> str:
        return self.manifest().get("instructions") or ""

    def tools(self) -> List[ProxyTool]:
        self.manifest()
        return list(self._tools)

    def resources(self) -> List[Resource]:
        return [
            Resource(
                uri=r["uri"], name=r.get("name", r["uri"]), description=r.get("description", ""),
                mime_type=r.get("mimeType", "text/markdown"), public=self.public,
                body=self._fetcher(r["url"]),
            )
            for r in self.manifest().get("resources", []) if r.get("uri") and r.get("url")
        ]

    def _fetcher(self, url: str):
        def fetch(context: Any) -> str:
            response = requests.get(url, headers=self._headers(url, _user_id(context) or "anonymous"), timeout=self.timeout)
            response.raise_for_status()
            return response.text
        return fetch

    def prompts(self) -> List[Prompt]:
        return [
            Prompt(
                name=p["name"], description=p.get("description", ""),
                arguments=p.get("arguments") or [], body=p.get("text", ""), public=self.public,
            )
            for p in self.manifest().get("prompts", []) if p.get("name")
        ]


_sources: List[RemoteSource] = []


def remote_instructions(profile: Any = None) -> List[str]:
    """Manifest ``instructions`` of every source this profile may see."""
    return [s.instructions for s in _sources if s.instructions and (profile is None or profile.serves_all_tools or s.public)]
