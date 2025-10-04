"""
Django middleware for orchestrator integration.
"""

import time
import logging
from typing import Callable
from django.http import HttpRequest, HttpResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class OrchestratorMiddleware(MiddlewareMixin):
    """
    Middleware for Django Orchestrator integration.
    
    Provides:
    - Request context for agents
    - Performance monitoring
    - Error tracking
    - User session integration
    """
    
    def __init__(self, get_response: Callable):
        """Initialize middleware."""
        self.get_response = get_response
        super().__init__(get_response)
    
    def process_request(self, request: HttpRequest):
        """Process incoming request."""
        # Add orchestrator context to request
        request.orchestrator_start_time = time.time()
        request.orchestrator_context = {
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'ip_address': self._get_client_ip(request),
            'session_key': request.session.session_key if hasattr(request, 'session') else None,
        }
        
        logger.debug(f"Orchestrator middleware: Processing request {request.path}")
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Process outgoing response."""
        if hasattr(request, 'orchestrator_start_time'):
            duration = time.time() - request.orchestrator_start_time
            
            # Add performance header
            response['X-Orchestrator-Duration'] = f"{duration:.3f}s"
            
            # Log slow requests
            if duration > 5.0:  # 5 seconds threshold
                logger.warning(
                    f"Slow request detected: {request.path} took {duration:.3f}s"
                )
        
        return response
    
    def process_exception(self, request: HttpRequest, exception: Exception):
        """Process exceptions."""
        if hasattr(request, 'orchestrator_context'):
            logger.error(
                f"Exception in orchestrator context: {exception}",
                extra={
                    'request_path': request.path,
                    'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
                    'orchestrator_context': request.orchestrator_context,
                }
            )
        
        # Don't handle the exception, just log it
        return None
    
    def _get_client_ip(self, request: HttpRequest) -> str:
        """Get client IP address."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or 'unknown'
