"""
MCP Agent Runner

Uses django_llm's LLMClient to run agentic loops with MCP tools.
No external dependencies — reuses existing django_llm infrastructure.
"""

import json
import logging
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class AgentMessage:
    """Single message in agent conversation history."""
    role: str  # "user", "assistant", "tool"
    content: str
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


@dataclass
class AgentContext:
    """Shared context for agent execution."""
    messages: List[AgentMessage] = field(default_factory=list)
    tool_call_count: int = 0
    max_tool_calls: int = 10
    tools: Dict[str, Any] = field(default_factory=dict)
    session_key: str = ""
    config: Any = None

    def add_message(self, role: str, content: str, **kwargs) -> None:
        self.messages.append(AgentMessage(role=role, content=content, **kwargs))

    def can_call_tool(self) -> bool:
        return self.tool_call_count < self.max_tool_calls

    def to_llm_messages(self, system_prompt: str) -> List[Dict[str, Any]]:
        """Convert to django_llm message format."""
        messages = [{"role": "system", "content": system_prompt}]
        for msg in self.messages:
            if msg.role == "tool" and msg.tool_call_id:
                messages.append({
                    "role": "tool",
                    "content": msg.content,
                    "tool_call_id": msg.tool_call_id,
                })
            elif msg.tool_calls:
                messages.append({
                    "role": "assistant",
                    "content": msg.content,
                    "tool_calls": msg.tool_calls,
                })
            else:
                messages.append({"role": msg.role, "content": msg.content})
        return messages


class MCPAgentRunner:
    """
    Runs agentic loops using django_llm's LLMClient.

    Flow:
    1. Send user message to LLM with tool definitions
    2. LLM may return tool calls
    3. Execute tools and return results to LLM
    4. Repeat until LLM returns final text response
    """

    def __init__(self):
        self._llm_client = None

    def _get_llm_client(self):
        """Lazy-load django_llm client, forced to use OpenRouter."""
        if self._llm_client is None:
            from django_cfg.modules.django_llm import LLMClient
            from django_cfg.modules.django_llm.llm.providers import LLMProvider
            # Force OpenRouter to avoid OpenAI quota issues
            self._llm_client = LLMClient(preferred_provider=LLMProvider.OPENROUTER)
        return self._llm_client

    def _get_default_model(self, context: AgentContext) -> str:
        """Get default model from MCP config or fallback to LLM client's primary provider."""
        # First check MCP config for explicit model
        try:
            config = context.config
            if hasattr(config, 'llm_model') and config.llm_model:
                return config.llm_model
        except (AttributeError, TypeError):
            pass

        # Fallback to django_llm's primary provider
        try:
            client = self._get_llm_client()
            provider = client.provider_manager.primary_provider
            # Get default model for this provider
            if provider:
                return provider.get("model", "openai/gpt-4.1-nano")
        except Exception:
            pass

        return "openai/gpt-4.1-nano"

    def _build_tools_definition(self, context: AgentContext) -> List[Dict[str, Any]]:
        """Build OpenAI-compatible tool definitions from MCP tools."""
        tools = []
        for name, tool in context.tools.items():
            tools.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool.description,
                    "parameters": tool.input_schema,
                }
            })
        return tools

    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any], context: AgentContext) -> str:
        """Execute an MCP tool and return result."""
        tool = context.tools.get(tool_name)
        if not tool:
            return f"Error: Tool '{tool_name}' not found"

        try:
            return tool.execute(context.config, arguments)
        except Exception as e:
            logger.exception(f"Tool execution error: {tool_name}")
            return f"Error executing {tool_name}: {str(e)}"

    def _build_system_prompt(self, context: AgentContext) -> str:
        """Build system prompt for the agent."""
        return (
            "You are a helpful assistant integrated with a Django application "
            "via the Model Context Protocol (MCP). "
            "You have access to tools that can query models, introspect the application, "
            "and execute commands. "
            "Use tools when you need data. Always explain what you're doing. "
            "Be concise but thorough."
        )

    def run(
        self,
        user_message: str,
        context: AgentContext,
        model: str = "openai/gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """
        Run the agent loop for a single user message.

        Returns the final assistant response text.
        """
        # Add user message to context
        context.add_message("user", user_message)

        # Get tools definition
        tools_def = self._build_tools_definition(context)
        system_prompt = self._build_system_prompt(context)

        client = self._get_llm_client()

        # Main agentic loop
        while context.can_call_tool():
            # Build messages for LLM
            messages = context.to_llm_messages(system_prompt)

            # Call LLM via django_llm
            try:
                response = client.chat_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools_def if tools_def else None,
                )
                # Handle both dict and Pydantic model responses
                if hasattr(response, 'choices'):
                    # Pydantic model (django_llm)
                    message = response.choices[0].message if response.choices else {}
                elif isinstance(response, dict):
                    message = response.get('choices', [{}])[0].get('message', {})
                else:
                    message = {}
            except Exception as e:
                logger.exception("LLM call failed")
                return f"Error: LLM call failed — {str(e)}"

            # Parse response
            content = getattr(message, 'content', '') if hasattr(message, 'content') else (message.get('content', '') if isinstance(message, dict) else '')
            tool_calls = getattr(message, 'tool_calls', None) if hasattr(message, 'tool_calls') else (message.get('tool_calls') if isinstance(message, dict) else None)

            if tool_calls:
                # LLM wants to call tools
                context.add_message(
                    "assistant",
                    content or "",
                    tool_calls=tool_calls,
                )
                context.tool_call_count += len(tool_calls)

                # Execute each tool call
                for tc in tool_calls:
                    func = tc.get("function", {})
                    tool_name = func.get("name", "unknown")
                    try:
                        arguments = json.loads(func.get("arguments", "{}"))
                    except json.JSONDecodeError:
                        arguments = {}

                    tool_result = self._execute_tool(tool_name, arguments, context)

                    context.add_message(
                        "tool",
                        tool_result,
                        tool_call_id=tc.get("id"),
                    )

            else:
                # Final text response
                if content:
                    context.add_message("assistant", content)
                return content

        return "Error: Max tool calls reached"


# Global instance
agent_runner = MCPAgentRunner()
