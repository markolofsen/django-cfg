"""
Base utilities and helper functions for callbacks.
"""

import logging
from typing import Dict, Any, List
from django.contrib.auth import get_user_model
from django.core.management import get_commands
import importlib

logger = logging.getLogger(__name__)


def get_available_commands():
    """Get all available Django management commands."""
    commands_dict = get_commands()
    commands_list = []
    
    for command_name, app_name in commands_dict.items():
        try:
            # Try to get command description
            if app_name == 'django_cfg':
                module_path = f'django_cfg.management.commands.{command_name}'
            else:
                module_path = f'{app_name}.management.commands.{command_name}'
            
            try:
                command_module = importlib.import_module(module_path)
                if hasattr(command_module, 'Command'):
                    command_class = command_module.Command
                    description = getattr(command_class, 'help', f'{command_name} command')
                else:
                    description = f'{command_name} command'
            except ImportError:
                description = f'{command_name} command'
            
            commands_list.append({
                'name': command_name,
                'app': app_name,
                'description': description,
                'is_core': app_name.startswith('django.'),
                'is_custom': app_name == 'django_cfg',
            })
        except Exception:
            # Skip problematic commands
            continue
    
    return commands_list


def get_commands_by_category():
    """Get commands categorized by type."""
    commands = get_available_commands()
    
    categorized = {
        'django_cfg': [],
        'django_core': [],
        'third_party': [],
        'project': [],
    }
    
    for cmd in commands:
        if cmd['app'] == 'django_cfg':
            categorized['django_cfg'].append(cmd)
        elif cmd['app'].startswith('django.'):
            categorized['django_core'].append(cmd)
        elif cmd['app'].startswith(('src.', 'api.', 'accounts.')):
            categorized['project'].append(cmd)
        else:
            categorized['third_party'].append(cmd)
    
    return categorized


def get_user_admin_urls():
    """Get admin URLs for user model."""
    try:
        User = get_user_model()
        
        app_label = User._meta.app_label
        model_name = User._meta.model_name
        
        return {
            'changelist': f'admin:{app_label}_{model_name}_changelist',
            'add': f'admin:{app_label}_{model_name}_add',
            'change': f'admin:{app_label}_{model_name}_change/{{id}}/',
            'delete': f'admin:{app_label}_{model_name}_delete/{{id}}/',
            'view': f'admin:{app_label}_{model_name}_view/{{id}}/',
        }
    except Exception:
        # Universal fallback - return admin index for all actions
        return {
            'changelist': 'admin:index',
            'add': 'admin:index',
            'change': 'admin:index',
            'delete': 'admin:index',
            'view': 'admin:index',
        }
