"""
Django Ngrok Service for django_cfg.

Simple ngrok integration following KISS principle.
"""

import os
import logging
import atexit
from typing import Optional
from django_cfg.modules.base import BaseCfgModule
from django_cfg.models.ngrok import NgrokConfig

logger = logging.getLogger(__name__)


class NgrokError(Exception):
    """Base exception for ngrok-related errors."""
    pass


class NgrokManager:
    """Simple ngrok tunnel manager."""
    
    def __init__(self, config: NgrokConfig):
        self.config = config
        self.tunnel_url: Optional[str] = None
        self.listener = None
        
        # Register cleanup on exit
        atexit.register(self.cleanup)
    
    def start_tunnel(self, port: int = 8000) -> Optional[str]:
        """Start ngrok tunnel for given port."""
        if not self.config.enabled:
            return None
        
        try:
            # Import ngrok (may not be available on Python < 3.12)
            import ngrok
            
            # Get auth token
            authtoken = self.config.auth.get_authtoken()
            
            # Create tunnel configuration
            tunnel_config = {
                "addr": f"http://127.0.0.1:{port}",
            }
            
            # Add auth token if available
            if authtoken:
                tunnel_config["authtoken"] = authtoken
            
            # Add domain if specified
            if self.config.tunnel.domain:
                tunnel_config["domain"] = self.config.tunnel.domain
            
            # Add basic auth if specified
            if self.config.tunnel.basic_auth:
                tunnel_config["basic_auth"] = self.config.tunnel.basic_auth
            
            # Start tunnel
            self.listener = ngrok.forward(**tunnel_config)
            self.tunnel_url = self.listener.url()
            
            logger.info(f"Ngrok tunnel started: {self.tunnel_url}")
            return self.tunnel_url
            
        except ImportError:
            logger.warning("ngrok package not available. Requires Python 3.12+ or install with: pip install ngrok")
            return None
        except Exception as e:
            logger.error(f"Failed to start ngrok tunnel: {e}")
            return None
    
    def stop_tunnel(self) -> None:
        """Stop ngrok tunnel."""
        if self.listener:
            try:
                self.listener.close()
                logger.info("Ngrok tunnel stopped")
            except Exception as e:
                logger.error(f"Error stopping ngrok tunnel: {e}")
            finally:
                self.listener = None
                self.tunnel_url = None
    
    def get_tunnel_url(self) -> Optional[str]:
        """Get current tunnel URL."""
        return self.tunnel_url
    
    def is_active(self) -> bool:
        """Check if tunnel is active."""
        return self.tunnel_url is not None
    
    def cleanup(self) -> None:
        """Cleanup on exit."""
        if self.is_active():
            logger.info("Cleaning up ngrok tunnel on exit...")
            self.stop_tunnel()


