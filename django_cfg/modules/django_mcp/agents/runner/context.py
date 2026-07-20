"""AgentMessage and AgentContext dataclasses."""

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

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
    user: Any = None
    request: Any = None

    def add_message(self, role: str, content: str, **kwargs) -> None:
        self.messages.append(AgentMessage(role=role, content=content, **kwargs))

    def can_call_tool(self) -> bool:
        # Kept for callers that still consult it; the harness enforces its own
        # per-run ceiling (UsageLimits) inside run_agent_sync/stream_agent_run.
        return self.tool_call_count < self.max_tool_calls
