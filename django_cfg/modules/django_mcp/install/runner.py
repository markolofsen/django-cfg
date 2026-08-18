"""Orchestration: resolve a target, resolve its key, report, then write.

The reporting step is not cosmetic. Nobody typed the key, so nobody has seen
it; printing which key was picked up *and which file it came from* is the only
moment an operator can catch "that is the wrong environment's key" before it is
written somewhere that fails silently later.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from pathlib import Path
from typing import NamedTuple, Optional

from . import claude, codex, keys
from .console import Console, mask
from .targets import Target


class InstallOptions(NamedTuple):
    agent: str = "all"
    scope: str = "user"
    key_env_var: Optional[str] = None
    explicit_key: Optional[str] = None
    dry_run: bool = False
    uninstall: bool = False
    skip_probe: bool = False
    key_var: str = keys.KEY_VAR
    display_root: Optional[Path] = None
    #: This process's own access key. Used only for a target that declares no
    #: env files — the local one, where this process IS the deployment.
    local_key: Optional[str] = None


def probe(url: str, timeout: int = 10) -> Optional[int]:
    """Ask the endpoint's ``/info/`` whether it is alive.

    A registration pointing at a dead endpoint fails silently later, inside an
    assistant, where the cause is not visible. Checking now costs one request.

    A ``401`` counts as alive — it means the server is up and *authenticating*,
    which is the correct answer to an unauthenticated probe.
    """
    info = url.rstrip("/") + "/info/"
    try:
        with urllib.request.urlopen(info, timeout=timeout) as response:
            return response.status
    except urllib.error.HTTPError as exc:
        return exc.code
    except Exception:
        return None


def run(target: Target, options: InstallOptions, console: Console) -> int:
    """Perform the install/uninstall. Returns a process exit code."""
    resolved = keys.ResolvedKey(None, "")

    if not target.url:
        # discovery could not find APP__API_URL for a remote target. Refusing is
        # the only safe answer: a guessed endpoint registers a client against a
        # server nobody chose, and that failure surfaces inside an assistant.
        console.err(f"no endpoint for --{target.kind}: no {'APP__API_URL'} in its env files")
        console.err(
            "checked: " + (", ".join(str(p) for p in target.env_files) or "(none declared)")
        )
        return 2

    if not options.uninstall and not options.key_env_var:
        resolved = keys.resolve(
            target.env_files,
            explicit=options.explicit_key,
            declared=target.access_key,
            var=options.key_var,
            display_root=options.display_root,
            fallback=options.local_key,
        )
        if not resolved.value:
            console.err(f"no access key — {resolved.source}")
            console.err(f"pass --key <key>, export {options.key_var}, or add it")
            console.err("to the dotenv file this target declares.")
            return 2

    if not options.uninstall:
        _report(target, resolved, options, console)
        if not options.skip_probe:
            _probe_and_report(target, console)

    if options.dry_run:
        console.bold("DRY RUN — nothing will be written")
        console.plain()

    console.bold("Uninstalling" if options.uninstall else "Installing")
    touched = False
    failed = False

    if options.agent in ("all", claude.AGENT):
        if claude.is_available():
            touched = True
            failed |= not claude.apply(
                target, resolved.value, console,
                scope=options.scope, dry_run=options.dry_run,
                uninstall=options.uninstall,
            )
        else:
            console.skip("claude: not installed")

    if options.agent in ("all", codex.AGENT):
        if codex.is_available():
            touched = True
            failed |= not codex.apply(
                target, resolved.value, console,
                key_env_var=options.key_env_var, dry_run=options.dry_run,
                uninstall=options.uninstall,
            )
        else:
            console.skip("codex: not installed")

    console.plain()
    if not touched:
        console.warn("no assistants changed — neither 'claude' nor 'codex' is on PATH")
        return 0
    if failed:
        console.err("finished with errors")
        return 1
    if not options.dry_run and not options.uninstall:
        console.bold("Done — restart the assistant, then ask it to list its MCP tools.")
        console.plain(f"Installed: {target.name} → {target.url}")
        # `mcp list` proves the handshake, not the tools: a green "Connected"
        # says nothing about whether a single tool actually returns data.
        console.plain("Verify: claude mcp list | codex mcp list — then CALL a tool,")
        console.plain("because a connected server can still fail every real call.")
    return 0


def _report(
    target: Target, resolved: keys.ResolvedKey, options: InstallOptions, console: Console
) -> None:
    console.bold("Target")
    console.plain(f"  target   : {target.kind}")
    console.plain(f"  name     : {target.name}")
    console.plain(f"  endpoint : {target.url}")
    if options.key_env_var:
        console.plain(f"  key      : read from ${options.key_env_var} at runtime (codex only)")
    else:
        console.plain(f"  key      : {mask(resolved.value)}  ({resolved.source})")

    if target.url.startswith("http://") and target.is_remote:
        console.warn("plain HTTP to a remote host — the key crosses the network in clear text")
    if target.url.startswith("http://localhost"):
        console.warn("'localhost' resolves to IPv6 ::1 first on macOS while runserver")
        console.warn("binds IPv4 only — the assistant will report ConnectionRefused.")
        console.warn("Use 127.0.0.1 instead.")
    console.plain()


def _probe_and_report(target: Target, console: Console) -> None:
    console.bold("Probe")
    code = probe(target.url)
    if code in (200, 401):
        console.ok(f"endpoint answers ({target.url.rstrip('/')}/info/ → {code})")
    else:
        console.warn(f"endpoint did not answer (→ {code or 'no response'})")
        if target.kind == "local":
            console.warn("start it with:  manage.py runserver")
        console.warn("continuing anyway — pass --skip-probe to silence this")
    console.plain()
