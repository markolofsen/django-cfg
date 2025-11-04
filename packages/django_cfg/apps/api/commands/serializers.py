"""
Django CFG Commands API Serializers.
"""

from rest_framework import serializers


class CommandMetadataSerializer(serializers.Serializer):
    """
    Serializer for command metadata.

    Includes security attributes from our base classes:
    - web_executable: Can be executed via web interface
    - requires_input: Requires interactive user input
    - is_destructive: Modifies or deletes data
    - is_allowed: Passes security checks
    - risk_level: Security risk assessment
    """

    web_executable = serializers.BooleanField(
        allow_null=True,
        help_text="Whether command can be executed via web interface"
    )
    requires_input = serializers.BooleanField(
        allow_null=True,
        help_text="Whether command requires interactive user input"
    )
    is_destructive = serializers.BooleanField(
        allow_null=True,
        help_text="Whether command modifies or deletes data"
    )
    is_allowed = serializers.BooleanField(
        help_text="Whether command passes security checks for web execution"
    )
    risk_level = serializers.ChoiceField(
        choices=['safe', 'caution', 'dangerous', 'unknown'],
        help_text="Security risk level assessment"
    )


class CommandSerializer(serializers.Serializer):
    """
    Serializer for Django management commands.

    Returns command information including:
    - Basic info (name, app, description)
    - Security metadata (web_executable, requires_input, is_destructive)
    - Execution status (is_allowed, risk_level)
    """

    name = serializers.CharField(
        help_text="Command name"
    )
    app = serializers.CharField(
        help_text="Django app that provides this command"
    )
    description = serializers.CharField(
        help_text="Short description of what the command does"
    )

    # Security metadata - flattened for easier API consumption
    web_executable = serializers.BooleanField(
        allow_null=True,
        help_text="Can be executed via web interface"
    )
    requires_input = serializers.BooleanField(
        allow_null=True,
        help_text="Requires interactive user input"
    )
    is_destructive = serializers.BooleanField(
        allow_null=True,
        help_text="Modifies or deletes data"
    )
    is_allowed = serializers.BooleanField(
        help_text="Passes security checks"
    )
    risk_level = serializers.ChoiceField(
        choices=['safe', 'caution', 'dangerous', 'unknown'],
        help_text="Security risk level"
    )


class CommandListResponseSerializer(serializers.Serializer):
    """
    Serializer for list commands API response.

    Returns categorized commands:
    - django_cfg: Custom django-cfg commands
    - django_core: Django built-in commands
    - third_party: Third-party app commands
    - project: Project-specific commands
    """

    status = serializers.ChoiceField(
        choices=['success', 'error'],
        help_text="Response status"
    )
    commands = serializers.DictField(
        child=serializers.ListField(child=CommandSerializer()),
        help_text="Categorized command lists"
    )
    total_commands = serializers.IntegerField(
        help_text="Total number of commands available"
    )
    timestamp = serializers.DateTimeField(
        help_text="Response timestamp"
    )


class CommandExecutionRequestSerializer(serializers.Serializer):
    """
    Serializer for command execution requests.
    """

    command = serializers.CharField(
        required=True,
        help_text="Name of the command to execute"
    )
    args = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=list,
        help_text="Positional arguments for the command"
    )
    options = serializers.DictField(
        required=False,
        default=dict,
        help_text="Named options for the command (e.g., {'--verbose': True})"
    )


class CommandHelpResponseSerializer(serializers.Serializer):
    """
    Serializer for command help API response.
    """

    status = serializers.ChoiceField(
        choices=['success', 'error'],
        help_text="Response status"
    )
    command = serializers.CharField(
        help_text="Command name"
    )
    app = serializers.CharField(
        help_text="Django app"
    )
    help = serializers.CharField(
        help_text="Full help text from command --help"
    )
    timestamp = serializers.DateTimeField(
        help_text="Response timestamp"
    )
