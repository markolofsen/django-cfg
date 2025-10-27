"""Views for serving Next.js static builds with automatic JWT injection.

JWT tokens are automatically injected into HTML responses for authenticated users.
This is specific to Next.js frontend apps only.
"""

import logging
from pathlib import Path
from django.http import Http404, HttpResponse, FileResponse
from django.views.static import serve
from django.views import View
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


class NextJSStaticView(View):
    """
    Serve Next.js static build files with automatic JWT token injection.

    Features:
    - Serves Next.js static export files
    - Automatically injects JWT tokens for authenticated users
    - Tokens injected into HTML responses only
    - Handles Next.js client-side routing (.html fallback)
    """

    app_name = 'admin'

    def get(self, request, path=''):
        """Serve static files from Next.js build with JWT injection."""
        import django_cfg

        base_dir = Path(django_cfg.__file__).parent / 'static' / 'frontend' / self.app_name

        if not base_dir.exists():
            raise Http404(f"Frontend app '{self.app_name}' not found. Run 'make build-admin' to build it.")

        # Default to index.html for root path
        if not path or path == '/':
            path = 'index.html'

        # Handle trailing slash (Next.js static export behavior)
        # /private/ -> private.html
        if path.endswith('/') and path != '/':
            path = path.rstrip('/') + '.html'

        # For routes without extension, try .html (Next.js static export behavior)
        file_path = base_dir / path
        if not file_path.exists() and not path.endswith('.html') and '.' not in Path(path).name:
            html_path = path + '.html'
            html_file = base_dir / html_path
            if html_file.exists():
                path = html_path

        # For HTML files, remove conditional GET headers to force full response
        # This allows JWT token injection (can't inject into 304 Not Modified responses)
        is_html_file = path.endswith('.html')
        if is_html_file and request.user.is_authenticated:
            request.META.pop('HTTP_IF_MODIFIED_SINCE', None)
            request.META.pop('HTTP_IF_NONE_MATCH', None)

        # Serve the static file
        response = serve(request, path, document_root=str(base_dir))

        # Convert FileResponse to HttpResponse for HTML files to enable JWT injection
        if isinstance(response, FileResponse):
            content_type = response.get('Content-Type', '')
            if 'text/html' in content_type and request.user.is_authenticated:
                content = b''.join(response.streaming_content)
                original_response = response
                response = HttpResponse(
                    content=content,
                    status=original_response.status_code,
                    content_type=content_type
                )
                # Copy headers from original response
                for header, value in original_response.items():
                    if header.lower() not in ('content-length', 'content-type'):
                        response[header] = value

        # Inject JWT tokens for authenticated users on HTML responses
        if self._should_inject_jwt(request, response):
            self._inject_jwt_tokens(request, response)

        return response

    def _should_inject_jwt(self, request, response):
        """Check if JWT tokens should be injected."""
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

    def _inject_jwt_tokens(self, request, response):
        """Inject JWT tokens into HTML response."""
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


class AdminView(NextJSStaticView):
    """Serve Next.js Admin Panel."""
    app_name = 'admin'
