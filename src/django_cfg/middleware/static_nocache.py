"""
Static files no-cache middleware for django-cfg.

Automatically disables caching for static files in development environments
to prevent browser caching issues during development.
"""

from django.conf import settings
from django_cfg.core.config import EnvironmentMode


class StaticNoCacheMiddleware:
    """
    Middleware to disable caching for static files in development.
    
    This ensures that JavaScript and CSS files are always fresh during development,
    preventing browser caching issues when files are updated.
    
    Automatically detects development mode based on:
    - DEBUG setting
    - ENV_MODE environment variable
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        
        # Determine if we should disable caching
        self.should_disable_cache = self._should_disable_cache()

    def _should_disable_cache(self):
        """Determine if caching should be disabled based on environment."""
        # Always disable in DEBUG mode
        if settings.DEBUG:
            return True
            
        # Check ENV_MODE if available
        env_mode = getattr(settings, 'ENV_MODE', None)
        if env_mode == EnvironmentMode.DEVELOPMENT or env_mode == EnvironmentMode.TEST:
            return True
            
        return False

    def __call__(self, request):
        response = self.get_response(request)
        
        # Apply no-cache headers for static files in development
        if self.should_disable_cache and request.path.startswith('/static/'):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            # Add ETag removal to prevent conditional requests
            if 'ETag' in response:
                del response['ETag']
        
        return response
