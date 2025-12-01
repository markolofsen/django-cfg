"""
HTML Link Fixer Utility

Fixes absolute URLs in HTML files after Next.js static export extraction.
Replaces absolute URLs like 'http://localhost:3000/admin/...' 
with correct basePath-aware paths like '/cfg/admin/admin/...'.

This fixes the issue where Next.js static export generates absolute URLs
that don't work when served from Django with basePath.
"""

import logging
from pathlib import Path
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


def get_base_path_for_app(app_name: str) -> str:
    """
    Get basePath for app based on app_name.
    
    For 'admin' app, basePath is '/cfg/admin'.
    Can be extended for other apps in the future.
    
    Args:
        app_name: Name of the app (e.g., 'admin')
        
    Returns:
        str: Base path for the app (e.g., '/cfg/admin')
        
    Examples:
        >>> get_base_path_for_app('admin')
        '/cfg/admin'
        >>> get_base_path_for_app('docs')
        '/cfg/docs'
    """
    if app_name == 'admin':
        return '/cfg/admin'
    # Default: assume /cfg/{app_name}
    return f'/cfg/{app_name}'


def _is_localhost_url(url: str) -> bool:
    """Check if URL is a localhost URL that should be fixed."""
    if not url or not isinstance(url, str):
        return False
    url_lower = url.lower()
    return any(host in url_lower for host in ['localhost', '127.0.0.1', '0.0.0.0'])


def _fix_url(url: str, base_path: str) -> str:
    """
    Fix a single URL by replacing localhost absolute URLs with basePath-aware paths.
    
    Args:
        url: URL to fix (e.g., 'http://localhost:3000/admin/dashboard')
        base_path: Base path to prepend (e.g., '/cfg/admin')
        
    Returns:
        Fixed URL or original URL if no fix needed
    """
    if not url or not isinstance(url, str):
        return url
    
    # Skip if already starts with basePath
    if url.startswith(base_path):
        return url
    
    # Skip if not a localhost URL
    if not _is_localhost_url(url):
        return url
    
    # Parse URL to extract path
    if url.startswith('http://') or url.startswith('https://'):
        # Extract path from absolute URL
        # Example: http://localhost:3000/admin/dashboard -> /admin/dashboard
        try:
            # Find the path part after host:port
            parts = url.split('/', 3)
            if len(parts) >= 4:
                path = '/' + parts[3]
            elif len(parts) == 3:
                path = '/'
            else:
                return url
            
            # Handle special case: http://localhost:3000/https://... (double protocol)
            if path.startswith('/https://') or path.startswith('/http://'):
                # Extract the real URL (remove leading slash)
                return path[1:]
            
            # Replace with basePath + path
            return f'{base_path}{path}'
        except Exception:
            return url
    elif url.startswith('//'):
        # Protocol-relative URL: //localhost:3000/admin/dashboard
        try:
            parts = url.split('/', 3)
            if len(parts) >= 4:
                path = '/' + parts[3]
            else:
                return url
            return f'{base_path}{path}'
        except Exception:
            return url
    
    return url


def fix_html_links_after_extraction(base_dir: Path, app_name: str) -> int:
    """
    Fix absolute URLs in HTML files after ZIP extraction using BeautifulSoup.
    
    Replaces absolute URLs like 'http://localhost:3000/admin/...' 
    with correct basePath-aware paths like '/cfg/admin/admin/...'.
    
    This fixes the issue where Next.js static export generates absolute URLs
    that don't work when served from Django with basePath.
    
    Args:
        base_dir: Directory where files were extracted
        app_name: Name of the app (e.g., 'admin')
        
    Returns:
        int: Number of HTML files that were fixed
        
    Examples:
        >>> from pathlib import Path
        >>> base_dir = Path('/path/to/extracted/files')
        >>> fixed_count = fix_html_links_after_extraction(base_dir, 'admin')
        >>> print(f"Fixed {fixed_count} HTML files")
    """
    base_path = get_base_path_for_app(app_name)
    
    html_files = list(base_dir.rglob('*.html'))
    fixed_count = 0
    
    for html_file in html_files:
        try:
            content = html_file.read_text(encoding='utf-8')
            original_content = content
            
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            changed = False
            
            # Fix href, src, action attributes in all tags
            url_attrs = ['href', 'src', 'action', 'data-href', 'data-src']
            for tag in soup.find_all(True):  # Find all tags
                for attr in url_attrs:
                    if attr in tag.attrs:
                        original_url = tag[attr]
                        fixed_url = _fix_url(original_url, base_path)
                        if fixed_url != original_url:
                            tag[attr] = fixed_url
                            changed = True
            
            # Fix content attributes in meta tags (og:image, twitter:image, etc.)
            for meta_tag in soup.find_all('meta'):
                if 'content' in meta_tag.attrs:
                    original_url = meta_tag['content']
                    fixed_url = _fix_url(original_url, base_path)
                    if fixed_url != original_url:
                        meta_tag['content'] = fixed_url
                        changed = True
            
            # Fix URLs in script tags (JSON strings)
            for script_tag in soup.find_all('script'):
                if script_tag.string:
                    script_content = script_tag.string
                    # Simple regex replacement for JSON URLs in script content
                    import re
                    pattern = r'"(authenticatedPath|unauthenticatedPath|url|href|src|image|og:image|twitter:image)":"(https?://[^"]+)"'
                    
                    def replace_json_url(match):
                        key = match.group(1)
                        url = match.group(2)
                        fixed_url = _fix_url(url, base_path)
                        return f'"{key}":"{fixed_url}"'
                    
                    new_script_content = re.sub(pattern, replace_json_url, script_content, flags=re.IGNORECASE)
                    if new_script_content != script_content:
                        script_tag.string = new_script_content
                        changed = True
            
            # Only write if content changed
            if changed:
                # Preserve original formatting as much as possible
                new_content = str(soup)
                html_file.write_text(new_content, encoding='utf-8')
                fixed_count += 1
                logger.debug(f"[{app_name}] Fixed links in {html_file.relative_to(base_dir)}")
                
        except Exception as e:
            logger.warning(f"[{app_name}] Failed to fix links in {html_file}: {e}")
    
    if fixed_count > 0:
        logger.info(f"[{app_name}] Fixed links in {fixed_count} HTML file(s) with basePath={base_path}")
    
    return fixed_count

