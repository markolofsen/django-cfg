"""
cfg_edge_ranges - show or refresh the Cloudflare ranges `core/edge.py` trusts.

    python manage.py cfg_edge_ranges              # print what is in use and where it came from
    python manage.py cfg_edge_ranges --refresh    # fetch api.cloudflare.com/client/v4/ips into the cache dir

The runtime never fetches. A refreshed copy wins over the bundled one; restart the processes to pick it up.
"""
from __future__ import annotations

import ipaddress
import json
import urllib.request

from django.core.management.base import BaseCommand, CommandError

API = "https://api.cloudflare.com/client/v4/ips"


class Command(BaseCommand):
    help = "Show or refresh the Cloudflare edge ranges used to trust CF-* headers"

    def add_arguments(self, parser):
        parser.add_argument("--refresh", action="store_true", help=f"Fetch {API} and store it in the cache dir")

    def handle(self, *args, **options):
        from django_cfg.core.edge import cloudflare_networks, ranges_cache_path
        from django_cfg.core.edge_ranges import FETCHED
        from django_cfg.core.utils.runtime_paths import ensure_dir

        path = ranges_cache_path()
        if options["refresh"]:
            try:
                with urllib.request.urlopen(API, timeout=15) as response:  # noqa: S310 - fixed https URL
                    result = json.load(response)["result"]
                cidrs = list(result["ipv4_cidrs"]) + list(result["ipv6_cidrs"])
                for cidr in cidrs:
                    ipaddress.ip_network(cidr)
            except Exception as exc:  # noqa: BLE001
                raise CommandError(f"Could not fetch Cloudflare ranges: {exc}") from exc
            if len(cidrs) < 10:
                raise CommandError(f"Refusing a suspiciously short list ({len(cidrs)} ranges)")
            target = ensure_dir(path.parent) / path.name
            target.write_text(f"# {API} etag {result.get('etag', '')}\n" + "\n".join(cidrs) + "\n")
            cloudflare_networks.cache_clear()
            self.stdout.write(self.style.SUCCESS(f"Wrote {len(cidrs)} ranges to {target}. Restart the app processes."))
            return

        source = str(path) if path.is_file() else f"bundled ({FETCHED})"
        networks = cloudflare_networks()
        self.stdout.write(f"{len(networks)} Cloudflare ranges in use, from {source}")
        for network in networks:
            self.stdout.write(f"  {network}")
