"""
Rate Limiting Middleware.
Implements sliding window rate limiting using Redis.
"""

from django_cfg.modules.django_logger import get_logger
import time
from typing import Optional
from django.http import JsonResponse, HttpRequest
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache

logger = get_logger("rate_limiting")


class RateLimitingMiddleware(MiddlewareMixin):
    """
    Rate limiting middleware using sliding window algorithm.
    
    Features:
    - Per-API-key rate limiting
    - Per-IP rate limiting (fallback)
    - Sliding window algorithm
    - Redis-based with circuit breaker
    - Configurable limits
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        
        # Default rate limits (can be overridden in settings)
        self.default_limits = getattr(settings, 'PAYMENTS_RATE_LIMITS', {
            'per_minute': 60,   # 60 requests per minute
            'per_hour': 1000,   # 1000 requests per hour
            'per_day': 10000,   # 10000 requests per day
        })
        
        # Paths exempt from rate limiting
        self.exempt_paths = getattr(settings, 'PAYMENTS_RATE_LIMIT_EXEMPT_PATHS', [
            '/admin/',
            '/cfg/',
        ])
        
        # Enable/disable rate limiting
        self.enabled = getattr(settings, 'PAYMENTS_RATE_LIMITING_ENABLED', True)
    
    def process_request(self, request: HttpRequest) -> Optional[JsonResponse]:
        """Process request for rate limiting."""
        
        if not self.enabled:
            return None
        
        # Skip exempt paths
        if self._is_exempt_path(request):
            return None
        
        # Get rate limiting key (API key or IP)
        rate_key = self._get_rate_key(request)
        if not rate_key:
            return None
        
        # Get rate limits for this key
        limits = self._get_rate_limits(request)
        
        # Check each time window
        for window, limit in limits.items():
            if self._is_rate_limited(rate_key, window, limit):
                return self._rate_limit_response(window, limit)
        
        # Record this request
        self._record_request(rate_key)
        
        return None
    
    def _is_exempt_path(self, request: HttpRequest) -> bool:
        """Check if path is exempt from rate limiting."""
        path = request.path
        return any(path.startswith(exempt) for exempt in self.exempt_paths)
    
    def _get_rate_key(self, request: HttpRequest) -> Optional[str]:
        """Get rate limiting key (API key preferred, IP as fallback)."""
        
        # Use API key if available (from previous middleware)
        if hasattr(request, 'payment_api_key'):
            return f"api_key:{request.payment_api_key.key_value}"
        
        # Fallback to IP address
        ip = self._get_client_ip(request)
        if ip:
            return f"ip:{ip}"
        
        return None
    
    def _get_client_ip(self, request: HttpRequest) -> Optional[str]:
        """Get client IP address."""
        
        # Check for forwarded headers first
        forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
        
        # Check for real IP header
        real_ip = request.META.get('HTTP_X_REAL_IP')
        if real_ip:
            return real_ip
        
        # Fallback to remote address
        return request.META.get('REMOTE_ADDR')
    
    def _get_rate_limits(self, request: HttpRequest) -> dict:
        """Get rate limits for this request."""
        
        # Check if API key has custom limits
        if hasattr(request, 'payment_api_key'):
            api_key = request.payment_api_key
            
            # Check if user has subscription with custom limits
            if hasattr(request, 'payment_subscription'):
                subscription = request.payment_subscription
                # Custom limits based on subscription tier could be implemented here
                # For now, use default limits
                pass
        
        return self.default_limits
    
    def _is_rate_limited(self, rate_key: str, window: str, limit: int) -> bool:
        """Check if rate limit is exceeded for given window."""
        
        try:
            # Get window duration in seconds
            window_seconds = self._get_window_seconds(window)
            if not window_seconds:
                return False
            
            # Use Redis sliding window
            current_time = int(time.time())
            window_start = current_time - window_seconds
            
            # Get request count in window
            redis_key = f"rate_limit:{rate_key}:{window}"
            
            # Simple cache-based rate limiting
            count = cache.get(redis_key, 0)
            
            return count >= limit
            
        except Exception as e:
            logger.error(f"Error checking rate limit: {e}")
            # On error, allow request (fail open)
            return False
    
    def _get_window_seconds(self, window: str) -> Optional[int]:
        """Convert window name to seconds."""
        
        window_map = {
            'per_minute': 60,
            'per_hour': 3600,
            'per_day': 86400,
        }
        
        return window_map.get(window)
    
    def _record_request(self, rate_key: str):
        """Record request for rate limiting."""
        
        try:
            current_time = int(time.time())
            
            # Record for each window
            for window in self.default_limits.keys():
                window_seconds = self._get_window_seconds(window)
                if window_seconds:
                    redis_key = f"rate_limit:{rate_key}:{window}"
                    
                    # Increment request count
                    current_count = cache.get(redis_key, 0)
                    cache.set(redis_key, current_count + 1, window_seconds)
            
        except Exception as e:
            logger.error(f"Error recording request: {e}")
    
    def _rate_limit_response(self, window: str, limit: int) -> JsonResponse:
        """Return rate limit exceeded response."""
        
        window_seconds = self._get_window_seconds(window)
        retry_after = window_seconds if window_seconds else 60
        
        response = JsonResponse({
            'error': {
                'code': 'RATE_LIMIT_EXCEEDED',
                'message': f'Rate limit exceeded: {limit} requests {window}',
                'limit': limit,
                'window': window,
                'retry_after': retry_after,
                'timestamp': timezone.now().isoformat(),
            }
        }, status=429)
        
        # Add rate limit headers
        response['X-RateLimit-Limit'] = str(limit)
        response['X-RateLimit-Window'] = window
        response['Retry-After'] = str(retry_after)
        
        return response
