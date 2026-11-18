"""The MCP tab: each profile, the credential the signed-in admin can use on it, and install commands.

**Whose key.** A profile is described for one person, never in general:

1. ``personal``: a static key the profile binds to *this* account
   (``access_key`` or an ``extra_keys`` entry whose ``service_username`` is this
   user), or the user's own ``UserAPIKey`` when the profile accepts it (checked
   with ``auth.authenticate``, the function the endpoint itself calls, so the
   tab cannot claim a key works when the endpoint would refuse it).
2. ``personal_missing``: the profile takes ``UserAPIKey`` (the default
   validator) and this user has none yet: "Create key" (``POST``).
3. ``oauth``: no key needed; the client signs in on first use.
4. ``shared``: the profile's unbound deployment key (``MCP__ACCESS_KEY``). It is
   nobody's own key, so only a superuser may reveal it, and the page says so.
5. ``unavailable``: nothing this user may use (a key bound to another account
   is never shown).

**The value never reaches the HTML.** Commands are rendered with a mask; the
real ones come from ``reveal_payload`` behind a ``POST`` (see ``views.py``).

Command formats follow ``@djangocfg/widget-mcp`` (``widgets/mcp/src/install.ts``)
and the vendors' pages read 2026-11-18: Claude Code
``claude mcp add --transport http <name> <url> --header "..."`` with
``--scope user`` (code.claude.com/docs/en/mcp); Codex ``[mcp_servers.<name>]``
with ``url`` and ``http_headers`` in ``~/.codex/config.toml``, and
``codex mcp add <name> --url <url>`` for a server that signs in
(learn.chatgpt.com/docs/extend/mcp). One difference from the widget: the generic
JSON entry carries ``"type": "http"``, which Claude Code requires for a ``url``
entry and other clients accept.
"""

from __future__ import annotations

import json
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger(__name__)

KEY_HEADER = "X-MCP-Access-Key"
KEY_ENV = "MCP_API_KEY"

#: Characters a key may hold to go into a shell word, a TOML string and a header.
_SAFE_KEY = re.compile(r"^[A-Za-z0-9._~+/=-]{8,256}$")
#: A URL that is safe unquoted in a shell line and inside TOML/JSON strings.
_SAFE_URL = re.compile(r"^https?://[A-Za-z0-9.-]+(:[0-9]{1,5})?/[A-Za-z0-9._~/-]*$")
_SAFE_ALIAS = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")

#: Stands in for the key while the masked commands are built.
_SENTINEL = "KEYSENTINEL0123456789"

PERSONAL = "personal"
PERSONAL_MISSING = "personal_missing"
OAUTH = "oauth"
SHARED = "shared"
UNAVAILABLE = "unavailable"


class UnsafeValue(ValueError):
    """A URL, alias or key that cannot be put into a command safely."""


def mask(key: str) -> str:
    """Eight dots and the last four characters; nothing else of the key."""
    return "••••••••" + (key[-4:] if len(key) >= 16 else "")


# --- commands ---------------------------------------------------------------


def build_commands(alias: str, url: str, key: Optional[str]) -> dict[str, str]:
    """Install commands for one server. ``key=None`` builds the sign-in (OAuth) variants.

    Raises ``UnsafeValue`` rather than quoting its way around a strange value:
    a command that is wrong is worse than no command.
    """
    if not _SAFE_ALIAS.match(alias or ""):
        raise UnsafeValue("alias")
    if not _SAFE_URL.match(url or ""):
        raise UnsafeValue("url")
    if key is not None and key != _SENTINEL and not _SAFE_KEY.match(key):
        raise UnsafeValue("key")

    install = url.rstrip("/") + "/install.sh"
    if key is None:
        return {
            "claude": (
                f"claude mcp remove --scope user {alias} 2>/dev/null; "
                f"claude mcp add --scope user --transport http {alias} {url}"
            ),
            "codex": f"codex mcp add {alias} --url {url} && codex mcp login {alias}",
            "codex_toml": f'[mcp_servers.{alias}]\nurl = "{url}"\n',
            "json": json.dumps({"mcpServers": {alias: {"type": "http", "url": url}}}, indent=2),
            "install": f"curl -fsSL '{install}' | sh",
        }

    table = f'[mcp_servers.{alias}]\nurl = "{url}"\nhttp_headers = {{ "{KEY_HEADER}" = "{key}" }}\n'
    printf_body = table.replace("\n", "\\n")  # printf expands \n; the key charset has no % or '
    return {
        "claude": (
            f"claude mcp remove --scope user {alias} 2>/dev/null; "
            f"claude mcp add --scope user --transport http {alias} {url} "
            f'--header "{KEY_HEADER}: {key}"'
        ),
        # `codex mcp add` takes no header, so the table goes into config.toml.
        "codex": (
            f"codex mcp remove {alias} 2>/dev/null; mkdir -p ~/.codex && "
            f"printf '\\n{printf_body}' >> ~/.codex/config.toml"
        ),
        "codex_toml": table,
        "json": json.dumps(
            {"mcpServers": {alias: {"type": "http", "url": url, "headers": {KEY_HEADER: key}}}}, indent=2
        ),
        "install": f"curl -fsSL '{install}' | {KEY_ENV}='{key}' sh",
    }


