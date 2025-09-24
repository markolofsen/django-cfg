"""
Management command to run Django development server with ngrok tunnel.

Simple implementation following KISS principle.
"""

import os
from django.core.management.commands.runserver import Command as RunServerCommand
from django_cfg.modules.django_ngrok import get_ngrok_service
import logging

logger = logging.getLogger(__name__)


class Command(RunServerCommand):
    """Enhanced runserver command with ngrok tunnel support."""
    
    help = f'{RunServerCommand.help.rstrip(".")} with ngrok tunnel.'
    
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
        tunnel_url = ngrok_service.start_tunnel(server_port)
        
        if tunnel_url:
            self.stdout.write(
                self.style.SUCCESS(
                    f"ngrok forwarding to http://127.0.0.1:{server_port} "
                    f"from ingress url: {tunnel_url}"
                )
            )
            
            # Set environment variables for ngrok URL
            self._set_ngrok_env_vars(tunnel_url)
            
            # Update ALLOWED_HOSTS if needed
            self._update_allowed_hosts(tunnel_url)
            
            # Update config URLs if enabled
            ngrok_service.update_config_urls()
            
            # Show webhook URL example
            webhook_url = ngrok_service.get_webhook_url("/api/webhooks/")
            self.stdout.write(
                self.style.HTTP_INFO(
                    f"Webhook URL example: {webhook_url}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING("Failed to start ngrok tunnel")
            )
    
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
            
            self.stdout.write(
                self.style.HTTP_INFO(
                    f"Environment variables set: NGROK_URL={tunnel_url}"
                )
            )
            logger.info(f"Set ngrok environment variables: {tunnel_url}")
            
        except Exception as e:
            logger.warning(f"Could not set ngrok environment variables: {e}")
    
    def _update_allowed_hosts(self, tunnel_url: str):
        """Update ALLOWED_HOSTS with ngrok domain."""
        try:
            from django.conf import settings
            from urllib.parse import urlparse
            
            parsed = urlparse(tunnel_url)
            ngrok_host = parsed.netloc
            
            # Add to ALLOWED_HOSTS if not already present
            if hasattr(settings, 'ALLOWED_HOSTS'):
                if ngrok_host not in settings.ALLOWED_HOSTS:
                    settings.ALLOWED_HOSTS.append(ngrok_host)
                    logger.info(f"Added {ngrok_host} to ALLOWED_HOSTS")
        
        except Exception as e:
            logger.warning(f"Could not update ALLOWED_HOSTS: {e}")
