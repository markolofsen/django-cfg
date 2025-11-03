"""Views for serving Next.js static builds with automatic JWT injection.

JWT tokens are automatically injected into HTML responses for authenticated users.
This is specific to Next.js frontend apps only.

Features:
- Automatic extraction of ZIP archives with metadata comparison (size + mtime)
- Auto-reextraction when ZIP content changes (size or timestamp)
- Marker file (.zip_meta) tracks ZIP metadata for reliable comparison
- Cache busting (no-store headers for HTML)
- SPA routing with fallback strategies
- JWT token injection for authenticated users
"""

import logging
import zipfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from django.http import Http404, HttpResponse, FileResponse
from django.views.static import serve
from django.views import View
from django.views.decorators.clickjacking import xframe_options_exempt
from django.utils.decorators import method_decorator
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import UserPassesTestMixin
from rest_framework_simplejwt.tokens import RefreshToken

logger = logging.getLogger(__name__)


class ZipExtractionMixin:
    """
    Mixin for automatic ZIP extraction with metadata-based refresh.

    Provides intelligent ZIP archive handling:
    - Auto-extraction when directory doesn't exist
    - Auto-reextraction when ZIP metadata changes (size or mtime)
    - Marker file (.zip_meta) tracks ZIP state for reliable comparison
    - Works correctly in Docker where timestamps can be misleading

    Usage:
        class MyView(ZipExtractionMixin, View):
            app_name = 'myapp'  # Will look for myapp.zip
    """

    def extract_zip_if_needed(self, base_dir: Path, zip_path: Path, app_name: str) -> bool:
        """
        Extract ZIP archive if needed based on ZIP metadata (size + mtime) comparison.

        Logic:
        1. If directory doesn't exist → extract
        2. If marker file doesn't exist → extract
        3. If ZIP metadata changed (size or mtime) → remove and re-extract
        4. If metadata matches → use existing

        Uses marker file (.zip_meta) to track ZIP metadata. More reliable than
        just mtime comparison, especially in Docker where timestamps can be misleading.

        Args:
            base_dir: Target directory for extraction
            zip_path: Path to ZIP archive
            app_name: Name of the app (for logging)

        Returns:
            bool: True if extraction succeeded or not needed, False if failed
        """
        should_extract = False

        # Check if ZIP exists first
        if not zip_path.exists():
            logger.error(f"[{app_name}] ZIP not found: {zip_path}")
            return False

        # Get ZIP metadata (size + mtime for reliable comparison)
        zip_stat = zip_path.stat()
        current_meta = f"{zip_stat.st_size}:{zip_stat.st_mtime}"

        # Marker file stores ZIP metadata
        marker_file = base_dir / '.zip_meta'

        # Priority 1: If directory doesn't exist at all - always extract
        if not base_dir.exists():
            should_extract = True
            logger.info(f"[{app_name}] Directory doesn't exist, will extract")

        # Priority 2: Marker file doesn't exist - extract (first run or corrupted)
        elif not marker_file.exists():
            should_extract = True
            logger.info(f"[{app_name}] No marker file found, will extract")

        # Priority 3: Compare stored metadata with current ZIP metadata
        else:
            try:
                stored_meta = marker_file.read_text().strip()
                if stored_meta != current_meta:
                    logger.info(f"[{app_name}] ZIP metadata changed (stored: {stored_meta}, current: {current_meta}), re-extracting")
                    try:
                        shutil.rmtree(base_dir)
                        should_extract = True
                    except Exception as e:
                        logger.error(f"[{app_name}] Failed to remove old directory: {e}")
                        return False
                else:
                    logger.info(f"[{app_name}] ZIP unchanged (meta: {current_meta}), using existing directory")
            except Exception as e:
                logger.warning(f"[{app_name}] Failed to read marker file: {e}, will re-extract")
                should_extract = True

        # Extract ZIP if needed
        if should_extract:
            logger.info(f"[{app_name}] Extracting {zip_path.name} to {base_dir}...")
            try:
                base_dir.parent.mkdir(parents=True, exist_ok=True)
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(base_dir)

                # Write marker file with current metadata
                marker_file.write_text(current_meta)
                logger.info(f"[{app_name}] Successfully extracted {zip_path.name} and saved marker (meta: {current_meta})")
                return True
            except Exception as e:
                logger.error(f"[{app_name}] Failed to extract: {e}")
                return False

        # Directory exists and is up-to-date
        return True


