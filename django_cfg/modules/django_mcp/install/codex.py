"""Registering with Codex, by splicing its ``config.toml``.

Codex's CLI cannot set HTTP headers (``codex mcp add`` targets stdio servers),
so a keyed remote server has to be written into ``~/.codex/config.toml``
directly. That file is a **real user file** — on a working machine it holds
dozens of unrelated ``[projects."…"]`` tables, hand-written comments, and other
``[mcp_servers.*]`` entries.

So it is edited by **text splice**, never by parsing to a dict and
re-serialising: round-tripping through ``tomllib`` plus a writer discards every
comment and reorders every table, which is a destructive edit to somebody's
config dressed up as a settings change.

A splice can fail in three ways, and all three are checked against the *result*
before anything is written:

1. produce invalid TOML;
2. produce valid TOML with the wrong entry in it;
3. produce valid TOML that quietly dropped somebody else's tables.

The write is then atomic and mode 0600, with a timestamped backup — the file
holds an access key, so it must never be world-readable nor observed
half-written.
"""

from __future__ import annotations

import os
import re
import shutil
import tomllib  # stdlib since 3.11; django_cfg requires 3.12+
from datetime import datetime
from pathlib import Path
from typing import Optional

from .console import Console
from .targets import ACCESS_KEY_HEADER, Target

CODEX_CONFIG = Path.home() / ".codex" / "config.toml"

AGENT = "codex"


class CodexError(RuntimeError):
    """The edit was refused. Nothing was written."""


def is_available() -> bool:
    return shutil.which("codex") is not None


def section_name(server: str) -> str:
    return f"[mcp_servers.{server}]"


def has_section(text: str, server: str) -> bool:
    return bool(
        re.search(rf"^\s*{re.escape(section_name(server))}\s*$", text, re.MULTILINE)
    )


def strip_section(text: str, server: str) -> str:
    """Remove exactly one table, up to the next table header or EOF."""
    pattern = re.compile(
        rf"^[ \t]*{re.escape(section_name(server))}[ \t]*$.*?(?=^[ \t]*\[|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    return pattern.sub("", text)


def render(
    original: str,
    target: Target,
    key: Optional[str],
    *,
    key_env_var: Optional[str] = None,
    uninstall: bool = False,
) -> tuple[str, str]:
    """Return ``(new_text, action)`` without touching the filesystem.

    Split from the write so the interesting half is testable against a string
    rather than against a developer's real Codex config.
    """
    present = has_section(original, target.name)

    if uninstall:
        if not present:
            return original, "absent"
        return strip_section(original, target.name).rstrip() + "\n", "remove"

    lines = [section_name(target.name), f'url = "{target.url}"']
    if key_env_var:
        # Keeps the secret out of the file entirely; Codex resolves it per
        # request. Strictly better whenever the operator can arrange the var.
        lines.append(f'env_http_headers = {{ "{ACCESS_KEY_HEADER}" = "{key_env_var}" }}')
    elif key:
        lines.append(f'http_headers = {{ "{ACCESS_KEY_HEADER}" = "{key}" }}')
    block = "\n".join(lines) + "\n"

    base = (strip_section(original, target.name) if present else original).rstrip()
    return ((base + "\n\n" + block) if base else block), ("update" if present else "add")


def validate(original: str, updated: str, target: Target, *, uninstall: bool) -> dict:
    """Parse the result and prove the splice did what it claimed."""
    try:
        parsed = tomllib.loads(updated)
    except tomllib.TOMLDecodeError as exc:
        raise CodexError(f"refusing to write — result would be invalid TOML ({exc})") from exc

    if not uninstall:
        entry = parsed.get("mcp_servers", {}).get(target.name)
        if not entry or entry.get("url") != target.url:
            raise CodexError("refusing to write — the new entry did not parse back as expected")

    before = set(tomllib.loads(original)) if original.strip() else set()
    lost = before - set(parsed) - {"mcp_servers"}
    if lost:
        raise CodexError(
            f"refusing to write — these top-level tables would be lost: {sorted(lost)}"
        )
    return parsed


def apply(
    target: Target,
    key: Optional[str],
    console: Console,
    *,
    key_env_var: Optional[str] = None,
    dry_run: bool = False,
    uninstall: bool = False,
    path: Optional[Path] = None,
) -> bool:
    path = path or CODEX_CONFIG
    try:
        original = path.read_text(encoding="utf-8") if path.exists() else ""
    except OSError as exc:
        console.err(f"codex: cannot read {path} — {exc}")
        return False

    updated, action = render(
        original, target, key, key_env_var=key_env_var, uninstall=uninstall
    )
    if action == "absent":
        console.skip(f"codex: {target.name} not registered — nothing to do")
        return True

    try:
        validate(original, updated, target, uninstall=uninstall)
    except CodexError as exc:
        console.err(f"codex: {exc}")
        return False

    if dry_run:
        console.ok(f"codex: would {action} {section_name(target.name)} in {path}")
        return True

    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        if path.exists():
            # Timestamped, not a single `.bak`: a second run must not overwrite
            # the only copy of what the file looked like before the first.
            backup = path.with_name(f"config.toml.bak-{datetime.now():%Y%m%d-%H%M%S}")
            shutil.copy2(path, backup)
            console.skip(f"codex: backup → {backup.name}")

        tmp = path.with_suffix(".toml.tmp")
        tmp.write_text(updated, encoding="utf-8")
        os.chmod(tmp, 0o600)  # the file may hold an access key
        tmp.replace(path)  # atomic: never a half-written config
    except OSError as exc:
        console.err(f"codex: {exc}")
        return False

    past = {"add": "added", "update": "updated", "remove": "removed"}[action]
    console.ok(f"codex: {past} {section_name(target.name)} in {path}")
    return True
