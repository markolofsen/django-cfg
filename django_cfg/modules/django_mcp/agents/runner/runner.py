"""MCPAgentRunner — agentic loop on the django_llm pydantic-ai harness.

This used to be a hand-rolled loop that called ``LLMClient.chat_completion`` and
duck-typed the provider's tool-call wire format itself
(``getattr(message, 'tool_calls', ...) if hasattr(...) else message.get(...)``) —
two near-identical copies, one for ``run`` and one for ``stream``. That is exactly
what pydantic-ai exists to own, and the django_llm agent plane now wraps it: this
class builds a ``pydantic_ai.Agent`` from the MCP tools and delegates the loop to the
harness's ``run_agent_sync`` / ``stream_agent_run``.

The PUBLIC surface is unchanged on purpose — ``run(...) -> str`` and
``stream(...) -> Generator[dict]`` keep their signatures and the SSE-event-dict
contract (``tool_start`` / ``tool_result`` / ``text`` / ``error`` / ``done``), so
neither caller (``MCPAgentService``, ``MCPAgentStreamView``) changes.
"""

import logging
from typing import Any, Dict, Generator, List

from asgiref.sync import async_to_sync

from django_cfg.modules.django_mcp.services.context import MCPContext

from ._deps import MCPAgentDeps
from ._harness_tools import build_harness_tools
from .context import AgentContext

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a helpful assistant integrated with a Django application "
    "via the Model Context Protocol (MCP). "
    "You have access to tools that can query models, introspect the application, "
    "and execute commands. "
    "Use tools when you need data. Always explain what you're doing. "
    "Be concise but thorough."
)


