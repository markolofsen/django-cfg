"""
Management command to run Django development server with ngrok tunnel.

Simple implementation following KISS principle.
"""

import os
import time

from django.core.management.commands.runserver import Command as RunServerCommand

from django_cfg.utils import get_logger
from django_cfg.modules.django_ngrok import get_ngrok_service


class Command(RunServerCommand):
    """Enhanced runserver command with ngrok tunnel support."""

    # Web execution metadata
    web_executable = False
    requires_input = False
    is_destructive = False

    help = f'{RunServerCommand.help.rstrip(".")} with ngrok tunnel.'

    def __init__(self, *args, **kwargs):
        """Initialize with logger."""
        super().__init__(*args, **kwargs)
        self.logger = get_logger('runserver_ngrok')

    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--domain',
            help='Custom ngrok domain (requires paid plan)'
        )
        parser.add_argument(
            '--no-ngrok',
            action='store_true',
            help='Disable ngrok tunnel even if configured'
        )

    def handle(self, *args, **options):
        """Handle the command with ngrok integration."""

        # Check if ngrok should be disabled
        if options.get('no_ngrok'):
            self.stdout.write("Ngrok disabled by --no-ngrok flag")
            return super().handle(*args, **options)

        # Get ngrok service
        try:
            ngrok_service = get_ngrok_service()

            # Check if ngrok is configured and enabled
            config = ngrok_service.get_config()
            if not config or not hasattr(config, 'ngrok') or not config.ngrok or not config.ngrok.enabled:
                self.stdout.write("Ngrok not configured or disabled")
                return super().handle(*args, **options)
        except Exception as e:
            self.stdout.write(f"Error accessing ngrok configuration: {e}")
            return super().handle(*args, **options)

        # Override domain if provided
        if options.get('domain'):
            config.ngrok.tunnel.domain = options['domain']

        # Start the server normally first
        self.stdout.write("Starting Django development server...")

        # Call parent handle but intercept the server start
        return super().handle(*args, **options)

    def on_bind(self, server_port):
        """Called when server binds to port - start ngrok tunnel here."""
        super().on_bind(server_port)

        # Start ngrok tunnel
        ngrok_service = get_ngrok_service()

        self.stdout.write("🚇 Starting ngrok tunnel...")
        self.logger.info(f"Starting ngrok tunnel for port {server_port}")

        tunnel_url = ngrok_service.start_tunnel(server_port)

        if tunnel_url:
            # Wait for tunnel to be fully established
            self.stdout.write("⏳ Waiting for tunnel to be established...")
            self.logger.info("Waiting for ngrok tunnel to be fully established")

            max_retries = 10
            retry_count = 0
            tunnel_ready = False

            while retry_count < max_retries and not tunnel_ready:
                time.sleep(1)
                retry_count += 1

                # Check if tunnel is actually accessible
                try:
                    current_url = ngrok_service.get_tunnel_url()
                    if current_url and current_url == tunnel_url:
                        tunnel_ready = True
                        self.logger.info(f"Ngrok tunnel established successfully: {tunnel_url}")
                        break
                except Exception as e:
                    self.logger.warning(f"Tunnel check attempt {retry_count} failed: {e}")

                self.stdout.write(f"⏳ Tunnel check {retry_count}/{max_retries}...")

            if tunnel_ready:
                # Set environment variables for ngrok URL
                self._set_ngrok_env_vars(tunnel_url)

                # Update ALLOWED_HOSTS if needed
                self._update_allowed_hosts(tunnel_url)

                # Brief success message - detailed info will be shown by startup_display
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Ngrok tunnel ready: {tunnel_url}")
                )
                self.logger.info(f"Ngrok tunnel fully ready: {tunnel_url}")
            else:
                self.stdout.write(
                    self.style.WARNING("⚠️ Ngrok tunnel started but may not be fully ready")
                )
                self.logger.warning("Ngrok tunnel started but readiness check failed")
        else:
            error_msg = "Failed to start ngrok tunnel"
            self.stdout.write(self.style.ERROR(f"❌ {error_msg}"))
            self.logger.error(error_msg)

    def _set_ngrok_env_vars(self, tunnel_url: str):
        """Set environment variables with ngrok URL for easy access."""
        try:
            from urllib.parse import urlparse

            # Set main ngrok URL
            os.environ['NGROK_URL'] = tunnel_url
            os.environ['DJANGO_NGROK_URL'] = tunnel_url

            # Parse URL components
            parsed = urlparse(tunnel_url)
            os.environ['NGROK_HOST'] = parsed.netloc
            os.environ['NGROK_SCHEME'] = parsed.scheme

            # Set API URL (same as tunnel URL for most cases)
            os.environ['NGROK_API_URL'] = tunnel_url

            # Environment variables set - no need for verbose output
            self.logger.info(f"Set ngrok environment variables: {tunnel_url}")

        except Exception as e:
            self.logger.warning(f"Could not set ngrok environment variables: {e}")

    def _update_allowed_hosts(self, tunnel_url: str):
        """Update ALLOWED_HOSTS with ngrok domain."""
        try:
            from urllib.parse import urlparse

            from django.conf import settings

            parsed = urlparse(tunnel_url)
            ngrok_host = parsed.netloc

            # Add to ALLOWED_HOSTS if not already present
            if hasattr(settings, 'ALLOWED_HOSTS'):
                if ngrok_host not in settings.ALLOWED_HOSTS:
                    settings.ALLOWED_HOSTS.append(ngrok_host)
                    self.logger.info(f"Added {ngrok_host} to ALLOWED_HOSTS")

        except Exception as e:
            self.logger.warning(f"Could not update ALLOWED_HOSTS: {e}")
