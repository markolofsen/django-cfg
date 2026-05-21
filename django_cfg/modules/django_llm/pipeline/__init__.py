"""
Pipeline — decorator layers around the LLM client.

The reliability core: a classified retry helper, a circuit breaker, a
model-cascade router, and a client-side rate limiter. The cost layer adds
per-attempt spend tracking, a wasted-spend metric, and a billed-but-unusable
cost-leak alert.

Host-agnostic — depends only on the ``core`` error taxonomy, the stdlib,
and (for the Telegram alert) the ``_integration`` host seam.
"""

from .circuit_breaker import CircuitBreaker, CircuitState
from .cost import CostEvent, CostTracker, alert_wasted_call
from .ratelimit import RateLimiter
from .retry import compute_backoff, retry_call
from .router import ModelRouter

__all__ = [
    "CircuitBreaker",
    "CircuitState",
    "CostEvent",
    "CostTracker",
    "alert_wasted_call",
    "compute_backoff",
    "retry_call",
    "ModelRouter",
    "RateLimiter",
]
