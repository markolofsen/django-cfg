"""
Utility functions for Django Unfold integration.
"""

from typing import Callable, Union
import logging
from django.http import HttpRequest

logger = logging.getLogger(__name__)


def auto_resolve_url(url_name_or_path: str) -> Union[str, Callable[[HttpRequest], str]]:
    """
    Automatically convert URL names to resolver functions.
    
    If the string doesn't start with '/' or 'http', treat it as a URL name
    and return a function that will resolve it at runtime.
    
    Args:
        url_name_or_path: URL name (e.g., 'admin:app_model_changelist') or direct path
        
    Returns:
        Direct URL string or callable that resolves URL name
    """
    if not url_name_or_path or url_name_or_path.startswith(("/", "http")):
        # It's already a direct URL, return as is
        return url_name_or_path
    
    # It's a URL name, create a resolver function
    url_name = url_name_or_path
    
    def resolve_url(request: HttpRequest) -> str:
        try:
            from django.urls import reverse
            from django.urls.exceptions import NoReverseMatch
            resolved = reverse(url_name)
            logger.debug(f"Auto-resolved URL: {url_name} -> {resolved}")
            return resolved
        except (NoReverseMatch, Exception) as e:
            logger.warning(f"Could not resolve URL '{url_name}': {e}")
            return url_name
    
    return resolve_url


def get_link_for_unfold(link: Union[str, Callable]) -> Union[str, Callable]:
    """
    Get the link in the format expected by Unfold.
    
    Args:
        link: Direct URL string or resolver function
        
    Returns:
        Link in format expected by Unfold (string or callable)
    """
    if callable(link):
        # It's a resolver function, Unfold will call it with request
        return link
    else:
        # It's a direct URL
        return link


# Convenience functions for common admin URLs
def admin_changelist(app_label: str, model_name: str) -> Callable[[HttpRequest], str]:
    """Create URL resolver for admin changelist."""
    return auto_resolve_url(f"admin:{app_label}_{model_name}_changelist")


def admin_add(app_label: str, model_name: str) -> Callable[[HttpRequest], str]:
    """Create URL resolver for admin add form."""
    return auto_resolve_url(f"admin:{app_label}_{model_name}_add")


def admin_change(app_label: str, model_name: str, obj_id: str = "0") -> Callable[[HttpRequest], str]:
    """Create URL resolver for admin change form."""
    return auto_resolve_url(f"admin:{app_label}_{model_name}_change/{obj_id}/")


def admin_model_url(model_class, action: str = "changelist") -> Callable[[HttpRequest], str]:
    """
    Create URL resolver for any Django model admin action.
    
    Args:
        model_class: Django model class
        action: Admin action ('changelist', 'add', 'change', etc.)
        
    Returns:
        URL resolver function
    """
    try:
        app_label = model_class._meta.app_label
        model_name = model_class._meta.model_name
        return auto_resolve_url(f"admin:{app_label}_{model_name}_{action}")
    except Exception:
        # Fallback to admin index
        return auto_resolve_url("admin:index")


def user_admin_url() -> Callable[[HttpRequest], str]:
    """Create URL resolver for current AUTH_USER_MODEL admin changelist."""
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        return admin_model_url(User, "changelist")
    except Exception:
        # Fallback to admin index
        return auto_resolve_url("admin:index")


def create_navigation_item(title: str, icon: str, model_class=None, url_name: str = None, direct_url: str = None):
    """
    Create NavigationItem with automatic URL resolution.
    
    Args:
        title: Navigation item title
        icon: Material icon name
        model_class: Django model class (for admin URLs)
        url_name: Django URL name
        direct_url: Direct URL path
        
    Returns:
        NavigationItem with proper URL resolution
    """
    from .models.navigation import NavigationItem
    
    if model_class:
        # Use model admin changelist
        link = admin_model_url(model_class, "changelist")
    elif url_name:
        # Use URL name
        link = auto_resolve_url(url_name)
    elif direct_url:
        # Use direct URL
        link = direct_url
    else:
        # Fallback
        link = "#"
    
    return NavigationItem(title=title, icon=icon, link=link)
