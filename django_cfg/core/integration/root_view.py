"""What a person sees opening the backend's own address (`api.<domain>/`).

Not a page of ours: a redirect to the public site (`DjangoConfig.site_url`),
or a one-line text answer when there is nowhere else to send them. Added by
`add_django_cfg_urls` after the project's routes, so a project's own `""`
route still wins.
"""

from urllib.parse import urlparse

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect


def _public_site(request: HttpRequest) -> str | None:
    from django_cfg.core.state import get_current_config

    config = get_current_config()
    url = (getattr(config, "site_url", "") or "").strip()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return None
    # A site_url pointing back at this host would loop.
    if parsed.netloc.lower() == request.get_host().lower():
        return None
    return url


def root_view(request: HttpRequest) -> HttpResponse:
    # 302, not 301: site_url can change, and a permanent redirect is cached by browsers.
    site = _public_site(request)
    if site:
        return HttpResponseRedirect(site)
    return HttpResponse("OK\n", content_type="text/plain; charset=utf-8")
