"""Generic manage views: they hold no data, every call goes through the store."""

from __future__ import annotations

from drf_spectacular.utils import extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    ConnectionListSerializer, KeyCreatedSerializer, KeyCreateSerializer, KeyListSerializer,
    ProblemSerializer, RevokedSerializer, UsageSerializer,
)
from .store import StoreRefusal, supports

TAG = "mcp-manage"
NO_STORE = {"Cache-Control": "no-store"}
_ERRORS = {401: ProblemSerializer, 404: ProblemSerializer}


def problem(code: str, detail: str, status: int, headers=None) -> Response:
    return Response({"code": code, "detail": detail, "status": status}, status=status,
                    content_type="application/problem+json", headers=headers)


class ManageView(APIView):
    """Base: signed-in users only, `no-store` on everything, 404 for a part the store lacks."""

    permission_classes = [IsAuthenticated]
    store = None  # set by as_view(store=...)
    needs: dict = {}  # HTTP method -> store method it requires

    def get_authenticate_header(self, request):
        # An anonymous call is a 401 whatever the project's first authenticator is.
        return super().get_authenticate_header(request) or "Bearer"

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        need = self.needs.get(request.method.lower())
        if need and not supports(self.store, need):
            raise _Unsupported()

    def handle_exception(self, exc):
        if isinstance(exc, _Unsupported):
            return problem("unsupported", "This part of MCP access is not available.", 404)
        if isinstance(exc, StoreRefusal):
            headers = {"Retry-After": "3600"} if exc.status == 429 else None
            return problem(exc.code, exc.message, exc.status, headers)
        return super().handle_exception(exc)

    def finalize_response(self, request, response, *args, **kwargs):
        response = super().finalize_response(request, response, *args, **kwargs)
        response["Cache-Control"] = "no-store"
        return response


class _Unsupported(Exception):
    pass


class KeysView(ManageView):
    needs = {"get": "list_keys", "post": "create_key"}

    @extend_schema(operation_id="mcp_manage_keys_list", responses={200: KeyListSerializer, **_ERRORS}, tags=[TAG])
    def get(self, request):
        """The user's keys, newest first. Never the secret."""
        return Response(KeyListSerializer({"results": self.store.list_keys(request.user)}).data)

    @extend_schema(operation_id="mcp_manage_keys_create", request=KeyCreateSerializer,
                   responses={201: KeyCreatedSerializer, 409: ProblemSerializer, 422: ProblemSerializer, 429: ProblemSerializer, **_ERRORS}, tags=[TAG])
    def post(self, request):
        """A new key. `key` is in this response only."""
        data = KeyCreateSerializer(data=request.data)
        if not data.is_valid():
            return problem("invalid", str(data.errors), 422)
        v = data.validated_data
        row, secret = self.store.create_key(request.user, v["name"], v["scopes"], v["expires_in_days"])
        return Response(KeyCreatedSerializer({**row, "key": secret}).data, status=201)


class KeyView(ManageView):
    needs = {"delete": "revoke_key"}

    @extend_schema(operation_id="mcp_manage_keys_revoke", responses={204: None, **_ERRORS}, tags=[TAG])
    def delete(self, request, pk: int):
        """Revoke a key. Repeating it, or another user's id, is also 204."""
        self.store.revoke_key(request.user, pk)
        return Response(status=204)


class ConnectionsView(ManageView):
    needs = {"get": "list_connections"}

    @extend_schema(operation_id="mcp_manage_connections_list", responses={200: ConnectionListSerializer, **_ERRORS}, tags=[TAG])
    def get(self, request):
        """The OAuth clients the user allowed, newest first."""
        return Response(ConnectionListSerializer({"results": self.store.list_connections(request.user)}).data)


class ConnectionView(ManageView):
    needs = {"delete": "revoke_connection"}

    @extend_schema(operation_id="mcp_manage_connections_revoke", responses={204: None, **_ERRORS}, tags=[TAG])
    def delete(self, request, pk: int):
        """End one connection. Repeating it, or another user's id, is also 204."""
        self.store.revoke_connection(request.user, pk)
        return Response(status=204)


class RevokeAllView(ManageView):
    needs = {"post": "revoke_all"}

    @extend_schema(operation_id="mcp_manage_revoke_all", request=None, responses={200: RevokedSerializer, **_ERRORS}, tags=[TAG])
    def post(self, request):
        """Revoke every key and end every connection of the user."""
        keys, connections = self.store.revoke_all(request.user)
        return Response(RevokedSerializer({"revoked": keys, "connections": connections}).data)


class UsageView(ManageView):
    needs = {"get": "usage"}

    @extend_schema(operation_id="mcp_manage_usage", responses={200: UsageSerializer, **_ERRORS}, tags=[TAG])
    def get(self, request):
        """Units spent today and this hour against the caps, and calls per tool in the last 24 hours."""
        return Response(UsageSerializer(self.store.usage(request.user)).data)
