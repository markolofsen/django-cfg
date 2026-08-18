"""Connecting AI coding assistants to this project's MCP server.

The server is already served at ``/cfg/mcp/``; everything here writes the
**client** side, so an assistant knows the URL and the access key. Two commands
use it:

``manage.py mcp_install``
    Register (or remove) the server with Claude Code and Codex.
``manage.py mcp_doctor``
    Check the three things that must all hold before a tool call works, each of
    which fails invisibly on its own.

Layout, and the reason for the split:

``targets.py``
    *Mechanism* for naming endpoints. The facts — which host is production,
    which dotenv holds its key — belong to the project and are declared in its
    ``mcp/__init__.py``. A framework that hardcoded one deployment's hostnames
    would know about one product.
``keys.py``
    Where the key comes from, and from where. Carries the ``_SHELL_KEY``
    snapshot that keeps a dotenv value from impersonating an exported one.
``claude.py`` / ``codex.py``
    The two assistants, which are genuinely asymmetric: Claude Code exposes
    ``--header`` through its own CLI, Codex does not, so the latter means
    splicing a user's ``config.toml`` and validating the result three ways.
``runner.py``
    Orchestration and the report an operator reads before anything is written.

Why any of this is a framework concern rather than a shell script per project:
the URL and the access key already live in the Django config. Anything external
has to be told them again, and a second copy of a credential goes stale
silently — which is exactly how a *local* development key came to be registered
against production, connecting cleanly and failing only on the first real call.
"""

from .console import Console, mask
from .keys import KEY_VAR, ResolvedKey, read_env_file, resolve as resolve_key
from .runner import InstallOptions, probe, run
from .targets import (
    ACCESS_KEY_HEADER,
    DEFAULT_LOCAL_URL,
    Target,
    TargetError,
    local_target,
    remote_target,
    resolve as resolve_target,
)

__all__ = [
    "ACCESS_KEY_HEADER",
    "Console",
    "DEFAULT_LOCAL_URL",
    "InstallOptions",
    "KEY_VAR",
    "ResolvedKey",
    "Target",
    "TargetError",
    "local_target",
    "mask",
    "probe",
    "read_env_file",
    "remote_target",
    "resolve_key",
    "resolve_target",
    "run",
]