@method_decorator(xframe_options_exempt, name='dispatch')
class NextJSStaticView(ZipExtractionMixin, View):
    """
    Serve Next.js static build files with automatic JWT token injection.

    Features:
    - Serves Next.js static export files like a static file server
    - Smart ZIP extraction: compares ZIP metadata (size + mtime) with marker file
    - Automatically injects JWT tokens for authenticated users
    - Tokens injected into HTML responses only
    - Handles Next.js client-side routing (.html fallback)
    - Automatically serves index.html for directory paths
    - X-Frame-Options exempt to allow embedding in iframes

    ZIP Extraction Logic:
    - If directory doesn't exist: extract from ZIP
    - If marker file missing: extract from ZIP
    - If ZIP metadata changed: remove and re-extract
    - If metadata matches: use existing files
    - Marker file (.zip_meta) ensures reliable comparison in Docker

    Path resolution examples:
    - /cfg/admin/              → /cfg/admin/index.html
    - /cfg/admin/private/      → /cfg/admin/private/index.html (if exists)
    - /cfg/admin/private/      → /cfg/admin/private.html (fallback)
    - /cfg/admin/tasks         → /cfg/admin/tasks.html
    - /cfg/admin/tasks         → /cfg/admin/tasks/index.html (fallback)
    """

    app_name = 'admin'

    def get(self, request, path=''):
        """Serve static files from Next.js build with JWT injection."""
        import django_cfg

        base_dir = Path(django_cfg.__file__).parent / 'static' / 'frontend' / self.app_name
        zip_path = Path(django_cfg.__file__).parent / 'static' / 'frontend' / f'{self.app_name}.zip'

        # Extract ZIP if needed using mixin
        if not self.extract_zip_if_needed(base_dir, zip_path, self.app_name):
            return render(request, 'frontend/404.html', status=404)

        # Ensure directory exists
        if not base_dir.exists():
            logger.error(f"[{self.app_name}] Directory doesn't exist after extraction attempt")
            return render(request, 'frontend/404.html', status=404)

        original_path = path  # Store for logging

        # Default to index.html for root path
        if not path or path == '/':
            path = 'index.html'
            logger.debug(f"Root path requested, serving: {path}")

        # Resolve file path with SPA routing fallback strategy
        path = self._resolve_spa_path(base_dir, path)

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

        # Disable caching for HTML files (prevent Cloudflare/browser caching)
        if is_html_file:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response

    def _resolve_spa_path(self, base_dir, path):
        """
        Resolve SPA path with multiple fallback strategies.

        Resolution order:
        1. Exact file match (e.g., script.js, style.css)
        2. path/index.html (e.g., private/centrifugo/index.html)
        3. path.html (e.g., private.html for /private)
        4. Fallback to root index.html for SPA routing

        Examples:
            /private/centrifugo → private/centrifugo/index.html
            /private → private.html OR private/index.html
            /_next/static/... → _next/static/... (exact match)
            /unknown/route → index.html (SPA fallback)
        """
        file_path = base_dir / path

        # Remove trailing slash for processing
        path_normalized = path.rstrip('/')

        # Strategy 1: Exact file match (for static assets like JS, CSS, images)
        if file_path.exists() and file_path.is_file():
            logger.debug(f"[SPA Router] Exact match: {path}")
            return path

        # Strategy 2: Try path/index.html (most common for SPA routes)
        index_in_dir = base_dir / path_normalized / 'index.html'
        if index_in_dir.exists():
            resolved_path = f"{path_normalized}/index.html"
            logger.debug(f"[SPA Router] Resolved {path} → {resolved_path}")
            return resolved_path

        # Strategy 3: Try with trailing slash + index.html
        if path.endswith('/'):
            index_path = path + 'index.html'
            if (base_dir / index_path).exists():
                logger.debug(f"[SPA Router] Trailing slash resolved: {index_path}")
                return index_path

        # Strategy 4: Try path.html (Next.js static export behavior)
        html_file = base_dir / (path_normalized + '.html')
        if html_file.exists():
            resolved_path = path_normalized + '.html'
            logger.debug(f"[SPA Router] HTML file match: {resolved_path}")
            return resolved_path

        # Strategy 5: Check if it's a directory without index.html
        if file_path.exists() and file_path.is_dir():
            # Try index.html in that directory
            index_in_existing_dir = file_path / 'index.html'
            if index_in_existing_dir.exists():
                resolved_path = f"{path_normalized}/index.html"
                logger.debug(f"[SPA Router] Directory with index: {resolved_path}")
                return resolved_path

        # Strategy 6: SPA fallback - serve root index.html
        # This allows client-side routing to handle unknown routes
        root_index = base_dir / 'index.html'
        if root_index.exists():
            logger.debug(f"[SPA Router] Fallback to index.html for route: {path}")
            return 'index.html'

        # Strategy 7: Nothing found - return original path (will 404)
        logger.warning(f"[SPA Router] No match found for: {path}")
        return path

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


class AdminView(UserPassesTestMixin, NextJSStaticView):
    """Serve Next.js Admin Panel. Only accessible to admin users."""
    app_name = 'admin'

    def test_func(self):
        """Check if user is admin (staff or superuser)."""
        return self.request.user.is_authenticated and (
            self.request.user.is_staff or self.request.user.is_superuser
        )

    def handle_no_permission(self):
        """Redirect to admin login if not authenticated, otherwise 403."""
        if not self.request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(self.request.get_full_path())
        # User is authenticated but not admin - show 403
        return render(self.request, 'frontend/403.html', status=403)
