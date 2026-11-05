"""Transcription that survives content blocks.

    from django_cfg.modules.django_llm.features.transcribe import (
        DEFAULT_CHAIN, Policy, make_ask, transcribe)

    result = transcribe(duration_s, cut, make_ask(call), DEFAULT_CHAIN)
    result.text, result.gaps, result.cost_usd

See ``runner`` for the policy and ``@docs`` in the docs site for the contract.
"""

from .defaults import DEFAULT_CHAIN
from .engines import INSTRUCTION, Ask, Call, make_ask
from .errors import ContentBlocked, Fatal, ModelUnavailable, NothingTranscribed, Transient, TranscribeError
from .models import Answer, ChainEntry, Gap, Policy, Result, Segment
from .runner import plan, transcribe, transcribe_range

__all__ = [
    "Answer", "Ask", "Call", "ChainEntry", "ContentBlocked", "DEFAULT_CHAIN", "Fatal", "Gap", "INSTRUCTION",
    "ModelUnavailable", "NothingTranscribed", "Policy", "Result", "Segment", "Transient", "TranscribeError",
    "make_ask", "plan", "transcribe", "transcribe_range",
]
