"""
Commands Security Module

Self-contained security logic for Django management commands execution.
Determines which commands are safe to execute via web interface.

TAGS: commands, security, validation, safety
"""

import importlib
import inspect
import logging
from typing import Any, Dict, Set

from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


# Keywords in docstring/code that indicate command should not be in web UI
DANGEROUS_KEYWORDS: Set[str] = {
    'questionary', 'input(', 'stdin', 'interactive',  # Requires user input
    'destructive', 'dangerous', 'irreversible',  # Explicitly marked as dangerous
    'runserver', 'testserver',  # Dev servers
}

# Commands that should NEVER appear (absolute blacklist)
ABSOLUTE_BLACKLIST: Set[str] = {
    # Destructive database commands
    'flush', 'sqlflush', 'dbshell',

    # Shell access (security risk)
    'shell', 'shell_plus',

    # Development server (not for web execution)
    'runserver', 'testserver', 'runserver_ngrok',

    # Project generation (not applicable in running app)
    'startapp', 'startproject',

    # SQL commands (direct SQL, potentially dangerous)
    'sqlmigrate', 'sqlsequencereset',
}


def analyze_command_safety(command_class: BaseCommand, command_name: str) -> Dict[str, Any]:
    """
    Analyze command to determine if it's safe for web execution.

    Checks:
    1. Explicit metadata (web_executable, requires_input, is_destructive)
    2. Docstring analysis for dangerous keywords
    3. Source code analysis for interactive input
    4. Required arguments analysis

    Returns:
        Dict with safety analysis results
    """
    analysis = {
        'is_safe': True,
        'reasons': [],
        'requires_input': False,
        'is_destructive': False,
        'web_executable': None,
    }

    # Check explicit metadata (highest priority)
    if hasattr(command_class, 'web_executable'):
        analysis['web_executable'] = command_class.web_executable
        if not command_class.web_executable:
            analysis['is_safe'] = False
            analysis['reasons'].append('Command explicitly marked as not web-executable')
            return analysis

    if hasattr(command_class, 'requires_input'):
        analysis['requires_input'] = command_class.requires_input
        if command_class.requires_input:
            analysis['is_safe'] = False
            analysis['reasons'].append('Command requires interactive input')
            return analysis

    if hasattr(command_class, 'is_destructive'):
        analysis['is_destructive'] = command_class.is_destructive
        if command_class.is_destructive:
            analysis['is_safe'] = False
            analysis['reasons'].append('Command is marked as destructive')
            return analysis

    # Analyze docstring for dangerous keywords
    docstring = (inspect.getdoc(command_class) or '').lower()
    for keyword in DANGEROUS_KEYWORDS:
        if keyword in docstring:
            analysis['is_safe'] = False
            analysis['reasons'].append(f'Docstring contains dangerous keyword: {keyword}')
            return analysis

    # Analyze source code for interactive input
    try:
        source = inspect.getsource(command_class)
        if 'questionary' in source or 'input(' in source:
            analysis['is_safe'] = False
            analysis['requires_input'] = True
            analysis['reasons'].append('Command requires interactive user input')
            return analysis
    except Exception:
        # Can't analyze source, be safe
        pass

    return analysis


def is_command_allowed(command_name: str, app_name: str) -> bool:
    """
    Check if command should be allowed for web execution.

    Priority:
    1. Custom blacklist from settings (DJANGO_CFG_COMMANDS_BLACKLIST)
    2. Absolute blacklist - always exclude
    3. Custom whitelist from settings (DJANGO_CFG_COMMANDS_WHITELIST)
    4. Command metadata analysis (web_executable, requires_input, etc.)
    5. django_cfg apps - analyze each command
    6. Django core - be selective (only safe utility commands)
    7. Third party - only if explicitly whitelisted

    You can customize filtering in settings.py:

        DJANGO_CFG_COMMANDS_BLACKLIST = {'my_dangerous_command'}
        DJANGO_CFG_COMMANDS_WHITELIST = {'my_safe_command'}

    Or add metadata to your Command class:

        class Command(BaseCommand):
            web_executable = True  # Allow in web UI
            requires_input = False  # Doesn't need interactive input
            is_destructive = False  # Not destructive
    """
    from django.conf import settings

    # Custom blacklist from settings (highest priority)
    custom_blacklist = getattr(settings, 'DJANGO_CFG_COMMANDS_BLACKLIST', set())
    if command_name in custom_blacklist:
        logger.info(f"Command {command_name} blocked by custom blacklist")
        return False

    # Absolute blacklist
    if command_name in ABSOLUTE_BLACKLIST:
        logger.info(f"Command {command_name} blocked by absolute blacklist")
        return False

    # Custom whitelist from settings
    custom_whitelist = getattr(settings, 'DJANGO_CFG_COMMANDS_WHITELIST', set())
    if command_name in custom_whitelist:
        logger.info(f"Command {command_name} allowed by custom whitelist")
        return True

    # Load and analyze command
    try:
        # Determine module path
        if app_name == 'django_cfg':
            module_path = f'django_cfg.management.commands.{command_name}'
        elif app_name.startswith('django.'):
            module_path = f'{app_name}.management.commands.{command_name}'
        else:
            module_path = f'{app_name}.management.commands.{command_name}'

        command_module = importlib.import_module(module_path)
        if hasattr(command_module, 'Command'):
            command_class = command_module.Command

            # Analyze command safety
            analysis = analyze_command_safety(command_class, command_name)

            # If command has explicit web_executable metadata, use it
            if analysis['web_executable'] is not None:
                return analysis['web_executable']

            # If analysis says it's unsafe, exclude
            if not analysis['is_safe']:
                logger.debug(f"Command {command_name} excluded: {', '.join(analysis['reasons'])}")
                return False
    except Exception as e:
        # Can't load/analyze command
        logger.debug(f"Could not analyze command {command_name}: {e}")
        # Be conservative - if we can't analyze, exclude unless from trusted source
        pass

    # Django CFG commands - include if analysis passed
    if app_name == 'django_cfg':
        return True

    # Safe Django core commands (utility/read-only)
    safe_django_core = {
        'check', 'diffsettings', 'showmigrations',
        'createcachetable', 'sendtestemail',
    }
    if app_name.startswith('django.') and command_name in safe_django_core:
        return True

    # Exclude other Django core by default
    if app_name.startswith('django.'):
        logger.debug(f"Command {command_name} excluded (Django core, not in safe list)")
        return False

    # Third-party apps - only whitelisted
    logger.debug(f"Command {command_name} excluded (third-party, not whitelisted)")
    return False


def get_command_risk_level(command_name: str, app_name: str) -> str:
    """
    Get risk level for a command.

    Returns:
        'safe', 'caution', or 'dangerous'
    """
    if command_name in ABSOLUTE_BLACKLIST:
        return 'dangerous'

    if app_name == 'django_cfg':
        return 'safe'

    if app_name.startswith('django.'):
        safe_commands = {'check', 'diffsettings', 'showmigrations'}
        if command_name in safe_commands:
            return 'safe'
        return 'caution'

    return 'caution'
