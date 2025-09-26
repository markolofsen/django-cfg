"""
Usage Tracking Middleware for the Universal Payment System v2.0.

Lightweight middleware for tracking API usage and analytics.
"""

import time
from typing import Optional
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.core.cache import cache

from ..config.helpers import MiddlewareConfigHelper
from django_cfg.modules.django_logger import get_logger

logger = get_logger("usage_tracking_middleware")


class UsageTrackingMiddleware(MiddlewareMixin):
    """
    Usage Tracking Middleware for API analytics and monitoring.
    
    Features:
    - Request/response time tracking
    - Endpoint usage statistics
    - User activity monitoring
    - Performance metrics
    - Error rate tracking
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        
        # Load configuration from django-cfg
        try:
            middleware_config = MiddlewareConfigHelper.get_middleware_config()
            
            # Configuration from django-cfg
            self.enabled = middleware_config['usage_tracking_enabled']
            self.track_anonymous = middleware_config['track_anonymous_usage']
            self.api_prefixes = middleware_config['api_prefixes']
            self.cache_timeout = middleware_config['cache_timeouts']['default']
            
            # Static exempt paths
            self.exempt_paths = [
                '/api/health/',
                '/admin/',
                '/static/',
                '/media/',
            ]
            
        except Exception as e:
            logger.warning(f"Failed to load usage tracking config, using defaults: {e}")
            # Fallback defaults
            self.enabled = True
            self.track_anonymous = False
            self.api_prefixes = ['/api/']
            self.exempt_paths = ['/api/health/', '/admin/']
            self.cache_timeout = 3600
        
        logger.info(f"Usage Tracking Middleware initialized", extra={
            'enabled': self.enabled,
            'track_anonymous': self.track_anonymous
        })
    
    def process_request(self, request: HttpRequest) -> Optional[HttpResponse]:
        """
        Process incoming request - start timing and prepare tracking.
        """
        if not self.enabled:
            return None
        
        # Check if we should track this request
        if not self._should_track_request(request):
            return None
        
        # Start timing
        request._usage_start_time = time.time()
        
        # Store request info for tracking
        request._usage_info = {
            'method': request.method,
            'path': request.path,
            'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown'),
            'ip_address': self._get_client_ip(request),
            'authenticated': hasattr(request, 'api_key') or (hasattr(request, 'user') and request.user.is_authenticated)
        }
        
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Process response - track usage and performance metrics.
        """
        if not self.enabled or not hasattr(request, '_usage_start_time'):
            return response
        
        try:
            # Calculate response time
            response_time = (time.time() - request._usage_start_time) * 1000  # ms
            
            # Get usage info
            usage_info = getattr(request, '_usage_info', {})
            
            # Track the request
            self._track_request(request, response, response_time, usage_info)
            
            # Add performance headers
            response['X-Response-Time'] = f"{response_time:.2f}ms"
            
        except Exception as e:
            logger.warning(f"Usage tracking failed: {e}")
        
        return response
    
    def _should_track_request(self, request: HttpRequest) -> bool:
        """
        Determine if we should track this request.
        """
        # Check if path is in API prefixes
        is_api_request = any(request.path.startswith(prefix) for prefix in self.api_prefixes)
        
        if not is_api_request:
            return False
        
        # Check exempt paths
        if request.path in self.exempt_paths:
            return False
        
        # Check if we should track anonymous requests
        if not self.track_anonymous:
            is_authenticated = (
                hasattr(request, 'api_key') or 
                (hasattr(request, 'user') and request.user.is_authenticated)
            )
            if not is_authenticated:
                return False
        
        return True
    
    def _track_request(self, request: HttpRequest, response: HttpResponse, response_time: float, usage_info: dict):
        """
        Track request usage and performance metrics.
        """
        try:
            # Get user identifier
            user_id = None
            if hasattr(request, 'api_key'):
                user_id = request.api_key.user.id
            elif hasattr(request, 'user') and request.user.is_authenticated:
                user_id = request.user.id
            
            # Track endpoint usage
            self._track_endpoint_usage(usage_info['path'], usage_info['method'], response.status_code)
            
            # Track user activity
            if user_id:
                self._track_user_activity(user_id, usage_info['path'], response_time)
            
            # Track performance metrics
            self._track_performance_metrics(usage_info['path'], response_time, response.status_code)
            
            # Track errors
            if response.status_code >= 400:
                self._track_error(usage_info, response.status_code)
            
            # Log request
            logger.debug(f"Request tracked", extra={
                'path': usage_info['path'],
                'method': usage_info['method'],
                'status_code': response.status_code,
                'response_time_ms': round(response_time, 2),
                'user_id': user_id,
                'authenticated': usage_info['authenticated']
            })
            
        except Exception as e:
            logger.warning(f"Failed to track request: {e}")
    
    def _track_endpoint_usage(self, path: str, method: str, status_code: int):
        """
        Track endpoint usage statistics.
        """
        try:
            today = timezone.now().date().isoformat()
            hour = timezone.now().hour
            
            # Daily endpoint usage
            daily_key = f"endpoint_usage:{path}:{method}:{today}"
            cache.set(daily_key, cache.get(daily_key, 0) + 1, timeout=86400 * 2)
            
            # Hourly endpoint usage
            hourly_key = f"endpoint_usage_hourly:{path}:{method}:{today}:{hour}"
            cache.set(hourly_key, cache.get(hourly_key, 0) + 1, timeout=86400)
            
            # Status code tracking
            status_key = f"endpoint_status:{path}:{method}:{status_code}:{today}"
            cache.set(status_key, cache.get(status_key, 0) + 1, timeout=86400 * 2)
            
        except Exception as e:
            logger.warning(f"Failed to track endpoint usage: {e}")
    
    def _track_user_activity(self, user_id: int, path: str, response_time: float):
        """
        Track user activity and performance.
        """
        try:
            today = timezone.now().date().isoformat()
            
            # Update last activity
            cache.set(f"user_last_activity:{user_id}", timezone.now().isoformat(), timeout=86400 * 30)
            
            # Daily user requests
            daily_requests_key = f"user_requests:{user_id}:{today}"
            cache.set(daily_requests_key, cache.get(daily_requests_key, 0) + 1, timeout=86400 * 2)
            
            # User endpoint usage
            user_endpoint_key = f"user_endpoint:{user_id}:{path}:{today}"
            cache.set(user_endpoint_key, cache.get(user_endpoint_key, 0) + 1, timeout=86400 * 2)
            
            # User performance tracking
            perf_key = f"user_performance:{user_id}:{today}"
            perf_data = cache.get(perf_key, {'total_time': 0.0, 'request_count': 0})
            perf_data['total_time'] += response_time
            perf_data['request_count'] += 1
            perf_data['avg_response_time'] = perf_data['total_time'] / perf_data['request_count']
            
            cache.set(perf_key, perf_data, timeout=86400 * 2)
            
        except Exception as e:
            logger.warning(f"Failed to track user activity: {e}")
    
    def _track_performance_metrics(self, path: str, response_time: float, status_code: int):
        """
        Track performance metrics for monitoring.
        """
        try:
            today = timezone.now().date().isoformat()
            
            # Global performance metrics
            global_perf_key = f"global_performance:{today}"
            global_perf = cache.get(global_perf_key, {
                'total_requests': 0,
                'total_time': 0.0,
                'slow_requests': 0,  # > 1000ms
                'fast_requests': 0,  # < 100ms
            })
            
            global_perf['total_requests'] += 1
            global_perf['total_time'] += response_time
            
            if response_time > 1000:
                global_perf['slow_requests'] += 1
            elif response_time < 100:
                global_perf['fast_requests'] += 1
            
            global_perf['avg_response_time'] = global_perf['total_time'] / global_perf['total_requests']
            
            cache.set(global_perf_key, global_perf, timeout=86400 * 2)
            
            # Update system average response time for adaptive rate limiting
            cache.set('system_avg_response_time', global_perf['avg_response_time'], timeout=300)
            
        except Exception as e:
            logger.warning(f"Failed to track performance metrics: {e}")
    
    def _track_error(self, usage_info: dict, status_code: int):
        """
        Track error occurrences for monitoring.
        """
        try:
            today = timezone.now().date().isoformat()
            
            # Global error tracking
            error_key = f"errors:{status_code}:{today}"
            cache.set(error_key, cache.get(error_key, 0) + 1, timeout=86400 * 7)
            
            # Endpoint-specific error tracking
            endpoint_error_key = f"endpoint_errors:{usage_info['path']}:{status_code}:{today}"
            cache.set(endpoint_error_key, cache.get(endpoint_error_key, 0) + 1, timeout=86400 * 7)
            
            # Log significant errors
            if status_code >= 500:
                logger.error(f"Server error tracked", extra={
                    'status_code': status_code,
                    'path': usage_info['path'],
                    'method': usage_info['method'],
                    'ip_address': usage_info['ip_address'],
                    'user_agent': usage_info['user_agent']
                })
            
        except Exception as e:
            logger.warning(f"Failed to track error: {e}")
    
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
