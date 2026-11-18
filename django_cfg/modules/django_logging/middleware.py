"""RequestIdMiddleware: sets the request id contextvar and echoes it as ``X-Request-ID``."""
from __future__ import annotations

from asgiref.sync import iscoroutinefunction, markcoroutinefunction
from django.conf import settings

from .context import new_request_id, request_id_var

HEADER = "X-Request-ID"


class RequestIdMiddleware:
    sync_capable = True
    async_capable = True

    def __init__(self, get_response):
        self.get_response = get_response
        if iscoroutinefunction(get_response):
            markcoroutinefunction(self)

    def _id(self, request):
        trust = getattr(settings, "DJANGO_CFG_TRUST_REQUEST_ID", True)
        return new_request_id(request.META.get("HTTP_X_REQUEST_ID"), request.META.get("REMOTE_ADDR", ""), bool(trust))

    def __call__(self, request):
        if iscoroutinefunction(self.get_response):
            return self._acall(request)
        rid = self._id(request)
        token = request_id_var.set(rid)
        try:
            response = self.get_response(request)
        finally:
            request_id_var.reset(token)
        if rid:
            response[HEADER] = rid
        return response

    async def _acall(self, request):
        rid = self._id(request)
        token = request_id_var.set(rid)
        try:
            response = await self.get_response(request)
        finally:
            request_id_var.reset(token)
        if rid:
            response[HEADER] = rid
        return response
