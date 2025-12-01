"""
SPA Path Resolver Utility

Resolves paths for Single Page Application (SPA) routing with multiple fallback strategies.
Used for Next.js static export where client-side routing handles unknown routes.
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def resolve_spa_path(base_dir: Path, path: str) -> str:
    """
    Resolve SPA path with multiple fallback strategies.
    
    Resolution order:
    1. Exact file match (e.g., script.js, style.css)
    2. path/index.html (e.g., private/centrifugo/index.html)
    3. path.html (e.g., private.html for /private)
    4. Fallback to root index.html for SPA routing
    
    Args:
        base_dir: Base directory for static files
        path: Requested path (e.g., '/private/centrifugo' or 'private/centrifugo')
        
    Returns:
        str: Resolved file path relative to base_dir
        
    Examples:
        >>> from pathlib import Path
        >>> base_dir = Path('/path/to/static')
        >>> resolve_spa_path(base_dir, '/private/centrifugo')
        'private/centrifugo/index.html'
        >>> resolve_spa_path(base_dir, '/private')
        'private.html'
        >>> resolve_spa_path(base_dir, '/_next/static/chunk.js')
        '_next/static/chunk.js'
        >>> resolve_spa_path(base_dir, '/unknown/route')
        'index.html'
    """
    file_path = base_dir / path
    
    # Remove trailing slash for processing
    path_normalized = path.lstrip('/').rstrip('/')
    
    # Strategy 1: Exact file match (for static assets like JS, CSS, images)
    if file_path.exists() and file_path.is_file():
        logger.debug(f"[SPA Router] Exact match: {path}")
        return path.lstrip('/')
    
    # Strategy 2: Try path/index.html (most common for SPA routes)
    index_in_dir = base_dir / path_normalized / 'index.html'
    if index_in_dir.exists():
        resolved_path = f"{path_normalized}/index.html"
        logger.debug(f"[SPA Router] Resolved {path} → {resolved_path}")
        return resolved_path
    
    # Strategy 3: Try with trailing slash + index.html
    if path.endswith('/'):
        index_path = path_normalized + '/index.html'
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
    normalized_file_path = base_dir / path_normalized
    if normalized_file_path.exists() and normalized_file_path.is_dir():
        # Try index.html in that directory
        index_in_existing_dir = normalized_file_path / 'index.html'
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
    return path.lstrip('/')

