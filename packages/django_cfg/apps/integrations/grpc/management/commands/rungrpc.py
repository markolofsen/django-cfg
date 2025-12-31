"""
Django management command to run async gRPC server with auto-reload support.

Usage:
    # Development mode (with auto-reload)
    python manage.py rungrpc

    # Production mode (no auto-reload)
    python manage.py rungrpc --noreload

    # Custom host and port
    python manage.py rungrpc --host 0.0.0.0 --port 50051

    # With Centrifugo test event on startup
    python manage.py rungrpc --test

    # Disable specific features
    python manage.py rungrpc --no-reflection --no-health-check

Auto-reload behavior:
    - Enabled by default in development mode (ENV_MODE != "production")
    - Disabled by default in production mode (ENV_MODE == "production")
    - Use --noreload to explicitly disable auto-reload
    - Server will restart automatically when Python files change

Test mode:
    - Use --test to send a test Centrifugo event on server startup
    - Useful for verifying Centrifugo integration is working
    - Event published to: grpc#rungrpc#startup#test
"""

from __future__ import annotations

import asyncio
import logging
import signal
import sys
import threading

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import autoreload

from django_cfg.core.config import get_current_config
from django_cfg.utils import get_logger
from django_cfg.apps.integrations.grpc.utils.streaming_logger import (
    setup_streaming_logger,
    log_server_start,
    log_server_shutdown,
)

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
    Run async gRPC server with auto-discovered services and hot-reload.

    Features:
    - Async server with grpc.aio
    - Auto-discovers and registers services
    - Hot-reload in development mode (watches for file changes)
    - Configurable host, port
    - Health check support
    - Reflection support
    - Graceful shutdown
    - Signal handling

    Hot-reload:
    - Automatically enabled in development mode (ENV_MODE != "production")
    - Automatically disabled in production mode (ENV_MODE == "production")
    - Use --noreload to explicitly disable in development
    - Works like Django's runserver - restarts on code changes
    """

    # Web execution metadata
    web_executable = False
    requires_input = False
    is_destructive = False

    help = "Run async gRPC server with optional hot-reload support"

    def __init__(self, *args, **kwargs):
        """Initialize with self.logger and async server reference."""
        super().__init__(*args, **kwargs)
        self.logger = get_logger('rungrpc')
        self.streaming_logger = None  # Will be initialized when server starts
        self.server = None
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
        parser.add_argument(
            "--noreload",
            action="store_false",
            dest="use_reloader",
            help="Disable auto-reloader (default: enabled in dev mode)",
        )
        parser.add_argument(
            "--test",
            action="store_true",
            help="Send test Centrifugo event on startup (for testing integration)",
        )

    def handle(self, *args, **options):
        """Run async gRPC server with optional auto-reload."""
        config = get_current_config()

        # Determine if we should use auto-reload
        # Changed default to False for stability with bidirectional streaming
        use_reloader = options.get("use_reloader", False)

        # Check if we're in production mode (disable reloader in production)
        if config and hasattr(config, 'is_production'):
            is_production = config.is_production  # property, not method
        else:
            # Fallback to settings
            env_mode = getattr(settings, "ENV_MODE", "development").lower()
            is_production = env_mode == "production"

        # Disable reloader in production by default
        if is_production and options.get("use_reloader") is None:
            use_reloader = False
            self.stdout.write(
                self.style.WARNING(
                    "Production mode - auto-reloader disabled"
                )
            )

        # Enable asyncio debug if requested
        if options.get("asyncio_debug"):
            asyncio.get_event_loop().set_debug(True)
            self.logger.info("Asyncio debug mode enabled")

        # Run with or without reloader
        if use_reloader:
            from datetime import datetime
            current_time = datetime.now().strftime('%H:%M:%S')

            self.stdout.write(
                self.style.SUCCESS(
                    f"🔄 Auto-reloader enabled - watching for file changes [{current_time}]"
                )
            )
            self.stdout.write(
                self.style.WARNING(
                    "⚠️  Note: Active streaming connections will be dropped on reload. Use --noreload for stable bots."
                )
            )

            # Setup autoreload to watch project directory
            from django.utils.autoreload import autoreload_started

            def watch_project_files(sender, **kwargs):
                """Automatically watch Django project directory for changes."""
                base_dir = getattr(settings, 'BASE_DIR', None)
                if base_dir:
                    sender.watch_dir(str(base_dir), '*.py')
                    self.logger.debug(f"Watching project directory: {base_dir}")

            autoreload_started.connect(watch_project_files)

            # Use autoreload to restart on code changes
            autoreload.run_with_reloader(
                lambda: asyncio.run(self._async_main(*args, **options))
            )
        else:
            # Run directly without reloader - catch KeyboardInterrupt to exit cleanly
            try:
                asyncio.run(self._async_main(*args, **options))
            except KeyboardInterrupt:
                # Clean exit - shutdown already handled in _async_main
                pass

    async def _async_main(self, *args, **options):
        """Main async server loop."""
        # Start gRPC startup timer
        from django_cfg.core.integration.timing import start_grpc_timer
        start_grpc_timer()

        # Setup streaming logger for detailed gRPC logging
        self.streaming_logger = setup_streaming_logger(
            name='grpc_rungrpc',
            level=logging.DEBUG,
            console_level=logging.INFO
        )

        config = get_current_config()
        use_reloader = options.get("use_reloader", True)

        # Determine production mode
        if config and hasattr(config, 'is_production'):
            is_production = config.is_production  # property, not method
        else:
            env_mode = getattr(settings, "ENV_MODE", "development").lower()
            is_production = env_mode == "production"

        # Log startup using reusable function
        start_time = log_server_start(
            self.streaming_logger,
            server_type="gRPC Server",
            mode="Production" if is_production else "Development",
            hotreload_enabled=use_reloader
        )

        # Import models here to avoid AppRegistryNotReady
        from django_cfg.apps.integrations.grpc.models import GRPCServerStatus
        from django_cfg.apps.integrations.grpc.services.management.config_helper import (
            get_grpc_config,
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
                # Nested Pydantic2 configs
                "keepalive": grpc_server_config_obj.keepalive,
                "connection_limits": grpc_server_config_obj.connection_limits,
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
        service_count, registered_service_names = await self._register_services_async(self.server)

        # Add health check with registered services
        health_servicer = None
        if enable_health_check:
            health_servicer = await self._add_health_check_async(self.server)

        # Add reflection with explicit service names
        # (grpc.aio.server doesn't expose registered handlers like sync server)
        if enable_reflection:
            await self._add_reflection_async(self.server, registered_service_names)

        # Bind server with optional TLS
        address = f"{host}:{port}"

        # Check for TLS configuration
        grpc_config = get_grpc_config()
        tls_config = grpc_config.tls if grpc_config else None

        if tls_config and tls_config.enabled:
            # TLS enabled - use secure port
            try:
                credentials = tls_config.get_server_credentials()
                if credentials:
                    self.server.add_secure_port(address, credentials)
                    self.stdout.write(
                        self.style.SUCCESS(f"gRPC server with TLS listening on {address}")
                    )
                else:
                    # TLS enabled but no credentials - fall back to insecure with warning
                    self.stdout.write(
                        self.style.WARNING(
                            f"TLS enabled but no credentials configured. "
                            f"Falling back to insecure port on {address}"
                        )
                    )
                    self.server.add_insecure_port(address)
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Failed to configure TLS: {e}. Using insecure port.")
                )
                self.server.add_insecure_port(address)
        else:
            # No TLS - use insecure port
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
            }

            server_status = await GRPCServerStatus.objects.astart_server(
                host=host,
                port=port,
                pid=os.getpid(),
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
                await server_status.amark_running()
            except Exception as e:
                self.logger.warning(f"Could not mark server as running: {e}")

        # Start heartbeat background task
        # Get interval from GRPCObservabilityConfig (default 300 = 5 min)
        heartbeat_interval = 300
        if config and hasattr(config, 'grpc') and config.grpc:
            obs_config = config.grpc.observability
            if obs_config:
                heartbeat_interval = obs_config.heartbeat_interval

        heartbeat_task = None
        if server_status:
            heartbeat_task = asyncio.create_task(
                self._heartbeat_loop(interval=heartbeat_interval)
            )
            self.logger.info(f"Started heartbeat background task ({heartbeat_interval}s interval)")

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

        # Note: We don't setup custom signal handlers - Python's default
        # KeyboardInterrupt handling works fine with our try/except block

        # Keep server running
        self.stdout.write(self.style.SUCCESS("\n✅ Async gRPC server is running..."))

        # Show reloader status
        if use_reloader and not is_production:
            self.stdout.write(
                self.style.SUCCESS(
                    "🔄 Auto-reloader active - server will restart on code changes"
                )
            )

        self.stdout.write("Press CTRL+C to stop\n")

        # Log server ready
        self.streaming_logger.info("✅ Server ready and accepting connections")
        if use_reloader:
            self.streaming_logger.info("🔄 Watching for file changes...")

        # Send test Centrifugo event if --test flag is set
        if options.get("test"):
            self.streaming_logger.info("🧪 Sending test Centrifugo event...")
            try:
                from django_cfg.apps.integrations.grpc.services.centrifugo.demo import send_demo_event

                test_result = await send_demo_event(
                    channel="grpc#rungrpc#startup#test",
                    metadata={
                        "source": "rungrpc",
                        "action": "startup_test",
                        "mode": "Development" if not is_production else "Production",
                        "host": host,
                        "port": port,
                    }
                )

                if test_result:
                    self.streaming_logger.info("✅ Test Centrifugo event sent successfully")
                    self.stdout.write(self.style.SUCCESS("🧪 Test event published to Centrifugo"))
                else:
                    self.streaming_logger.warning("⚠️ Test Centrifugo event failed")
                    self.stdout.write(self.style.WARNING("⚠️ Test event failed (check Centrifugo config)"))

            except Exception as e:
                self.streaming_logger.error(f"❌ Failed to send test event: {e}")
                self.stdout.write(
                    self.style.ERROR(f"❌ Test event error: {e}")
                )

        shutdown_reason = "Unknown"
        try:
            try:
                await self.server.wait_for_termination()
                shutdown_reason = "Normal termination"
            except KeyboardInterrupt:
                shutdown_reason = "Keyboard interrupt"
                # Re-raise to be caught by outer handler
                raise
        finally:
            # Always perform graceful shutdown - even if KeyboardInterrupt
            self.stdout.write("\n🛑 Shutting down gracefully...")

            # Mark server as stopping
            if server_status:
                try:
                    await server_status.amark_stopping()
                except Exception as e:
                    self.logger.warning(f"Could not mark server as stopping: {e}")

            # Stop the server - CRITICAL to do this before event loop closes
            try:
                await self.server.stop(grace=5)
                self.logger.info("Server stopped gracefully")
            except asyncio.CancelledError:
                # Expected - gRPC cancels internal tasks during shutdown
                self.logger.info("Server shutdown completed")
            except Exception as e:
                self.logger.error(f"Error stopping server: {e}")

            # Cancel heartbeat task
            if heartbeat_task and not heartbeat_task.done():
                heartbeat_task.cancel()
                try:
                    await heartbeat_task
                except asyncio.CancelledError:
                    pass

            # Mark server as stopped
            if server_status:
                try:
                    await server_status.amark_stopped()
                except Exception as e:
                    self.logger.warning(f"Could not mark server as stopped: {e}")

            # Log shutdown
            log_server_shutdown(
                self.streaming_logger,
                start_time,
                server_type="gRPC Server",
                reason=shutdown_reason
            )

            self.stdout.write(self.style.SUCCESS("✅ Server stopped"))

    def _build_grpc_options(self, config: dict) -> list:
        """
        Build gRPC server options from configuration.

        Args:
            config: GRPC_SERVER configuration dict with nested Pydantic2 configs

        Returns:
            List of gRPC options tuples
        """
        options = []

        # Message size limits
        max_send = config.get("max_send_message_length", 4 * 1024 * 1024)
        max_receive = config.get("max_receive_message_length", 4 * 1024 * 1024)

        options.append(("grpc.max_send_message_length", max_send))
        options.append(("grpc.max_receive_message_length", max_receive))

        # Keepalive settings - use nested Pydantic2 config if available
        keepalive = config.get("keepalive")
        if keepalive and hasattr(keepalive, "to_grpc_options"):
            # Use Pydantic2 config with to_grpc_options() method
            options.extend(keepalive.to_grpc_options())
        else:
            # Fallback for legacy/flat config or settings dict
            keepalive_time = config.get("keepalive_time_ms", 10000)  # 10s
            keepalive_timeout = config.get("keepalive_timeout_ms", 5000)  # 5s
            options.append(("grpc.keepalive_time_ms", keepalive_time))
            options.append(("grpc.keepalive_timeout_ms", keepalive_timeout))
            options.append(("grpc.keepalive_permit_without_calls", True))
            options.append(("grpc.http2.min_time_between_pings_ms", 5000))
            options.append(("grpc.http2.max_pings_without_data", 0))

        # Connection limits - use nested Pydantic2 config if available
        connection_limits = config.get("connection_limits")
        if connection_limits and hasattr(connection_limits, "to_grpc_options"):
            # Use Pydantic2 config with to_grpc_options() method
            options.extend(connection_limits.to_grpc_options())
        else:
            # Fallback for legacy/flat config or settings dict
            max_connection_idle = config.get("max_connection_idle_ms", 7200000)  # 2 hours
            max_connection_age = config.get("max_connection_age_ms", 0)  # Unlimited for streaming
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

    async def _add_reflection_async(self, server, registered_service_names: list[str] = None):
        """
        Add reflection service to async server.

        Args:
            server: Async gRPC server instance
            registered_service_names: List of service names to expose via reflection.
                                     For grpc.aio.server(), the server._state doesn't exist,
                                     so we must pass service names explicitly.
        """
        try:
            from grpc_reflection.v1alpha import reflection

            # Use provided service names (required for async server)
            # grpc.aio.server() does NOT have _state.generic_handlers like sync server
            service_names = list(registered_service_names) if registered_service_names else []

            # Fallback: try to get from server._state (works for sync server only)
            if not service_names and hasattr(server, '_state') and hasattr(server._state, 'generic_handlers'):
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

            self.logger.info(f"Server reflection enabled for {len(service_names)} service(s): {service_names}")

        except ImportError:
            self.logger.warning(
                "grpcio-reflection not installed. "
                "Install with: pip install grpcio-reflection"
            )
        except Exception as e:
            self.logger.error(f"Failed to enable server reflection: {e}")

    async def _register_services_async(self, server) -> tuple[int, list[str]]:
        """
        Discover and register services to async server.

        Args:
            server: Async gRPC server instance

        Returns:
            Tuple of (number of services registered, list of service names)
        """
        try:
            from django_cfg.apps.integrations.grpc.services.discovery import discover_and_register_services

            # IMPORTANT: Do NOT use asyncio.to_thread() here!
            # grpc.aio.server is NOT thread-safe for adding handlers.
            # Running add_generic_rpc_handlers() in a different thread
            # causes the handlers to NOT be visible to the server.
            #
            # The discover_and_register_services() function is fast
            # (just imports and calls add_generic_rpc_handlers) so
            # running it synchronously is fine.
            count, service_names = discover_and_register_services(server)
            return count, service_names

        except Exception as e:
            self.logger.error(f"Failed to register services: {e}", exc_info=True)
            self.stdout.write(
                self.style.ERROR(f"Error registering services: {e}")
            )
            return 0, []

    async def _heartbeat_loop(self, interval: int = 30):
        """
        Periodically update server heartbeat with auto-recovery.

        If server record is deleted from database, automatically re-registers
        the server to maintain monitoring continuity.

        Args:
            interval: Heartbeat interval in seconds (default: 30)
        """
        from django_cfg.apps.integrations.grpc.models import GRPCServerStatus

        try:
            while True:
                await asyncio.sleep(interval)

                if not self.server_status or not self.server_config:
                    self.logger.warning("No server status or config available")
                    continue

                try:
                    # Check if record still exists (Django 5.2: Native async ORM)
                    record_exists = await GRPCServerStatus.objects.filter(
                        id=self.server_status.id
                    ).aexists()

                    if not record_exists:
                        # Record was deleted - re-register server
                        self.logger.warning(
                            "Server record was deleted from database, "
                            "re-registering..."
                        )

                        # Re-register server (Django 5.2: Native async ORM)
                        new_server_status = await GRPCServerStatus.objects.astart_server(
                            **self.server_config
                        )

                        # Mark as running (Django 5.2: Native async ORM)
                        await new_server_status.amark_running()

                        # Update reference
                        self.server_status = new_server_status

                        self.logger.warning(
                            f"✅ Successfully re-registered server (ID: {new_server_status.id})"
                        )
                    else:
                        # Record exists - just update heartbeat (Django 5.2: Native async ORM)
                        await self.server_status.amark_running()
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

        Note:
            We rely on Python's default KeyboardInterrupt handling.
            Custom signal handler only needed for force-exit on second Ctrl+C.
        """
        # Check if we're in the main thread
        if threading.current_thread() is not threading.main_thread():
            # In autoreload mode, Django handles signals
            return

        # Track shutdown attempts for force-exit on second signal
        shutdown_initiated = {'value': False}

        def handle_signal(sig, frame):
            """Handle second Ctrl+C with force exit."""
            if shutdown_initiated['value']:
                self.stdout.write(self.style.WARNING("\n⚠️  Forcing shutdown..."))
                sys.exit(1)

            shutdown_initiated['value'] = True
            # Let KeyboardInterrupt propagate naturally
            raise KeyboardInterrupt()

        signal.signal(signal.SIGINT, handle_signal)
        signal.signal(signal.SIGTERM, handle_signal)
