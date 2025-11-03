"""
Django management command to run gRPC server.

Usage:
    python manage.py rungrpc
    python manage.py rungrpc --host 0.0.0.0 --port 50051
    python manage.py rungrpc --workers 20
"""

from __future__ import annotations

import logging
import signal
import sys
from concurrent import futures

from django.conf import settings
from django.core.management.base import BaseCommand

# Check dependencies before importing grpc
from django_cfg.apps.integrations.grpc._cfg import check_grpc_dependencies

try:
    check_grpc_dependencies(raise_on_missing=True)
except Exception as e:
    print(str(e))
    sys.exit(1)

# Now safe to import grpc
import grpc

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Run gRPC server with auto-discovered services.

    Features:
    - Auto-discovers and registers services
    - Configurable host, port, and workers
    - Health check support
    - Reflection support
    - Graceful shutdown
    - Signal handling
    """

    help = "Run gRPC server"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--host",
            type=str,
            default=None,
            help="Server host (default: from settings or [::])",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=None,
            help="Server port (default: from settings or 50051)",
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=None,
            help="Max worker threads (default: from settings or 10)",
        )
        parser.add_argument(
            "--no-reflection",
            action="store_true",
            help="Disable server reflection",
        )
        parser.add_argument(
            "--no-health-check",
            action="store_true",
            help="Disable health check service",
        )

    def handle(self, *args, **options):
        """Run gRPC server."""
        # Import models here to avoid AppRegistryNotReady
        from django_cfg.apps.integrations.grpc.models import GRPCServerStatus

        # Get configuration
        grpc_server_config = getattr(settings, "GRPC_SERVER", {})

        # Get server parameters
        host = options["host"] or grpc_server_config.get("host", "[::]")
        port = options["port"] or grpc_server_config.get("port", 50051)
        max_workers = options["workers"] or grpc_server_config.get("max_workers", 10)

        # Server options
        enable_reflection = not options["no_reflection"] and grpc_server_config.get(
            "enable_reflection", False
        )
        enable_health_check = not options["no_health_check"] and grpc_server_config.get(
            "enable_health_check", True
        )

        # gRPC options
        grpc_options = self._build_grpc_options(grpc_server_config)

        # Create server
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=max_workers),
            options=grpc_options,
            interceptors=self._build_interceptors(),
        )

        # Discover and register services FIRST
        service_count = self._register_services(server)

        # Add health check with registered services
        health_servicer = None
        if enable_health_check:
            health_servicer = self._add_health_check(server)

        # Add reflection
        if enable_reflection:
            self._add_reflection(server)

        # Bind server
        address = f"{host}:{port}"
        server.add_insecure_port(address)

        # Track server status in database
        server_status = None
        try:
            import os
            from django_cfg.apps.integrations.grpc.services import ServiceDiscovery

            # Get registered services metadata
            discovery = ServiceDiscovery()
            services_metadata = discovery.get_registered_services()

            server_status = GRPCServerStatus.objects.start_server(
                host=host,
                port=port,
                pid=os.getpid(),
                max_workers=max_workers,
                enable_reflection=enable_reflection,
                enable_health_check=enable_health_check,
            )

            # Store registered services in database
            server_status.registered_services = services_metadata
            server_status.save(update_fields=["registered_services"])

        except Exception as e:
            logger.warning(f"Could not start server status tracking: {e}")

        # Start server
        server.start()

        # Mark server as running
        if server_status:
            try:
                server_status.mark_running()
            except Exception as e:
                logger.warning(f"Could not mark server as running: {e}")

        # Display gRPC-specific startup info
        try:
            from django_cfg.core.integration.display import GRPCDisplayManager
            from django_cfg.apps.integrations.grpc.services import ServiceDiscovery

            # Get registered service names
            discovery = ServiceDiscovery()
            services_metadata = discovery.get_registered_services()
            service_names = [s.get('name', 'Unknown') for s in services_metadata]

            # Display startup info
            grpc_display = GRPCDisplayManager()
            grpc_display.display_grpc_startup(
                host=host,
                port=port,
                max_workers=max_workers,
                enable_reflection=enable_reflection,
                enable_health_check=enable_health_check,
                registered_services=service_count,
                service_names=service_names,
            )
        except Exception as e:
            logger.warning(f"Could not display gRPC startup info: {e}")

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers(server, server_status)

        # Keep server running
        self.stdout.write(self.style.SUCCESS("\n✅ gRPC server is running..."))
        self.stdout.write("Press CTRL+C to stop\n")

        try:
            server.wait_for_termination()
        except KeyboardInterrupt:
            # Signal handler will take care of graceful shutdown
            pass

    def _build_grpc_options(self, config: dict) -> list:
        """
        Build gRPC server options from configuration.

        Args:
            config: GRPC_SERVER configuration dict

        Returns:
            List of gRPC options tuples
        """
        options = []

        # Message size limits
        max_send = config.get("max_send_message_length", 4 * 1024 * 1024)
        max_receive = config.get("max_receive_message_length", 4 * 1024 * 1024)

        options.append(("grpc.max_send_message_length", max_send))
        options.append(("grpc.max_receive_message_length", max_receive))

        # Keep-alive settings (HTTP/2 PING frames for connection health)
        # Default: 60s ping interval (detect dead connections quickly)
        keepalive_time = config.get("keepalive_time_ms", 60000)  # 60s (was 2h)
        keepalive_timeout = config.get("keepalive_timeout_ms", 20000)  # 20s

        options.append(("grpc.keepalive_time_ms", keepalive_time))
        options.append(("grpc.keepalive_timeout_ms", keepalive_timeout))

        # Send pings even if no active RPCs (important for idle connections)
        options.append(("grpc.keepalive_permit_without_calls", True))

        # Anti-abuse protection: min time between successive pings
        options.append(("grpc.http2.min_time_between_pings_ms", 10000))  # 10s
        options.append(("grpc.http2.min_ping_interval_without_data_ms", 5000))  # 5s
        options.append(("grpc.http2.max_pings_without_data", 2))

        # Connection limits
        max_connection_idle = config.get("max_connection_idle_ms", 7200000)  # 2 hours
        max_connection_age = config.get("max_connection_age_ms", 86400000)  # 24 hours
        max_connection_age_grace = config.get("max_connection_age_grace_ms", 300000)  # 5 min

        options.append(("grpc.max_connection_idle_ms", max_connection_idle))
        options.append(("grpc.max_connection_age_ms", max_connection_age))
        options.append(("grpc.max_connection_age_grace_ms", max_connection_age_grace))

        return options

    def _build_interceptors(self) -> list:
        """
        Build server interceptors from configuration.

        Returns:
            List of interceptor instances
        """
        grpc_framework_config = getattr(settings, "GRPC_FRAMEWORK", {})
        interceptor_paths = grpc_framework_config.get("SERVER_INTERCEPTORS", [])

        interceptors = []

        for interceptor_path in interceptor_paths:
            try:
                # Import interceptor class
                module_path, class_name = interceptor_path.rsplit(".", 1)

                import importlib
                module = importlib.import_module(module_path)
                interceptor_class = getattr(module, class_name)

                # Instantiate interceptor
                interceptor = interceptor_class()
                interceptors.append(interceptor)

                logger.debug(f"Loaded interceptor: {class_name}")

            except Exception as e:
                logger.error(f"Failed to load interceptor {interceptor_path}: {e}")

        return interceptors

    def _add_health_check(self, server):
        """
        Add health check service with per-service status tracking.

        Args:
            server: gRPC server instance

        Returns:
            health_servicer: Health servicer instance (for dynamic updates) or None
        """
        try:
            from grpc_health.v1 import health, health_pb2, health_pb2_grpc

            # Create health servicer
            health_servicer = health.HealthServicer()

            # Set overall server status
            health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
            logger.info("Overall server health: SERVING")

            # Get registered service names
            service_names = []
            if hasattr(server, '_state') and hasattr(server._state, 'generic_handlers'):
                for handler in server._state.generic_handlers:
                    if hasattr(handler, 'service_name'):
                        # service_name() returns a callable or list
                        names = handler.service_name()
                        if callable(names):
                            names = names()
                        if isinstance(names, str):
                            service_names.append(names)
                        elif isinstance(names, (list, tuple)):
                            service_names.extend(names)

            # Set per-service health status
            for service_name in service_names:
                health_servicer.set(
                    service_name,
                    health_pb2.HealthCheckResponse.SERVING
                )
                logger.info(f"Service '{service_name}' health: SERVING")

            # Register health service
            health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

            logger.info(
                f"✅ Health check enabled for {len(service_names)} service(s)"
            )

            # Return servicer for dynamic health updates
            return health_servicer

        except ImportError:
            logger.warning(
                "grpcio-health-checking not installed. "
                "Install with: pip install 'django-cfg[grpc]'"
            )
            return None
        except Exception as e:
            logger.error(f"Failed to add health check service: {e}")
            return None

    def _add_reflection(self, server):
        """
        Add reflection service to server.

        Args:
            server: gRPC server instance
        """
        try:
            from grpc_reflection.v1alpha import reflection

            # Get service names from registered services
            service_names = []
            if hasattr(server, '_state') and hasattr(server._state, 'generic_handlers'):
                for handler in server._state.generic_handlers:
                    if hasattr(handler, 'service_name'):
                        # service_name() returns a callable or list
                        names = handler.service_name()
                        if callable(names):
                            names = names()
                        if isinstance(names, str):
                            service_names.append(names)
                        elif isinstance(names, (list, tuple)):
                            service_names.extend(names)

            # Add grpc.reflection.v1alpha.ServerReflection service itself
            service_names.append('grpc.reflection.v1alpha.ServerReflection')

            # Add reflection
            reflection.enable_server_reflection(service_names, server)

            logger.info(f"Server reflection enabled for {len(service_names)} service(s)")

        except ImportError:
            logger.warning(
                "grpcio-reflection not installed. "
                "Install with: pip install grpcio-reflection"
            )
        except Exception as e:
            logger.error(f"Failed to enable server reflection: {e}")

    def _register_services(self, server) -> int:
        """
        Discover and register services to server.

        Args:
            server: gRPC server instance

        Returns:
            Number of services registered
        """
        try:
            from django_cfg.apps.integrations.grpc.services.discovery import discover_and_register_services

            count = discover_and_register_services(server)
            return count

        except Exception as e:
            logger.error(f"Failed to register services: {e}", exc_info=True)
            self.stdout.write(
                self.style.ERROR(f"Error registering services: {e}")
            )
            return 0

    def _setup_signal_handlers(self, server, server_status=None):
        """
        Setup signal handlers for graceful shutdown.

        Args:
            server: gRPC server instance
            server_status: GRPCServerStatus instance (optional)
        """
        # Flag to prevent multiple shutdown attempts
        shutdown_initiated = {'value': False}

        def handle_signal(sig, frame):
            # Prevent multiple shutdown attempts
            if shutdown_initiated['value']:
                return
            shutdown_initiated['value'] = True

            self.stdout.write("\n🛑 Shutting down gracefully...")

            # Mark server as stopping
            if server_status:
                try:
                    server_status.mark_stopping()
                except Exception as e:
                    logger.warning(f"Could not mark server as stopping: {e}")

            # Stop server with grace period
            server.stop(grace=5)

            # Mark server as stopped
            if server_status:
                try:
                    server_status.mark_stopped()
                except Exception as e:
                    logger.warning(f"Could not mark server as stopped: {e}")

            self.stdout.write(self.style.SUCCESS("✅ Server stopped"))

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
