"""OpenRouter provider-routing policy — choose WHICH upstream provider serves a
model, typed and in one place.

On OpenRouter a single model slug (e.g. ``moonshotai/kimi-k2.6``) is served by
many providers (Moonshot, Together, Fireworks, DeepInfra …) at different speed,
price, and uptime. The ``provider`` object in the request body picks among them.
This module is the SINGLE source of truth for that policy so chat, coding, and
the fusion council all route the same way instead of each hand-rolling a dict.

The default (:data:`BALANCED`) deliberately sets NO ``sort``: OpenRouter's own
default load-balancer already does the cost/speed/health balance we want — it
deprioritizes a provider with a recent outage, then picks among the cheapest
weighted by 1/price², keeping the rest as fallbacks. Pinning ``sort`` would
DISABLE that balance and collapse to one axis. So "balanced" = let the
load-balancer run, just cap the price ceiling. Aggressive-speed presets
(:data:`THROUGHPUT`) opt into ``sort="throughput"`` explicitly — that's for
coding / interactive turns where latency dominates and we accept losing the
price balance.

Slow upstreams are handled a layer up (the latency scorer's ``latency_ok`` gate
drops known-slow MODELS before dispatch); this object tunes provider choice
WITHIN a chosen model.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

#: OpenRouter's documented sort axes. Setting any of these DISABLES the default
#: price+uptime load-balancer and routes purely on that axis (providers tried in
#: order). ``None`` (the balanced default) keeps the load-balancer on.
ProviderSort = Literal["price", "throughput", "latency"]


@dataclass(frozen=True)
class ProviderPolicy:
    """Typed OpenRouter ``provider`` routing preferences.

    Only non-None fields are rendered, so the default policy emits a minimal
    object. Maps 1:1 to OpenRouter's ``provider`` request field.
    """

    #: Sort axis. None = keep OpenRouter's balanced load-balancer (recommended
    #: default). "throughput"/"latency"/"price" each pin one axis and disable it.
    sort: ProviderSort | None = None
    #: Per-provider failover within the model. OpenRouter defaults this to True;
    #: we keep it explicit so a policy reads as a complete intent.
    allow_fallbacks: bool | None = True
    #: Price ceiling — drop providers above it. Shape mirrors OpenRouter:
    #: ``{"prompt": <usd_per_1m>, "completion": <usd_per_1m>}``. Caps cost
    #: WITHOUT disabling the balancer (unlike ``sort="price"``).
    max_price: dict[str, float] | None = None
    #: Hard allow/deny lists + preference order (provider slugs). Usually unset.
    order: tuple[str, ...] | None = None
    only: tuple[str, ...] | None = None
    ignore: tuple[str, ...] | None = None
    #: Route only to providers that honor all request params (e.g. json_schema).
    require_parameters: bool | None = None

    def to_dict(self) -> dict[str, Any]:
        """Render as the OpenRouter ``provider`` object (omitting None fields)."""
        out: dict[str, Any] = {}
        if self.sort is not None:
            out["sort"] = self.sort
        if self.allow_fallbacks is not None:
            out["allow_fallbacks"] = self.allow_fallbacks
        if self.max_price is not None:
            out["max_price"] = dict(self.max_price)
        if self.order is not None:
            out["order"] = list(self.order)
        if self.only is not None:
            out["only"] = list(self.only)
        if self.ignore is not None:
            out["ignore"] = list(self.ignore)
        if self.require_parameters is not None:
            out["require_parameters"] = self.require_parameters
        return out

    def merge_into(self, caller: dict[str, Any] | None) -> dict[str, Any]:
        """Merge this policy UNDER a caller-supplied ``provider`` dict.

        The caller wins every key it sets (explicit request beats default
        policy); this policy only fills what the caller left out. Returns a new
        dict suitable for ``extra_body["provider"]``.
        """
        merged = self.to_dict()
        if caller:
            merged.update(caller)
        return merged


#: The default policy: NO sort (keep OpenRouter's cost/speed/health balance) +
#: explicit fallbacks. Used for ordinary chat and the fusion council unless a
#: preset overrides. "Balanced price/speed" per product intent.
BALANCED = ProviderPolicy()

#: Speed-first: pin ``sort="throughput"`` so OpenRouter routes to the fastest
#: provider of the model. Trades the price balance for latency — for coding /
#: interactive turns where a slow node bottlenecks the whole experience.
THROUGHPUT = ProviderPolicy(sort="throughput")

#: Cheapest-first: pin ``sort="price"``. For bulk / background work where speed
#: doesn't matter and every cent does.
CHEAPEST = ProviderPolicy(sort="price")
