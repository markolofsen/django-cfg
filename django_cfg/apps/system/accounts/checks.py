"""System checks for the OAuth sign-in setup (findings: ``services/oauth/diagnostics.py``)."""

from django.core.checks import Warning, register


@register("django_cfg")
def check_oauth_setup(app_configs, **kwargs):
    from .services.oauth.diagnostics import collect_findings

    return [Warning(f.message, hint=f.hint or None, id=f.id) for f in collect_findings()]
