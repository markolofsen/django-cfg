"""Where the MCP access key comes from, and — as importantly — from where.

Typing the key by hand does not survive rotation: the value is per-deployment
and not in the source, so a human copying it between a ``.env`` and a terminal
is the only thing keeping every registered assistant working. Reading it from
the file that actually configures the target is what deletes that manual step.

Precedence, highest first:

1. an explicit value passed by the operator — overriding on purpose;
2. ``$MCP__ACCESS_KEY`` **as the shell had it** — how CI supplies one without
   editing a file, and matching django_cfg's own env-over-file precedence;
3. the dotenv files the target declares, in order.

Point 2 carries a trap worth stating in full, because it was observed rather
than imagined. Importing a project's ``mcp/__init__.py`` typically loads its
settings through pydantic-settings, and pydantic-settings **writes dotenv values
into ``os.environ``**. From that moment a file value is indistinguishable from an
exported one, so a production install resolved the *local development* key while
truthfully reporting its source as ``$MCP__ACCESS_KEY``. That registration then
connects, lists every tool, and 401s on the first call — inside an assistant,
where nobody reads status codes. ``_SHELL_KEY`` is therefore snapshotted at
import, before any project config can run, which is the only thing that keeps
"the operator exported this" separate from "a file happened to define it".
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Iterable, NamedTuple, Optional

#: Environment variable the key is read from, and the name projects should use
#: in their dotenv files. One spelling so the resolver and the server agree.
KEY_VAR = "MCP__ACCESS_KEY"

#: ``$MCP__ACCESS_KEY`` as the *shell* had it, captured before anything else
#: runs. See the module docstring — this is a real bug, not defensive style.
_SHELL_KEY: Optional[str] = os.environ.get(KEY_VAR) or None


class ResolvedKey(NamedTuple):
    """A key and where it came from.

    The source is not decoration. A key silently resolved from the wrong file
    produces a registration that connects, lists every tool, and fails only on
    the first real call. Printing the source is the one chance an operator gets
    to notice "that is the wrong environment's key" before it is written.
    """

    value: Optional[str]
    source: str


# Deliberately not a dotenv library. This reads one flat `KEY=value` file with
# no interpolation, no `export`, no multiline — which is what these files are,
# and what Docker's own parser accepts. A dependency here would mean the
# installer needs installing.
_LINE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*?)\s*$")


def read_env_file(path: Path) -> dict[str, str]:
    """Parse ``KEY=value`` pairs. A missing file yields ``{}``, not an error.

    On a fresh checkout the local dotenv may genuinely not exist yet, and that
    is a reason to fall through to the next source rather than to fail.
    """
    try:
        if not path.is_file():
            return {}
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        # Unreadable is the same answer as absent: try the next source.
        return {}

    values: dict[str, str] = {}
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = _LINE.match(line)
        if not match:
            continue
        name, raw = match.groups()
        if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
            raw = raw[1:-1]
        values[name] = raw
    return values


def resolve(
    env_files: Iterable[Path],
    *,
    explicit: Optional[str] = None,
    declared: Optional[str] = None,
    var: str = KEY_VAR,
    display_root: Optional[Path] = None,
    fallback: Optional[str] = None,
) -> ResolvedKey:
    """Resolve the access key for a target from its declared sources.

    ``fallback`` is the running process's own key, and is used **only** when the
    target declares no files — i.e. the local target, where this process is the
    deployment. It is deliberately not a fallback for remote targets: there it
    would silently register the development key against production.
    """
    if explicit:
        return ResolvedKey(explicit, "--key")

    # The project stated this deployment's key outright, which beats every
    # inferred source: nothing else in the process knows a remote key.
    if declared:
        return ResolvedKey(declared, "config")

    paths = list(env_files)

    # A target that names its own files is a *different deployment*, and its
    # files outrank the environment. This is not a preference — it is a bug that
    # was observed: running inside `manage.py`, Django has already loaded this
    # project's `.env.local` through pydantic-settings, which **writes those
    # values into os.environ**. Even a snapshot taken at import is already
    # polluted, because the settings module is imported first. Honouring the
    # environment here resolved `--prod` to the *local development key* while
    # truthfully reporting its source as `$MCP__ACCESS_KEY` — a registration
    # that connects, lists every tool, and 401s on the first real call.
    #
    # For a target with no files the process IS the deployment, so the reverse
    # holds and the environment is exactly right.
    if not paths:
        # `_SHELL_KEY`, not `os.environ`: captured at import, before this
        # module's own project config could add to it.
        if var == KEY_VAR and _SHELL_KEY:
            return ResolvedKey(_SHELL_KEY, f"${var}")
        if var != KEY_VAR and (value := os.environ.get(var)):
            return ResolvedKey(value, f"${var}")
        if fallback:
            return ResolvedKey(fallback, "this project's own config")
        return ResolvedKey(None, "no key file is declared for this target")

    for path in paths:
        if value := read_env_file(path).get(var):
            return ResolvedKey(value, _display(path, display_root))

    listed = ", ".join(_display(p, display_root) for p in paths)
    return ResolvedKey(None, f"{var} not found in {listed}")


def _display(path: Path, root: Optional[Path]) -> str:
    """A path short enough to print, relative to the project when possible."""
    if root:
        try:
            return str(path.relative_to(root))
        except ValueError:
            pass
    try:
        return "~/" + str(path.relative_to(Path.home()))
    except ValueError:
        return str(path)
