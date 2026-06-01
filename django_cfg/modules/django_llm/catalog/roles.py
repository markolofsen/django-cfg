"""Model roles and per-role verdicts.

A role is *what a model is for*. The catalog grades every model
per role rather than crowning one "best" model — because the same
model earns a different verdict depending on the job: Qwen3.5-Flash is
fine for cheap CLASSIFY, a P99 runaway for EXTRACTION, and a
narrate-after-first-call failure for TOOL_CHAT.
"""

from __future__ import annotations

from enum import Enum


class ModelRole(str, Enum):
    """What a model is being asked to do."""

    EXTRACTION = "extraction"   # structured JSON from text — hot path, determinism over IQ
    TOOL_CHAT = "tool_chat"     # agentic chat with multi-tool chains
    CLASSIFY = "classify"       # cheap structured classification, no tools
    ESCALATION = "escalation"   # hard semantics / customer-facing — quality over cost
    VISION = "vision"           # multimodal image understanding


class Verdict(str, Enum):
    """How a model performs in a given role."""

    GOOD = "good"        # benchmarked or production-proven for this role
    OK = "ok"            # works, with caveats — see ModelTraits.issues
    AVOID = "avoid"      # known to fail this role
    UNKNOWN = "unknown"  # not yet assessed
