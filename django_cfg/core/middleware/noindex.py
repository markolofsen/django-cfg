"""Keep a Django-CFG backend out of search results.

A django-cfg project is an API and an admin, usually on `api.<domain>`; its
public pages live in a separate frontend. So every response carries
`X-Robots-Tag`, on by default (`DjangoConfig.search_indexing = False`).

A header, not `robots.txt`: JSON is not governed by robots.txt, and a URL
disallowed from crawling never has its noindex read.
"""

from typing import Callable

from django.http import HttpRequest, HttpResponse

from django_cfg.core.admin_access import is_admin_path

X_ROBOTS_TAG = "noindex, nofollow, noarchive"


class NoIndexMiddleware:
    """Add `X-Robots-Tag` to every response; no-store on /cfg/ and the admin."""

    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        response["X-Robots-Tag"] = X_ROBOTS_TAG
        if request.path.startswith("/cfg/") or is_admin_path(request.path):
            response["Cache-Control"] = "no-cache, no-store, must-revalidate"
        return response
