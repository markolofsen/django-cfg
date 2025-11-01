"""
Django management command to run gRPC server.

Usage:
    python manage.py rungrpc
    python manage.py rungrpc --host 0.0.0.0 --port 50051
    python manage.py rungrpc --workers 20
"""

import logging
import signal
import sys
from concurrent import futures

import grpc
from django.conf import settings
from django.core.management.base import BaseCommand

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
        self.stdout.write(self.style.SUCCESS(f"Creating gRPC server with {max_workers} workers..."))
        server = grpc.server(
            futures.ThreadPoolExecutor(max_workers=max_workers),
            options=grpc_options,
            interceptors=self._build_interceptors(),
        )

        # Add health check
        if enable_health_check:
            self._add_health_check(server)

        # Discover and register services
        self.stdout.write("Discovering services...")
        service_count = self._register_services(server)

        if service_count == 0:
            self.stdout.write(
                self.style.WARNING(
                    "No services registered. "
                    "Make sure you have services defined in your apps."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f"Registered {service_count} service(s)")
            )

        # Add reflection
        if enable_reflection:
            self._add_reflection(server)
            self.stdout.write(self.style.SUCCESS("Server reflection enabled"))

        # Bind server
        address = f"{host}:{port}"
        server.add_insecure_port(address)

        # Start server
        self.stdout.write(self.style.SUCCESS(f"\nStarting gRPC server on {address}..."))
        self.stdout.write(self.style.SUCCESS(f"Health check: {'enabled' if enable_health_check else 'disabled'}"))
        self.stdout.write(self.style.SUCCESS(f"Reflection: {'enabled' if enable_reflection else 'disabled'}"))
        self.stdout.write("")

        server.start()

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers(server)

        # Keep server running
        try:
            self.stdout.write(self.style.SUCCESS("✅ gRPC server is running..."))
            self.stdout.write("Press CTRL+C to stop")
            server.wait_for_termination()
        except KeyboardInterrupt:
            self.stdout.write("\nShutting down...")
            server.stop(grace=5)
            self.stdout.write(self.style.SUCCESS("Server stopped"))

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

        # Keepalive settings
        keepalive_time = config.get("keepalive_time_ms", 7200000)
        keepalive_timeout = config.get("keepalive_timeout_ms", 20000)

        options.append(("grpc.keepalive_time_ms", keepalive_time))
        options.append(("grpc.keepalive_timeout_ms", keepalive_timeout))
        options.append(("grpc.http2.max_pings_without_data", 0))

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
        Add health check service to server.

        Args:
            server: gRPC server instance
        """
        try:
            from grpc_health.v1 import health, health_pb2_grpc

            # Create health servicer
            health_servicer = health.HealthServicer()

            # Mark all services as serving
            health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)

            # Add to server
            health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

            logger.info("Health check service added")

        except ImportError:
            logger.warning(
                "grpcio-health-checking not installed. "
                "Install with: pip install grpcio-health-checking"
            )
        except Exception as e:
            logger.error(f"Failed to add health check service: {e}")

    def _add_reflection(self, server):
        """
        Add reflection service to server.

        Args:
            server: gRPC server instance
        """
        try:
            from grpc_reflection.v1alpha import reflection

            # Get service names
            service_names = [
                desc.full_name
                for desc in server._state.generic_handlers[0].service_name()
            ] if hasattr(server, '_state') and hasattr(server._state, 'generic_handlers') else []

            # Add reflection
            reflection.enable_server_reflection(service_names, server)

            logger.info("Server reflection enabled")

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
            from django_cfg.modules.django_grpc.services import discover_and_register_services

            count = discover_and_register_services(server)
            return count

        except Exception as e:
            logger.error(f"Failed to register services: {e}", exc_info=True)
            self.stdout.write(
                self.style.ERROR(f"Error registering services: {e}")
            )
            return 0

    def _setup_signal_handlers(self, server):
        """
        Setup signal handlers for graceful shutdown.

        Args:
            server: gRPC server instance
        """
        def handle_signal(sig, frame):
            self.stdout.write(f"\nReceived signal {sig}, shutting down...")
            server.stop(grace=5)
            sys.exit(0)

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
