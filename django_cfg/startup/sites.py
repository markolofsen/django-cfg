"""System check for the declared sites.

django_cfg.W020  `security_domains` repeats a host a declared site (or the
                 deployment `api_url`) already declares. Harmless, redundant:
                 site hosts are allowed automatically, so `security_domains`
                 is for extra hosts only. Never an error.

Duplicate keys, shared origins, a shared host for `site_url` and `api_url`,
brand fields set next to `sites`, and http outside development are rejected
when the config loads, not here.
"""

from __future__ import annotations

from django.core.checks import Tags, Warning, register


@register(Tags.security)
def check_redundant_security_domains(app_configs, **kwargs):
    from django_cfg.core.site import redundant_security_domains
    from django_cfg.core.state.registry import get_current_config

    config = get_current_config()
    if config is None:
        return []
    return [
        Warning(
            f"security_domains repeats {entry!r}, which {owner} already declares.",
            hint="Remove it: hosts of declared sites and the deployment api_url are allowed "
                 "automatically. Keep security_domains for extra hosts (mcp.*, internal names, wildcards).",
            id="django_cfg.W020",
        )
        for entry, owner in redundant_security_domains(config)
    ]
