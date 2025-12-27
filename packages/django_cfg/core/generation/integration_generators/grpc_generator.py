"""
gRPC framework generator.

Handles gRPC server, authentication, and proto configuration.
Size: ~250 lines (focused on gRPC framework)
"""

import logging
from typing import TYPE_CHECKING, Any, Dict, List

if TYPE_CHECKING:
    from ...base.config_model import DjangoConfig

logger = logging.getLogger(__name__)


class GRPCSettingsGenerator:
    """
    Generates gRPC framework settings.

    Responsibilities:
    - Configure gRPC server settings
    - Setup authentication and interceptors
    - Configure proto generation
    - Auto-detect if gRPC should be enabled
    - Resolve handlers hook from ROOT_URLCONF

    Example:
        ```python
        generator = GRPCSettingsGenerator(config)
        settings = generator.generate()
        ```
    """

    def __init__(self, config: "DjangoConfig"):
        """
        Initialize generator with configuration.

        Args:
            config: DjangoConfig instance
        """
        self.config = config

    def generate(self) -> Dict[str, Any]:
        """
        Generate gRPC framework settings.

        Returns:
            Dictionary with gRPC configuration

        Example:
            >>> generator = GRPCSettingsGenerator(config)
            >>> settings = generator.generate()
        """
        # Check if gRPC should be enabled
        if not self._should_enable_grpc():
            logger.debug("⏭️  gRPC disabled")
            return {}

        try:
            return self._generate_grpc_settings()
        except ImportError as e:
            logger.warning(f"Failed to import gRPC dependencies: {e}")
            logger.info("💡 Install with: pip install django-cfg[grpc]")
            return {}
        except Exception as e:
            logger.error(f"Failed to generate gRPC settings: {e}")
            return {}

    def _should_enable_grpc(self) -> bool:
        """
        Check if gRPC should be enabled.

        Returns:
            True if gRPC should be enabled
        """
        # Check if grpc config exists and is enabled
        if not hasattr(self.config, "grpc") or not self.config.grpc:
            return False

        if not self.config.grpc.enabled:
            return False

        # Check if gRPC dependencies are available
        from django_cfg.apps.integrations.grpc._cfg import check_grpc_available
        if not check_grpc_available():
            logger.warning("gRPC enabled but dependencies not installed")
            logger.info("💡 Install with: pip install django-cfg[grpc]")
            return False

        return True

    def _generate_grpc_settings(self) -> Dict[str, Any]:
        """
        Generate gRPC-specific settings.

        Returns:
            Dictionary with gRPC configuration
        """
        settings = {}

        # Generate GRPC_FRAMEWORK settings
        grpc_framework = self._build_grpc_framework_settings()
        if grpc_framework:
            settings["GRPC_FRAMEWORK"] = grpc_framework

        # Generate server-specific settings
        grpc_server = self._build_grpc_server_settings()
        if grpc_server:
            settings["GRPC_SERVER"] = grpc_server

        # Generate auth-specific settings
        grpc_auth = self._build_grpc_auth_settings()
        if grpc_auth:
            settings["GRPC_AUTH"] = grpc_auth

        # Generate proto-specific settings
        grpc_proto = self._build_grpc_proto_settings()
        if grpc_proto:
            settings["GRPC_PROTO"] = grpc_proto

        # Generate Centrifugo interceptor settings
        grpc_centrifugo = self._build_grpc_centrifugo_settings()
        if grpc_centrifugo:
            settings["GRPC_CENTRIFUGO"] = grpc_centrifugo

        logger.info("✅ gRPC framework enabled (async)")
        logger.info(f"   - Server: {self.config.grpc.server.host}:{self.config.grpc.server.port}")
        max_streams = self.config.grpc.server.max_concurrent_streams or "unlimited"
        logger.info(f"   - Max concurrent streams: {max_streams}")
        logger.info(f"   - Auth: {'enabled' if self.config.grpc.auth.enabled else 'disabled'}")
        logger.info(f"   - Reflection: {'enabled' if self.config.grpc.server.enable_reflection else 'disabled'}")

        return settings

    def _build_grpc_framework_settings(self) -> Dict[str, Any]:
        """
        Build GRPC_FRAMEWORK settings dictionary.

        Returns:
            Dictionary with framework-level gRPC settings
        """
        grpc_config = self.config.grpc

        # Resolve handlers hook (replace {ROOT_URLCONF} placeholder)
        handlers_hook = self._resolve_handlers_hook(grpc_config.handlers_hook)

        # Build interceptors list
        interceptors = self._build_interceptors()

        framework_settings = {
            "ROOT_HANDLERS_HOOK": handlers_hook,
            "SERVER_INTERCEPTORS": interceptors,
        }

        # Add auto-registration settings
        if grpc_config.auto_register_apps:
            framework_settings["AUTO_REGISTER_APPS"] = grpc_config.enabled_apps

        # Add custom services
        if grpc_config.custom_services:
            framework_settings["CUSTOM_SERVICES"] = grpc_config.custom_services

        return framework_settings

    def _build_grpc_server_settings(self) -> Dict[str, Any]:
        """
        Build GRPC_SERVER settings dictionary.

        Returns:
            Dictionary with server configuration
        """
        server_config = self.config.grpc.server

        server_settings = {
            "host": server_config.host,
            "port": server_config.port,
            "max_concurrent_streams": server_config.max_concurrent_streams,
            "asyncio_debug": server_config.asyncio_debug,
            "enable_reflection": server_config.enable_reflection,
            "enable_health_check": server_config.enable_health_check,
            "max_send_message_length": server_config.max_send_message_length,
            "max_receive_message_length": server_config.max_receive_message_length,
            # Nested keepalive config (Pydantic2)
            "keepalive": server_config.keepalive,
            "connection_limits": server_config.connection_limits,
        }

        # Add optional compression
        if server_config.compression:
            server_settings["compression"] = server_config.compression

        # Add custom interceptors from config
        if server_config.interceptors:
            server_settings["custom_interceptors"] = server_config.interceptors

        return server_settings

    def _build_grpc_auth_settings(self) -> Dict[str, Any]:
        """
        Build GRPC_AUTH settings dictionary.

        Returns:
            Dictionary with authentication configuration
        """
        auth_config = self.config.grpc.auth

        auth_settings = {
            "enabled": auth_config.enabled,
            "require_auth": auth_config.require_auth,
            "api_key_header": auth_config.api_key_header,
            "accept_django_secret_key": auth_config.accept_django_secret_key,
            "public_methods": auth_config.public_methods,
        }

        return auth_settings

    def _build_grpc_proto_settings(self) -> Dict[str, Any]:
        """
        Build GRPC_PROTO settings dictionary.

        Returns:
            Dictionary with proto generation configuration
        """
        proto_config = self.config.grpc.proto

        proto_settings = {
            "auto_generate": proto_config.auto_generate,
            "output_dir": proto_config.output_dir,
            "package_prefix": proto_config.package_prefix,
            "include_services": proto_config.include_services,
            "field_naming": proto_config.field_naming,
        }

        return proto_settings

    def _build_grpc_centrifugo_settings(self) -> Dict[str, Any]:
        """
        Build GRPC_CENTRIFUGO settings dictionary.

        Returns:
            Dictionary with Centrifugo interceptor configuration
        """
        grpc_config = self.config.grpc

        centrifugo_settings = {
            "enabled": True,
            "publish_start": False,
            "publish_end": True,
            "publish_errors": True,
            "publish_stream_messages": False,
            "channel_template": "grpc#{service}#{method}#meta",
            "error_channel_template": "grpc#{service}#{method}#errors",
            "metadata": {},
        }

        return centrifugo_settings

    def _build_interceptors(self) -> List[str]:
        """
        Build list of server interceptors.

        IMPORTANT: Interceptors are executed in reverse order for requests!
        The first interceptor in the list wraps all others.

        Architecture (after consolidation to fix bidi streaming bug):
            Auth → Observability → Handler (only 2 layers!)

        The ObservabilityInterceptor combines:
        - MetricsInterceptor (metrics collection)
        - LoggingInterceptor (request/response logging)
        - RequestLoggerInterceptor (DB request logging)
        - CentrifugoInterceptor (real-time event publishing)

        This eliminates 4 layers of async generator nesting that caused
        StopAsyncIteration after ~15 messages in bidirectional streaming.

        Returns:
            List of interceptor class paths
        """
        interceptors = []

        # NOTE: Interceptors are applied in REVERSE order (last added = first executed)!
        # So add them in reverse order of execution:

        # 2. Add ObservabilityInterceptor (combines metrics, logging, request_logger, centrifugo)
        # This is executed AFTER auth (which sets contextvars)
        interceptors.append(
            "django_cfg.apps.integrations.grpc.services.interceptors.ObservabilityInterceptor"
        )

        # 1. Add auth interceptor LAST in list (executed FIRST - sets contextvars!)
        if self.config.grpc.auth.enabled:
            interceptors.append(
                "django_cfg.apps.integrations.grpc.auth.ApiKeyAuthInterceptor"
            )

        # 3. Add custom interceptors from server config
        if self.config.grpc.server.interceptors:
            interceptors.extend(self.config.grpc.server.interceptors)

        return interceptors

    def _resolve_handlers_hook(self, handlers_hook: str) -> str:
        """
        Resolve handlers hook path.

        Replaces {ROOT_URLCONF} placeholder with actual ROOT_URLCONF value.

        Args:
            handlers_hook: Handler hook path (may contain {ROOT_URLCONF})

        Returns:
            Resolved handler hook path

        Example:
            >>> self._resolve_handlers_hook("{ROOT_URLCONF}.grpc_handlers")
            'myproject.urls.grpc_handlers'
        """
        if "{ROOT_URLCONF}" in handlers_hook:
            # Get ROOT_URLCONF from config
            root_urlconf = getattr(self.config, "root_urlconf", None)
            if not root_urlconf:
                # Fall back to default Django pattern
                root_urlconf = f"{self.config.project_name}.urls"
                logger.debug(
                    f"ROOT_URLCONF not set, using default: {root_urlconf}"
                )

            handlers_hook = handlers_hook.replace("{ROOT_URLCONF}", root_urlconf)

        return handlers_hook


__all__ = ["GRPCSettingsGenerator"]
