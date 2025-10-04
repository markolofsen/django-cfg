"""
Action decorator wrapper for Unfold integration.

Provides type-safe action decorators with consistent styling.
"""

from typing import Optional, Callable, Any
from functools import wraps
from unfold.decorators import action as unfold_action
from unfold.enums import ActionVariant as UnfoldActionVariant

from django_cfg.modules.django_logging import get_logger
from ..models.action_models import ActionVariant


logger = get_logger("django_admin.decorators.actions")

def action(
    description: str,
    variant: Optional[ActionVariant] = None,
    icon: Optional[str] = None,
    permissions: Optional[list] = None,
    url_path: Optional[str] = None,
    attrs: Optional[dict] = None
) -> Callable:
    """
    Enhanced action decorator with Django Admin Utilities integration.
    
    Args:
        description: Action description shown in admin
        variant: Action style variant (ActionVariant enum)
        icon: Material icon name
        permissions: Required permissions list
        url_path: URL path for standalone action buttons (creates separate button)
        attrs: Additional attributes for the action
    
    Usage:
        # Bulk action (works on selected items)
        @action(description="Activate items", variant=ActionVariant.SUCCESS)
        def activate_items(self, request, queryset):
            updated = queryset.update(is_active=True)
            self.message_user(request, f"Activated {updated} items.")
        
        # Standalone action button (url_path creates separate button)
        @action(
            description="Update Rates",
            variant=ActionVariant.SUCCESS,
            url_path="update-rates",
            icon="sync"
        )
        def update_rates(self, request):
            # Standalone action logic (no queryset parameter)
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, request: Any, *args, **kwargs) -> Any:
            try:
                # For url_path actions, there's no queryset parameter
                if url_path:
                    return func(self, request, *args, **kwargs)
                else:
                    # For bulk actions, pass queryset as second parameter
                    queryset = args[0] if args else kwargs.get('queryset')
                    return func(self, request, queryset, *args[1:], **kwargs)
            except Exception as e:
                # Log error and show user message
                logger.error(f"Error in action {func.__name__}: {e}")
                
                self.message_user(
                    request,
                    f"Error executing action: {str(e)}",
                    level='ERROR'
                )
        
        # Convert our ActionVariant to Unfold ActionVariant
        action_variant = None
        if variant:
            # Direct mapping since values are the same
            unfold_variant_mapping = {
                ActionVariant.DEFAULT: UnfoldActionVariant.DEFAULT,
                ActionVariant.PRIMARY: UnfoldActionVariant.PRIMARY,
                ActionVariant.SUCCESS: UnfoldActionVariant.SUCCESS,
                ActionVariant.INFO: UnfoldActionVariant.INFO,
                ActionVariant.WARNING: UnfoldActionVariant.WARNING,
                ActionVariant.DANGER: UnfoldActionVariant.DANGER,
            }
            action_variant = unfold_variant_mapping.get(variant, UnfoldActionVariant.DEFAULT)
        
        # Build decorator kwargs
        decorator_kwargs = {'description': description}
        if action_variant:
            decorator_kwargs['variant'] = action_variant
        if icon:
            decorator_kwargs['icon'] = icon
        if permissions:
            decorator_kwargs['permissions'] = permissions
        if url_path:
            decorator_kwargs['url_path'] = url_path
        if attrs:
            decorator_kwargs['attrs'] = attrs
        
        # Apply Unfold decorator
        return unfold_action(**decorator_kwargs)(wrapper)
    
    return decorator
