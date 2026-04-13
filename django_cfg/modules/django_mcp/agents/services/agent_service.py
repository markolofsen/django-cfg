"""
MCP Agent Service

Handles agent execution logic separately from the view layer.
"""

import logging
from typing import Any, Dict, Optional

from django_cfg.modules.django_mcp.handlers.tools import tool_registry
from django_cfg.modules.django_mcp.agents.runner import AgentContext, agent_runner

logger = logging.getLogger(__name__)


class MCPAgentService:
    """
    Service for executing MCP agents.

    Usage:
        service = MCPAgentService()
        result = service.run_agent("How many users?", session_id="abc123")
    """

    def run_agent(
        self,
        message: str,
        session_id: str = "agent-session",
        model: Optional[str] = None,
        mcp_config: Any = None,
    ) -> Dict[str, Any]:
        """
        Execute an agent query.

        Args:
            message: User message
            session_id: Session identifier
            model: LLM model override (uses config default if None)
            mcp_config: MCP configuration for context

        Returns:
            dict with response, tool_calls, session_id
        """
        # Collect available tools
        tools = {}
        for tool in tool_registry.get_all_tools(None):
            tools[tool.name] = tool

        # Build agent context
        context = AgentContext(
            tools=tools,
            session_key=session_id,
            config=mcp_config,
        )

        # Determine model
        if not model and mcp_config:
            model = getattr(mcp_config, 'llm_model', 'openai/gpt-4.1-nano')

        # Execute agent
        response = agent_runner.run(message, context, model=model)

        return {
            "response": response,
            "tool_calls": context.tool_call_count,
            "session_id": context.session_key,
        }


# Global instance
agent_service = MCPAgentService()
