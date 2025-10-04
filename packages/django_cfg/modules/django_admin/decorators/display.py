"""
Display decorator wrapper for Unfold integration.

Provides type-safe display decorators with our admin utilities.
"""

from typing import Optional, Callable, Any, Union
from functools import wraps
from django.utils.safestring import SafeString, mark_safe
from unfold.decorators import display as unfold_display
from django_cfg.modules.django_logging import get_logger

logger = get_logger('django_admin.decorators.display')

def display(
    function: Optional[Callable] = None,
    *,
    boolean: Optional[bool] = None,
    image: Optional[bool] = None,
    ordering: Optional[str] = None,
    description: Optional[str] = None,
    empty_value: Optional[str] = None,
    dropdown: Optional[bool] = None,
    label: Union[bool, str, dict, None] = None,
    header: Optional[bool] = None
) -> Callable:
    """
    Enhanced display decorator with Django Admin Utilities integration.
    
    This decorator wraps unfold.decorators.display with additional features:
    - Automatic HTML safety detection and marking
    - Empty value handling with customizable fallback
    - Error handling with logging
    
    Args:
        function: Function to decorate (for direct usage)
        boolean: Show as boolean icon (True/False icons)
        image: Show as image thumbnail
        ordering: Field name for sorting
        description: Column header text
        empty_value: Default value for empty/None fields
        dropdown: Show as dropdown menu
        label: Show as label badge (bool, str, or dict for styling)
        header: Show as header with avatar
    
    Usage:
        @display(description="User", header=True)
        def user_display(self, obj):
            return self.display_user_with_avatar(obj, 'user')
        
        @display(description="Status", label=True)
        def status_display(self, obj):
            return self.display_status_auto(obj, 'status')
            
        @display(description="Has Embedding", boolean=True)
        def has_embedding_display(self, obj):
            return obj.has_embedding
            
        @display(description="Avatar", image=True)
        def avatar_display(self, obj):
            return obj.avatar.url if obj.avatar else None
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, obj: Any) -> Any:
            try:
                result = func(self, obj)
                
                # Handle empty values (use our default if unfold's empty_value is None)
                if result is None or result == "":
                    return empty_value if empty_value is not None else "—"
                
                # Auto-mark HTML as safe if it contains HTML tags
                if isinstance(result, str) and ('<' in result and '>' in result):
                    return mark_safe(result)
                
                # SafeString is already safe
                if isinstance(result, SafeString):
                    return result
                
                return result
            except Exception as e:
                # Log error and return safe fallback
                logger.error(f"Error in display method {func.__name__}: {e}")
                return empty_value if empty_value is not None else "—"
        
        # Apply Unfold decorator with all parameters
        return unfold_display(
            function=None,  # We handle the function ourselves
            boolean=boolean,
            image=image,
            ordering=ordering,
            description=description,
            empty_value=empty_value,
            dropdown=dropdown,
            label=label,
            header=header
        )(wrapper)
    
    # Support both @display and @display(...) usage
    if function is not None:
        # Direct usage: @display
        return decorator(function)
    else:
        # Parametrized usage: @display(...)
        return decorator
