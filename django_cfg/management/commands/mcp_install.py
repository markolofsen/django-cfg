"""Register this project's MCP server with local AI coding assistants.

Usage:
    python manage.py mcp_install --local
    python manage.py mcp_install --prod
    python manage.py mcp_install --local --uninstall
    python manage.py mcp_install --url https://staging.example.com/cfg/mcp/ --name staging

The project already serves MCP at ``/cfg/mcp/``; this only writes the client
side, so an assistant knows the URL and the access key.

Why a command rather than a shell script per project: the endpoint and the key
already live in the Django config. Anything external has to be told them again,
and a second copy of a credential goes stale silently — which is how a *local*
development key came to be registered against production, connecting cleanly,
listing every tool, and failing only on the first real call.

The flags are whatever the project declared via ``mcp.add_target(...)``. There
is deliberately **no default target**: both ends serve the same tools over the
same protocol, so a client aimed at the wrong one does not fail — it answers
from the other environment's database.

The machinery lives in ``django_cfg.modules.django_mcp.install``; this file is
argument parsing and nothing else.
"""

from __future__ import annotations

from django_cfg.management.utils import SafeCommand
from django_cfg.modules.django_mcp.install import (
    Console,
    InstallOptions,
    Target,
    TargetError,
    resolve_target,
    run,
)
from django_cfg.modules.django_mcp.install.discovery import (
    base_dir,
    declared_kinds,
    mcp_config,
    registry,
)


class Command(SafeCommand):
    help = "Register this project's MCP server with Claude Code and/or Codex"

    def add_arguments(self, parser):
        parser.add_argument("--target", help="target name declared by this project")
        for kind in declared_kinds():
            parser.add_argument(
                f"--{kind}", action="store_true", help=f"shorthand for --target {kind}"
            )
        parser.add_argument("--url", help="some other endpoint; requires --name")
        parser.add_argument("--name", help="override the server name for this target")
        parser.add_argument("--key", help="access key; overrides what the files resolve to")
        parser.add_argument(
            "--key-env-var",
            help="codex only: read the key from this variable at runtime rather "
            "than writing it into the config file",
        )
        parser.add_argument("--agent", choices=("all", "claude", "codex"), default="all")
        parser.add_argument(
            "--scope", choices=("local", "user", "project"), default="user",
            help="Claude Code config scope (default: user)",
        )
        parser.add_argument("--uninstall", action="store_true")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--skip-probe", action="store_true")

    def handle(self, *args, **options):
        console = Console(self)

        try:
            target = self._target(options)
        except TargetError as exc:
            console.err(str(exc))
            return

        exit_code = run(
            target,
            InstallOptions(
                agent=options["agent"],
                scope=options["scope"],
                key_env_var=options["key_env_var"],
                explicit_key=options["key"],
                dry_run=options["dry_run"],
                uninstall=options["uninstall"],
                skip_probe=options["skip_probe"],
                display_root=base_dir(),
                # Only consumed by a target that declares no env files, i.e.
                # the local one, where this process is the deployment.
                local_key=getattr(mcp_config(), "access_key", None),
            ),
            console,
        )
        if exit_code:
            # SystemExit so a scripted caller sees the failure; Django would
            # otherwise exit 0 on a refused install.
            raise SystemExit(exit_code)

    # ── target selection ────────────────────────────────────────────────────

    def _target(self, options: dict) -> Target:
        kind = options.get("target")
        chosen = [k for k in declared_kinds() if options.get(k)]
        if kind and chosen:
            raise TargetError(f"pick one: --target {kind} or --{chosen[0]}")
        if len(chosen) > 1:
            raise TargetError(
                "pick one target, not " + ", ".join(f"--{c}" for c in chosen)
            )
        kind = kind or (chosen[0] if chosen else None)

        return resolve_target(
            registry(), kind=kind, url=options.get("url"), name=options.get("name")
        )
