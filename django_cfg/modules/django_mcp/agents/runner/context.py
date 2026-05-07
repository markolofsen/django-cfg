"""AgentMessage and AgentContext dataclasses."""

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
