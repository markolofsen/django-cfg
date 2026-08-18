"""Management Command Execution Tool for MCP."""

import io
import sys
import logging
from typing import Any, Dict
from django.core.management import call_command

from django_cfg.modules.django_mcp.tools.base import MCPTool
from django_cfg.modules.django_mcp.services.context import MCPContext

logger = logging.getLogger(__name__)


class ExecuteCommandTool(MCPTool):
    """Execute a whitelisted Django management command."""

    name = "execute_command"
    description = "Execute a Django management command. Only whitelisted commands are allowed."
    input_schema = {
        "type": "object",
        "properties": {
            "command": {"type": "string", "description": "Command name (e.g., 'createsuperuser')"},
            "args": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Positional arguments",
            },
            "options": {
                "type": "object",
                "description": "Command options (e.g., {'verbosity': 2})",
            },
        },
        "required": ["command"],
    }

    def is_available(self, context: MCPContext) -> bool:
        """Hidden entirely unless this project whitelisted a command.

        Registration is unconditional because it happens at import, before there
        is a config to ask. Without this filter the tool is *listed* on every
        deployment — including the overwhelmingly common one that whitelisted
        nothing — where every call answers "not whitelisted". An agent reads
        that as a broken server rather than as a disabled feature, and a listed
        tool that never works is worse than an absent one.
        """
        commands = getattr(context.config, "commands", None)
        return bool(
            commands
            and getattr(commands, "enabled", False)
            and getattr(commands, "allowed_commands", [])
        )

    def execute(self, context: MCPContext, arguments: Dict[str, Any]) -> str:
        """Execute the execute_command tool."""
        command_name = arguments.get("command")

        if not command_name:
            return "Error: Command name is required"

        # Check if command is whitelisted
        if not context.config.is_command_allowed(command_name):
            return f"Error: Command '{command_name}' is not whitelisted for MCP execution"

        # Check user permissions (staff only for command execution)
        if not context.is_staff():
            return "Error: Only staff users can execute management commands"

        # Capture stdout/stderr
        stdout = io.StringIO()
        stderr = io.StringIO()
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        try:
            sys.stdout = stdout
            sys.stderr = stderr

            args = arguments.get("args", [])
            options = arguments.get("options", {})

            # Execute command
            call_command(command_name, *args, **options, stdout=stdout, stderr=stderr)

            output = stdout.getvalue()
            error_output = stderr.getvalue()

            result = {"command": command_name, "success": True}
            if output:
                result["output"] = output
            if error_output:
                result["stderr"] = error_output

            return str(result)

        except Exception as e:
            logger.exception(f"Error executing management command {command_name}")
            return f"Error executing command '{command_name}': {str(e)}"
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


# Create instance
execute_command_tool = ExecuteCommandTool()
