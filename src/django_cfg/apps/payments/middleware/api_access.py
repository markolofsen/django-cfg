"""
API Access Control Middleware.
Handles API key authentication and subscription validation.
"""

from django_cfg.modules.django_logger import get_logger
from typing import Optional, Tuple
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.utils import timezone
from ..models import APIKey, Subscription, EndpointGroup
from ..services import ApiKeyCache, RateLimitCache
from ..services.security import error_handler, SecurityError

logger = get_logger("api_access")


class APIAccessMiddleware(MiddlewareMixin):
    """
    Middleware for API access control using API keys and subscriptions.
    
    Features:
    - API key validation
    - Subscription status checking
    - Endpoint access control
    - Usage tracking
    """
    
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.api_key_cache = ApiKeyCache()
        self.rate_limit_cache = RateLimitCache()
        
        # Paths that don't require API key authentication
        self.exempt_paths = getattr(settings, 'PAYMENTS_EXEMPT_PATHS', [
            '/api/v1/api-key/validate/',
            '/api/v1/api-key/create/',
            '/admin/',
            '/cfg/',
        ])
        
        # API prefixes that require authentication
        self.api_prefixes = getattr(settings, 'PAYMENTS_API_PREFIXES', [
            '/api/v1/',
        ])
    
    def process_request(self, request: HttpRequest) -> Optional[JsonResponse]:
        """Process incoming request for API access control."""
        
        # Skip non-API requests
        if not self._is_api_request(request):
            return None
        
        # Skip exempt paths
        if self._is_exempt_path(request):
            return None
        
        # Extract API key
        api_key = self._extract_api_key(request)
        if not api_key:
            security_error = SecurityError(
                "API key required for protected endpoint",
                details={'path': request.path, 'method': request.method}
            )
            error_handler.handle_error(security_error, {
                'middleware': 'api_access',
                'operation': 'api_key_extraction'
            }, request)
            
            return self._error_response(
                'API key required', 
                status=401,
                error_code='MISSING_API_KEY'
            )
        
        # Validate API key
        api_key_obj = self._validate_api_key(api_key)
        if not api_key_obj:
            security_error = SecurityError(
                f"Invalid or expired API key attempted",
                details={
                    'api_key_prefix': api_key[:8] + '...' if len(api_key) > 8 else api_key,
                    'path': request.path,
                    'method': request.method,
                    'ip_address': self._get_client_ip(request)
                }
            )
            error_handler.handle_error(security_error, {
                'middleware': 'api_access',
                'operation': 'api_key_validation'
            }, request)
            
            return self._error_response(
                'Invalid or expired API key',
                status=401,
                error_code='INVALID_API_KEY'
            )
        
        # Check subscription access
        endpoint_group = self._get_endpoint_group(request)
        if endpoint_group:
            subscription = self._check_subscription_access(api_key_obj.user, endpoint_group)
            if not subscription:
                return self._error_response(
                    f'No active subscription for {endpoint_group.display_name}',
                    status=403,
                    error_code='NO_SUBSCRIPTION'
                )
            
            # Check usage limits
            if self._is_usage_exceeded(subscription):
                return self._error_response(
                    'Usage limit exceeded for this subscription',
                    status=429,
                    error_code='USAGE_EXCEEDED'
                )
            
            # Store subscription in request for usage tracking
            request.payment_subscription = subscription
        
        # Store API key in request
        request.payment_api_key = api_key_obj
        request.payment_user = api_key_obj.user
        
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Process response to track API usage."""
        
        # Track usage if API key was used
        if hasattr(request, 'payment_api_key') and hasattr(request, 'payment_subscription'):
            self._track_usage(request.payment_api_key, request.payment_subscription, request)
        
        return response
    
    def _is_api_request(self, request: HttpRequest) -> bool:
        """Check if request is an API request."""
        path = request.path
        return any(path.startswith(prefix) for prefix in self.api_prefixes)
    
    def _is_exempt_path(self, request: HttpRequest) -> bool:
        """Check if path is exempt from API key requirement."""
        path = request.path
        return any(path.startswith(exempt) for exempt in self.exempt_paths)
    
    def _extract_api_key(self, request: HttpRequest) -> Optional[str]:
        """Extract API key from request headers or query params."""
        
        # Try Authorization header first (Bearer token)
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        
        # Try X-API-Key header
        api_key = request.META.get('HTTP_X_API_KEY')
        if api_key:
            return api_key
        
        # Try query parameter (less secure, for testing)
        api_key = request.GET.get('api_key')
        if api_key:
            return api_key
        
        return None
    
    def _validate_api_key(self, api_key: str) -> Optional[APIKey]:
        """Validate API key using Redis cache with DB fallback."""
        
        try:
            # Try Redis first
            cached_key = self.redis_service.get_api_key(api_key)
            if cached_key:
                return cached_key
            
            # Fallback to database
            api_key_obj = APIKey.objects.select_related('user').filter(
                key_value=api_key,
                is_active=True
            ).first()
            
            if api_key_obj and api_key_obj.is_valid():
                # Cache valid key
                self.redis_service.cache_api_key(api_key_obj)
                
                # Update last used
                api_key_obj.record_usage()
                
                return api_key_obj
            
            return None
            
        except Exception as e:
            logger.error(f"Error validating API key: {e}")
            return None
    
    def _get_endpoint_group(self, request: HttpRequest) -> Optional[EndpointGroup]:
        """Determine endpoint group based on request path."""
        
        # This would be customized per project
        # For now, return None (no endpoint group restrictions)
        # In real implementation, this would map URL patterns to endpoint groups
        
        path = request.path
        
        # Example mapping (would be configurable)
        endpoint_mappings = {
            '/api/v1/payments/': 'payments',
            '/api/v1/subscriptions/': 'billing',
            '/api/v1/users/': 'user_management',
        }
        
        for path_prefix, group_name in endpoint_mappings.items():
            if path.startswith(path_prefix):
                try:
                    return EndpointGroup.objects.get(name=group_name, is_active=True)
                except EndpointGroup.DoesNotExist:
                    continue
        
        return None
    
    def _check_subscription_access(self, user, endpoint_group: EndpointGroup) -> Optional[Subscription]:
        """Check if user has active subscription for endpoint group."""
        
        try:
            # Get active subscription for this endpoint group
            subscription = Subscription.objects.filter(
                user=user,
                endpoint_group=endpoint_group,
                status='active',
                expires_at__gt=timezone.now()
            ).first()
            
            return subscription
            
        except Exception as e:
            logger.error(f"Error checking subscription access: {e}")
            return None
    
    def _is_usage_exceeded(self, subscription: Subscription) -> bool:
        """Check if subscription usage limit is exceeded."""
        
        try:
            # Check current usage against limit
            if subscription.usage_limit == 0:  # Unlimited
                return False
            
            return subscription.usage_current >= subscription.usage_limit
            
        except Exception as e:
            logger.error(f"Error checking usage limits: {e}")
            return False
    
    def _track_usage(self, api_key: APIKey, subscription: Subscription, request: HttpRequest):
        """Track API usage for billing and analytics."""
        
        try:
            # Increment subscription usage
            subscription.usage_current += 1
            subscription.save(update_fields=['usage_current'])
            
            # Update Redis cache
            self.redis_service.increment_usage(api_key.key_value, subscription.id)
            
            # Log usage for analytics
            logger.info(
                f"API usage tracked - User: {api_key.user.id}, "
                f"Subscription: {subscription.id}, "
                f"Path: {request.path}, "
                f"Usage: {subscription.usage_current}/{subscription.usage_limit}"
            )
            
        except Exception as e:
            logger.error(f"Error tracking usage: {e}")
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip
    
    def _error_response(self, message: str, status: int = 400, error_code: str = 'ERROR') -> JsonResponse:
        """Return standardized error response."""
        
        return JsonResponse({
            'error': {
                'code': error_code,
                'message': message,
                'timestamp': timezone.now().isoformat(),
            }
        }, status=status)
