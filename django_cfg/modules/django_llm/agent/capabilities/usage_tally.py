"""Count the tokens of every finished model request into a `UsageTally`, so a run that ends early still books what it spent.

Always on in `kind_source`. It reads `response.usage` after each request and never changes the response; a failing hook costs a
count, never the run.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic_ai.capabilities import AbstractCapability

from django_cfg.modules.django_llm.agent.runtime.tally import UsageTally

log = logging.getLogger(__name__)


class UsageTallyCapability(AbstractCapability[Any]):
    def __init__(self, tally: UsageTally) -> None:
        self.tally = tally

    async def after_model_request(self, ctx, *, request_context, response):
        try:
            usage = getattr(response, "usage", None)
            self.tally.add(getattr(usage, "input_tokens", 0), getattr(usage, "output_tokens", 0), str(getattr(response, "model_name", "") or ""))
        except Exception:  # noqa: BLE001 - a count must not change a run
            log.exception("usage tally: could not count a request")
        return response


def usage_tally_capability(tally: UsageTally) -> UsageTallyCapability:
    return UsageTallyCapability(tally)
