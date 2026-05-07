"""MCPAgentRunner — agentic loop using django_llm."""

import json
import logging
from typing import Any, Dict, Generator, List, Optional

from .context import AgentContext, AgentMessage

logger = logging.getLogger(__name__)


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
        try:
            config = context.config
            if hasattr(config, 'llm_model') and config.llm_model:
                return config.llm_model
        except (AttributeError, TypeError):
            pass

        try:
            client = self._get_llm_client()
            provider = client.provider_manager.primary_provider
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
        context.add_message("user", user_message)

        tools_def = self._build_tools_definition(context)
        system_prompt = self._build_system_prompt(context)

        client = self._get_llm_client()

        while context.can_call_tool():
            messages = context.to_llm_messages(system_prompt)

            try:
                response = client.chat_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools_def if tools_def else None,
                )
                if hasattr(response, 'choices'):
                    message = response.choices[0].message if response.choices else {}
                elif isinstance(response, dict):
                    message = response.get('choices', [{}])[0].get('message', {})
                else:
                    message = {}
            except Exception as e:
                logger.exception("LLM call failed")
                return f"Error: LLM call failed — {str(e)}"

            content = getattr(message, 'content', '') if hasattr(message, 'content') else (message.get('content', '') if isinstance(message, dict) else '')
            tool_calls = getattr(message, 'tool_calls', None) if hasattr(message, 'tool_calls') else (message.get('tool_calls') if isinstance(message, dict) else None)

            if tool_calls:
                context.add_message(
                    "assistant",
                    content or "",
                    tool_calls=tool_calls,
                )
                context.tool_call_count += len(tool_calls)

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
                if content:
                    context.add_message("assistant", content)
                return content

        return "Error: Max tool calls reached"

    def stream(
        self,
        user_message: str,
        context: AgentContext,
        model: str = "openai/gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> Generator[Dict[str, Any], None, None]:
        """
        Run agent loop yielding SSE-ready event dicts at each step.

        Event types:
            {"event": "tool_start",  "name": "<tool>", "args": {...}}
            {"event": "tool_result", "name": "<tool>", "result": "<text>"}
            {"event": "text",        "content": "<final answer>"}
            {"event": "error",       "message": "<msg>"}
            {"event": "done"}
        """
        context.add_message("user", user_message)
        tools_def = self._build_tools_definition(context)
        system_prompt = self._build_system_prompt(context)
        client = self._get_llm_client()

        while context.can_call_tool():
            messages = context.to_llm_messages(system_prompt)
            try:
                response = client.chat_completion(
                    messages=messages,
                    model=model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools_def if tools_def else None,
                )
                if hasattr(response, 'choices'):
                    message = response.choices[0].message if response.choices else {}
                elif isinstance(response, dict):
                    message = response.get('choices', [{}])[0].get('message', {})
                else:
                    message = {}
            except Exception as e:
                logger.exception("LLM call failed")
                yield {"event": "error", "message": f"LLM call failed — {str(e)}"}
                yield {"event": "done"}
                return

            content = getattr(message, 'content', '') if hasattr(message, 'content') else (message.get('content', '') if isinstance(message, dict) else '')
            tool_calls = getattr(message, 'tool_calls', None) if hasattr(message, 'tool_calls') else (message.get('tool_calls') if isinstance(message, dict) else None)

            if tool_calls:
                context.add_message("assistant", content or "", tool_calls=tool_calls)
                context.tool_call_count += len(tool_calls)

                for tc in tool_calls:
                    func = tc.get("function", {})
                    tool_name = func.get("name", "unknown")
                    try:
                        arguments = json.loads(func.get("arguments", "{}"))
                    except json.JSONDecodeError:
                        arguments = {}

                    yield {"event": "tool_start", "name": tool_name, "args": arguments}

                    tool_result = self._execute_tool(tool_name, arguments, context)
                    context.add_message("tool", tool_result, tool_call_id=tc.get("id"))

                    yield {"event": "tool_result", "name": tool_name, "result": tool_result}
            else:
                if content:
                    context.add_message("assistant", content)
                yield {"event": "text", "content": content or ""}
                yield {"event": "done"}
                return

        yield {"event": "error", "message": "Max tool calls reached"}
        yield {"event": "done"}


# Global instance
agent_runner = MCPAgentRunner()