class MCPAgentRunner:
    """Runs agentic loops for MCP tools on the django_llm harness."""

    def _build_agent(self, context: AgentContext, model: str):
        """Assemble a pydantic-ai Agent over the MCP tools.

        The harness resolves the provider (OpenRouter first) from django_llm, so we
        no longer force it by hand — ``build_chat_model`` does what the old
        ``LLMClient(preferred_provider=OPENROUTER)`` did, in one place.
        """
        from pydantic_ai import Agent
        from django_cfg.modules.django_llm.agent.runtime.model_builder import (
            build_chat_model,
        )
        from django_cfg.modules.django_llm.agent.capabilities import (
            CapabilitySpec,
            build_capabilities,
        )

        return Agent(
            model=build_chat_model(model),
            deps_type=MCPAgentDeps,
            system_prompt=_SYSTEM_PROMPT,
            tools=build_harness_tools(context.tools),
            retries=2,
            # The always-on lenient-JSON defence, nothing situational — MCP tool
            # calls run over the same cheap models whose stringified-JSON args the
            # assembler's lenient capability exists to repair.
            capabilities=build_capabilities(CapabilitySpec()),
        )

    def _prior_history(self, context: AgentContext) -> List:
        """Convert the pre-seeded context history to harness ModelMessages.

        The view seeds ``context.messages`` from the Redis store BEFORE the new user
        message is added, so here it is exactly the prior turns.
        """
        from django_cfg.modules.django_llm.agent.runtime.history import (
            convert_history,
        )

        return convert_history(
            [{"role": m.role, "content": m.content} for m in context.messages]
        )

    def _build_deps(self, context: AgentContext) -> MCPAgentDeps:
        """Build the full context expected by every MCPTool.execute call."""
        return MCPAgentDeps(
            context=MCPContext(
                user=context.user,
                request=context.request,
                session_key=context.session_key,
                config=context.config,
            )
        )

    def run(
        self,
        user_message: str,
        context: AgentContext,
        model: str = "openai/gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> str:
        """Run the agent loop for a single user message; return the final text.

        ``temperature`` / ``max_tokens`` are accepted for signature compatibility;
        the harness owns model settings now (it deliberately omits temperature — the
        OpenRouter ``openai/`` slugs mis-classify as reasoning models and drop it).
        """
        from django_cfg.modules.django_llm.agent.runtime.runner import run_agent_sync

        agent = self._build_agent(context, model)
        history = self._prior_history(context)
        deps = self._build_deps(context)

        result = async_to_sync(run_agent_sync)(
            agent=agent,
            deps=deps,
            user_message=user_message,
            message_history=history,
            is_admin_chat=False,  # no HITL action-guard concept in django_mcp
            log_prefix="MCPAgent",
        )
        context.tool_call_count += len(result.called_tools)
        return result.text

    def stream(
        self,
        user_message: str,
        context: AgentContext,
        model: str = "openai/gpt-4o-mini",
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> Generator[Dict[str, Any], None, None]:
        """Run the loop, yielding SSE-ready event dicts.

        Contract preserved from the hand-rolled version:
            {"event": "tool_start",  "name": ..., "args": {...}}
            {"event": "tool_result", "name": ..., "result": "..."}
            {"event": "text",        "content": "<final answer>"}
            {"event": "error",       "message": "..."}
            {"event": "done"}

        The harness streams TEXT DELTAS; the old runner emitted a single ``text``
        event with the whole answer, and the view joins ``text`` chunks into the
        stored reply. We accumulate deltas and emit ONE ``text`` at the end so that
        contract — and the persisted history — is byte-for-byte what it was.
        """
        agent = self._build_agent(context, model)
        history = self._prior_history(context)
        deps = self._build_deps(context)

        yield from _drain_stream(agent, deps, user_message, history)


def _drain_stream(agent, deps, user_message, history) -> Generator[Dict[str, Any], None, None]:
    """Bridge the harness's async event stream to a sync generator of MCP dicts.

    The harness ``stream_agent_run`` is an async iterator; a Django
    ``StreamingHttpResponse`` consumes a SYNC generator. We pump the async stream on
    an event loop and re-yield each mapped dict. Text deltas are buffered and flushed
    as one ``text`` event just before ``done`` (the old contract).
    """
    import asyncio

    from django_cfg.modules.django_llm.agent.runtime.streaming import (
        StreamRunResult,
        stream_agent_run,
    )
    from django_cfg.modules.django_llm.agent.bus.events import (
        DoneEvent,
        ErrorEvent,
        TextDeltaEvent,
        ToolCallEvent,
        ToolResultEvent,
    )

    text_parts: list[str] = []

    async def _agen():
        out = StreamRunResult()
        async for ev in stream_agent_run(
            agent=agent,
            deps=deps,
            user_message=user_message,
            message_history=history,
            deferred_tool_results=None,
            is_admin_chat=True,  # expose tool events — MCP admin stream shows the trace
            out=out,
            log_prefix="MCPAgent",
        ):
            yield ev

    # Pump the async generator from sync code, mapping each harness event to the
    # django_mcp dict shape. A private loop keeps this independent of any ambient one.
    loop = asyncio.new_event_loop()
    try:
        agen = _agen()
        while True:
            try:
                ev = loop.run_until_complete(agen.__anext__())
            except StopAsyncIteration:
                break

            if isinstance(ev, TextDeltaEvent):
                if ev.delta:
                    text_parts.append(ev.delta)
            elif isinstance(ev, ToolCallEvent):
                yield {"event": "tool_start", "name": ev.tool, "args": ev.args}
            elif isinstance(ev, ToolResultEvent):
                yield {"event": "tool_result", "name": ev.tool, "result": ev.result}
            elif isinstance(ev, ErrorEvent):
                yield {"event": "error", "message": ev.error}
            elif isinstance(ev, DoneEvent):
                pass  # text flushed below, then our own done
    finally:
        # ``_agen`` owns pydantic-ai's async event stream. Close it while its
        # private loop is still alive; otherwise Python schedules ``aclose()``
        # after the loop has already been closed and emits
        # ``Task was destroyed while it is pending``. In the SSE path that can
        # also discard the final text event, leaving the browser with an empty
        # assistant message.
        loop.run_until_complete(agen.aclose())
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()

    yield {"event": "text", "content": "".join(text_parts)}
    yield {"event": "done"}


# Global instance
agent_runner = MCPAgentRunner()
