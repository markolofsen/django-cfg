"""`UsageTally`: the tokens of the model requests that finished, counted as they finish.

A run's authoritative usage arrives with its last event. A run that is cancelled, cut off by a disconnect or failed late never gets
there, and the tokens it already paid for would book as zero. The tally is filled by `capabilities.usage_tally` after every completed
request, and the driver reads it when a run ends without usage. A request cut off mid-stream reported nothing and is not counted.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class UsageTally:
    input_tokens: int = 0
    output_tokens: int = 0
    requests: int = 0
    model: str = ""  # the slug that served the newest request (through a fallback chain: the one that won)

    def add(self, input_tokens: int | None, output_tokens: int | None, model: str = "") -> None:
        self.input_tokens += int(input_tokens or 0)
        self.output_tokens += int(output_tokens or 0)
        self.requests += 1
        if model:
            self.model = model
