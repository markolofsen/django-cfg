"""
Django CFG Commands API Views

Web interface for executing Django management commands.
"""

import json
import logging
import time

from django.contrib.auth.decorators import user_passes_test
from django.core.management import call_command, get_commands
from django.http import JsonResponse, StreamingHttpResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


def is_staff_user(user):
    """Check if user is staff member."""
    return user.is_authenticated and user.is_staff


@require_http_methods(["GET"])
@user_passes_test(is_staff_user)
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
                **_get_command_metadata(command_name, app_name),
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
@user_passes_test(is_staff_user)
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

        # Security check - use same filtering as dashboard
        from django_cfg.modules.django_unfold.callbacks.base import is_command_allowed

        app_name = available_commands.get(command_name)
        if not is_command_allowed(command_name, app_name):
            return JsonResponse({
                "status": "error",
                "error": f"Command '{command_name}' is not allowed via web interface for security reasons",
                "suggestion": "Only safe django_cfg commands and whitelisted utilities can be executed via web.",
            }, status=403)

        # Create streaming response generator
        def stream_command_execution():
            """Generator that yields command output in SSE format."""
            start_time = time.time()

            # Send start event
            yield f"data: {json.dumps({'type': 'start', 'command': command_name, 'args': args})}\n\n"

            try:
                # Capture command output using StringIO
                import sys
                from io import StringIO

                # Create output buffer
                output_buffer = StringIO()

                # Redirect stdout/stderr to buffer
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = output_buffer
                sys.stderr = output_buffer

                try:
                    # Execute Django command directly using call_command
                    call_command(command_name, *args, **options)
                    return_code = 0
                except Exception as e:
                    # Command execution failed
                    output_buffer.write(f"\nError: {str(e)}\n")
                    return_code = 1
                finally:
                    # Restore stdout/stderr
                    sys.stdout = old_stdout
                    sys.stderr = old_stderr

                # Get all output
                output = output_buffer.getvalue()

                # Stream output line by line
                if output:
                    for line in output.split('\n'):
                        if line.strip():
                            yield f"data: {json.dumps({'type': 'output', 'line': line})}\n\n"

                execution_time = time.time() - start_time

                # Send completion event
                yield f"data: {json.dumps({'type': 'complete', 'return_code': return_code, 'execution_time': round(execution_time, 2)})}\n\n"

                # Log command execution
                if return_code == 0:
                    logger.info(
                        f"Command executed: {command_name} {' '.join(args)} "
                        f"by user {request.user.username} in {execution_time:.2f}s"
                    )
                else:
                    logger.error(
                        f"Command failed: {command_name} {' '.join(args)} "
                        f"by user {request.user.username} in {execution_time:.2f}s"
                    )

            except Exception as cmd_error:
                execution_time = time.time() - start_time

                logger.error(
                    f"Command failed: {command_name} {' '.join(args)} "
                    f"by user {request.user.username}: {cmd_error}"
                )

                # Send error event
                yield f"data: {json.dumps({'type': 'error', 'message': str(cmd_error), 'execution_time': round(execution_time, 2)})}\n\n"

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
@user_passes_test(is_staff_user)
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


def _get_command_metadata(command_name: str, app_name: str) -> dict:
    """
    Get security metadata for a command.

    Returns:
        Dict with web_executable, requires_input, is_destructive, is_allowed
    """
    try:
        from django.core.management import load_command_class
        from django_cfg.apps.api.dashboard.services.commands_security import is_command_allowed, get_command_risk_level

        command_instance = load_command_class(app_name, command_name)

        return {
            'web_executable': getattr(command_instance, 'web_executable', None),
            'requires_input': getattr(command_instance, 'requires_input', None),
            'is_destructive': getattr(command_instance, 'is_destructive', None),
            'is_allowed': is_command_allowed(command_name, app_name),
            'risk_level': get_command_risk_level(command_name, app_name),
        }
    except Exception as e:
        logger.debug(f"Could not load metadata for {command_name}: {e}")
        return {
            'web_executable': None,
            'requires_input': None,
            'is_destructive': None,
            'is_allowed': False,
            'risk_level': 'unknown',
        }


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