class DjangoNgrok(BaseCfgModule):
    """Main ngrok service for django-cfg."""
    
    def __init__(self):
        super().__init__()
        self._manager: Optional[NgrokManager] = None
    
    @property
    def manager(self) -> Optional[NgrokManager]:
        """Get ngrok manager (lazy-loaded)."""
        if self._manager is None:
            try:
                config = self.get_config()
                if config and hasattr(config, 'ngrok') and config.ngrok:
                    self._manager = NgrokManager(config.ngrok)
            except Exception as e:
                logger.warning(f"Failed to get ngrok config: {e}")
                return None
        return self._manager
    
    @manager.setter
    def manager(self, value: Optional[NgrokManager]) -> None:
        """Set NgrokManager instance (for testing)."""
        self._manager = value
    
    @manager.deleter
    def manager(self) -> None:
        """Delete NgrokManager instance (for testing)."""
        self._manager = None
    
    def start_tunnel(self, port: int = 8000) -> Optional[str]:
        """Start ngrok tunnel."""
        if not self.manager:
            return None
        return self.manager.start_tunnel(port)
    
    def stop_tunnel(self) -> None:
        """Stop ngrok tunnel."""
        if self.manager:
            self.manager.stop_tunnel()
    
    def get_tunnel_url(self) -> Optional[str]:
        """Get current tunnel URL from manager or environment variables."""
        # First try to get from manager (active tunnel)
        if self.manager:
            tunnel_url = self.manager.get_tunnel_url()
            if tunnel_url:
                return tunnel_url
        
        # Fallback to environment variables (set by runserver_ngrok)
        return self.get_tunnel_url_from_env()
    
    def is_tunnel_active(self) -> bool:
        """Check if tunnel is active."""
        if not self.manager:
            return False
        return self.manager.is_active()
    
    def get_webhook_url(self, path: Optional[str] = None) -> str:
        """Get webhook URL with ngrok tunnel or fallback to api_url."""
        # Get path from config if not provided
        if path is None:
            config = self.get_config()
            if config and hasattr(config, 'ngrok') and config.ngrok:
                path = config.ngrok.webhook_path
            else:
                path = "/webhooks/"
        
        # Try to get tunnel URL first
        try:
            tunnel_url = self.get_tunnel_url()
            if tunnel_url:
                return f"{tunnel_url.rstrip('/')}/{path.lstrip('/')}"
        except Exception as e:
            logger.warning(f"Ngrok tunnel not available: {e}")
        
        # Fallback to api_url from config
        try:
            config = self.get_config()
            if config and hasattr(config, 'api_url'):
                return f"{config.api_url.rstrip('/')}/{path.lstrip('/')}"
        except Exception as e:
            logger.warning(f"Failed to get config for webhook URL: {e}")
        
        # Ultimate fallback
        return f"http://localhost:8000/{path.lstrip('/')}"
    
    def get_api_url(self) -> str:
        """Get API URL - tunnel URL if active, otherwise config api_url."""
        # Try tunnel URL first
        tunnel_url = self.get_tunnel_url()
        if tunnel_url:
            return tunnel_url
        
        # Fallback to config api_url
        config = self.get_config()
        if config and hasattr(config, 'api_url'):
            return config.api_url
        
        # Ultimate fallback
        return "http://localhost:8000"
    
    def get_tunnel_url_from_env(self) -> Optional[str]:
        """Get ngrok tunnel URL from environment variables."""
        # Try different environment variable names
        env_vars = ['NGROK_URL', 'DJANGO_NGROK_URL', 'NGROK_API_URL']
        
        for env_var in env_vars:
            url = os.environ.get(env_var)
            if url and url.startswith(('http://', 'https://')):
                return url
        
        return None
    
    def get_ngrok_host_from_env(self) -> Optional[str]:
        """Get ngrok host from environment variables."""
        return os.environ.get('NGROK_HOST')
    
    def get_ngrok_scheme_from_env(self) -> Optional[str]:
        """Get ngrok scheme from environment variables."""
        return os.environ.get('NGROK_SCHEME', 'https')
    
    def is_ngrok_available_from_env(self) -> bool:
        """Check if ngrok URL is available from environment variables."""
        return self.get_tunnel_url_from_env() is not None
    
    def get_effective_tunnel_url(self) -> Optional[str]:
        """Get effective tunnel URL (alias for get_tunnel_url for clarity)."""
        return self.get_tunnel_url()
    
    def update_config_urls(self) -> None:
        """Update config URLs with tunnel URL if tunnel is active and update_api_url is enabled."""
        config = self.get_config()
        if not config or not hasattr(config, 'ngrok') or not config.ngrok:
            return
        
        # Only update if enabled in config
        if not config.ngrok.update_api_url:
            return
        
        tunnel_url = self.get_tunnel_url()
        if tunnel_url:
            # Update api_url with tunnel URL
            config.api_url = tunnel_url
            logger.info(f"Updated api_url to tunnel URL: {tunnel_url}")


# Global instance for easy access
_ngrok_service = None

def get_ngrok_service() -> DjangoNgrok:
    """Get global ngrok service instance."""
    global _ngrok_service
    if _ngrok_service is None:
        _ngrok_service = DjangoNgrok()
    return _ngrok_service


# Convenience functions
def start_tunnel(port: int = 8000) -> Optional[str]:
    """Start ngrok tunnel."""
    return get_ngrok_service().start_tunnel(port)


def stop_tunnel() -> None:
    """Stop ngrok tunnel."""
    get_ngrok_service().stop_tunnel()


def get_tunnel_url() -> Optional[str]:
    """Get current tunnel URL."""
    return get_ngrok_service().get_tunnel_url()


def get_webhook_url(path: str = "/webhooks/") -> str:
    """Get webhook URL with ngrok tunnel or fallback."""
    return get_ngrok_service().get_webhook_url(path)


def get_api_url() -> str:
    """Get API URL - tunnel URL if active, otherwise config api_url."""
    return get_ngrok_service().get_api_url()


def get_tunnel_url_from_env() -> Optional[str]:
    """Get ngrok tunnel URL from environment variables."""
    return get_ngrok_service().get_tunnel_url_from_env()


def get_ngrok_host_from_env() -> Optional[str]:
    """Get ngrok host from environment variables."""
    return get_ngrok_service().get_ngrok_host_from_env()


def is_ngrok_available_from_env() -> bool:
    """Check if ngrok URL is available from environment variables."""
    return get_ngrok_service().is_ngrok_available_from_env()


def get_effective_tunnel_url() -> Optional[str]:
    """Get effective tunnel URL (from manager or environment)."""
    return get_ngrok_service().get_effective_tunnel_url()


# Export public API
__all__ = [
    "DjangoNgrok",
    "NgrokManager", 
    "NgrokError",
    "get_ngrok_service",
    "start_tunnel",
    "stop_tunnel", 
    "get_tunnel_url",
    "get_webhook_url",
    "get_api_url",
    "get_tunnel_url_from_env",
    "get_ngrok_host_from_env",
    "is_ngrok_available_from_env",
    "get_effective_tunnel_url",
]
