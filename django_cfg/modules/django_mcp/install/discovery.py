"""Turning a project's declared targets into concrete endpoints.

A target names a **deployment**, and the deployment is described by the dotenv
files that configure it. Everything else is derived:

===============  ==========================================================
endpoint         ``APP__API_URL`` from those files + ``endpoint_path``
access key       ``MCP__ACCESS_KEY`` from the same files
registration     ``<project>_<target>``
===============  ==========================================================

The local target declares no files, because for it the *running process is the
target*: its own config already answers both questions.

Why remote targets cannot work the same way, stated plainly because it is the
whole reason this indirection exists: ``manage.py mcp_install --prod`` runs on
a laptop, configured by ``.env.local``. ``get_current_config()`` there returns
the **development** URL and the **development** key. Registering those against
production produces a client that connects, lists every tool, and 401s on the
first real call — inside an assistant, where nobody sees the status code. The
files are the only place the target deployment's own values exist.

Shared by ``mcp_install`` and ``mcp_doctor`` deliberately: two commands
resolving "which endpoint does --prod mean" by separate code is how they come
to disagree, and a doctor that checks a different target than the installer
writes is worse than no doctor.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Optional

from .keys import read_env_file
from .targets import Target

#: Variable holding the backend's own base URL. Matches ``DjangoConfig.api_url``,
#: which is what a project's dotenv sets and what the server serves under.
URL_VAR = "APP__API_URL"

KEY_VAR = "MCP__ACCESS_KEY"

#: 127.0.0.1, never "localhost": on macOS that name resolves to IPv6 ``::1``
#: first while ``runserver`` binds IPv4 only, so an assistant reports
#: ConnectionRefused against a server ``curl`` reaches without trouble.
LOCAL_FALLBACK_URL = "http://127.0.0.1:8000"


def mcp_config() -> Optional[Any]:
    """The live MCP config, or None when MCP is disabled for this project.

    Wraps the module's own ``is_enabled``/``get_mcp_config`` pair rather than
    re-deriving it: those raise when MCP is off, and both commands here want
    "off" to be an answer they can report, not an exception.
    """
    from django_cfg.modules.django_mcp import get_mcp_config, is_enabled

    try:
        return get_mcp_config() if is_enabled() else None
    except Exception:
        # No config registered at all (e.g. settings never built).
        return None


def django_config() -> Optional[Any]:
    """The live ``DjangoConfig``, or None when none is registered."""
    from django_cfg.core.state import get_current_config

    return get_current_config()


def base_dir() -> Optional[Path]:
    from django.conf import settings

    base = getattr(settings, "BASE_DIR", None)
    return Path(base) if base else None


def project_slug() -> str:
    """A short, filesystem-safe name for this project.

    Used to build registration names. Derived from ``project_name`` when the
    project set one, falling back to the checkout directory — both are stable
    for a given project, which is what matters: a name that changed between
    runs would orphan the previous registration instead of updating it.
    """
    config = django_config()
    raw = getattr(config, "project_name", None) if config else None
    if not raw:
        base = base_dir()
        raw = base.name if base else "django_cfg"
    slug = re.sub(r"[^0-9a-zA-Z]+", "_", str(raw)).strip("_").lower()
    return slug or "django_cfg"


def declared_kinds() -> list[str]:
    """Target names this project declared, sorted.

    Read at ``add_arguments`` time so ``--help`` lists exactly the targets that
    exist here rather than a fixed local/prod pair the project may not have.
    """
    config = mcp_config()
    return sorted(getattr(config, "install_targets", {}) or {}) if config else []


def _resolve_paths(raw_paths: list[str], base: Optional[Path]) -> tuple[Path, ...]:
    resolved = []
    for raw in raw_paths:
        path = Path(raw).expanduser()
        # Relative to BASE_DIR, not the cwd: the command runs from wherever the
        # operator happens to be standing.
        resolved.append(path if path.is_absolute() or base is None else (base / path).resolve())
    return tuple(resolved)


def _endpoint(api_url: str, endpoint_path: str) -> str:
    return f"{api_url.rstrip('/')}/{endpoint_path.strip('/')}/"


def registry() -> dict[str, Target]:
    """The declared targets, with endpoint, name and key sources all resolved."""
    config = mcp_config()
    if config is None:
        return {}

    base = base_dir()
    slug = project_slug()
    endpoint_path = getattr(config, "endpoint_path", "/cfg/mcp/")
    built: dict[str, Target] = {}

    for kind, declared in (getattr(config, "install_targets", {}) or {}).items():
        files = _resolve_paths(list(declared.env_files), base)
        name = declared.server_name or f"{slug}_{kind}"

        api_url = declared.url or _first_value(files, URL_VAR)
        if not api_url and not files:
            # The local target: the running process *is* the deployment, so its
            # own api_url is exactly right.
            django = django_config()
            api_url = (getattr(django, "api_url", None) if django else None) or LOCAL_FALLBACK_URL

        # Left unresolved rather than guessed when a remote target supplied
        # neither: inventing a URL would register a client against an endpoint
        # nobody chose. The caller reports what it looked at.
        url = _endpoint(_delocalhost(api_url), endpoint_path) if api_url else ""

        built[kind] = Target(kind, url, name, files, declared.access_key)
    return built


def _delocalhost(url: str) -> str:
    """Swap 'localhost' for 127.0.0.1 — see LOCAL_FALLBACK_URL."""
    return url.replace("//localhost", "//127.0.0.1")


def _first_value(paths: tuple[Path, ...], var: str) -> Optional[str]:
    for path in paths:
        if value := read_env_file(path).get(var):
            return value
    return None
