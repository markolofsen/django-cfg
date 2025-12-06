"""
Views for Next.js admin integration.

Serves Next.js static files with SPA routing support and JWT injection.

Features:
- Automatic extraction with metadata comparison (ZIP size + mtime vs marker file)
- Cache busting (no-store headers for HTML)
- SPA routing with fallback strategies
- JWT token injection for authenticated users

ZIP Location:
- Solution project: {BASE_DIR}/static/nextjs_admin.zip → {BASE_DIR}/static/nextjs_admin/

Extraction Logic:
- Marker file (.zip_meta) tracks ZIP metadata (size:mtime)
- Re-extracts when metadata changes (size or timestamp)
- Reliable in Docker where timestamps can be misleading
- Ensures fresh builds are deployed automatically
"""

import logging
from pathlib import Path
from django.http import Http404, HttpResponse, FileResponse
from django.views.static import serve
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django_cfg.apps.system.frontend.views import ZipExtractionMixin

logger = logging.getLogger(__name__)


@method_decorator(xframe_options_exempt, name='dispatch')
class NextJsAdminView(ZipExtractionMixin, LoginRequiredMixin, View):
    """
    Serve Next.js admin panel with JWT injection and SPA routing.

    Features:
    - Serves Next.js static build files from solution project
    - Smart ZIP extraction: metadata comparison (size + mtime) with marker file
    - Cache busting: no-store headers for HTML files
    - Automatic JWT token injection for authenticated users
    - SPA routing support (path/to/route → path/to/route/index.html)

    ZIP Location:
    - {BASE_DIR}/static/nextjs_admin.zip → {BASE_DIR}/static/nextjs_admin/

    ZIP Extraction Logic:
    - If directory doesn't exist: extract from ZIP
    - If marker file missing: extract from ZIP
    - If ZIP metadata changed: remove and re-extract
    - If metadata matches: use existing files
    - Marker file (.zip_meta) ensures reliable comparison in Docker

    URL Examples:
        /cfg/nextjs-admin/admin/                    → admin/index.html
        /cfg/nextjs-admin/admin/crypto              → admin/crypto/index.html
        /cfg/nextjs-admin/admin/_next/static/...    → _next/static/...
    """

    def get(self, request, path=''):
        """Serve Next.js files with JWT injection and SPA routing."""
        from django_cfg.core.config import get_current_config
        import django_cfg

        config = get_current_config()
        if not config or not config.nextjs_admin:
            raise Http404("Next.js admin not configured")

        nextjs_config = config.nextjs_admin

        # Use solution project static directory
        from django.conf import settings
        zip_path = Path(settings.BASE_DIR) / 'static' / 'nextjs_admin.zip'
        base_dir = Path(settings.BASE_DIR) / 'static' / 'nextjs_admin'

        # Check if ZIP exists
        if not zip_path.exists():
            logger.error(f"[nextjs_admin] ZIP not found: {zip_path}")
            return render(request, 'frontend/404.html', status=404)

        logger.info(f"[nextjs_admin] Using ZIP from solution project: {zip_path}")

        # Extract ZIP if needed using mixin
        if not self.extract_zip_if_needed(base_dir, zip_path, 'nextjs_admin'):
            return render(request, 'frontend/404.html', status=404)

        # Ensure directory exists
        if not base_dir.exists():
            logger.error(f"[nextjs_admin] Directory doesn't exist after extraction attempt")
            return render(request, 'frontend/404.html', status=404)

        static_dir = base_dir

        # Resolve path with SPA routing
        resolved_path, is_fallback = self._resolve_spa_path(static_dir, path, nextjs_config)

        # If route doesn't exist in static build, show helpful error page
        # This prevents infinite redirect loops when Next.js tries to navigate
        # to routes that weren't exported (e.g., /private without index.html)
        if is_fallback:
            logger.warning(f"[nextjs_admin] Route not found in static build: {path}")
            return render(request, 'frontend/route_not_found.html', {
                'path': path,
            }, status=404)

        # Remove conditional GET headers for HTML files to enable JWT injection
        is_html = resolved_path.endswith('.html')
        if is_html and request.user.is_authenticated:
            request.META.pop('HTTP_IF_MODIFIED_SINCE', None)
            request.META.pop('HTTP_IF_NONE_MATCH', None)

        # Serve the file
        try:
            response = serve(request, resolved_path, document_root=str(static_dir))
        except Http404:
            # If file not found, show helpful error page instead of generic 404
            logger.warning(f"[nextjs_admin] File not found: {resolved_path}")
            return render(request, 'frontend/route_not_found.html', {
                'path': path,
            }, status=404)

        # Convert FileResponse to HttpResponse for HTML to enable content modification
        if isinstance(response, FileResponse) and is_html:
            content = b''.join(response.streaming_content)
            response = HttpResponse(
                content=content,
                status=response.status_code,
                content_type=response.get('Content-Type', 'text/html')
            )

        # Inject JWT tokens for authenticated users
        if is_html and request.user.is_authenticated:
            self._inject_jwt_tokens(request, response)

        # Disable caching for HTML files (prevent Cloudflare/browser caching)
        if is_html:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response

    def _resolve_spa_path(self, base_dir: Path, path: str, nextjs_config) -> tuple[str, bool]:
        """
        Resolve SPA path with Next.js routing conventions.

        Resolution order:
        1. Default to /admin for empty path or /admin path
        2. Exact file match (static assets)
        3. path/index.html (SPA routes)
        4. path.html (single page)
        5. Fallback to admin/index.html (NOT root index.html to prevent redirect loops)

        Returns:
            tuple[str, bool]: (resolved_path, is_fallback)
            - resolved_path: The path to serve
            - is_fallback: True if this is a fallback (route doesn't exist in static build)

        Examples:
            '' → ('admin/index.html', False)
            'admin' → ('admin/index.html', False)
            'admin/centrifugo' → ('admin/centrifugo/index.html', False)
            '_next/static/...' → ('_next/static/...', False)
            'private' (no index.html) → ('admin/index.html', True) - fallback!
        """
        # Empty path or 'admin' - serve /admin route
        if not path or path == '/' or path == 'admin' or path == 'admin/':
            admin_index = base_dir / 'admin' / 'index.html'
            if admin_index.exists():
                return 'admin/index.html', False
            # Fallback to root index.html
            return 'index.html', False

        path_normalized = path.rstrip('/')
        file_path = base_dir / path

        # Strategy 1: Exact file match (for static assets)
        if file_path.exists() and file_path.is_file():
            logger.debug(f"[Next.js SPA] Exact match: {path}")
            return path, False

        # Strategy 2: Try path/index.html (most common for SPA)
        index_in_dir = base_dir / path_normalized / 'index.html'
        if index_in_dir.exists():
            resolved = f"{path_normalized}/index.html"
            logger.debug(f"[Next.js SPA] Resolved {path} → {resolved}")
            return resolved, False

        # Strategy 3: Try with trailing slash + index.html
        if path.endswith('/'):
            index_path = path + 'index.html'
            if (base_dir / index_path).exists():
                logger.debug(f"[Next.js SPA] Trailing slash: {index_path}")
                return index_path, False

        # Strategy 4: Try path.html
        html_file = base_dir / f"{path_normalized}.html"
        if html_file.exists():
            resolved = f"{path_normalized}.html"
            logger.debug(f"[Next.js SPA] HTML file: {resolved}")
            return resolved, False

        # Strategy 5: Check if directory with index.html
        if file_path.exists() and file_path.is_dir():
            index_in_existing = file_path / 'index.html'
            if index_in_existing.exists():
                resolved = f"{path_normalized}/index.html"
                logger.debug(f"[Next.js SPA] Directory index: {resolved}")
                return resolved, False

        # Strategy 6: SAFE FALLBACK - redirect to admin/index.html instead of root
        # This prevents redirect loops when Next.js app tries to navigate to
        # routes that don't exist in static export (e.g., /private without index.html)
        admin_index = base_dir / 'admin' / 'index.html'
        if admin_index.exists():
            logger.warning(f"[Next.js SPA] Route not found: {path} → fallback to admin/index.html")
            return 'admin/index.html', True

        # Last resort: root index.html
        root_index = base_dir / 'index.html'
        if root_index.exists():
            logger.warning(f"[Next.js SPA] Route not found: {path} → fallback to index.html")
            return 'index.html', True

        # Not found - return original (will 404)
        logger.warning(f"[Next.js SPA] No match for: {path}")
        return path, False

    def _inject_jwt_tokens(self, request, response):
        """Inject JWT tokens into HTML response."""
        try:
            from rest_framework_simplejwt.tokens import RefreshToken

            # Generate tokens
            refresh = RefreshToken.for_user(request.user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Injection script
            injection_script = f"""
<script>
(function() {{
    try {{
        localStorage.setItem('auth_token', '{access_token}');
        localStorage.setItem('refresh_token', '{refresh_token}');
        console.log('[Next.js Admin] JWT tokens injected');
    }} catch (e) {{
        console.error('[Next.js Admin] Failed to inject tokens:', e);
    }}
}})();
</script>
"""

            # Decode content
            try:
                content = response.content.decode('utf-8')
            except UnicodeDecodeError:
                logger.warning("Failed to decode HTML, skipping JWT injection")
                return

            # Inject before </head> or </body>
            if '</head>' in content:
                content = content.replace('</head>', f'{injection_script}</head>', 1)
                logger.debug(f"JWT tokens injected before </head> for user {request.user.pk}")
            elif '</body>' in content:
                content = content.replace('</body>', f'{injection_script}</body>', 1)
                logger.debug(f"JWT tokens injected before </body> for user {request.user.pk}")
            else:
                logger.warning("No </head> or </body> tag found, skipping JWT injection")
                return

            # Update response
            response.content = content.encode('utf-8')
            response['Content-Length'] = len(response.content)

        except ImportError:
            logger.error("djangorestframework-simplejwt not installed, skipping JWT injection")
        except Exception as e:
            logger.error(f"Failed to inject JWT tokens: {e}", exc_info=True)
