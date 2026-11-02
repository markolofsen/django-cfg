"""Check that social sign-in will work, and print what to register at each provider.

Usage:
    python manage.py oauth_check
    python manage.py oauth_check --probe

Per provider: on or off (and why), the redirect URIs to register for every
site origin, the console link. Then the setup findings (the same list the
system checks warn about). Exit code 1 when there is a finding or a probe fails.

``--probe`` makes one request to the provider's token endpoint with a dummy
code. It spends nothing and changes nothing; the answer tells whether the
client id and secret are known to the provider.
"""

from __future__ import annotations

from django_cfg.management.utils import SafeCommand
from django_cfg.modules.django_mcp.install import Console


class Command(SafeCommand):
    help = "Diagnose OAuth sign-in providers and print the redirect URIs to register"

    def add_arguments(self, parser):
        parser.add_argument(
            "--probe",
            action="store_true",
            help="ask each enabled provider whether the client id and secret are accepted",
        )

    def handle(self, *args, **options):
        from django_cfg.apps.system.accounts.services.oauth.diagnostics import CONFIG_CLASSES, collect_findings
        from django_cfg.apps.system.accounts.services.oauth.redirect import registered_redirect_uris, subdomain_accepted
        from django_cfg.apps.system.accounts.services.oauth.registry import all_providers
        from django_cfg.core.exceptions import ConfigurationError

        console = Console(self)
        failed = False
        console.bold("OAuth sign-in")

        for provider in all_providers():
            console.plain()
            console.bold(provider.name)
            if provider.is_enabled():
                console.ok("enabled")
            else:
                console.skip(f"off: set {' and '.join(CONFIG_CLASSES[provider.id].env_names())}")
                continue

            try:
                uris = registered_redirect_uris(provider.id)
            except ConfigurationError as exc:
                console.err(f"no site to build redirect URIs from: {exc}")
                failed = True
                uris = []
            if uris:
                console.plain("  Authorized redirect URIs (register all of them):")
                for key, uri in uris:
                    console.plain(f"    {uri}   [{key}]")
                for key, origins, pattern in subdomain_accepted(provider.id):
                    console.plain(f"  Also accepted by the subdomain rule [{key}]: {origins}")
                    console.plain(f"    Register {pattern} at the provider before users sign in from it.")
            if provider.id == "google":
                console.plain("  Authorized JavaScript origins: not needed (server-side flow).")
            console.plain(f"  Console: {provider.console_url}")

            if options["probe"]:
                result = provider.probe()
                if result.ok:
                    console.ok(f"probe: {result.detail}")
                else:
                    console.err(f"probe: {result.detail}")
                    failed = True

        findings = collect_findings()
        console.plain()
        if findings:
            console.bold("Findings")
            for finding in findings:
                console.warn(f"{finding.id}: {finding.message}")
                if finding.hint:
                    console.plain(f"      {finding.hint}")
            failed = True
        else:
            console.ok("no setup findings")

        if failed:
            raise SystemExit(1)
