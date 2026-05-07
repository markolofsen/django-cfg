"""MCP agent serializers."""

from rest_framework import serializers


class AgentChatRequestSerializer(serializers.Serializer):
    """Request serializer for MCP agent chat endpoint."""
    message = serializers.CharField(
        required=True,
        help_text="User message to the agent",
    )
    model = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="LLM model override (e.g., 'anthropic/claude-3.5-haiku')",
    )
    session_id = serializers.CharField(
        required=False,
        default="agent-session",
        help_text="Session identifier for continuity",
    )


class AgentChatResponseSerializer(serializers.Serializer):
    """Response serializer for MCP agent chat endpoint."""
    response = serializers.CharField(help_text="Agent's text response")
    tool_calls = serializers.IntegerField(help_text="Number of tools called")
    session_id = serializers.CharField(help_text="Session identifier")
