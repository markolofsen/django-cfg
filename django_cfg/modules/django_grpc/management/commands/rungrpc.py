"""
Django management command to run async gRPC server.

Usage:
    python manage.py rungrpc
    python manage.py rungrpc --noreload
    python manage.py rungrpc --host 0.0.0.0 --port 50051

Hot-reload:
    Enabled by default in development (ENV_MODE != "production").
    Use --noreload to disable.
    Active streaming connections will be dropped on reload.
"""

from __future__ import annotations

import asyncio
import logging
import sys

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


def check_internal_secret_config(grpc_module_cfg) -> list[str]:
    """S-1: Startup check for internal_secret in multi-container deployments.

    Returns list of warning messages (empty if all OK).
    Called by _async_main before server starts and can be tested independently.
    """
    warnings: list[str] = []
    if grpc_module_cfg is None:
        return warnings

    try:
        from django_cfg.modules.django_grpc.services.management.config_helper import (
            is_production,
        )
        if is_production():
            warnings.append(
                "[gRPC] STARTUP: Running in production. Ensure GRPC__INTERNAL_SECRET "
                "env var is set to the same value in all containers (Django REST + gRPC) "
                "so internal bypass (x-internal-secret) works across processes."
            )
    except Exception:
        pass

    return warnings


class Command(BaseCommand):
    help = "Run async gRPC server (grpc.aio) with auto-discovered services"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.server = None
        self._health_servicer = None  # kept alive so NOT_SERVING can be set at shutdown

    def add_arguments(self, parser):
        parser.add_argument("--host", type=str, default=None)
        parser.add_argument("--port", type=int, default=None)
        parser.add_argument("--no-reflection", action="store_true")
        parser.add_argument("--no-health-check", action="store_true")
        parser.add_argument("--asyncio-debug", action="store_true")
        parser.add_argument(
            "--noreload",
            action="store_false",
            dest="use_reloader",
            help="Disable auto-reloader",
        )

    def handle(self, *args, **options):
        # Check grpc is available
        try:
            import grpc  # noqa: F401
        except ImportError:
            self.stderr.write(self.style.ERROR(
                "grpcio is not installed. Install with: pip install grpcio grpcio-tools"
            ))
            sys.exit(1)

        from django_cfg.modules.django_grpc.services.management.config_helper import (
            is_production as _is_production,
        )

        use_reloader = options.get("use_reloader", False)

        if _is_production():
            use_reloader = False

        # asyncio debug mode: pass to asyncio.run(debug=) — NOT to asyncio.get_event_loop()
        # because asyncio.run() always creates a fresh loop (Python 3.10+).
        asyncio_debug = bool(options.get("asyncio_debug"))

        if use_reloader:
            from django.utils import autoreload
            self.stdout.write(self.style.WARNING(
                "Auto-reloader active — streaming connections will drop on reload. "
                "Use --noreload for stable connections."
            ))
            autoreload.run_with_reloader(
                lambda: asyncio.run(self._async_main(*args, **options), debug=asyncio_debug)
            )
        else:
            try:
                asyncio.run(self._async_main(*args, **options), debug=asyncio_debug)
            except KeyboardInterrupt:
                pass

    async def _async_main(self, *args, **options):
        import grpc
        import grpc.aio

        from django_cfg.modules.django_grpc.config.server import GrpcServerConfig
        from django_cfg.modules.django_grpc.services.management.config_helper import (
            get_grpc_module_config,
            get_enable_reflection,
        )

        # Read server config
        grpc_module_cfg = get_grpc_module_config()
        server_cfg: GrpcServerConfig = grpc_module_cfg.server if grpc_module_cfg else GrpcServerConfig()

        host = options.get("host") or server_cfg.host
        port = options.get("port") or server_cfg.port
        # get_enable_reflection() smart-defaults: True in development, False in production.
        # --no-reflection flag always forces off; explicit server_cfg.enable_reflection is respected.
        enable_reflection = (
            not options.get("no_reflection", False) and get_enable_reflection()
        )
        enable_health_check = (
            not options.get("no_health_check", False) and server_cfg.enable_health_check
        )

        grpc_options = server_cfg.get_channel_options()

        # S-1: Startup check — internal_secret in multi-container deployments
        for warn_msg in check_internal_secret_config(grpc_module_cfg):
            logger.warning(warn_msg)

        # Security warnings — emit before server starts so ops teams see them in startup logs
        require_auth = grpc_module_cfg.auth.require_auth if grpc_module_cfg else False
        if not require_auth:
            logger.warning(
                "[gRPC] SECURITY: require_auth=False (default). "
                "All gRPC methods are publicly accessible without authentication. "
                "Set GrpcAuthConfig(require_auth=True) for production deployments."
            )
        if enable_reflection and not require_auth:
            logger.warning(
                "[gRPC] SECURITY: Server reflection is enabled AND require_auth=False. "
                "Any unauthenticated caller can enumerate all service names, methods, "
                "and protobuf schemas via grpcurl or the reflection API. "
                "Set enable_reflection=False or require_auth=True for production."
            )
        elif enable_reflection:
            logger.info(
                "[gRPC] NOTE: Server reflection is enabled. "
                "Disable with enable_reflection=False in production."
            )

        # Build interceptors
        from django_cfg.modules.django_grpc.services.interceptors import build_interceptors
        interceptors = build_interceptors(grpc_module_cfg)

        self.server = grpc.aio.server(
            options=grpc_options,
            interceptors=interceptors,
        )

        # Discover and register services
        service_count, service_names = await self._register_services()

        # Health check
        if enable_health_check:
            await self._add_health_check()

        # Reflection
        if enable_reflection:
            self._add_reflection(service_names)

        # Bind — I-1: use secure port when server_cfg.tls is configured.
        address = f"{host}:{port}"
        tls_cfg = server_cfg.tls
        if tls_cfg is not None and tls_cfg.enabled:
            credentials = tls_cfg.get_server_credentials()
            if credentials is None:
                logger.warning(
                    "[gRPC] server_cfg.tls.enabled=True but get_server_credentials() "
                    "returned None (cert_path/key_path missing). Falling back to insecure port."
                )
                self.server.add_insecure_port(address)
            else:
                self.server.add_secure_port(address, credentials)
                logger.info("[gRPC] TLS enabled — binding secure port %s", address)
        else:
            self.server.add_insecure_port(address)

        # Start D1 log worker
        try:
            from django_cfg.modules.django_grpc.events.log_worker import start_log_worker
            start_log_worker()
        except Exception as e:
            logger.debug("Could not start D1 log worker: %s", e)

        await self.server.start()

        # Register running status in D1 so health-check reflects reality
        _d1_status_row = None
        try:
            import os
            import socket as _socket
            from django_cfg.modules.django_grpc.events.service import GrpcD1Service
            from django_cfg.modules.django_grpc.events.types import GrpcServerStatusRow
            _d1_status_row = GrpcServerStatusRow(
                host=host,
                port=port,
                address=address,
                pid=os.getpid(),
                hostname=_socket.gethostname(),
                status="running",
            )
            await asyncio.to_thread(GrpcD1Service().upsert_server_status, _d1_status_row)
        except Exception as _e:
            logger.debug("Could not write server status to D1: %s", _e)

        self.stdout.write(self.style.SUCCESS(
            f"gRPC server listening on {address} "
            f"({service_count} service(s) registered)"
        ))
        self.stdout.write("Press CTRL+C to stop\n")

        try:
            await self.server.wait_for_termination()
        except KeyboardInterrupt:
            pass
        finally:
            self.stdout.write("\nShutting down gracefully...")
            # Signal NOT_SERVING BEFORE stopping so load balancers stop routing
            # new traffic during the drain window.
            if self._health_servicer is not None:
                try:
                    from grpc_health.v1 import health_pb2
                    self._health_servicer.set("", health_pb2.HealthCheckResponse.NOT_SERVING)
                except Exception:
                    pass
            try:
                await self.server.stop(grace=server_cfg.shutdown_grace_seconds)
            except Exception:
                pass
            # Drain log worker — must happen before event loop tears down so buffered
            # entries are flushed; stop_log_worker cancels the task and awaits it.
            try:
                from django_cfg.modules.django_grpc.events.log_worker import stop_log_worker
                await stop_log_worker(timeout=10.0)
            except Exception as _e:
                logger.debug("Error stopping log worker: %s", _e)
            # Mark server as stopped in D1
            if _d1_status_row is not None:
                try:
                    from django_cfg.modules.django_grpc.events.service import GrpcD1Service
                    await asyncio.to_thread(
                        GrpcD1Service().upsert_server_status,
                        _d1_status_row.model_copy(update={"status": "stopped"}),
                    )
                except Exception:
                    pass
            self.stdout.write(self.style.SUCCESS("Server stopped."))

    async def _register_services(self) -> tuple[int, list[str]]:
        try:
            from django_cfg.modules.django_grpc.services.discovery import (
                discover_and_register_services,
            )
            count, names = discover_and_register_services(self.server)
            return count, names
        except Exception as e:
            logger.error("Failed to register gRPC services: %s", e, exc_info=True)
            return 0, []

    async def _add_health_check(self):
        try:
            from grpc_health.v1 import health_pb2, health_pb2_grpc
            from grpc_health.v1.health import aio
            servicer = aio.HealthServicer()
            servicer.set("", health_pb2.HealthCheckResponse.SERVING)
            health_pb2_grpc.add_HealthServicer_to_server(servicer, self.server)
            # Store reference so shutdown can flip to NOT_SERVING before draining.
            self._health_servicer = servicer
        except ImportError:
            logger.warning("grpcio-health-checking not installed (pip install grpcio-health-checking)")
        except Exception as e:
            logger.warning("Could not add health check: %s", e)

    def _add_reflection(self, service_names: list[str]) -> None:
        if self.server is None:
            return
        try:
            from grpc_reflection.v1alpha import reflection
            names = list(service_names) + ["grpc.reflection.v1alpha.ServerReflection"]
            reflection.enable_server_reflection(names, self.server)
        except ImportError:
            logger.warning("grpcio-reflection not installed (pip install grpcio-reflection)")
        except Exception as e:
            logger.warning("Could not add reflection: %s", e)
