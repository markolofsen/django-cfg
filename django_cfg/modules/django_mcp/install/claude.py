"""Registering with Claude Code, through its own CLI.

Claude Code exposes ``claude mcp add --transport http … --header``, so the
vendor's CLI owns the config format and this module only has to call it
correctly. That asymmetry is the whole reason this half is short and the Codex
half is not.
"""

from __future__ import annotations

import shutil
import subprocess
from typing import Optional

from .console import Console
from .targets import ACCESS_KEY_HEADER, Target

AGENT = "claude"


def is_available() -> bool:
    return shutil.which("claude") is not None


def apply(
    target: Target,
    key: Optional[str],
    console: Console,
    *,
    scope: str = "user",
    dry_run: bool = False,
    uninstall: bool = False,
) -> bool:
    """Register or remove the server. Returns ``True`` on success."""
    if uninstall:
        if dry_run:
            console.ok(f"claude: would remove {target.name}")
            return True
        if _run(["claude", "mcp", "remove", target.name, "-s", scope]):
            console.ok(f"claude: removed {target.name}")
        else:
            console.skip(f"claude: {target.name} was not registered")
        return True

    if dry_run:
        console.ok(f"claude: would add {target.name} → {target.url} ({scope} scope)")
        return True

    # `mcp add` refuses an existing name, so re-running would fail rather than
    # update. Removing first is what makes a key rotation a one-command fix.
    _run(["claude", "mcp", "remove", target.name, "-s", scope])

    argv = [
        "claude", "mcp", "add",
        "--transport", "http",
        target.name, target.url,
        "-s", scope,
    ]
    if key:
        argv += ["--header", f"{ACCESS_KEY_HEADER}: {key}"]

    if not _run(argv):
        console.err("claude: registration failed")
        return False
    console.ok(f"claude: added {target.name} ({scope} scope)")
    return True


def _run(argv: list[str]) -> bool:
    """Run a `claude` subcommand, swallowing its output.

    The CLI is chatty on success and its failure text is rarely more useful than
    the line printed instead. ``check=False`` because "was not registered" is an
    expected outcome of the pre-emptive remove above, not an error.
    """
    try:
        result = subprocess.run(
            argv,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=60,
            check=False,
        )
    except (subprocess.TimeoutExpired, OSError):
        return False
    return result.returncode == 0
