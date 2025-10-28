"""
Views for Next.js admin integration.

Serves Next.js static files with SPA routing support and JWT injection.
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

logger = logging.getLogger(__name__)


@method_decorator(xframe_options_exempt, name='dispatch')
class NextJsAdminView(LoginRequiredMixin, View):
    """
    Serve Next.js admin panel with JWT injection and SPA routing.

    Features:
    - Serves Next.js static build files
    - Automatic JWT token injection for authenticated users
    - SPA routing support (path/to/route → path/to/route/index.html)
    - Development mode support (proxies to dev server conceptually)

    URL Examples:
        /cfg/admin/                    → private.html (or index.html)
        /cfg/admin/private/centrifugo  → private/centrifugo/index.html
        /cfg/admin/_next/static/...    → _next/static/...
    """

    def get(self, request, path=''):
        """Serve Next.js files with JWT injection and SPA routing."""
        from django_cfg.core.config import get_current_config
        import django_cfg
        import zipfile

        config = get_current_config()
        if not config or not config.nextjs_admin:
            raise Http404("Next.js admin not configured")

        nextjs_config = config.nextjs_admin

        # Use extracted directory from static/frontend/nextjs_admin/
        base_dir = Path(django_cfg.__file__).parent / 'static' / 'frontend' / 'nextjs_admin'

        # Check if ZIP archive exists and extract if needed
        if not base_dir.exists():
            # Try django_cfg package location first
            zip_path = Path(django_cfg.__file__).parent / 'static' / 'frontend' / 'nextjs_admin.zip'

            # Fallback: Try solution project static directory
            if not zip_path.exists():
                from django.conf import settings
                solution_zip = Path(settings.BASE_DIR) / 'static' / 'nextjs_admin.zip'
                if solution_zip.exists():
                    zip_path = solution_zip
                    logger.info(f"Using ZIP from solution project: {solution_zip}")

            if zip_path.exists():
                logger.info(f"Extracting nextjs_admin.zip to {base_dir}...")
                try:
                    base_dir.parent.mkdir(parents=True, exist_ok=True)
                    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                        zip_ref.extractall(base_dir)
                    logger.info(f"Successfully extracted nextjs_admin.zip from {zip_path}")
                except Exception as e:
                    logger.error(f"Failed to extract nextjs_admin.zip: {e}")
                    return render(request, 'frontend/404.html', status=404)
            else:
                logger.error(f"nextjs_admin.zip not found in django_cfg or solution project")
                return render(request, 'frontend/404.html', status=404)

        static_dir = base_dir

        # Resolve path with SPA routing
        resolved_path = self._resolve_spa_path(static_dir, path, nextjs_config)

        # Remove conditional GET headers for HTML files to enable JWT injection
        is_html = resolved_path.endswith('.html')
        if is_html and request.user.is_authenticated:
            request.META.pop('HTTP_IF_MODIFIED_SINCE', None)
            request.META.pop('HTTP_IF_NONE_MATCH', None)

        # Serve the file
        try:
            response = serve(request, resolved_path, document_root=str(static_dir))
        except Http404:
            # If file not found, try fallback to root index.html for SPA
            root_index = static_dir / 'index.html'
            if root_index.exists():
                response = serve(request, 'index.html', document_root=str(static_dir))
            else:
                raise

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

        return response

    def _resolve_spa_path(self, base_dir: Path, path: str, nextjs_config) -> str:
        """
        Resolve SPA path with Next.js routing conventions.

        Resolution order:
        1. Default to /admin for empty path or /admin path
        2. Exact file match (static assets)
        3. path/index.html (SPA routes)
        4. path.html (single page)
        5. Fallback to index.html

        Examples:
            '' → 'admin/index.html'
            'admin' → 'admin/index.html'
            'admin/centrifugo' → 'admin/centrifugo/index.html'
            '_next/static/...' → '_next/static/...' (exact)
        """
        # Empty path or 'admin' - serve /admin route
        if not path or path == '/' or path == 'admin' or path == 'admin/':
            admin_index = base_dir / 'admin' / 'index.html'
            if admin_index.exists():
                return 'admin/index.html'
            # Fallback to root index.html
            return 'index.html'

        path_normalized = path.rstrip('/')
        file_path = base_dir / path

        # Strategy 1: Exact file match (for static assets)
        if file_path.exists() and file_path.is_file():
            logger.debug(f"[Next.js SPA] Exact match: {path}")
            return path

        # Strategy 2: Try path/index.html (most common for SPA)
        index_in_dir = base_dir / path_normalized / 'index.html'
        if index_in_dir.exists():
            resolved = f"{path_normalized}/index.html"
            logger.debug(f"[Next.js SPA] Resolved {path} → {resolved}")
            return resolved

        # Strategy 3: Try with trailing slash + index.html
        if path.endswith('/'):
            index_path = path + 'index.html'
            if (base_dir / index_path).exists():
                logger.debug(f"[Next.js SPA] Trailing slash: {index_path}")
                return index_path

        # Strategy 4: Try path.html
        html_file = base_dir / f"{path_normalized}.html"
        if html_file.exists():
            resolved = f"{path_normalized}.html"
            logger.debug(f"[Next.js SPA] HTML file: {resolved}")
            return resolved

        # Strategy 5: Check if directory with index.html
        if file_path.exists() and file_path.is_dir():
            index_in_existing = file_path / 'index.html'
            if index_in_existing.exists():
                resolved = f"{path_normalized}/index.html"
                logger.debug(f"[Next.js SPA] Directory index: {resolved}")
                return resolved

        # Strategy 6: Fallback to root index.html (SPA will handle routing)
        root_index = base_dir / 'index.html'
        if root_index.exists():
            logger.debug(f"[Next.js SPA] Fallback to index.html for: {path}")
            return 'index.html'

        # Not found - return original (will 404)
        logger.warning(f"[Next.js SPA] No match for: {path}")
        return path

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