def masked_commands(alias: str, url: str, masked: str) -> dict[str, str]:
    """The commands as the page shows them before "Show": the key replaced by its mask."""
    return {k: v.replace(_SENTINEL, masked) for k, v in build_commands(alias, url, _SENTINEL).items()}


# --- credential -------------------------------------------------------------


@dataclass
class Credential:
    kind: str
    label: str
    hint: str
    masked: str = ""
    revealable: bool = False
    creatable: bool = False


@dataclass
class ProfileView:
    name: str
    alias: str
    url: str
    path: str
    tools: str
    tool_count: Optional[int]
    oauth: bool
    rate_limit: str
    credential: Credential
    commands: dict = field(default_factory=dict)
    error: str = ""


def _username(user) -> str:
    try:
        return user.get_username()
    except Exception:
        return ""


def _bound_key(profile, user) -> Optional[tuple[str, str]]:
    """``(key, label)`` of a static key the profile binds to this very account."""
    name = _username(user)
    if not name:
        return None
    if getattr(profile, "access_key", None) and getattr(profile, "service_username", None) == name:
        return profile.access_key, "access key bound to your account"
    for extra in getattr(profile, "extra_keys", None) or []:
        if extra.service_username == name:
            return extra.access_key, f"key “{extra.label}” bound to your account"
    return None


def _user_api_key(user):
    try:
        from django_cfg.apps.system.accounts.models import UserAPIKey

        return UserAPIKey.objects.filter(user=user).first()
    except Exception:
        return None


def _accepts(profile, user, key: str) -> bool:
    from django_cfg.modules.django_mcp.auth import authenticate

    caller = authenticate(key, profile)
    return bool(caller is not None and getattr(caller, "pk", None) is not None and caller.pk == user.pk)


def _takes_user_keys(profile) -> bool:
    from django_cfg.modules.django_mcp.config_builder import DEFAULT_KEY_VALIDATOR

    return getattr(profile, "key_validator", None) == DEFAULT_KEY_VALIDATOR


def secret_for(profile, user) -> tuple[Optional[str], str]:
    """``(value, kind)`` this user may hold on ``profile``. Called only behind POST."""
    bound = _bound_key(profile, user)
    if bound:
        return bound[0], PERSONAL
    api_key = _user_api_key(user)
    if api_key is not None and _accepts(profile, user, api_key.full_key):
        return api_key.full_key, PERSONAL
    if getattr(profile, "oauth", None):
        return None, OAUTH
    if getattr(profile, "access_key", None) and not getattr(profile, "service_username", None):
        if getattr(user, "is_superuser", False):
            return profile.access_key, SHARED
    return None, UNAVAILABLE


def describe_credential(profile, user) -> Credential:
    """What the page says about the key, with a mask at most."""
    bound = _bound_key(profile, user)
    if bound:
        return Credential(PERSONAL, bound[1], "Only you see it.", mask(bound[0]), revealable=True)

    api_key = _user_api_key(user)
    if api_key is not None and _accepts(profile, user, api_key.full_key):
        return Credential(
            PERSONAL,
            "your personal API key",
            "The same key for all your assistants. Regenerating it ends every connection made with it.",
            mask(api_key.full_key),
            revealable=True,
        )
    if api_key is None and _takes_user_keys(profile):
        return Credential(
            PERSONAL_MISSING,
            "no personal API key yet",
            "This profile takes your personal API key. Create it to get the commands.",
            creatable=True,
        )
    if getattr(profile, "oauth", None):
        return Credential(OAUTH, "sign-in (OAuth), no key", "The assistant opens a sign-in page on first use.")

    access_key = getattr(profile, "access_key", None)
    if access_key and not getattr(profile, "service_username", None):
        if getattr(user, "is_superuser", False):
            return Credential(
                SHARED,
                "shared deployment key (MCP__ACCESS_KEY)",
                "Not personal: everyone holding it acts as the same machine client. Changing it means a redeploy.",
                mask(access_key),
                revealable=True,
            )
        return Credential(
            UNAVAILABLE,
            "shared deployment key",
            "Only a superuser can reveal it. This profile does not take personal keys.",
        )
    return Credential(UNAVAILABLE, "no key for your account", "Ask the operator for a key bound to your account.")


