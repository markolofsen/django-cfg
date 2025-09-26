"""
Rate Limiting Middleware for the Universal Payment System v2.0.

Advanced rate limiting with sliding window algorithm and subscription-aware limits.
"""

import time
import json
from typing import Optional, Dict, Any, Tuple
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.core.cache import cache
from datetime import datetime, timedelta

from ..config.helpers import MiddlewareConfigHelper
from django_cfg.modules.django_logger import get_logger

logger = get_logger("rate_limiting_middleware")


class RateLimitingMiddleware(MiddlewareMixin):
    """
    Advanced Rate Limiting Middleware with sliding window algorithm.
    
    Features:
    - Sliding window rate limiting
    - Subscription-aware rate limits
    - Per-user and per-IP limiting
    - Burst allowance
    - Rate limit headers
    - Redis-based distributed limiting
    - Graceful degradation
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        
        # Load configuration from django-cfg
        try:
            middleware_config = MiddlewareConfigHelper.get_middleware_config()
            
            # Configuration from django-cfg
            self.enabled = middleware_config['rate_limiting_enabled']
            self.default_limits = middleware_config['default_rate_limits']
            self.cache_timeout = middleware_config['cache_timeouts']['rate_limit']
            
            # Static defaults
            self.strict_mode = True
            self.burst_allowance = 0.5
            self.window_size = 60  # seconds
            self.window_precision = 10  # sub-windows
            self.exempt_paths = [
                '/api/health/',
                '/admin/',
                '/static/',
                '/media/',
            ]
            
        except Exception as e:
            logger.warning(f"Failed to load rate limiting config, using defaults: {e}")
            # Fallback defaults
            self.enabled = True
            self.strict_mode = True
            self.default_limits = {
                'anonymous': 60,
                'authenticated': 300,
                'free': 100,
                'basic': 500,
                'premium': 2000,
                'enterprise': 10000,
            }
            self.burst_allowance = 0.5
            self.window_size = 60
            self.window_precision = 10
            self.exempt_paths = ['/api/health/', '/admin/']
            self.cache_timeout = 300
        
        logger.info(f"Rate Limiting Middleware initialized", extra={
            'enabled': self.enabled,
            'default_limits': self.default_limits,
            'window_size': self.window_size,
            'burst_allowance': self.burst_allowance
        })
    
    def process_request(self, request: HttpRequest) -> Optional[JsonResponse]:
        """
        Process request for rate limiting.
        
        Returns JsonResponse if rate limit exceeded, None to continue.
        """
        if not self.enabled:
            return None
        
        # Check if path is exempt
        if request.path in self.exempt_paths:
            return None
        
        start_time = time.time()
        
        try:
            # Determine rate limit for this request
            rate_limit, limit_type = self._get_rate_limit(request)
            
            # Get client identifier
            client_id = self._get_client_identifier(request)
            
            # Check rate limit
            allowed, current_usage, reset_time = self._check_rate_limit(
                client_id, rate_limit, limit_type
            )
            
            if not allowed:
                # Rate limit exceeded
                processing_time = (time.time() - start_time) * 1000
                
                logger.warning(f"Rate limit exceeded", extra={
                    'client_id': client_id,
                    'limit_type': limit_type,
                    'rate_limit': rate_limit,
                    'current_usage': current_usage,
                    'path': request.path,
                    'processing_time_ms': round(processing_time, 2)
                })
                
                return self._create_rate_limit_response(
                    rate_limit, current_usage, reset_time
                )
            
            # Add rate limit info to request
            request.rate_limit_info = {
                'limit': rate_limit,
                'remaining': max(0, rate_limit - current_usage),
                'reset_time': reset_time,
                'limit_type': limit_type
            }
            
            # Log successful rate limit check
            processing_time = (time.time() - start_time) * 1000
            logger.debug(f"Rate limit check passed", extra={
                'client_id': client_id,
                'limit_type': limit_type,
                'usage': current_usage,
                'limit': rate_limit,
                'processing_time_ms': round(processing_time, 2)
            })
            
            return None  # Continue processing
            
        except Exception as e:
            logger.error(f"Rate limiting error", extra={
                'path': request.path,
                'error': str(e),
                'processing_time_ms': round((time.time() - start_time) * 1000, 2)
            })
            
            if self.strict_mode:
                return JsonResponse({
                    'success': False,
                    'error': 'Rate limiting service unavailable',
                    'error_code': 'rate_limit_service_error'
                }, status=503)
            else:
                # Graceful degradation: allow request
                return None
    
    def _get_rate_limit(self, request: HttpRequest) -> Tuple[int, str]:
        """
        Determine the appropriate rate limit for this request.
        
        Returns tuple of (rate_limit, limit_type).
        """
        # Check if user is authenticated via API key
        if hasattr(request, 'api_key') and hasattr(request, 'subscription_access'):
            subscription_access = request.subscription_access
            
            if subscription_access.get('allowed'):
                tier = subscription_access.get('tier', 'free')
                rate_limit = self.default_limits.get(tier, self.default_limits['free'])
                return rate_limit, f"subscription_{tier}"
        
        # Check if user is authenticated (Django auth)
        if hasattr(request, 'user') and request.user.is_authenticated:
            return self.default_limits['authenticated'], 'authenticated'
        
        # Anonymous user
        return self.default_limits['anonymous'], 'anonymous'
    
    def _get_client_identifier(self, request: HttpRequest) -> str:
        """
        Get unique identifier for the client.
        
        Prioritizes API key, then user ID, then IP address.
        """
        # Use API key if available (most specific)
        if hasattr(request, 'api_key'):
            return f"api_key:{request.api_key.id}"
        
        # Use user ID if authenticated
        if hasattr(request, 'user') and request.user.is_authenticated:
            return f"user:{request.user.id}"
        
        # Fall back to IP address
        return f"ip:{self._get_client_ip(request)}"
    
    def _check_rate_limit(self, client_id: str, rate_limit: int, limit_type: str) -> Tuple[bool, int, int]:
        """
        Check rate limit using sliding window algorithm.
        
        Returns tuple of (allowed, current_usage, reset_time).
        """
        now = int(time.time())
        window_start = now - self.window_size
        
        # Cache key for this client's rate limit data
        cache_key = f"rate_limit:{client_id}:{limit_type}"
        
        # Get current window data
        window_data = cache.get(cache_key, {})
        
        # Clean old entries and count current usage
        current_usage = 0
        cleaned_data = {}
        
        for timestamp_str, count in window_data.items():
            timestamp = int(timestamp_str)
            if timestamp > window_start:
                cleaned_data[timestamp_str] = count
                current_usage += count
        
        # Calculate reset time (next window)
        reset_time = now + self.window_size
        
        # Check if we can allow this request
        burst_limit = int(rate_limit * (1 + self.burst_allowance))
        
        if current_usage >= burst_limit:
            # Hard limit exceeded
            return False, current_usage, reset_time
        elif current_usage >= rate_limit:
            # Soft limit exceeded, but within burst allowance
            logger.info(f"Burst allowance used", extra={
                'client_id': client_id,
                'current_usage': current_usage,
                'rate_limit': rate_limit,
                'burst_limit': burst_limit
            })
        
        # Add current request to window
        current_window = str(now // (self.window_size // self.window_precision) * (self.window_size // self.window_precision))
        cleaned_data[current_window] = cleaned_data.get(current_window, 0) + 1
        current_usage += 1
        
        # Save updated window data
        cache.set(cache_key, cleaned_data, timeout=self.cache_timeout)
        
        return True, current_usage, reset_time
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """
        Get client IP address from request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        
        x_real_ip = request.META.get('HTTP_X_REAL_IP')
        if x_real_ip:
            return x_real_ip
        
        return request.META.get('REMOTE_ADDR', 'unknown')
    
    def _create_rate_limit_response(self, rate_limit: int, current_usage: int, reset_time: int) -> JsonResponse:
        """
        Create rate limit exceeded response with proper headers.
        """
        response = JsonResponse({
            'success': False,
            'error': 'Rate limit exceeded',
            'error_code': 'rate_limit_exceeded',
            'rate_limit': {
                'limit': rate_limit,
                'current': current_usage,
                'reset_at': reset_time,
                'reset_in_seconds': max(0, reset_time - int(time.time()))
            },
            'timestamp': timezone.now().isoformat()
        }, status=429)
        
        # Add rate limit headers
        response['X-RateLimit-Limit'] = str(rate_limit)
        response['X-RateLimit-Remaining'] = '0'
        response['X-RateLimit-Reset'] = str(reset_time)
        response['Retry-After'] = str(max(1, reset_time - int(time.time())))
        
        return response
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Add rate limit headers to response.
        """
        if hasattr(request, 'rate_limit_info'):
            info = request.rate_limit_info
            
            response['X-RateLimit-Limit'] = str(info['limit'])
            response['X-RateLimit-Remaining'] = str(info['remaining'])
            response['X-RateLimit-Reset'] = str(info['reset_time'])
            response['X-RateLimit-Type'] = info['limit_type']
        
        return response


class AdaptiveRateLimitingMiddleware(RateLimitingMiddleware):
    """
    Adaptive Rate Limiting Middleware that adjusts limits based on system load.
    
    Extends base rate limiting with:
    - System load monitoring
    - Dynamic limit adjustment
    - Circuit breaker pattern
    - Performance-based throttling
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        
        # Adaptive configuration
        self.adaptive_enabled = getattr(settings, 'ADAPTIVE_RATE_LIMITING_ENABLED', False)
        self.load_threshold_high = getattr(settings, 'RATE_LIMIT_LOAD_THRESHOLD_HIGH', 0.8)
        self.load_threshold_critical = getattr(settings, 'RATE_LIMIT_LOAD_THRESHOLD_CRITICAL', 0.95)
        
        # Performance monitoring
        self.response_time_threshold = getattr(settings, 'RATE_LIMIT_RESPONSE_TIME_THRESHOLD', 1000)  # ms
        
        logger.info(f"Adaptive Rate Limiting initialized", extra={
            'adaptive_enabled': self.adaptive_enabled,
            'load_thresholds': {
                'high': self.load_threshold_high,
                'critical': self.load_threshold_critical
            }
        })
    
    def _get_rate_limit(self, request: HttpRequest) -> Tuple[int, str]:
        """
        Get adaptive rate limit based on system load and performance.
        """
        base_limit, limit_type = super()._get_rate_limit(request)
        
        if not self.adaptive_enabled:
            return base_limit, limit_type
        
        # Get system load factor
        load_factor = self._get_system_load_factor()
        
        # Adjust rate limit based on load
        if load_factor >= self.load_threshold_critical:
            # Critical load: reduce to 25% of normal
            adjusted_limit = int(base_limit * 0.25)
            limit_type += "_critical"
        elif load_factor >= self.load_threshold_high:
            # High load: reduce to 50% of normal
            adjusted_limit = int(base_limit * 0.5)
            limit_type += "_high_load"
        else:
            # Normal load
            adjusted_limit = base_limit
        
        return max(1, adjusted_limit), limit_type  # Ensure at least 1 request allowed
    
    def _get_system_load_factor(self) -> float:
        """
        Calculate system load factor (0.0 to 1.0).
        
        This is a simplified implementation. In production, you might want to:
        - Monitor CPU usage
        - Check database connection pool
        - Monitor Redis performance
        - Check response times
        """
        try:
            # Get average response time from cache
            avg_response_time = cache.get('system_avg_response_time', 100)  # ms
            
            # Simple load calculation based on response time
            if avg_response_time <= 200:
                return 0.1  # Low load
            elif avg_response_time <= 500:
                return 0.3  # Medium load
            elif avg_response_time <= 1000:
                return 0.6  # High load
            else:
                return 0.9  # Critical load
                
        except Exception as e:
            logger.warning(f"Failed to get system load factor: {e}")
            return 0.5  # Default to medium load
