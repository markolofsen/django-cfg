"""
Django management command to run async gRPC server.

Usage:
    python manage.py rungrpc
    python manage.py rungrpc --host 0.0.0.0 --port 50051
"""

from __future__ import annotations

import asyncio
import signal
import sys

from django.conf import settings
from django.core.management.base import BaseCommand

from django_cfg.modules.django_logging import get_logger

# Check dependencies before importing grpc
from django_cfg.apps.integrations.grpc._cfg import check_grpc_dependencies

try:
    check_grpc_dependencies(raise_on_missing=True)
except Exception as e:
    print(str(e))
    sys.exit(1)

# Now safe to import grpc
import grpc
import grpc.aio


class Command(BaseCommand):
    """
    Run async gRPC server with auto-discovered services.

    Features:
    - Async server with grpc.aio
    - Auto-discovers and registers services
    - Configurable host, port
    - Health check support
    - Reflection support
    - Graceful shutdown
    - Signal handling
    """

    # Web execution metadata
    web_executable = False
    requires_input = False
    is_destructive = False

    help = "Run async gRPC server"

    def __init__(self, *args, **kwargs):
        """Initialize with self.logger and async server reference."""
        super().__init__(*args, **kwargs)
        self.logger = get_logger('rungrpc')
        self.server = None
        self.shutdown_event = None
        self.server_status = None
        self.server_config = None  # Store config for re-registration

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
            "--no-reflection",
            action="store_true",
            help="Disable server reflection",
        )
        parser.add_argument(
            "--no-health-check",
            action="store_true",
            help="Disable health check service",
        )
        parser.add_argument(
            "--asyncio-debug",
            action="store_true",
            help="Enable asyncio debug mode",
        )

    def handle(self, *args, **options):
        """Run async gRPC server."""
        # Enable asyncio debug if requested
        if options.get("asyncio_debug"):
            asyncio.get_event_loop().set_debug(True)
            self.logger.info("Asyncio debug mode enabled")

        # Run async main
        asyncio.run(self._async_main(*args, **options))

    async def _async_main(self, *args, **options):
        """Main async server loop."""
        # Import models here to avoid AppRegistryNotReady
        from django_cfg.apps.integrations.grpc.models import GRPCServerStatus
        from django_cfg.apps.integrations.grpc.services.config_helper import (
            get_grpc_server_config,
        )

        # Get configuration
        grpc_server_config_obj = get_grpc_server_config()

        # Fallback to settings if not configured via django-cfg
        if not grpc_server_config_obj:
            grpc_server_config = getattr(settings, "GRPC_SERVER", {})
            host = options["host"] or grpc_server_config.get("host", "[::]")
            port = options["port"] or grpc_server_config.get("port", 50051)
            max_concurrent_streams = grpc_server_config.get("max_concurrent_streams", None)
            enable_reflection = not options["no_reflection"] and grpc_server_config.get(
                "enable_reflection", False
            )
            enable_health_check = not options["no_health_check"] and grpc_server_config.get(
                "enable_health_check", True
            )
        else:
            # Use django-cfg config
            host = options["host"] or grpc_server_config_obj.host
            port = options["port"] or grpc_server_config_obj.port
            max_concurrent_streams = grpc_server_config_obj.max_concurrent_streams
            enable_reflection = (
                not options["no_reflection"] and grpc_server_config_obj.enable_reflection
            )
            enable_health_check = (
                not options["no_health_check"]
                and grpc_server_config_obj.enable_health_check
            )
            grpc_server_config = {
                "host": grpc_server_config_obj.host,
                "port": grpc_server_config_obj.port,
                "max_concurrent_streams": grpc_server_config_obj.max_concurrent_streams,
                "enable_reflection": grpc_server_config_obj.enable_reflection,
                "enable_health_check": grpc_server_config_obj.enable_health_check,
                "compression": grpc_server_config_obj.compression,
                "max_send_message_length": grpc_server_config_obj.max_send_message_length,
                "max_receive_message_length": grpc_server_config_obj.max_receive_message_length,
                "keepalive_time_ms": grpc_server_config_obj.keepalive_time_ms,
                "keepalive_timeout_ms": grpc_server_config_obj.keepalive_timeout_ms,
            }

        # gRPC options
        grpc_options = self._build_grpc_options(grpc_server_config)

        # Add max_concurrent_streams if specified
        if max_concurrent_streams:
            grpc_options.append(("grpc.max_concurrent_streams", max_concurrent_streams))

        # Create async server
        self.server = grpc.aio.server(
            options=grpc_options,
            interceptors=await self._build_interceptors_async(),
        )

        # Discover and register services FIRST
        service_count = await self._register_services_async(self.server)

        # Add health check with registered services
        health_servicer = None
        if enable_health_check:
            health_servicer = await self._add_health_check_async(self.server)

        # Add reflection
        if enable_reflection:
            await self._add_reflection_async(self.server)

        # Bind server
        address = f"{host}:{port}"
        self.server.add_insecure_port(address)

        # Track server status in database
        server_status = None
        try:
            import os
            from django_cfg.apps.integrations.grpc.services import ServiceDiscovery

            # Store config for re-registration
            self.server_config = {
                'host': host,
                'port': port,
                'pid': os.getpid(),
                'max_workers': 0,
                'enable_reflection': enable_reflection,
                'enable_health_check': enable_health_check,
            }

            # Get registered services metadata (run in thread to avoid blocking)
            discovery = ServiceDiscovery()
            services_metadata = await asyncio.to_thread(
                discovery.get_registered_services
            )

            server_status = await asyncio.to_thread(
                GRPCServerStatus.objects.start_server,
                host=host,
                port=port,
                pid=os.getpid(),
                max_workers=0,  # Async server - no workers
                enable_reflection=enable_reflection,
                enable_health_check=enable_health_check,
            )

            # Store registered services in database
            server_status.registered_services = services_metadata
            await asyncio.to_thread(
                server_status.save,
                update_fields=["registered_services"]
            )

            # Store in instance for heartbeat
            self.server_status = server_status

        except Exception as e:
            self.logger.warning(f"Could not start server status tracking: {e}")

        # Start server
        await self.server.start()

        # Mark server as running
        if server_status:
            try:
                await asyncio.to_thread(server_status.mark_running)
            except Exception as e:
                self.logger.warning(f"Could not mark server as running: {e}")

        # Start heartbeat background task
        heartbeat_task = None
        if server_status:
            heartbeat_task = asyncio.create_task(
                self._heartbeat_loop(interval=30)
            )
            self.logger.info("Started heartbeat background task (30s interval)")

        # Display gRPC-specific startup info
        try:
            from django_cfg.core.integration.display import GRPCDisplayManager
            from django_cfg.apps.integrations.grpc.services import ServiceDiscovery

            # Get registered service names
            discovery = ServiceDiscovery()
            services_metadata = await asyncio.to_thread(
                discovery.get_registered_services
            )
            service_names = [s.get('name', 'Unknown') for s in services_metadata]

            # Display startup info
            grpc_display = GRPCDisplayManager()
            await asyncio.to_thread(
                grpc_display.display_grpc_startup,
                host=host,
                port=port,
                max_workers=0,  # Async server
                enable_reflection=enable_reflection,
                enable_health_check=enable_health_check,
                registered_services=service_count,
                service_names=service_names,
            )
        except Exception as e:
            self.logger.warning(f"Could not display gRPC startup info: {e}")

        # Setup signal handlers for graceful shutdown
        self._setup_signal_handlers_async(self.server, server_status)

        # Keep server running
        self.stdout.write(self.style.SUCCESS("\n✅ Async gRPC server is running..."))
        self.stdout.write("Press CTRL+C to stop\n")

        try:
            await self.server.wait_for_termination()
        except KeyboardInterrupt:
            # Signal handler will take care of graceful shutdown
            pass
        finally:
            # Cancel heartbeat task
            if heartbeat_task and not heartbeat_task.done():
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
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

    async def _build_interceptors_async(self) -> list:
        """
        Build async server interceptors from configuration.

        Returns:
            List of async interceptor instances
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

                self.logger.debug(f"Loaded async interceptor: {class_name}")

            except Exception as e:
                self.logger.error(f"Failed to load async interceptor {interceptor_path}: {e}")

        return interceptors

    async def _add_health_check_async(self, server):
        """
        Add health check service to async server.

        Args:
            server: Async gRPC server instance

        Returns:
            health_servicer: Health servicer instance or None
        """
        try:
            from grpc_health.v1 import health, health_pb2, health_pb2_grpc

            # Create health servicer
            health_servicer = health.HealthServicer()

            # Set overall server status
            health_servicer.set("", health_pb2.HealthCheckResponse.SERVING)
            self.logger.info("Overall server health: SERVING")

            # Get registered service names from async server
            service_names = []
            if hasattr(server, '_state') and hasattr(server._state, 'generic_handlers'):
                for handler in server._state.generic_handlers:
                    if hasattr(handler, 'service_name'):
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
                self.logger.info(f"Service '{service_name}' health: SERVING")

            # Register health service to async server
            health_pb2_grpc.add_HealthServicer_to_server(health_servicer, server)

            self.logger.info(
                f"✅ Health check enabled for {len(service_names)} service(s)"
            )

            return health_servicer

        except ImportError:
            self.logger.warning(
                "grpcio-health-checking not installed. "
                "Install with: pip install 'django-cfg[grpc]'"
            )
            return None
        except Exception as e:
            self.logger.error(f"Failed to add health check service: {e}")
            return None

    async def _add_reflection_async(self, server):
        """
        Add reflection service to async server.

        Args:
            server: Async gRPC server instance
        """
        try:
            from grpc_reflection.v1alpha import reflection

            # Get service names from async server
            service_names = []
            if hasattr(server, '_state') and hasattr(server._state, 'generic_handlers'):
                for handler in server._state.generic_handlers:
                    if hasattr(handler, 'service_name'):
                        names = handler.service_name()
                        if callable(names):
                            names = names()
                        if isinstance(names, str):
                            service_names.append(names)
                        elif isinstance(names, (list, tuple)):
                            service_names.extend(names)

            # Add grpc.reflection.v1alpha.ServerReflection service itself
            service_names.append('grpc.reflection.v1alpha.ServerReflection')

            # Add reflection to async server
            reflection.enable_server_reflection(service_names, server)

            self.logger.info(f"Server reflection enabled for {len(service_names)} service(s)")

        except ImportError:
            self.logger.warning(
                "grpcio-reflection not installed. "
                "Install with: pip install grpcio-reflection"
            )
        except Exception as e:
            self.logger.error(f"Failed to enable server reflection: {e}")

    async def _register_services_async(self, server) -> int:
        """
        Discover and register services to async server.

        Args:
            server: Async gRPC server instance

        Returns:
            Number of services registered
        """
        try:
            from django_cfg.apps.integrations.grpc.services.discovery import discover_and_register_services

            # Service registration is sync, run in thread
            count = await asyncio.to_thread(
                discover_and_register_services,
                server
            )
            return count

        except Exception as e:
            self.logger.error(f"Failed to register services: {e}", exc_info=True)
            self.stdout.write(
                self.style.ERROR(f"Error registering services: {e}")
            )
            return 0

    async def _heartbeat_loop(self, interval: int = 30):
        """
        Periodically update server heartbeat with auto-recovery.

        If server record is deleted from database, automatically re-registers
        the server to maintain monitoring continuity.

        Args:
            interval: Heartbeat interval in seconds (default: 30)
        """
        from django_cfg.apps.integrations.grpc.models import GRPCServerStatus
        from asgiref.sync import sync_to_async

        try:
            while True:
                await asyncio.sleep(interval)

                if not self.server_status or not self.server_config:
                    self.logger.warning("No server status or config available")
                    continue

                try:
                    # Check if record still exists
                    record_exists = await sync_to_async(
                        GRPCServerStatus.objects.filter(
                            id=self.server_status.id
                        ).exists
                    )()

                    if not record_exists:
                        # Record was deleted - re-register server
                        self.logger.warning(
                            "Server record was deleted from database, "
                            "re-registering..."
                        )

                        # Get services metadata for re-registration
                        from django_cfg.apps.integrations.grpc.services import ServiceDiscovery
                        discovery = ServiceDiscovery()
                        services_metadata = await asyncio.to_thread(
                            discovery.get_registered_services
                        )

                        # Re-register server
                        new_server_status = await asyncio.to_thread(
                            GRPCServerStatus.objects.start_server,
                            **self.server_config
                        )

                        # Store registered services
                        new_server_status.registered_services = services_metadata
                        await asyncio.to_thread(
                            new_server_status.save,
                            update_fields=["registered_services"]
                        )

                        # Mark as running
                        await asyncio.to_thread(new_server_status.mark_running)

                        # Update reference
                        self.server_status = new_server_status

                        self.logger.info(
                            f"Successfully re-registered server (ID: {new_server_status.id})"
                        )
                    else:
                        # Record exists - just update heartbeat
                        await asyncio.to_thread(self.server_status.mark_running)
                        self.logger.debug(f"Heartbeat updated (interval: {interval}s)")

                except Exception as e:
                    self.logger.warning(f"Failed to update heartbeat: {e}")

        except asyncio.CancelledError:
            self.logger.info("Heartbeat task cancelled")
            raise

    def _setup_signal_handlers_async(self, server, server_status=None):
        """
        Setup signal handlers for graceful async server shutdown.

        Args:
            server: Async gRPC server instance
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
                    import django
                    if django.VERSION >= (3, 0):
                        from asgiref.sync import sync_to_async
                        # Run in sync context
                        try:
                            server_status.mark_stopping()
                        except:
                            pass
                except Exception as e:
                    self.logger.warning(f"Could not mark server as stopping: {e}")

            # Stop async server
            try:
                # Create task to stop server
                loop = asyncio.get_event_loop()
                loop.create_task(server.stop(grace=5))
            except Exception as e:
                self.logger.error(f"Error stopping server: {e}")

            # Mark server as stopped (async-safe)
            if server_status:
                try:
                    from asgiref.sync import sync_to_async
                    # Wrap sync DB operation in sync_to_async
                    asyncio.create_task(sync_to_async(server_status.mark_stopped)())
                except Exception as e:
                    self.logger.warning(f"Could not mark server as stopped: {e}")

            self.stdout.write(self.style.SUCCESS("✅ Server stopped"))

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