def _tools_summary(profile) -> str:
    from django_cfg.modules.django_mcp.__cfg__ import ALL_TOOLS, PUBLIC_TOOLS

    tools = list(getattr(profile, "tools", None) or [])
    if ALL_TOOLS in tools:
        return "all tools"
    named = [t for t in tools if t != PUBLIC_TOOLS]
    parts = (["tools marked public"] if PUBLIC_TOOLS in tools else []) + named[:6]
    more = len(named) - 6
    return ", ".join(parts) + (f" and {more} more" if more > 0 else "") if parts else "no tools"


def _tool_count(profile) -> Optional[int]:
    try:
        from django_cfg.modules.django_mcp.handlers.tools import tool_registry

        return len(tool_registry.get_all_tools(None, profile=profile))
    except Exception:
        logger.exception("Overview: counting MCP tools failed")
        return None


def endpoint_url(request, config, mcp, profile) -> str:
    """The URL a client registers: what ``install.sh`` and ``SKILL.md`` use (D6)."""
    from django_cfg.modules.django_mcp.distribution.views import _DistributionView

    return _DistributionView._endpoint_url(request, config, mcp, profile)


def profile_alias(mcp, profile) -> str:
    from django_cfg.modules.django_mcp.distribution.skill import resolve_alias
    from django_cfg.modules.django_mcp.handlers.initialize import resolve_server_name

    return resolve_alias(mcp, profile, resolve_server_name(getattr(mcp, "server_name", None)))


def enabled_mcp(config) -> Any:
    mcp = getattr(config, "mcp", None) if config else None
    return mcp if mcp is not None and getattr(mcp, "enabled", False) else None


def profiles_for(request, config) -> list[ProfileView]:
    """Every profile as this user sees it. Never raises; a broken profile carries ``error``."""
    mcp = enabled_mcp(config)
    if mcp is None:
        return []
    views = []
    for name, profile in (getattr(mcp, "profiles", None) or {}).items():
        try:
            alias = profile_alias(mcp, profile)
            url = endpoint_url(request, config, mcp, profile)
            credential = describe_credential(profile, request.user)
            view = ProfileView(
                name=name,
                alias=alias,
                url=url,
                path=profile.path,
                tools=_tools_summary(profile),
                tool_count=_tool_count(profile),
                oauth=bool(getattr(profile, "oauth", None)),
                rate_limit=getattr(profile, "rate_limit", ""),
                credential=credential,
            )
            try:
                if credential.kind == OAUTH:
                    view.commands = build_commands(alias, url, None)
                elif credential.revealable:
                    view.commands = masked_commands(alias, url, credential.masked)
            except UnsafeValue as exc:
                view.error = f"No commands: the {exc} cannot be used in a shell line. Set DjangoConfig.api_url."
            views.append(view)
        except Exception:
            logger.exception("Overview: MCP profile %r could not be described", name)
            views.append(
                ProfileView(
                    name=name, alias="", url="", path=getattr(profile, "path", ""), tools="", tool_count=None,
                    oauth=False, rate_limit="", credential=Credential(UNAVAILABLE, "", ""),
                    error="This profile could not be read; see the server log.",
                )
            )
    return views


def reveal_payload(request, config, profile_name: str) -> Optional[dict]:
    """The real key and commands for this user on one profile, or None when there is nothing to give."""
    mcp = enabled_mcp(config)
    if mcp is None:
        return None
    profile = (getattr(mcp, "profiles", None) or {}).get(profile_name)
    if profile is None:
        return None
    value, kind = secret_for(profile, request.user)
    if not value:
        return None
    alias = profile_alias(mcp, profile)
    url = endpoint_url(request, config, mcp, profile)
    return {"kind": kind, "key": value, "masked": mask(value), "commands": build_commands(alias, url, value)}
