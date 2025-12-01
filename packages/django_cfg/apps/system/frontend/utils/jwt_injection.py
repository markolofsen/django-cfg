"""
JWT Token Injection Utility

Handles injection of JWT tokens into HTML responses for authenticated users.
"""

import logging
from django.http import HttpResponse, FileResponse
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


def should_inject_jwt(request, response) -> bool:
    """
    Check if JWT tokens should be injected into the response.
    
    Args:
        request: Django request object
        response: Django response object
        
    Returns:
        bool: True if JWT tokens should be injected, False otherwise
    """
    # Only for authenticated users
    if not request.user or not request.user.is_authenticated:
        return False
    
    # Only for HttpResponse (not FileResponse or StreamingHttpResponse)
    if not isinstance(response, HttpResponse) or isinstance(response, FileResponse):
        return False
    
    # Check if response has content attribute
    if not hasattr(response, 'content'):
        return False
    
    # Only for HTML responses
    content_type = response.get('Content-Type', '')
    return 'text/html' in content_type


def inject_jwt_tokens(request, response) -> None:
    """
    Inject JWT tokens into HTML response.
    
    Injects a script that stores access_token and refresh_token in localStorage.
    The script is injected before </head> or </body> tag.
    
    Args:
        request: Django request object (must have authenticated user)
        response: Django HttpResponse object with HTML content
        
    Raises:
        Exception: Logs errors but doesn't raise to avoid breaking the response
    """
    try:
        # Generate JWT tokens
        refresh = RefreshToken.for_user(request.user)
        access_token = str(refresh.access_token)
        refresh_token = str(refresh)
        
        # Create injection script
        injection_script = f"""
<script>
(function() {{
    try {{
        localStorage.setItem('auth_token', '{access_token}');
        localStorage.setItem('refresh_token', '{refresh_token}');
        console.log('[Django-CFG] JWT tokens injected successfully');
    }} catch (e) {{
        console.error('[Django-CFG] Failed to inject JWT tokens:', e);
    }}
}})();
</script>
"""
        
        # Decode response content
        try:
            content = response.content.decode('utf-8')
        except UnicodeDecodeError:
            logger.warning("Failed to decode response content as UTF-8, skipping JWT injection")
            return
        
        # Inject before </head> or </body>
        if '</head>' in content:
            content = content.replace('</head>', f'{injection_script}</head>', 1)
            logger.debug(f"JWT tokens injected before </head> for user {request.user.pk}")
        elif '</body>' in content:
            content = content.replace('</body>', f'{injection_script}</body>', 1)
            logger.debug(f"JWT tokens injected before </body> for user {request.user.pk}")
        else:
            logger.warning(f"No </head> or </body> tag found in HTML, skipping JWT injection")
            return
        
        # Update response
        response.content = content.encode('utf-8')
        response['Content-Length'] = len(response.content)
        
    except Exception as e:
        # Log error but don't break the response
        logger.error(f"Failed to inject JWT tokens for user {request.user.pk}: {e}", exc_info=True)


def convert_file_response_to_http_response(file_response: FileResponse, request) -> HttpResponse | None:
    """
    Convert FileResponse to HttpResponse for HTML files to enable JWT injection.
    
    Only converts if:
    - Response is a FileResponse
    - Content type is text/html
    - User is authenticated
    
    Args:
        file_response: Django FileResponse object
        request: Django request object
        
    Returns:
        HttpResponse if conversion needed, None otherwise
    """
    content_type = file_response.get('Content-Type', '')
    if 'text/html' in content_type and request.user.is_authenticated:
        content = b''.join(file_response.streaming_content)
        response = HttpResponse(
            content=content,
            status=file_response.status_code,
            content_type=content_type
        )
        # Copy headers from original response
        for header, value in file_response.items():
            if header.lower() not in ('content-length', 'content-type'):
                response[header] = value
        return response
    return None

