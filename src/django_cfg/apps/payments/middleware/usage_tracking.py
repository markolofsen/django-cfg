"""
Usage Tracking Middleware.
Tracks API usage for billing, analytics, and monitoring.
"""

from django_cfg.modules.django_logger import get_logger
import json
from typing import Optional, Dict, Any
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.utils import timezone
from django.core.cache import cache
from ..models import APIKey, Subscription, Transaction
from ..services import RateLimitCache

logger = get_logger("usage_tracking")


class UsageTrackingMiddleware(MiddlewareMixin):
    """
    Middleware for tracking API usage and creating billing records.
    
    Features:
    - Request/response logging
    - Usage analytics
    - Billing event creation
    - Performance monitoring
    - Error tracking
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        
        # Enable/disable usage tracking
        self.enabled = getattr(settings, 'PAYMENTS_USAGE_TRACKING_ENABLED', True)
        
        # Paths to track (empty means track all API paths)
        self.tracked_paths = getattr(settings, 'PAYMENTS_TRACKED_PATHS', [])
        
        # Paths to exclude from tracking
        self.excluded_paths = getattr(settings, 'PAYMENTS_EXCLUDED_PATHS', [
            '/admin/',
            '/cfg/',
            '/api/v1/api-key/validate/',
        ])
        
        # Track request bodies (be careful with sensitive data)
        self.track_request_body = getattr(settings, 'PAYMENTS_TRACK_REQUEST_BODY', False)
        
        # Track response bodies (be careful with large responses)
        self.track_response_body = getattr(settings, 'PAYMENTS_TRACK_RESPONSE_BODY', False)
    
    def process_request(self, request: HttpRequest) -> None:
        """Process incoming request for usage tracking."""
        
        if not self.enabled:
            return
        
        # Skip excluded paths
        if self._is_excluded_path(request):
            return
        
        # Only track if we have API key
        if not hasattr(request, 'payment_api_key'):
            return
        
        # Record request start time
        request._usage_start_time = timezone.now()
        
        # Prepare usage data
        request._usage_data = {
            'api_key_id': request.payment_api_key.id,
            'user_id': request.payment_api_key.user.id,
            'method': request.method,
            'path': request.path,
            'query_params': dict(request.GET),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': self._get_client_ip(request),
            'start_time': request._usage_start_time,
        }
        
        # Add subscription info if available
        if hasattr(request, 'payment_subscription'):
            request._usage_data.update({
                'subscription_id': request.payment_subscription.id,
                'endpoint_group_id': request.payment_subscription.endpoint_group.id,
                'tier': request.payment_subscription.tier,
            })
        
        # Track request body if enabled and safe
        if self.track_request_body and self._is_safe_to_track_body(request):
            try:
                request._usage_data['request_body'] = request.body.decode('utf-8')[:1000]  # Limit size
            except:
                pass
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Process response for usage tracking."""
        
        if not self.enabled or not hasattr(request, '_usage_data'):
            return response
        
        try:
            # Calculate response time
            end_time = timezone.now()
            response_time_ms = int((end_time - request._usage_start_time).total_seconds() * 1000)
            
            # Update usage data
            usage_data = request._usage_data
            usage_data.update({
                'end_time': end_time,
                'response_time_ms': response_time_ms,
                'status_code': response.status_code,
                'response_size': len(response.content) if hasattr(response, 'content') else 0,
            })
            
            # Track response body if enabled and safe
            if (self.track_response_body and 
                self._is_safe_to_track_response(response) and
                response.status_code < 400):
                try:
                    content = response.content.decode('utf-8')[:1000]  # Limit size
                    usage_data['response_body'] = content
                except:
                    pass
            
            # Track error details for failed requests
            if response.status_code >= 400:
                usage_data['is_error'] = True
                usage_data['error_category'] = self._categorize_error(response.status_code)
            else:
                usage_data['is_error'] = False
            
            # Store in Redis for real-time analytics
            self._store_usage_data(usage_data)
            
            # Create billing transaction if needed
            if hasattr(request, 'payment_subscription'):
                self._create_billing_transaction(request.payment_subscription, usage_data)
            
            # Log for debugging
            logger.info(
                f"API usage tracked - User: {usage_data['user_id']}, "
                f"Path: {usage_data['path']}, "
                f"Status: {usage_data['status_code']}, "
                f"Time: {response_time_ms}ms"
            )
            
        except Exception as e:
            logger.error(f"Error in usage tracking: {e}")
        
        return response
    
    def _is_excluded_path(self, request: HttpRequest) -> bool:
        """Check if path should be excluded from tracking."""
        path = request.path
        
        # Check excluded paths
        for excluded in self.excluded_paths:
            if path.startswith(excluded):
                return True
        
        # If tracked_paths is specified, only track those
        if self.tracked_paths:
            return not any(path.startswith(tracked) for tracked in self.tracked_paths)
        
        return False
    
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
    
    def _is_safe_to_track_body(self, request: HttpRequest) -> bool:
        """Check if it's safe to track request body."""
        
        # Don't track large bodies
        content_length = request.META.get('CONTENT_LENGTH')
        if content_length and int(content_length) > 10000:  # 10KB limit
            return False
        
        # Don't track file uploads
        content_type = request.META.get('CONTENT_TYPE', '')
        if 'multipart/form-data' in content_type:
            return False
        
        # Don't track sensitive endpoints
        sensitive_paths = ['/api/v1/api-key/', '/api/v1/payment/']
        path = request.path
        if any(path.startswith(sensitive) for sensitive in sensitive_paths):
            return False
        
        return True
    
    def _is_safe_to_track_response(self, response: HttpResponse) -> bool:
        """Check if it's safe to track response body."""
        
        # Don't track large responses
        if hasattr(response, 'content') and len(response.content) > 10000:  # 10KB limit
            return False
        
        # Only track JSON responses
        content_type = response.get('Content-Type', '')
        if 'application/json' not in content_type:
            return False
        
        return True
    
    def _categorize_error(self, status_code: int) -> str:
        """Categorize error by status code."""
        
        if 400 <= status_code < 500:
            return 'client_error'
        elif 500 <= status_code < 600:
            return 'server_error'
        else:
            return 'unknown_error'
    
    def _store_usage_data(self, usage_data: Dict[str, Any]):
        """Store usage data in Redis for analytics."""
        
        try:
            # Store daily usage stats
            date_key = usage_data['start_time'].strftime('%Y-%m-%d')
            user_id = usage_data['user_id']
            
            # Increment counters using Django cache
            daily_usage_key = f"payments:daily_usage:{user_id}:{date_key}"
            current_usage = cache.get(daily_usage_key, 0)
            cache.set(daily_usage_key, current_usage + 1, timeout=86400)  # 24 hours
            
            if usage_data.get('subscription_id'):
                sub_usage_key = f"payments:subscription_usage:{usage_data['subscription_id']}:{date_key}"
                current_sub_usage = cache.get(sub_usage_key, 0)
                cache.set(sub_usage_key, current_sub_usage + 1, timeout=86400)  # 24 hours
            
            # Store performance metrics
            if usage_data['response_time_ms'] > 0:
                perf_key = f"payments:performance:{usage_data['path'].replace('/', '_')}"
                response_times = cache.get(perf_key, [])
                response_times.append(usage_data['response_time_ms'])
                # Keep only last 100 measurements
                if len(response_times) > 100:
                    response_times = response_times[-100:]
                cache.set(perf_key, response_times, timeout=3600)  # 1 hour
            
            # Store error metrics
            if usage_data.get('is_error'):
                error_key = f"payments:errors:{usage_data['path'].replace('/', '_')}:{usage_data['status_code']}"
                current_errors = cache.get(error_key, 0)
                cache.set(error_key, current_errors + 1, timeout=3600)  # 1 hour
            
        except Exception as e:
            logger.error(f"Error storing usage data in Redis: {e}")
    
    def _create_billing_transaction(self, subscription: Subscription, usage_data: Dict[str, Any]):
        """Create billing transaction for usage-based pricing."""
        
        try:
            # Only create transaction for successful requests
            if usage_data.get('is_error'):
                return
            
            # Check if this endpoint has usage-based pricing
            # For now, we'll create a small transaction for each API call
            # This could be batched or calculated differently based on business logic
            
            cost_per_request = 0.001  # $0.001 per request (example)
            
            # Create transaction record
            Transaction.objects.create(
                user=subscription.user,
                subscription=subscription,
                transaction_type='debit',
                amount_usd=-cost_per_request,  # Negative for debit
                description=f"API usage: {usage_data['method']} {usage_data['path']}",
                metadata={
                    'api_call_id': f"{usage_data['api_key_id']}_{usage_data['start_time'].timestamp()}",
                    'endpoint': usage_data['path'],
                    'method': usage_data['method'],
                    'response_time_ms': usage_data['response_time_ms'],
                    'status_code': usage_data['status_code'],
                }
            )
            
        except Exception as e:
            logger.error(f"Error creating billing transaction: {e}")
