"""
API Access Control Middleware for the Universal Payment System v2.0.

Enhanced middleware with service layer integration, smart caching, and graceful degradation.
"""

import re
import time
from typing import Optional, Dict, Any, Tuple
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone
from django.core.cache import cache
from django.contrib.auth import get_user_model

from ..models import APIKey, Subscription
from ..config.helpers import MiddlewareConfigHelper
from django_cfg.modules.django_logger import get_logger

User = get_user_model()
logger = get_logger("api_access_middleware")


class APIAccessMiddleware(MiddlewareMixin):
    """
    Enhanced API Access Control Middleware.
    
    Features:
    - API key authentication with caching
    - Subscription validation
    - Endpoint access control
    - Usage tracking and analytics
    - Rate limiting integration
    - Graceful degradation
    - Service layer integration
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        
        # Load configuration from django-cfg and Constance
        try:
            middleware_config = MiddlewareConfigHelper.get_middleware_config()
            
            # Configuration from django-cfg
            self.enabled = middleware_config['enabled']
            self.protected_paths = middleware_config.get('protected_paths', [])
            self.protected_patterns_raw = middleware_config.get('protected_patterns', [])
            self.cache_timeout = middleware_config['cache_timeouts']['api_key']
            
            # Default settings (can be overridden by Constance)
            self.strict_mode = False
            self.require_api_key = True
            
            # Get Constance settings if available
            constance_settings = middleware_config.get('constance_settings')
            if constance_settings:
                # Override with dynamic settings from Constance if needed
                # For now, we keep static defaults
                pass
            
        except Exception as e:
            logger.warning(f"Failed to load middleware config, using defaults: {e}")
            # Fallback defaults - whitelist approach
            self.enabled = True
            self.protected_paths = [
                '/api/admin/',  # Admin API endpoints
                '/api/private/',  # Private API endpoints
                '/api/secure/',  # Secure API endpoints
            ]
            self.protected_patterns_raw = [
                r'^/api/admin/.*$',  # All admin API endpoints
                r'^/api/private/.*$',  # All private API endpoints  
                r'^/api/secure/.*$',  # All secure API endpoints
            ]
            self.cache_timeout = 300
            self.strict_mode = False
            self.require_api_key = True
        
        # Compile protected path patterns
        self.protected_patterns = [
            re.compile(pattern) for pattern in self.protected_patterns_raw
        ]
        
        logger.info(f"API Access Middleware initialized", extra={
            'enabled': self.enabled,
            'strict_mode': self.strict_mode,
            'require_api_key': self.require_api_key,
            'protected_paths': self.protected_paths
        })
    
    def process_request(self, request: HttpRequest) -> Optional[JsonResponse]:
        """
        Process incoming request for API access control.
        
        Returns JsonResponse if access should be denied, None to continue.
        """
        if not self.enabled:
            return None
        
        # Check if this path is protected (whitelist approach)
        if not self._is_protected_path(request.path):
            return None
        
        # Start timing for performance monitoring
        start_time = time.time()
        
        try:
            # Extract API key from request
            api_key_value = self._extract_api_key(request)
            
            if not api_key_value:
                if self.require_api_key:
                    return self._create_error_response(
                        'API key required',
                        'missing_api_key',
                        401
                    )
                else:
                    # API key not required, continue without authentication
                    return None
            
            # Validate API key
            api_key, validation_result = self._validate_api_key(api_key_value)
            
            if not validation_result['valid']:
                return self._create_error_response(
                    validation_result['message'],
                    validation_result['error_code'],
                    401
                )
            
            # Check subscription access
            subscription_result = self._check_subscription_access(api_key, request.path)
            
            if not subscription_result['allowed']:
                if self.strict_mode:
                    return self._create_error_response(
                        subscription_result['message'],
                        subscription_result['error_code'],
                        403
                    )
                else:
                    # Non-strict mode: add warning but allow access
                    request.subscription_warning = subscription_result
            
            # Add authentication info to request
            request.api_key = api_key
            request.authenticated_user = api_key.user
            request.subscription_access = subscription_result
            
            # Track usage (async to avoid blocking)
            self._track_usage_async(api_key, request)
            
            # Log successful authentication
            processing_time = (time.time() - start_time) * 1000  # ms
            logger.debug(f"API access granted", extra={
                'api_key_id': str(api_key.id),
                'user_id': api_key.user.id,
                'path': request.path,
                'processing_time_ms': round(processing_time, 2)
            })
            
            return None  # Continue processing
            
        except Exception as e:
            logger.error(f"API access middleware error", extra={
                'path': request.path,
                'error': str(e),
                'processing_time_ms': round((time.time() - start_time) * 1000, 2)
            })
            
            if self.strict_mode:
                return self._create_error_response(
                    'Authentication service unavailable',
                    'service_error',
                    503
                )
            else:
                # Graceful degradation: allow access but log the issue
                return None
    
    def _is_protected_path(self, path: str) -> bool:
        """
        Check if the given path is protected and requires API authentication.
        
        Whitelist approach: only paths explicitly listed as protected require API key.
        """
        # Check exact protected paths
        for protected_path in self.protected_paths:
            if path.startswith(protected_path):
                return True
        
        # Check protected patterns
        for pattern in self.protected_patterns:
            if pattern.match(path):
                return True
        
        # Path is not protected - no API key required
        return False
    
    def _extract_api_key(self, request: HttpRequest) -> Optional[str]:
        """
        Extract API key from request headers or query parameters.
        
        Supports multiple formats:
        - Authorization: Bearer <key>
        - Authorization: ApiKey <key>
        - X-API-Key: <key>
        - api_key query parameter
        """
        # Check Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer '
        elif auth_header.startswith('ApiKey '):
            return auth_header[7:]  # Remove 'ApiKey '
        
        # Check X-API-Key header
        api_key_header = request.META.get('HTTP_X_API_KEY')
        if api_key_header:
            return api_key_header
        
        # Check query parameter (less secure, but supported)
        api_key_param = request.GET.get('api_key')
        if api_key_param:
            logger.warning(f"API key provided via query parameter", extra={
                'path': request.path,
                'ip': self._get_client_ip(request)
            })
            return api_key_param
        
        return None
    
    def _validate_api_key(self, api_key_value: str) -> Tuple[Optional[APIKey], Dict[str, Any]]:
        """
        Validate API key with caching.
        
        Returns tuple of (APIKey instance, validation result dict).
        """
        # Check cache first
        cache_key = f"api_key_validation:{api_key_value[:10]}..."  # Partial key for security
        cached_result = cache.get(cache_key)
        
        if cached_result:
            if cached_result['valid']:
                try:
                    api_key = APIKey.objects.get(id=cached_result['api_key_id'])
                    return api_key, cached_result
                except APIKey.DoesNotExist:
                    # Cache is stale, continue with fresh validation
                    pass
            else:
                # Return cached negative result
                return None, cached_result
        
        # Fresh validation
        try:
            api_key = APIKey.get_valid_key(api_key_value)
            
            if api_key:
                result = {
                    'valid': True,
                    'api_key_id': str(api_key.id),
                    'user_id': api_key.user.id,
                    'message': 'API key valid'
                }
                
                # Cache positive result
                cache.set(cache_key, result, timeout=self.cache_timeout)
                
                return api_key, result
            else:
                result = {
                    'valid': False,
                    'message': 'Invalid or expired API key',
                    'error_code': 'invalid_api_key'
                }
                
                # Cache negative result for shorter time
                cache.set(cache_key, result, timeout=60)  # 1 minute
                
                return None, result
                
        except Exception as e:
            logger.error(f"API key validation error: {e}")
            return None, {
                'valid': False,
                'message': 'API key validation failed',
                'error_code': 'validation_error'
            }
    
    def _check_subscription_access(self, api_key: APIKey, path: str) -> Dict[str, Any]:
        """
        Check if user has valid subscription for the requested endpoint.
        """
        try:
            # Get user's active subscriptions
            active_subscriptions = Subscription.objects.filter(
                user=api_key.user,
                status=Subscription.SubscriptionStatus.ACTIVE,
                expires_at__gt=timezone.now()
            ).prefetch_related('endpoint_groups')
            
            if not active_subscriptions.exists():
                return {
                    'allowed': False,
                    'message': 'No active subscription found',
                    'error_code': 'no_active_subscription',
                    'upgrade_required': True
                }
            
            # For now, allow access if user has any active subscription
            # TODO: Implement endpoint-specific access control based on tariff/endpoint_group
            
            subscription = active_subscriptions.first()
            
            return {
                'allowed': True,
                'subscription_id': str(subscription.id),
                'tier': subscription.tier,
                'tier_name': subscription.tier,
                'requests_remaining': 'unlimited',  # TODO: Implement rate limiting per subscription
                'expires_at': subscription.expires_at.isoformat() if subscription.expires_at else None
            }
            
        except Exception as e:
            logger.error(f"Subscription access check error: {e}")
            return {
                'allowed': not self.strict_mode,  # Allow in non-strict mode
                'message': 'Subscription check failed',
                'error_code': 'subscription_check_error'
            }
    
    def _track_usage_async(self, api_key: APIKey, request: HttpRequest):
        """
        Track API usage asynchronously to avoid blocking the request.
        """
        try:
            # Increment usage counter (this will trigger signals)
            api_key.increment_usage(ip_address=self._get_client_ip(request))
            
            # Update usage analytics in cache
            today = timezone.now().date().isoformat()
            
            # Daily usage counter
            daily_key = f"api_usage_daily:{api_key.user.id}:{today}"
            cache.set(daily_key, cache.get(daily_key, 0) + 1, timeout=86400 * 2)
            
            # Endpoint usage counter
            endpoint_key = f"endpoint_usage:{request.path}:{today}"
            cache.set(endpoint_key, cache.get(endpoint_key, 0) + 1, timeout=86400 * 2)
            
        except Exception as e:
            logger.warning(f"Usage tracking failed: {e}")
    
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
    
    def _create_error_response(self, message: str, error_code: str, status_code: int) -> JsonResponse:
        """
        Create standardized error response.
        """
        return JsonResponse({
            'success': False,
            'error': message,
            'error_code': error_code,
            'timestamp': timezone.now().isoformat()
        }, status=status_code)
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """
        Process response to add headers and perform cleanup.
        """
        # Add API usage headers if authenticated
        if hasattr(request, 'api_key') and hasattr(request, 'subscription_access'):
            subscription_access = request.subscription_access
            
            if subscription_access.get('allowed'):
                response['X-RateLimit-Remaining'] = str(subscription_access.get('requests_remaining', 'unlimited'))
                response['X-Subscription-Tier'] = subscription_access.get('tier', 'unknown')
                
                if subscription_access.get('expires_at'):
                    response['X-Subscription-Expires'] = subscription_access['expires_at']
        
        # Add security headers
        response['X-API-Version'] = '2.0'
        response['X-Powered-By'] = 'Universal Payment System'
        
        return response
