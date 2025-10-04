"""
Standalone Actions Mixin for Django Admin.

Provides convenient decorators and utilities for creating standalone action buttons
that work independently of selected items (not bulk actions).
"""

from typing import Callable, Optional, Any
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
import threading

from unfold.decorators import action as unfold_action
from unfold.enums import ActionVariant as UnfoldActionVariant
from django_cfg.modules.django_logging import get_logger
from ..models.action_models import ActionVariant


logger = get_logger("django_admin.mixins.standalone_actions")


def standalone_action(
    description: str,
    variant: Optional[ActionVariant] = None,
    icon: Optional[str] = None,
    url_path: Optional[str] = None,
    background: bool = False,
    success_message: Optional[str] = None,
    error_message: Optional[str] = None
):
    """
    Decorator for creating standalone action buttons.
    
    Args:
        description: Button text
        variant: Button style (ActionVariant enum)
        icon: Material icon name
        url_path: URL path for the action (auto-generated if not provided)
        background: Run action in background thread
        success_message: Success message template (can use {result} placeholder)
        error_message: Error message template (can use {error} placeholder)
    
    Usage:
        @standalone_action(
            description="Update Rates",
            variant=ActionVariant.SUCCESS,
            icon="sync",
            background=True,
            success_message="💱 Rates update started! Refresh in 2-3 minutes.",
            error_message="❌ Failed to start update: {error}"
        )
        def update_rates(self, request):
            # Your logic here
            call_command('manage_currencies', '--populate')
            return "Update completed"
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(self, request: Any) -> HttpResponse:
            try:
                if background:
                    # Run in background thread
                    def background_task():
                        try:
                            result = func(self, request)
                            logger.info(f"Background action {func.__name__} completed: {result}")
                        except Exception as e:
                            logger.error(f"Background action {func.__name__} failed: {e}")
                    
                    thread = threading.Thread(target=background_task)
                    thread.daemon = True
                    thread.start()
                    
                    # Show immediate success message
                    if success_message:
                        messages.success(request, success_message)
                    else:
                        messages.success(request, f"{description} started in background.")
                        
                else:
                    # Run synchronously
                    result = func(self, request)
                    
                    # Show success message
                    if success_message:
                        msg = success_message.format(result=result) if result else success_message
                        messages.success(request, msg)
                    else:
                        messages.success(request, f"{description} completed successfully.")
                
                logger.info(f"Standalone action {func.__name__} executed by {request.user.username}")
                
            except Exception as e:
                # Show error message
                if error_message:
                    msg = error_message.format(error=str(e))
                    messages.error(request, msg)
                else:
                    messages.error(request, f"❌ {description} failed: {str(e)}")
                
                logger.error(f"Standalone action {func.__name__} failed: {e}")
            
            # Always redirect back
            return redirect(request.META.get('HTTP_REFERER', '/admin/'))
        
        # Convert ActionVariant to UnfoldActionVariant
        unfold_variant = UnfoldActionVariant.DEFAULT
        if variant:
            variant_mapping = {
                ActionVariant.DEFAULT: UnfoldActionVariant.DEFAULT,
                ActionVariant.PRIMARY: UnfoldActionVariant.PRIMARY,
                ActionVariant.SUCCESS: UnfoldActionVariant.SUCCESS,
                ActionVariant.INFO: UnfoldActionVariant.INFO,
                ActionVariant.WARNING: UnfoldActionVariant.WARNING,
                ActionVariant.DANGER: UnfoldActionVariant.DANGER,
            }
            unfold_variant = variant_mapping.get(variant, UnfoldActionVariant.DEFAULT)
        
        # Auto-generate url_path if not provided
        final_url_path = url_path or func.__name__.replace('_', '-')
        
        # Apply unfold decorator
        decorator_kwargs = {
            'description': description,
            'variant': unfold_variant,
            'url_path': final_url_path
        }
        if icon:
            decorator_kwargs['icon'] = icon
        
        return unfold_action(**decorator_kwargs)(wrapper)
    
    return decorator


class StandaloneActionsMixin:
    """
    Mixin for Django admin classes that provides utilities for standalone actions.
    
    Usage:
        class MyAdmin(OptimizedModelAdmin, DisplayMixin, StandaloneActionsMixin, ModelAdmin):
            actions_list = ['update_data', 'sync_external']
            
            @standalone_action(
                description="Update Data",
                variant=ActionVariant.SUCCESS,
                icon="sync",
                background=True
            )
            def update_data(self, request):
                # Your update logic
                return "Data updated"
    """
    
    def get_standalone_actions(self):
        """Get list of standalone action method names."""
        return getattr(self, 'actions_list', [])
    
    def execute_background_task(self, task_func: Callable, *args, **kwargs):
        """
        Utility method to execute tasks in background.
        
        Args:
            task_func: Function to execute
            *args, **kwargs: Arguments for the function
        """
        def background_task():
            try:
                result = task_func(*args, **kwargs)
                logger.info(f"Background task {task_func.__name__} completed: {result}")
                return result
            except Exception as e:
                logger.error(f"Background task {task_func.__name__} failed: {e}")
                raise
        
        thread = threading.Thread(target=background_task)
        thread.daemon = True
        thread.start()
        return thread
    
    def send_admin_notification(self, request, message: str, level: str = 'INFO'):
        """
        Send notification to admin user.
        
        Args:
            request: Django request object
            message: Notification message
            level: Message level (SUCCESS, INFO, WARNING, ERROR)
        """
        level_mapping = {
            'SUCCESS': messages.SUCCESS,
            'INFO': messages.INFO,
            'WARNING': messages.WARNING,
            'ERROR': messages.ERROR,
        }
        
        django_level = level_mapping.get(level.upper(), messages.INFO)
        messages.add_message(request, django_level, message)
        
        logger.info(f"Admin notification sent to {request.user.username}: {message}")
