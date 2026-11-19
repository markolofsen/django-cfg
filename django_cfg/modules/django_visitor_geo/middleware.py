"""Sets `request.geo` lazily: headers are parsed on first access, so a page that never reads geo pays nothing.

Runs after `RealIPMiddleware` (which resolves the edge). Logs nothing about the visitor.
"""

from django.utils.functional import SimpleLazyObject

from .geo import resolve_geo


class VisitorGeoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.geo = SimpleLazyObject(lambda: resolve_geo(request))
        return self.get_response(request)
