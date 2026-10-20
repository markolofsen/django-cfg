"""What a person sees opening the backend's own address (`api.<domain>/`).

Not a page of ours: a redirect to the same domain without the `api.` label —
`api.mlsbali.com/` → `https://mlsbali.com/`. Read from the request's host, so
one Django serving several brands sends each to its own site. A host with no
`api.` label (localhost, an IP, an internal name) gets a one-line text answer.

Added by `add_django_cfg_urls` after the project's routes, so a project's own
`""` route still wins.
"""

from django.http import HttpRequest, HttpResponse, HttpResponseRedirect

API_LABEL = "api."


def public_site_for(host: str) -> str | None:
    """`https://<domain>/` for `api.<domain>[:port]`, else None."""
    name = host.split(":")[0].strip().lower().rstrip(".")
    if not name.startswith(API_LABEL) or "." not in name[len(API_LABEL):]:
        return None
    return f"https://{name[len(API_LABEL):]}/"


def root_view(request: HttpRequest) -> HttpResponse:
    # 302, not 301: a permanent redirect is cached by browsers for good.
    site = public_site_for(request.get_host())
    if site:
        return HttpResponseRedirect(site)
    return HttpResponse("OK\n", content_type="text/plain; charset=utf-8")
