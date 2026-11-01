"""``request.site``: the resolved ``Site``, computed on first use.

Registered only when ``DjangoConfig.sites`` declares more than one site; a
single-site project reads ``site_for(request)`` and pays nothing.
"""

from django.utils.functional import SimpleLazyObject

from django_cfg.core.site import site_for


class SiteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.site = SimpleLazyObject(lambda: site_for(request))
        return self.get_response(request)
