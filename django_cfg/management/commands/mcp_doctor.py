"""Check that this project's MCP setup will actually work.

Usage:
    python manage.py mcp_doctor
    python manage.py mcp_doctor --skip-probe

Four things must all hold before an assistant can call a tool, and each one
fails **invisibly** on its own:

- the access key is set (an empty one does not disable the endpoint — it
  removes the requirement, so the server answers everybody);
- the key is bound to an account, or every staff-gated tool refuses in a way an
  agent reads as an empty result;
- that account exists, is active, and is not a superuser;
- the declared endpoints answer, and answer with a 401 rather than a 200.

None of this proves the tools work. A connected server with a valid key has
still shipped tools that raised on every call while listing cleanly — finish by
calling one.
"""

from __future__ import annotations

from django_cfg.management.utils import SafeCommand
from django_cfg.modules.django_mcp.install import Console
from django_cfg.modules.django_mcp.install.discovery import mcp_config, registry
from django_cfg.modules.django_mcp.install.doctor import diagnose, report


class Command(SafeCommand):
    help = "Diagnose this project's MCP server, key and client-facing endpoints"

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-probe",
            action="store_true",
            help="do not make network requests to the declared endpoints",
        )

    def handle(self, *args, **options):
        console = Console(self)
        config = mcp_config()

        if config is None:
            console.err("MCP is not enabled for this project.")
            console.plain("  Set mcp=DjangoMCPModuleConfig(enabled=True) and add an mcp/ folder.")
            raise SystemExit(1)

        console.bold("MCP doctor")
        console.plain()
        findings = diagnose(config, registry(), skip_probe=options["skip_probe"])
        if report(findings, console):
            raise SystemExit(1)
