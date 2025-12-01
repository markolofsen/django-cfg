"""
Compression Utility

Handles detection and serving of precompressed files (.br, .gz).
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def find_precompressed_file(base_dir: Path, path: str, accept_encoding: str) -> tuple[str | None, str | None]:
    """
    Find and return precompressed file (.br or .gz) if available and supported by browser.
    
    Brotli (.br) is preferred over Gzip (.gz) as it provides better compression.
    
    Args:
        base_dir: Base directory for static files
        path: Requested file path
        accept_encoding: Accept-Encoding header value (e.g., 'br, gzip, deflate')
        
    Returns:
        tuple: (compressed_path, encoding) if precompressed file found and supported,
               (None, None) otherwise
               
    Examples:
        >>> from pathlib import Path
        >>> base_dir = Path('/path/to/static')
        >>> find_precompressed_file(base_dir, '_app.js', 'br, gzip')
        ('_app.js.br', 'br')
        >>> find_precompressed_file(base_dir, '_app.js', 'gzip')
        ('_app.js.gz', 'gzip')
        >>> find_precompressed_file(base_dir, 'index.html', 'br, gzip')
        (None, None)  # HTML files are never compressed
    """
    accept_encoding_lower = accept_encoding.lower()
    
    # Check if browser supports brotli (preferred) or gzip
    supports_br = 'br' in accept_encoding_lower
    supports_gzip = 'gzip' in accept_encoding_lower
    
    if not (supports_br or supports_gzip):
        return None, None
    
    # Don't compress HTML files - we need to inject JWT tokens
    # JWT injection requires modifying content, which is incompatible with compression
    if path.endswith('.html'):
        return None, None
    
    # Build full file path
    file_path = base_dir / path
    
    # Check if original file exists (safety check)
    if not file_path.exists() or not file_path.is_file():
        return None, None
    
    # Try Brotli first (better compression, ~5-15% smaller than gzip)
    if supports_br:
        br_path = f"{path}.br"
        br_file = base_dir / br_path
        if br_file.exists() and br_file.is_file():
            return br_path, 'br'
    
    # Fallback to Gzip
    if supports_gzip:
        gz_path = f"{path}.gz"
        gz_file = base_dir / gz_path
        if gz_file.exists() and gz_file.is_file():
            return gz_path, 'gzip'
    
    # No precompressed file found or not supported
    return None, None

