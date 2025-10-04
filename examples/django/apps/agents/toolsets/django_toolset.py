"""
Core Django toolset with common Django operations.
"""

import logging
from typing import Dict, Any, List, Optional
from pydantic_ai.toolsets import AbstractToolset
from pydantic_ai import RunContext

from ..core.dependencies import DjangoDeps

logger = logging.getLogger(__name__)


class DjangoToolset(AbstractToolset[DjangoDeps]):
    """
    Core Django toolset providing common Django operations.
    
    Includes tools for:
    - User management
    - Session handling
    - Settings access
    - Logging
    """
    
    @property
    def id(self) -> str:
        return "django_core"
    
    async def get_user_info(self, ctx: RunContext[DjangoDeps]) -> Dict[str, Any]:
        """Get current user information."""
        user = ctx.deps.user
        
        return {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_active': user.is_active,
            'is_staff': user.is_staff,
            'is_superuser': user.is_superuser,
            'date_joined': user.date_joined.isoformat() if user.date_joined else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
        }
    
    async def get_user_permissions(self, ctx: RunContext[DjangoDeps]) -> List[str]:
        """Get user permissions."""
        user = ctx.deps.user
        
        # Get all permissions
        permissions = []
        
        # Direct user permissions
        user_perms = await user.user_permissions.aall()
        async for perm in user_perms:
            permissions.append(f"{perm.content_type.app_label}.{perm.codename}")
        
        # Group permissions
        groups = await user.groups.aall()
        async for group in groups:
            group_perms = await group.permissions.aall()
            async for perm in group_perms:
                perm_str = f"{perm.content_type.app_label}.{perm.codename}"
                if perm_str not in permissions:
                    permissions.append(perm_str)
        
        return sorted(permissions)
    
    async def check_permission(self, ctx: RunContext[DjangoDeps], permission: str) -> bool:
        """Check if user has specific permission."""
        user = ctx.deps.user
        
        # Handle superuser
        if user.is_superuser:
            return True
        
        # Check permission
        return user.has_perm(permission)
    
    async def get_session_data(self, ctx: RunContext[DjangoDeps], key: Optional[str] = None) -> Any:
        """Get session data."""
        session_data = ctx.deps.session_data
        
        if key:
            return session_data.get(key)
        
        return session_data
    
    async def log_message(
        self, 
        ctx: RunContext[DjangoDeps], 
        message: str, 
        level: str = "info",
        extra_data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Log message with user context."""
        user = ctx.deps.user
        
        # Prepare log data
        log_data = {
            'user_id': user.id,
            'username': user.username,
            'message': message,
        }
        
        if extra_data:
            log_data.update(extra_data)
        
        # Log based on level
        if level.lower() == 'debug':
            logger.debug(message, extra=log_data)
        elif level.lower() == 'info':
            logger.info(message, extra=log_data)
        elif level.lower() == 'warning':
            logger.warning(message, extra=log_data)
        elif level.lower() == 'error':
            logger.error(message, extra=log_data)
        elif level.lower() == 'critical':
            logger.critical(message, extra=log_data)
        else:
            logger.info(message, extra=log_data)
        
        return True
    
    async def get_django_setting(self, ctx: RunContext[DjangoDeps], setting_name: str) -> Any:
        """Get Django setting value (safe settings only)."""
        from django.conf import settings
        
        # Whitelist of safe settings to expose
        safe_settings = {
            'DEBUG',
            'TIME_ZONE',
            'LANGUAGE_CODE',
            'USE_TZ',
            'USE_I18N',
            'MEDIA_URL',
            'STATIC_URL',
            'DEFAULT_AUTO_FIELD',
        }
        
        if setting_name not in safe_settings:
            raise ValueError(f"Setting '{setting_name}' is not in the safe settings list")
        
        return getattr(settings, setting_name, None)
    
    async def get_app_config(self, ctx: RunContext[DjangoDeps], app_label: str) -> Dict[str, Any]:
        """Get Django app configuration."""
        from django.apps import apps
        
        try:
            app_config = apps.get_app_config(app_label)
            
            return {
                'name': app_config.name,
                'label': app_config.label,
                'verbose_name': app_config.verbose_name,
                'path': str(app_config.path),
                'models_module': app_config.models_module.__name__ if app_config.models_module else None,
            }
        except Exception as e:
            logger.error(f"Failed to get app config for '{app_label}': {e}")
            return {}
    
    async def format_datetime(
        self, 
        ctx: RunContext[DjangoDeps], 
        datetime_str: str, 
        format_str: str = "%Y-%m-%d %H:%M:%S"
    ) -> str:
        """Format datetime string using Django's timezone handling."""
        from django.utils import timezone
        from django.utils.dateparse import parse_datetime
        
        try:
            # Parse datetime
            dt = parse_datetime(datetime_str)
            if not dt:
                return datetime_str
            
            # Convert to user's timezone if available
            if hasattr(ctx.deps, 'request') and ctx.deps.request:
                # Use request timezone if available
                dt = timezone.localtime(dt)
            
            return dt.strftime(format_str)
        except Exception as e:
            logger.error(f"Failed to format datetime '{datetime_str}': {e}")
            return datetime_str
    
    async def get_model_info(self, ctx: RunContext[DjangoDeps], app_label: str, model_name: str) -> Dict[str, Any]:
        """Get Django model information."""
        from django.apps import apps
        
        try:
            model = apps.get_model(app_label, model_name)
            
            # Get field information
            fields = []
            for field in model._meta.fields:
                fields.append({
                    'name': field.name,
                    'type': field.__class__.__name__,
                    'null': field.null,
                    'blank': field.blank,
                    'help_text': field.help_text,
                })
            
            return {
                'app_label': model._meta.app_label,
                'model_name': model._meta.model_name,
                'verbose_name': str(model._meta.verbose_name),
                'verbose_name_plural': str(model._meta.verbose_name_plural),
                'db_table': model._meta.db_table,
                'fields': fields,
                'field_count': len(fields),
            }
        except Exception as e:
            logger.error(f"Failed to get model info for '{app_label}.{model_name}': {e}")
            return {}
