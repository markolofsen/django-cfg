"""
Django CFG Commands API Views

Web interface for executing Django management commands.
"""

import json
import subprocess
import threading
import time
import logging
from typing import Dict, Any, List
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import user_passes_test
from django.core.management import get_commands, call_command
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


def is_superuser(user):
    """Check if user is superuser."""
    return user.is_authenticated and user.is_superuser


@require_http_methods(["GET"])
@user_passes_test(is_superuser)
def list_commands_view(request):
    """
    List all available Django management commands.
    
    Returns:
        JSON response with categorized commands
    """
    try:
        # Get all available commands
        commands_dict = get_commands()
        
        # Categorize commands
        categorized_commands = {
            "django_cfg": [],
            "django_core": [],
            "third_party": [],
            "project": [],
        }
        
        for command_name, app_name in commands_dict.items():
            command_info = {
                "name": command_name,
                "app": app_name,
                "description": _get_command_description(command_name),
            }
            
            if app_name == "django_cfg":
                categorized_commands["django_cfg"].append(command_info)
            elif app_name.startswith("django."):
                categorized_commands["django_core"].append(command_info)
            elif app_name.startswith(("src.", "api.", "accounts.")):
                categorized_commands["project"].append(command_info)
            else:
                categorized_commands["third_party"].append(command_info)
        
        return JsonResponse({
            "status": "success",
            "commands": categorized_commands,
            "total_commands": len(commands_dict),
            "timestamp": timezone.now().isoformat(),
        })
        
    except Exception as e:
        logger.error(f"Error listing commands: {e}")
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "timestamp": timezone.now().isoformat(),
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
@user_passes_test(is_superuser)
def execute_command_view(request):
    """
    Execute a Django management command and stream output in real-time.
    
    Expected JSON payload:
    {
        "command": "command_name",
        "args": ["arg1", "arg2"],
        "options": {"--option": "value"}
    }
    
    Returns:
        StreamingHttpResponse with Server-Sent Events format
    """
    try:
        # Parse request data
        data = json.loads(request.body)
        command_name = data.get("command")
        args = data.get("args", [])
        options = data.get("options", {})
        
        if not command_name:
            return JsonResponse({
                "status": "error",
                "error": "Command name is required",
            }, status=400)
        
        # Validate command exists
        available_commands = get_commands()
        if command_name not in available_commands:
            return JsonResponse({
                "status": "error",
                "error": f"Command '{command_name}' not found",
                "available_commands": list(available_commands.keys()),
            }, status=400)
        
        # Security check - block dangerous commands
        dangerous_commands = [
            "flush", "sqlflush", "dbshell", "shell", "shell_plus",
            "reset_db", "migrate", "makemigrations", "loaddata"
        ]
        
        if command_name in dangerous_commands:
            return JsonResponse({
                "status": "error", 
                "error": f"Command '{command_name}' is not allowed via API for security reasons",
                "suggestion": "Use django_cfg management commands instead: show_config, test_email",
            }, status=403)
        
        # Create streaming response generator
        def stream_command_execution():
            """Generator that yields command output in SSE format."""
            start_time = time.time()
            
            # Send start event
            yield f"data: {json.dumps({'type': 'start', 'command': command_name, 'args': args})}\n\n"
            
            try:
                # Execute command with subprocess for real-time output
                import subprocess
                import sys
                import os
                
                # Find Django project root and manage.py
                from django.conf import settings
                
                # Try to find manage.py in project root
                if hasattr(settings, 'BASE_DIR'):
                    project_root = settings.BASE_DIR
                    manage_py_path = os.path.join(project_root, 'manage.py')
                else:
                    # Fallback: search for manage.py
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    while current_dir != '/':
                        manage_py_path = os.path.join(current_dir, 'manage.py')
                        if os.path.exists(manage_py_path):
                            project_root = current_dir
                            break
                        current_dir = os.path.dirname(current_dir)
                    else:
                        raise Exception("Could not find manage.py")
                
                # Build command
                cmd = [sys.executable, manage_py_path, command_name] + args
                
                # Add options to command
                for key, value in options.items():
                    if key.startswith('--'):
                        cmd.append(key)
                        if value is not True:  # Boolean flags don't need values
                            cmd.append(str(value))
                    else:
                        cmd.append(f"--{key}")
                        if value is not True:
                            cmd.append(str(value))
                
                # Start process
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    universal_newlines=True,
                    bufsize=1,
                    cwd=project_root
                )
                
                # Stream output line by line
                for line in iter(process.stdout.readline, ''):
                    if line:
                        line = line.rstrip('\n\r')
                        yield f"data: {json.dumps({'type': 'output', 'line': line})}\n\n"
                
                # Wait for process to complete
                return_code = process.wait()
                execution_time = time.time() - start_time
                
                # Send completion event
                yield f"data: {json.dumps({'type': 'complete', 'return_code': return_code, 'execution_time': round(execution_time, 2)})}\n\n"
                
                # Log command execution
                logger.info(
                    f"Command executed: {command_name} {' '.join(args)} "
                    f"by user {request.user.username} in {execution_time:.2f}s with exit code {return_code}"
                )
                
            except Exception as cmd_error:
                execution_time = time.time() - start_time
                
                logger.error(
                    f"Command failed: {command_name} {' '.join(args)} "
                    f"by user {request.user.username}: {cmd_error}"
                )
                
                # Send error event
                yield f"data: {json.dumps({'type': 'error', 'error': str(cmd_error), 'execution_time': round(execution_time, 2)})}\n\n"
        
        # Return streaming response
        response = StreamingHttpResponse(
            stream_command_execution(),
            content_type='text/event-stream'
        )
        response['Cache-Control'] = 'no-cache'
        response['X-Accel-Buffering'] = 'no'  # Disable nginx buffering
        
        return response
        
    except json.JSONDecodeError:
        return JsonResponse({
            "status": "error",
            "error": "Invalid JSON payload",
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in execute_command_view: {e}")
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "timestamp": timezone.now().isoformat(),
        }, status=500)


@require_http_methods(["GET"])
@user_passes_test(is_superuser)
def command_help_view(request, command_name):
    """
    Get help information for a specific command.
    
    Args:
        command_name: Name of the Django management command
    """
    try:
        available_commands = get_commands()
        
        if command_name not in available_commands:
            return JsonResponse({
                "status": "error",
                "error": f"Command '{command_name}' not found",
            }, status=404)
        
        # Get command help
        help_text = _get_command_help(command_name)
        
        return JsonResponse({
            "status": "success",
            "command": command_name,
            "app": available_commands[command_name],
            "help": help_text,
            "timestamp": timezone.now().isoformat(),
        })
        
    except Exception as e:
        logger.error(f"Error getting help for command {command_name}: {e}")
        return JsonResponse({
            "status": "error",
            "error": str(e),
            "timestamp": timezone.now().isoformat(),
        }, status=500)


def _get_command_description(command_name: str) -> str:
    """Get short description for a command."""
    try:
        from django.core.management import load_command_class
        command_class = load_command_class(get_commands()[command_name], command_name)
        return getattr(command_class, 'help', f'Django management command: {command_name}')
    except Exception:
        return f'Django management command: {command_name}'


def _get_command_help(command_name: str) -> str:
    """Get full help text for a command."""
    try:
        from django.core.management import load_command_class
        command_class = load_command_class(get_commands()[command_name], command_name)
        
        # Create command instance to get help
        command_instance = command_class()
        parser = command_instance.create_parser('manage.py', command_name)
        
        return parser.format_help()
    except Exception as e:
        return f"Could not retrieve help for command '{command_name}': {str(e)}"
