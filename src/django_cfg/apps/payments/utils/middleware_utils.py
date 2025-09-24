"""
Utilities for middleware processing.
"""

from typing import Optional, List
from django.http import HttpRequest
from django.conf import settings


def get_client_ip(request: HttpRequest) -> Optional[str]:
    """
    Get client IP address from request.
    Handles various proxy headers and configurations.
    """
    
    # Check for forwarded headers first
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        # Take first IP in chain (original client)
        return forwarded_for.split(',')[0].strip()
    
    # Check for real IP header (common with nginx)
    real_ip = request.META.get('HTTP_X_REAL_IP')
    if real_ip:
        return real_ip.strip()
    
    # Check for Cloudflare header
    cf_ip = request.META.get('HTTP_CF_CONNECTING_IP')
    if cf_ip:
        return cf_ip.strip()
    
    # Fallback to remote address
    remote_addr = request.META.get('REMOTE_ADDR')
    if remote_addr:
        return remote_addr.strip()
    
    return None


def is_api_request(request: HttpRequest, api_prefixes: Optional[List[str]] = None) -> bool:
    """
    Check if request is an API request based on path prefixes.
    
    Args:
        request: Django HTTP request
        api_prefixes: List of API prefixes to check (defaults to settings)
    """
    
    if api_prefixes is None:
        api_prefixes = getattr(settings, 'PAYMENTS_API_PREFIXES', ['/api/'])
    
    path = request.path
    return any(path.startswith(prefix) for prefix in api_prefixes)


def extract_api_key(request: HttpRequest) -> Optional[str]:
    """
    Extract API key from request headers or query parameters.
    Supports multiple authentication methods.
    
    Priority:
    1. Authorization header (Bearer token)
    2. X-API-Key header
    3. Query parameter (less secure, for testing)
    """
    
    # Method 1: Authorization header (Bearer token)
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]  # Remove 'Bearer ' prefix
    
    # Method 2: X-API-Key header
    api_key_header = request.META.get('HTTP_X_API_KEY')
    if api_key_header:
        return api_key_header.strip()
    
    # Method 3: Custom header variations
    custom_headers = [
        'HTTP_X_API_TOKEN',
        'HTTP_APIKEY',
        'HTTP_API_TOKEN',
    ]
    
    for header in custom_headers:
        value = request.META.get(header)
        if value:
            return value.strip()
    
    # Method 4: Query parameter (less secure, mainly for testing)
    if getattr(settings, 'PAYMENTS_ALLOW_API_KEY_IN_QUERY', False):
        query_key = request.GET.get('api_key') or request.GET.get('apikey')
        if query_key:
            return query_key.strip()
    
    return None


def is_exempt_path(request: HttpRequest, exempt_paths: Optional[List[str]] = None) -> bool:
    """
    Check if request path is exempt from API key requirements.
    
    Args:
        request: Django HTTP request
        exempt_paths: List of exempt path prefixes (defaults to settings)
    """
    
    if exempt_paths is None:
        exempt_paths = getattr(settings, 'PAYMENTS_EXEMPT_PATHS', [
            '/admin/',
            '/cfg/',
            '/api/v1/api-key/validate/',
        ])
    
    path = request.path
    return any(path.startswith(exempt) for exempt in exempt_paths)


def get_request_metadata(request: HttpRequest) -> dict:
    """
    Extract useful metadata from request for logging and analytics.
    """
    
    return {
        'method': request.method,
        'path': request.path,
        'query_string': request.META.get('QUERY_STRING', ''),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'referer': request.META.get('HTTP_REFERER', ''),
        'ip_address': get_client_ip(request),
        'content_type': request.META.get('CONTENT_TYPE', ''),
        'content_length': request.META.get('CONTENT_LENGTH', 0),
        'host': request.META.get('HTTP_HOST', ''),
        'scheme': request.scheme,
        'is_secure': request.is_secure(),
    }


def should_track_request_body(request: HttpRequest, max_size: int = 10000) -> bool:
    """
    Determine if request body should be tracked for analytics.
    
    Args:
        request: Django HTTP request
        max_size: Maximum body size to track (bytes)
    """
    
    # Check content length
    content_length = request.META.get('CONTENT_LENGTH')
    if content_length and int(content_length) > max_size:
        return False
    
    # Don't track file uploads
    content_type = request.META.get('CONTENT_TYPE', '')
    if 'multipart/form-data' in content_type:
        return False
    
    # Don't track binary content
    if 'application/octet-stream' in content_type:
        return False
    
    # Don't track sensitive endpoints
    sensitive_paths = getattr(settings, 'PAYMENTS_SENSITIVE_PATHS', [
        '/api/v1/api-key/',
        '/api/v1/payment/',
        '/api/v1/subscription/',
    ])
    
    path = request.path
    if any(path.startswith(sensitive) for sensitive in sensitive_paths):
        return False
    
    return True


def should_track_response_body(response, max_size: int = 10000) -> bool:
    """
    Determine if response body should be tracked for analytics.
    
    Args:
        response: Django HTTP response
        max_size: Maximum body size to track (bytes)
    """
    
    # Don't track large responses
    if hasattr(response, 'content') and len(response.content) > max_size:
        return False
    
    # Only track successful JSON responses
    if not (200 <= response.status_code < 300):
        return False
    
    # Check content type
    content_type = response.get('Content-Type', '')
    if 'application/json' not in content_type:
        return False
    
    return True


def format_error_response(error_code: str, 
                         message: str, 
                         status_code: int = 400,
                         additional_data: Optional[dict] = None) -> dict:
    """
    Format standardized error response for middleware.
    
    Args:
        error_code: Machine-readable error code
        message: Human-readable error message
        status_code: HTTP status code
        additional_data: Additional error data
    """
    
    from django.utils import timezone
    
    error_response = {
        'error': {
            'code': error_code,
            'message': message,
            'status_code': status_code,
            'timestamp': timezone.now().isoformat(),
        }
    }
    
    if additional_data:
        error_response['error'].update(additional_data)
    
    return error_response
