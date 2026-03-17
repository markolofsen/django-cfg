"""
django_grpc.services.auth.jwt_auth — JWT Bearer token interceptor.

Uses rest_framework_simplejwt token format (HS256, Django SECRET_KEY).
Validates token locally — zero network requests on hot path.

Token format (simplejwt defaults):
    header:  {"alg": "HS256", "typ": "JWT"}
    payload: {
        "token_type": "access",
        "exp":     <unix timestamp>,
        "iat":     <unix timestamp>,
        "jti":     "<uuid>",
        "user_id": <int>,
        "email":   "<str>",        # optional — add via custom TokenObtainPairSerializer
        "roles":   ["<str>", ...]  # optional — add via custom TokenObtainPairSerializer
    }

Go client sends:  metadata "authorization: Bearer <access_token>"
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

import jwt as pyjwt

logger = logging.getLogger(__name__)

_REFLECTION_METHOD = "/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo"

# K-1 fix: reflection removed from the unconditional public-methods set.
# Previously, reflection was always public even when require_auth=True — any
# anonymous caller could enumerate all service names, methods, and protobuf
# schemas via grpcurl.  Now controlled by GrpcServerConfig.reflection_require_auth:
#   - False (default) → reflection re-added at runtime → backward compatible
#   - True           → reflection requires a valid JWT (or reflection_admin_key)
_DEFAULT_PUBLIC_METHODS: frozenset = frozenset({
    "/grpc.health.v1.Health/Check",
    "/grpc.health.v1.Health/Watch",
})


def _get_secret_key() -> str:
    """Get Django SECRET_KEY via config_helper — single source of truth."""
    from django_cfg.modules.django_grpc.services.management.config_helper import get_secret_key
    return get_secret_key()


def _get_jwt_algorithm() -> str:
    """Read jwt_algorithm from grpc_module auth config. Falls back to HS256."""
    try:
        from django_cfg.modules.django_grpc.__cfg__ import settings as grpc_settings
        return grpc_settings.auth.jwt_algorithm
    except Exception:
        return "HS256"


def decode_jwt(token: str) -> Optional[dict]:
    """
    Decode and verify a simplejwt access token.

    Returns payload dict on success, None on any failure (expired, bad sig, wrong type).
    Uses PyJWT directly — simplejwt always installs it.
    Runs synchronously; call via asyncio.to_thread() from async context.
    """
    if not token:
        return None
    try:
        payload = pyjwt.decode(
            token,
            _get_secret_key(),
            algorithms=[_get_jwt_algorithm()],
            options={"require": ["exp", "user_id", "token_type"]},
        )
        # Only accept access tokens, not refresh tokens
        if payload.get("token_type") != "access":
            logger.debug("JWT rejected: token_type=%s", payload.get("token_type"))
            return None
        return payload
    except Exception as exc:
        logger.debug("JWT decode failed: %s", exc)
        return None


try:
    import grpc
    import grpc.aio
    _grpc_interceptor_base = grpc.aio.ServerInterceptor
except ImportError:
    grpc = None  # type: ignore[assignment]
    _grpc_interceptor_base = object  # type: ignore[assignment,misc]


class JWTAuthInterceptor(_grpc_interceptor_base):  # type: ignore[misc]
    """
    gRPC JWT interceptor. Validates simplejwt Bearer token from request metadata.

    require_auth=False (default):
        Anonymous requests pass through.
        Authenticated requests get GrpcUserContext populated in ContextVar.

    require_auth=True:
        Requests without a valid JWT are rejected with UNAUTHENTICATED.

    public_methods:
        Set of full method names always allowed without auth.
        Health check and reflection are always included automatically.
    """

    def __init__(
        self,
        require_auth: bool = False,
        public_methods: Optional[set] = None,
    ) -> None:
        self.require_auth = require_auth
        self.public_methods: frozenset = (
            frozenset(public_methods) | _DEFAULT_PUBLIC_METHODS
            if public_methods is not None
            else _DEFAULT_PUBLIC_METHODS
        )

    def _build_effective_public_methods(self) -> frozenset:
        """Build effective public methods set, adding reflection if not auth-gated.

        K-1: reads GrpcServerConfig.reflection_require_auth at runtime so that
        changes to the config model are picked up without restarting the interceptor.
        Default (reflection_require_auth=False) restores backward-compatible behaviour.
        """
        try:
            from django_cfg.modules.django_grpc.services.management.config_helper import (
                get_grpc_module_config,
            )
            cfg = get_grpc_module_config()
            server_cfg = cfg.server if cfg else None
            if server_cfg is None or not server_cfg.reflection_require_auth:
                # reflection is not auth-gated — add it back as public
                return self.public_methods | frozenset({_REFLECTION_METHOD})
        except Exception as e:
            # config not available → keep reflection public (safe default)
            logger.warning("Failed to load gRPC config for reflection auth check: %s", e)
            return self.public_methods | frozenset({_REFLECTION_METHOD})
        return self.public_methods

    async def intercept_service(self, continuation, handler_call_details):
        from .context import GrpcUserContext, _grpc_user_var
        from ..interceptors.wrapped_handler import WrappedHandler

        effective_public = self._build_effective_public_methods()

        # Always bypass auth for public methods (health + optionally reflection)
        if handler_call_details.method in effective_public:
            return await continuation(handler_call_details)

        # Internal secret bypass — trusted Django→gRPC calls skip all auth.
        # Same pattern as reflection_admin_key below.
        try:
            from django_cfg.modules.django_grpc.services.management.config_helper import (
                get_grpc_module_config,
            )
            cfg = get_grpc_module_config()
            internal_secret = cfg.auth.internal_secret if cfg else None
            if internal_secret:
                metadata = dict(handler_call_details.invocation_metadata)
                req_secret = metadata.get("x-internal-secret", "")
                if isinstance(req_secret, bytes):
                    req_secret = req_secret.decode()
                if req_secret == internal_secret:
                    return await continuation(handler_call_details)
        except Exception as e:
            logger.debug("Failed to check internal_secret: %s", e)

        # K-1: check reflection_admin_key bypass for reflection endpoint
        if handler_call_details.method == _REFLECTION_METHOD:
            try:
                from django_cfg.modules.django_grpc.services.management.config_helper import (
                    get_grpc_module_config,
                )
                cfg = get_grpc_module_config()
                admin_key = cfg.server.reflection_admin_key if cfg else None
                if admin_key:
                    metadata = dict(handler_call_details.invocation_metadata)
                    request_key = metadata.get("x-admin-key", "")
                    if isinstance(request_key, bytes):
                        request_key = request_key.decode()
                    if request_key == admin_key:
                        return await continuation(handler_call_details)
            except Exception as e:
                logger.debug("Failed to check reflection_admin_key: %s", e)

        # Extract Bearer token from metadata
        metadata = dict(handler_call_details.invocation_metadata)
        auth_val = metadata.get("authorization", "")
        auth_str = auth_val.decode() if isinstance(auth_val, bytes) else auth_val
        raw_token = auth_str.removeprefix("Bearer ").strip()

        user_ctx: Optional[GrpcUserContext] = None
        if raw_token:
            payload = await asyncio.to_thread(decode_jwt, raw_token)
            if payload is not None:
                user_ctx = {
                    "user_id":          payload.get("user_id"),
                    "email":            payload.get("email", ""),
                    "roles":            payload.get("roles", []),
                    "is_authenticated": True,
                    "is_active":        1,
                    # A5: safe defaults — missing claims → False, never KeyError in handlers
                    "is_staff":         bool(payload.get("is_staff", False)),
                    "is_superuser":     bool(payload.get("is_superuser", False)),
                }

        if user_ctx is not None:
            _grpc_user_var.set(user_ctx)  # type: ignore[arg-type]

            handler = await continuation(handler_call_details)
            if handler is None:
                return None  # type: ignore[return-value]

            wrapped: dict = {}
            for attr in ("unary_unary", "unary_stream", "stream_unary", "stream_stream"):
                behavior = getattr(handler, attr)
                if behavior is not None:
                    wrapped[attr] = self._attach_user(behavior, user_ctx, handler_type=attr)
            return WrappedHandler(handler, **wrapped)  # type: ignore[return-value]

        if self.require_auth:
            handler = await continuation(handler_call_details)

            async def _deny_coro(req_or_iter, ctx):  # noqa: ANN001
                await ctx.abort(grpc.StatusCode.UNAUTHENTICATED, "Valid JWT token required")  # type: ignore[union-attr]

            async def _deny_gen(req_or_iter, ctx):  # noqa: ANN001
                await ctx.abort(grpc.StatusCode.UNAUTHENTICATED, "Valid JWT token required")  # type: ignore[union-attr]
                return
                yield  # make it an async generator

            deny_map: dict = {}
            if handler and getattr(handler, "unary_unary", None):   deny_map["unary_unary"]   = _deny_coro
            if handler and getattr(handler, "stream_unary", None):  deny_map["stream_unary"]  = _deny_coro
            if handler and getattr(handler, "unary_stream", None):  deny_map["unary_stream"]  = _deny_gen
            if handler and getattr(handler, "stream_stream", None): deny_map["stream_stream"] = _deny_gen

            if deny_map:
                return WrappedHandler(handler, **deny_map)  # type: ignore[return-value]
            return grpc.unary_unary_rpc_method_handler(_deny_coro)  # type: ignore[return-value,union-attr]

        # Anonymous pass-through
        return await continuation(handler_call_details)

    def _attach_user(self, behavior, user_ctx, handler_type: str = "unary_unary"):
        """Wrap a handler to set GrpcUserContext in ContextVar before each call.

        Explicit dispatch by handler_type — avoids inspect.isasyncgenfunction()
        which can return False for gRPC-wrapped async generators.
        """
        from .context import _grpc_user_var

        if handler_type in ("unary_stream", "stream_stream"):
            async def async_gen_wrapper(*args, **kwargs):
                _grpc_user_var.set(user_ctx)  # type: ignore[arg-type]
                async for item in behavior(*args, **kwargs):
                    yield item
            return async_gen_wrapper

        async def coro_wrapper(*args, **kwargs):
            _grpc_user_var.set(user_ctx)  # type: ignore[arg-type]
            return await behavior(*args, **kwargs)

        return coro_wrapper


__all__ = ["JWTAuthInterceptor", "decode_jwt"]
