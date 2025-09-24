"""
Public Endpoints Middleware

Middleware that ignores invalid JWT tokens on public endpoints to prevent
authentication errors on endpoints with AllowAny permissions.
"""

import logging
import re
from typing import List, Optional, Set
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class PublicEndpointsMiddleware(MiddlewareMixin):
    """
    Middleware that temporarily removes Authorization headers for public endpoints.
    
    This prevents Django from trying to authenticate invalid JWT tokens on endpoints
    that have AllowAny permissions, which can cause "User not found" errors.
    
    Features:
    - ✅ Configurable public endpoint patterns
    - ✅ Smart JWT token detection
    - ✅ Automatic restoration of headers after processing
    - ✅ Detailed logging for debugging
    - ✅ Performance optimized with compiled regex patterns
    """
    
    # Default public endpoint patterns
    DEFAULT_PUBLIC_PATTERNS = [
        r'^/api/accounts/otp/',           # OTP endpoints (request, verify)
        r'^/cfg/accounts/otp/',           # CFG OTP endpoints
        r'^/api/accounts/token/refresh/', # Token refresh
        r'^/cfg/accounts/token/refresh/', # CFG Token refresh
        r'^/api/health/',                 # Health check endpoints
        r'^/cfg/api/health/',             # CFG Health check endpoints
        r'^/admin/login/',                # Django admin login
        r'^/api/schema/',                 # API schema endpoints
        r'^/api/docs/',                   # API documentation
    ]
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.public_patterns: List[re.Pattern] = []
        self.stats = {
            'requests_processed': 0,
            'tokens_ignored': 0,
            'public_endpoints_hit': 0,
        }
        self._compile_patterns()
    
    def _compile_patterns(self):
        """Compile regex patterns for better performance."""
        patterns = self._get_public_patterns()
        self.public_patterns = [re.compile(pattern) for pattern in patterns]
        logger.debug(f"Compiled {len(self.public_patterns)} public endpoint patterns")
    
    def _get_public_patterns(self) -> List[str]:
        """Get public endpoint patterns from Django settings or use defaults."""
        from django.conf import settings
        
        # Try to get patterns from settings
        custom_patterns = getattr(settings, 'PUBLIC_ENDPOINT_PATTERNS', None)
        if custom_patterns:
            logger.debug(f"Using custom public patterns: {len(custom_patterns)} patterns")
            return custom_patterns
        
        # Use defaults
        logger.debug(f"Using default public patterns: {len(self.DEFAULT_PUBLIC_PATTERNS)} patterns")
        return self.DEFAULT_PUBLIC_PATTERNS
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if the request path matches any public endpoint pattern."""
        for pattern in self.public_patterns:
            if pattern.match(path):
                return True
        return False
    
    def _has_jwt_token(self, request: HttpRequest) -> bool:
        """Check if request has a JWT Authorization header."""
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        return auth_header.startswith('Bearer ')
    
    def _extract_auth_header(self, request: HttpRequest) -> Optional[str]:
        """Extract and remove Authorization header from request."""
        return request.META.pop('HTTP_AUTHORIZATION', None)
    
    def _restore_auth_header(self, request: HttpRequest, auth_header: str):
        """Restore Authorization header to request."""
        if auth_header:
            request.META['HTTP_AUTHORIZATION'] = auth_header
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Process incoming request and temporarily remove auth header for public endpoints.
        """
        self.stats['requests_processed'] += 1
        
        # Check if this is a public endpoint
        if not self._is_public_endpoint(request.path):
            return None
        
        self.stats['public_endpoints_hit'] += 1
        
        # Check if request has JWT token
        if not self._has_jwt_token(request):
            return None
        
        # Store the auth header and remove it temporarily
        auth_header = self._extract_auth_header(request)
        if auth_header:
            self.stats['tokens_ignored'] += 1
            # Store in request for restoration later
            request._original_auth_header = auth_header
            
            logger.debug(
                f"Temporarily removed auth header for public endpoint: {request.path}",
                extra={
                    'path': request.path,
                    'method': request.method,
                    'has_token': bool(auth_header),
                }
            )
        
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Restore Authorization header after request processing.
        """
        # Restore auth header if it was temporarily removed
        if hasattr(request, '_original_auth_header'):
            self._restore_auth_header(request, request._original_auth_header)
            delattr(request, '_original_auth_header')
            
            logger.debug(
                f"Restored auth header for public endpoint: {request.path}",
                extra={
                    'path': request.path,
                    'status_code': response.status_code,
                }
            )
        
        return response
    
    def get_stats(self) -> dict:
        """Get middleware statistics."""
        return {
            **self.stats,
            'public_patterns_count': len(self.public_patterns),
            'middleware_active': True,
        }
    
    def reset_stats(self):
        """Reset middleware statistics."""
        self.stats = {
            'requests_processed': 0,
            'tokens_ignored': 0,
            'public_endpoints_hit': 0,
        }
        logger.info("PublicEndpointsMiddleware stats reset")


# Convenience function for getting middleware stats
def get_public_endpoints_stats() -> dict:
    """Get statistics from PublicEndpointsMiddleware if available."""
    try:
        # This would need to be implemented if we want global stats access
        # For now, return basic info
        return {
            'middleware_available': True,
            'note': 'Use middleware.get_stats() method for detailed statistics'
        }
    except Exception as e:
        logger.error(f"Error getting public endpoints stats: {e}")
        return {
            'middleware_available': False,
            'error': str(e)
        }
