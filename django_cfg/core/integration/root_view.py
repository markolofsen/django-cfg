"""What a person sees opening the backend's own address (`api.<domain>/`).

Not a page of ours: a redirect to the site whose `api_url` host this is —
`api.mlsbali.com/` → `https://mlsbali.com/`. One Django serving several sites
sends each to its own; a single-site project has one. Any other host (localhost,
an IP, an internal name, an unregistered domain) gets a one-line text answer.

Added by `add_django_cfg_urls` after the project's routes, so a project's own
`""` route still wins.
"""

from urllib.parse import urlsplit

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

from django_cfg.core.site import sites


def public_site_for(host: str) -> str | None:
    """The `site_url` of the site whose `api_url` host is `host`, with a trailing slash."""
    name = host.split(":")[0].strip().lower().rstrip(".")
    # A loopback API host never has a public page to send people to, and a
    # site whose API lives on its own host would redirect to itself.
    if name in {"localhost", "127.0.0.1", "::1"} or name.endswith(".localhost"):
        return None
    for site in sites():
        if urlsplit(site.api_url).hostname == name and urlsplit(site.site_url).hostname != name:
            return site.site_url + "/"
    return None


def root_view(request: HttpRequest) -> HttpResponse:
    # 302, not 301: a permanent redirect is cached by browsers for good.
    target = public_site_for(request.get_host())
    if target:
        return HttpResponseRedirect(target)
    return HttpResponse("OK\n", content_type="text/plain; charset=utf-8")
