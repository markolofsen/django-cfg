"""
Frontend utilities for Next.js static build processing.
"""

from .html_link_fixer import get_base_path_for_app, fix_html_links_after_extraction
from .spa_path_resolver import resolve_spa_path
from .compression import find_precompressed_file
from .jwt_injection import should_inject_jwt, inject_jwt_tokens, convert_file_response_to_http_response
from .downloader import download_frontend_asset, ensure_frontend_asset, get_asset_path

__all__ = [
    'get_base_path_for_app',
    'fix_html_links_after_extraction',
    'resolve_spa_path',
    'find_precompressed_file',
    'should_inject_jwt',
    'inject_jwt_tokens',
    'convert_file_response_to_http_response',
    # Downloader
    'download_frontend_asset',
    'ensure_frontend_asset',
    'get_asset_path',
]

