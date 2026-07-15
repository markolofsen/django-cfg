"""Return type for ChatAgent.run_sync()."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from django_cfg.modules.django_llm.agent.runtime.cost import RunCost


@dataclass(frozen=True, slots=True)
class AgentSyncResult:
    """Typed return type of a synchronous agent run.

    Attributes:
        text: Final assistant text output.
        pending_token: ``ct_<hex>`` confirmation token when the agent
            called ``propose_send_customer_message``, otherwise ``None``.
        called_tools: Ordered list of tool names the model actually called
            this turn. Used by Telegram handler to append a tool trace.
        cost: What the run cost — token split + priced USD (``None`` when it
            could not be priced). ``None`` on the whole run only when usage was
            unavailable (a timeout/error before any model response). The sync path
            used to discard usage entirely; this is where it now lands.
    """

    text: str
    pending_token: str | None
    called_tools: list[str] = field(default_factory=list)
    cost: Optional["RunCost"] = None
