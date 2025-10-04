"""
User Activity Middleware for Django CFG

Tracks user activity by updating last_login field for authenticated users
making API requests. Only works when accounts app is enabled.
"""

import logging
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.deprecation import MiddlewareMixin
from django_cfg.modules.base import BaseCfgModule

logger = logging.getLogger(__name__)


class UserActivityMiddleware(MiddlewareMixin, BaseCfgModule):
    """
    Middleware to track user activity via last_login field.
    
    Updates the last_login field for authenticated users on API requests.
    Only active when django_cfg accounts app is enabled.
    
    Features:
    - Updates last_login every 5 minutes to avoid database spam
    - Only tracks API requests (not regular web requests)
    - Only works when accounts app is enabled
    - KISS principle - no configuration needed
    """
    
    def __init__(self, get_response=None):
        """Initialize the middleware."""
        super().__init__(get_response)
        BaseCfgModule.__init__(self)
        self.get_response = get_response
        
        # Cache for tracking last update times (in memory)
        self._last_updates = {}
        
        # Fixed configuration - KISS principle
        self.update_interval = 300  # 5 minutes
        self.api_only = True  # Only track API requests
    
    def process_request(self, request):
        """
        Process incoming request to track user activity.
        
        Args:
            request: Django HttpRequest object
        """
        # Only process if accounts app is enabled
        if not self.is_accounts_enabled():
            return None
        
        # Only track authenticated users
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return None
        
        # Only track API requests if api_only is enabled
        if self.api_only and not self._is_api_request(request):
            return None
        
        try:
            self._update_user_activity(request.user, request)
        except Exception as e:
            # Log error but don't break the request
            logger.warning(f"Failed to update user activity: {e}")
        
        return None
    
    def _is_api_request(self, request):
        """
        Check if this is an API request using intelligent detection.
        
        Args:
            request: Django HttpRequest object
            
        Returns:
            bool: True if this is an API request
        """
        # Primary detection: Check for JSON-related indicators
        content_type = request.content_type or ''
        accept_header = request.META.get('HTTP_ACCEPT', '')
        
        # 1. JSON Content-Type or Accept header
        if ('application/json' in content_type or 
            'application/json' in accept_header):
            return True
        
        # 2. DRF format parameter
        if request.GET.get('format') in ['json', 'api']:
            return True
        
        # 3. Common REST API HTTP methods with specific paths
        if request.method in ['POST', 'PUT', 'PATCH', 'DELETE']:
            path = request.path_info
            # Only track REST operations, not form submissions
            if not path.endswith('/') or 'admin' not in path:
                return True
        
        # 4. Check if path matches configured API prefixes
        path = request.path_info
        try:
            config = self.get_config()
            if config:
                # Check Django Revolution API prefix
                if hasattr(config, 'revolution') and config.revolution:
                    api_prefix = f"/{getattr(config.revolution, 'api_prefix', 'api')}/"
                    if path.startswith(api_prefix):
                        return True
                
                # Check Django CFG prefix (always /cfg/ by default)
                if path.startswith('/cfg/'):
                    return True
        except Exception:
            # Fallback to basic path detection
            if path.startswith(('/api/', '/cfg/')):
                return True
        
        return False
    
    def _update_user_activity(self, user, request):
        """
        Update user's last_login field if enough time has passed.
        
        Args:
            user: User instance
            request: Django HttpRequest object
        """
        now = timezone.now()
        user_id = user.pk
        
        # Check if we should update (avoid database spam)
        last_update = self._last_updates.get(user_id)
        if last_update and (now - last_update).total_seconds() < self.update_interval:
            return
        
        # Update user's last_login
        User = get_user_model()
        try:
            # Use update() to avoid triggering signals and save() overhead
            User.objects.filter(pk=user_id).update(last_login=now)
            
            # Cache the update time
            self._last_updates[user_id] = now
            
            # Log the activity (optional, for debugging)
            logger.debug(f"Updated last_login for user {user.email} from {request.path}")
            
            # Clean up old cache entries (keep only last 1000 users)
            if len(self._last_updates) > 1000:
                # Remove oldest entries
                sorted_items = sorted(self._last_updates.items(), key=lambda x: x[1])
                self._last_updates = dict(sorted_items[-500:])
                
        except Exception as e:
            logger.error(f"Failed to update last_login for user {user_id}: {e}")
    
    def get_activity_stats(self):
        """
        Get middleware activity statistics.
        
        Returns:
            dict: Statistics about tracked users and configuration
        """
        return {
            'tracked_users': len(self._last_updates),
            'update_interval': self.update_interval,
            'api_only': self.api_only,
            'accounts_enabled': self.is_accounts_enabled(),
            'middleware_active': self.is_accounts_enabled(),
        }
