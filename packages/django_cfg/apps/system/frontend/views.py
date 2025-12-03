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

from .utils import (
    fix_html_links_after_extraction,
    resolve_spa_path,
    find_precompressed_file,
    should_inject_jwt,
    inject_jwt_tokens,
    convert_file_response_to_http_response,
    ensure_frontend_asset,
)

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

        # Check if ZIP exists, try to download if not
        if not zip_path.exists():
            logger.info(f"[{app_name}] ZIP not found locally, attempting auto-download...")
            if not ensure_frontend_asset(app_name):
                logger.error(f"[{app_name}] ZIP not found and download failed: {zip_path}")
                return False
            logger.info(f"[{app_name}] ZIP downloaded successfully")

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

                # Fix HTML links after extraction
                # fix_html_links_after_extraction(base_dir, app_name)

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
    Serve Next.js static build files with automatic JWT token injection and precompression support.

    Features:
    - Serves Next.js static export files like a static file server
    - Smart ZIP extraction: compares ZIP metadata (size + mtime) with marker file
    - Automatically injects JWT tokens for authenticated users (HTML only)
    - **Precompression support**: Automatically serves .br or .gz files if available
    - Handles Next.js client-side routing (.html fallback)
    - Automatically serves index.html for directory paths
    - X-Frame-Options exempt to allow embedding in iframes

    Compression Strategy:
    - Brotli (.br) preferred over Gzip (.gz) - ~5-15% better compression
    - Automatically detects browser support via Accept-Encoding header
    - Skips compression for HTML files (JWT injection requires uncompressed content)
    - Only serves precompressed files, no runtime compression

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

    Compression examples:
    - _app.js (br supported)   → _app.js.br + Content-Encoding: br
    - _app.js (gzip supported) → _app.js.gz + Content-Encoding: gzip
    - _app.js (no support)     → _app.js (uncompressed)
    - index.html               → index.html (never compressed, needs JWT injection)
    """

    app_name = 'admin'

    def get(self, request, path=''):
        """Serve static files from Next.js build with JWT injection and compression support."""
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
        path = resolve_spa_path(base_dir, path)

        # For HTML files, remove conditional GET headers to force full response
        # This allows JWT token injection (can't inject into 304 Not Modified responses)
        is_html_file = path.endswith('.html')
        if is_html_file and request.user.is_authenticated:
            request.META.pop('HTTP_IF_MODIFIED_SINCE', None)
            request.META.pop('HTTP_IF_NONE_MATCH', None)

        # Try to serve precompressed file if browser supports it
        accept_encoding = request.META.get('HTTP_ACCEPT_ENCODING', '')
        compressed_path, encoding = find_precompressed_file(base_dir, path, accept_encoding)
        if compressed_path:
            logger.debug(f"[Compression] Serving {encoding} for {path}")
            response = serve(request, compressed_path, document_root=str(base_dir))
            response['Content-Encoding'] = encoding
            # Remove Content-Length as it's incorrect for compressed content
            if 'Content-Length' in response:
                del response['Content-Length']
        else:
            # Serve the static file normally
            response = serve(request, path, document_root=str(base_dir))

        # Convert FileResponse to HttpResponse for HTML files to enable JWT injection
        if isinstance(response, FileResponse):
            converted_response = convert_file_response_to_http_response(response, request)
            if converted_response:
                response = converted_response

        # Inject JWT tokens for authenticated users on HTML responses
        if should_inject_jwt(request, response):
            inject_jwt_tokens(request, response)

        # Disable caching for HTML files (prevent Cloudflare/browser caching)
        if is_html_file:
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response


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
