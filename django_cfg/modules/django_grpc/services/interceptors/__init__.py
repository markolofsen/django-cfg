"""django_grpc.services.interceptors — gRPC server interceptors."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from django_cfg.modules.django_grpc.__cfg__ import DjangoGrpcModuleConfig


def _as_grpc_config(config: Any) -> "DjangoGrpcModuleConfig | None":
    """Return config typed as DjangoGrpcModuleConfig if it is one, else None."""
    try:
        from django_cfg.modules.django_grpc.__cfg__ import DjangoGrpcModuleConfig
        if isinstance(config, DjangoGrpcModuleConfig):
            return config
    except Exception:
        pass
    return None


def build_interceptors(config: Any | None = None) -> list:
    """
    Build and return interceptors in the correct order.

    Order is critical:
        [OTel →] ErrorHandling → Auth → Observability
        Auth sets _grpc_user_var; Observability reads it.
        OTel is outermost when enabled (H-7).

    Max 2 interceptors wrapping request_iterator (streaming buffer constraint).
    See @dev/v3/bugs_and_constraints.md for details.

    Args:
        config: DjangoGrpcModuleConfig instance, or None for defaults.
    """
    import logging
    from .errors import ErrorHandlingInterceptor
    from .observability import ObservabilityInterceptor

    _logger = logging.getLogger(__name__)
    interceptors: list = []

    # Resolve to typed config (None if not DjangoGrpcModuleConfig) — needed here for OTel check
    cfg = _as_grpc_config(config)

    # H-7: OTel interceptor — outermost layer (optional; requires opentelemetry-instrumentation-grpc)
    otel_enabled = cfg.observability.otel_enabled if cfg else False
    if otel_enabled:
        try:
            from opentelemetry.instrumentation.grpc import OpenTelemetryServerInterceptor  # type: ignore[import-untyped]
            interceptors.append(OpenTelemetryServerInterceptor())
        except ImportError:
            _logger.warning(
                "observability.otel_enabled=True but opentelemetry-instrumentation-grpc is not installed; "
                "OTel interceptor skipped"
            )

    # Error handler (grpc.aio.ServerInterceptor — no request_iterator wrapping)
    interceptors.append(ErrorHandlingInterceptor())

    # Auth interceptor: custom class or built-in JWT.
    # Custom interceptor replaces JWT entirely (e.g., API key / CLI token auth).
    custom_interceptor_class = cfg.auth.interceptor_class if cfg else ""
    if custom_interceptor_class:
        import importlib
        module_path, class_name = custom_interceptor_class.rsplit(".", 1)
        mod = importlib.import_module(module_path)
        interceptor_cls = getattr(mod, class_name)
        interceptors.append(interceptor_cls())
        _logger.info("Auth interceptor: %s (custom)", class_name)
    else:
        # A4: always register JWTAuthInterceptor so that valid tokens always set user context,
        # even when require_auth=False. The interceptor passes anonymous requests through when
        # require_auth=False, but still populates _grpc_user_var for valid tokens.
        require_auth = cfg.auth.require_auth if cfg else False
        public_methods: set[str] = set(cfg.auth.public_methods) if cfg else set()

        from ..auth.jwt_auth import JWTAuthInterceptor
        interceptors.append(JWTAuthInterceptor(
            require_auth=require_auth,
            public_methods=public_methods,
        ))

    # Observability (always last — reads auth context set by auth interceptor)
    enable_request_logging = cfg.persistence.log_requests if cfg else True
    interceptors.append(ObservabilityInterceptor(
        enable_request_logging=enable_request_logging,
    ))

    # Sanity check: auth interceptor must come before observability
    auth_names = {"JWTAuthInterceptor", "AuthInterceptor", "CLITokenAuthInterceptor"}
    auth_indices = [i for i, x in enumerate(interceptors) if type(x).__name__ in auth_names]
    obs_indices = [i for i, x in enumerate(interceptors) if type(x).__name__ == "ObservabilityInterceptor"]
    if auth_indices and obs_indices:
        assert auth_indices[-1] < obs_indices[0], (
            "Auth interceptor must be registered before ObservabilityInterceptor"
        )

    return interceptors


__all__ = ["build_interceptors"]
