"""System checks for `config.edge` and `config.visitor_geo`.

django_cfg.W040  edge.trust="secret" without edge.secret: no request is ever trusted, geo is always empty.
django_cfg.W041  The bundled Cloudflare ranges are older than 180 days and no refreshed copy exists:
                 a new Cloudflare range would be treated as an unknown proxy. Run `manage.py cfg_edge_ranges --refresh`
                 or update django-cfg.
django_cfg.W042  visitor_geo.level="city" with coords_precision 2: about 1 km, close to an address. Use 1 unless
                 the product needs it.
"""

from __future__ import annotations

from datetime import date

from django.core.checks import Tags, Warning, register


@register(Tags.security)
def check_edge(app_configs, **kwargs):
    from django_cfg.core.edge import get_edge_config, ranges_cache_path
    from django_cfg.core.edge_ranges import FETCHED
    from django_cfg.modules.django_visitor_geo.geo import get_visitor_geo_config

    problems = []
    edge = get_edge_config()
    if edge.trust == "secret" and not (edge.secret and edge.secret.get_secret_value()):
        problems.append(Warning(
            "edge.trust is 'secret' but edge.secret is empty: no request is trusted.",
            hint="Set EDGE__SECRET to the value your Cloudflare Transform Rule writes into X-Edge-Auth.",
            id="django_cfg.W040",
        ))
    if edge.trust == "cloudflare":
        try:
            refreshed = ranges_cache_path().is_file()
        except Exception:  # noqa: BLE001
            refreshed = False
        if not refreshed and (date.today() - date.fromisoformat(FETCHED)).days > 180:
            problems.append(Warning(
                f"Bundled Cloudflare ranges date from {FETCHED}.",
                hint="Run `manage.py cfg_edge_ranges --refresh` (or update django-cfg).",
                id="django_cfg.W041",
            ))
    geo = get_visitor_geo_config()
    if geo.level == "city" and geo.coords_precision >= 2:
        problems.append(Warning(
            "visitor_geo keeps coordinates to about 1 km.",
            hint="Set visitor_geo.coords_precision=1 (about 11 km) unless the product needs more.",
            id="django_cfg.W042",
        ))
    return problems
