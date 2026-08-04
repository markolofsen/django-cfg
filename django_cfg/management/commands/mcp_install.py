"""Register this project's MCP server with local AI coding assistants.

Usage:
    python manage.py mcp_install                    # all detected assistants
    python manage.py mcp_install --agent claude
    python manage.py mcp_install --agent codex
    python manage.py mcp_install --url https://api.example.com/cfg/mcp/
    python manage.py mcp_install --dry-run
    python manage.py mcp_install --uninstall

The project already serves MCP at ``/cfg/mcp/``; this only writes the client
side, so an assistant knows the URL and the access key.

Why a command instead of a shell script: the URL and the access key already
live in the Django config. Anything external would have to be told them again,
and a second copy of a credential goes stale silently.

Transport asymmetry, and why the two agents are handled differently:

- **Claude Code** exposes ``claude mcp add --transport http … --header``, so the
  vendor's own CLI owns the config format.
- **Codex** does NOT expose header configuration through its CLI (``codex mcp
  add`` targets stdio servers), so a remote HTTP server with an access-key
  header must be written into ``~/.codex/config.toml`` directly.

An assistant that is not installed is skipped, not an error.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

from django_cfg.management.utils import SafeCommand

#: Key under which this server is registered in both assistants.
DEFAULT_SERVER_NAME = "django_cfg"

#: Header the MCP endpoint authenticates with.
ACCESS_KEY_HEADER = "X-MCP-Access-Key"

AGENT_ALL = "all"
AGENT_CLAUDE = "claude"
AGENT_CODEX = "codex"

CODEX_CONFIG = Path.home() / ".codex" / "config.toml"


class Command(SafeCommand):
    help = "Register this project's MCP server with Claude Code and/or Codex"

    def add_arguments(self, parser):
        parser.add_argument(
            "--agent",
            choices=[AGENT_ALL, AGENT_CLAUDE, AGENT_CODEX],
            default=AGENT_ALL,
            help="Which assistant to target (default: all detected)",
        )
        parser.add_argument(
            "--url",
            help="MCP endpoint URL. Defaults to http://localhost:8000/cfg/mcp/",
        )
        parser.add_argument(
            "--name",
            default=DEFAULT_SERVER_NAME,
            help=f"Server name in the assistant's config (default: {DEFAULT_SERVER_NAME})",
        )
        parser.add_argument(
            "--access-key",
            help="Override the access key. Defaults to the configured one.",
        )
        parser.add_argument(
            "--key-env-var",
            help=(
                "Read the access key from this environment variable at runtime "
                "instead of writing it into the config file. Codex only — "
                "Claude Code has no equivalent and will store the literal value."
            ),
        )
        parser.add_argument(
            "--scope",
            choices=["local", "user", "project"],
            default="user",
            help="Claude Code config scope (default: user)",
        )
        parser.add_argument(
            "--uninstall",
            action="store_true",
            help="Remove the registration instead of adding it",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would change without writing anything",
        )

    # ── entry point ─────────────────────────────────────────────────────────

    def handle(self, *args, **options):
        self.dry_run = options["dry_run"]
        self.name = options["name"]
        agent = options["agent"]
        uninstall = options["uninstall"]

        config = self._mcp_config()
        if config is None and not uninstall:
            self.stderr.write(self.style.ERROR("MCP is not enabled in this project's config."))
            self.stderr.write("Set `mcp=DjangoMCPModuleConfig(enabled=True)` and add an `mcp/` folder.")
            return

        url = options["url"] or self._default_url()
        key = options["access_key"] or (getattr(config, "access_key", None) if config else None)
        key_env_var = options["key_env_var"]

        if not uninstall and not key and not key_env_var:
            self.stderr.write(self.style.ERROR("No access key configured."))
            self.stderr.write("Set one via `mcp.set_access_key(...)`, or pass --access-key/--key-env-var.")
            return

        if self.dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN — nothing will be written\n"))

        if not uninstall:
            self._report_target(url, key, key_env_var)

        touched = False
        if agent in (AGENT_ALL, AGENT_CLAUDE):
            touched |= self._do_claude(url, key, options["scope"], uninstall)
        if agent in (AGENT_ALL, AGENT_CODEX):
            touched |= self._do_codex(url, key, key_env_var, uninstall)

        if not touched:
            self.stdout.write(self.style.WARNING(
                "\nNo assistants were changed. Neither `claude` nor `codex` was found on PATH."
            ))
            return

        if not uninstall and not self.dry_run:
            self.stdout.write(self.style.SUCCESS("\nDone. Restart the assistant to pick up the change."))

    # ── configuration discovery ─────────────────────────────────────────────

    def _mcp_config(self) -> Any:
        """The live MCP config, or None when MCP is disabled."""
        try:
            from django_cfg.core.state import get_current_config
        except ImportError:
            return None
        config = get_current_config()
        mcp = getattr(config, "mcp", None) if config else None
        if mcp is None or not getattr(mcp, "enabled", False):
            return None
        return mcp

    def _default_url(self) -> str:
        return "http://localhost:8000/cfg/mcp/"

    def _report_target(self, url: str, key: str | None, key_env_var: str | None) -> None:
        self.stdout.write(f"Server name : {self.name}")
        self.stdout.write(f"Endpoint    : {url}")
        if key_env_var:
            self.stdout.write(f"Access key  : read from ${key_env_var} at runtime")
        else:
            self.stdout.write(f"Access key  : {self._mask(key)}")
        if url.startswith("http://") and "localhost" not in url and "127.0.0.1" not in url:
            self.stdout.write(self.style.WARNING(
                "  ! Plain HTTP to a non-local host — the access key crosses the "
                "network in clear text."
            ))
        self.stdout.write("")

    @staticmethod
    def _mask(key: str | None) -> str:
        if not key:
            return "(none)"
        return key[:4] + "…" + key[-4:] if len(key) > 12 else "…"

    # ── Claude Code ─────────────────────────────────────────────────────────

    def _do_claude(self, url: str, key: str | None, scope: str, uninstall: bool) -> bool:
        binary = shutil.which("claude")
        if not binary:
            self.stdout.write("claude  : not installed — skipped")
            return False

        if uninstall:
            return self._run(
                [binary, "mcp", "remove", self.name, "-s", scope],
                label="claude", action=f"remove {self.name}",
            )

        # `mcp add` fails when the name already exists; removing first makes the
        # command idempotent (re-running updates the URL or key).
        if not self.dry_run:
            subprocess.run(
                [binary, "mcp", "remove", self.name, "-s", scope],
                capture_output=True, timeout=30, check=False,
            )

        cmd = [binary, "mcp", "add", "--transport", "http", self.name, url, "-s", scope]
        if key:
            cmd += ["--header", f"{ACCESS_KEY_HEADER}: {key}"]
        return self._run(cmd, label="claude", action=f"add {self.name} ({scope} scope)")

    def _run(self, cmd: list[str], *, label: str, action: str) -> bool:
        if self.dry_run:
            shown = " ".join(self._redact(c) for c in cmd)
            self.stdout.write(f"{label:8}: would run: {shown}")
            return True
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        except (subprocess.TimeoutExpired, OSError) as exc:
            self.stderr.write(self.style.ERROR(f"{label:8}: {exc}"))
            return False
        if proc.returncode != 0:
            detail = (proc.stderr or proc.stdout or "").strip().splitlines()
            self.stderr.write(self.style.ERROR(
                f"{label:8}: failed — {detail[-1] if detail else 'unknown error'}"
            ))
            return False
        self.stdout.write(self.style.SUCCESS(f"{label:8}: {action}"))
        return True

    @staticmethod
    def _redact(arg: str) -> str:
        if ACCESS_KEY_HEADER in arg:
            return f"{ACCESS_KEY_HEADER}: ***"
        return arg

    # ── Codex ───────────────────────────────────────────────────────────────

    def _do_codex(self, url: str, key: str | None, key_env_var: str | None, uninstall: bool) -> bool:
        if not shutil.which("codex"):
            self.stdout.write("codex   : not installed — skipped")
            return False

        # Codex's CLI cannot set HTTP headers (documented: header configuration
        # is not exposed there), so a keyed remote server must go into the TOML.
        existing = CODEX_CONFIG.read_text() if CODEX_CONFIG.exists() else ""
        section = f"[mcp_servers.{self.name}]"

        if uninstall:
            if section not in existing:
                self.stdout.write(f"codex   : {self.name} not registered — nothing to do")
                return False
            updated = self._strip_section(existing, section)
            return self._write_codex(updated, f"removed {self.name}")

        block = self._codex_block(url, key, key_env_var)
        updated = (
            self._strip_section(existing, section) if section in existing else existing
        )
        if updated and not updated.endswith("\n"):
            updated += "\n"
        updated = f"{updated}\n{block}" if updated.strip() else block
        verb = "updated" if section in existing else "added"
        return self._write_codex(updated, f"{verb} {section}")

    def _codex_block(self, url: str, key: str | None, key_env_var: str | None) -> str:
        lines = [
            f"[mcp_servers.{self.name}]",
            f'url = "{url}"',
        ]
        if key_env_var:
            # Keeps the secret out of the file — Codex resolves it per request.
            lines.append(f'env_http_headers = {{ "{ACCESS_KEY_HEADER}" = "{key_env_var}" }}')
        elif key:
            lines.append(f'http_headers = {{ "{ACCESS_KEY_HEADER}" = "{key}" }}')
        return "\n".join(lines) + "\n"

    @staticmethod
    def _strip_section(text: str, section: str) -> str:
        """Drop one ``[mcp_servers.<name>]`` table, leaving the rest untouched.

        Only the target table is removed — a following table header ends it, so
        unrelated settings and their comments survive.
        """
        pattern = re.compile(
            r"^\s*" + re.escape(section) + r"\s*$.*?(?=^\s*\[|\Z)",
            re.MULTILINE | re.DOTALL,
        )
        return pattern.sub("", text).rstrip() + "\n"

    def _write_codex(self, content: str, action: str) -> bool:
        if self.dry_run:
            self.stdout.write(f"codex   : would write {CODEX_CONFIG} ({action})")
            return True
        try:
            CODEX_CONFIG.parent.mkdir(parents=True, exist_ok=True)
            if CODEX_CONFIG.exists():
                # The file holds unrelated user settings; keep a copy before
                # rewriting it.
                backup = CODEX_CONFIG.with_suffix(".toml.bak")
                shutil.copy2(CODEX_CONFIG, backup)
            CODEX_CONFIG.write_text(content)
        except OSError as exc:
            self.stderr.write(self.style.ERROR(f"codex   : {exc}"))
            return False
        self.stdout.write(self.style.SUCCESS(f"codex   : {action} in {CODEX_CONFIG}"))
        return True
