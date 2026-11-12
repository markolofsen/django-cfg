"""Values the transcribe plane takes and returns. Plain data, no I/O."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Literal

Engine = Literal["chat", "stt"]
GapReason = Literal["blocked", "failed"]


@dataclass(frozen=True)
class ChainEntry:
    """One model in the fallback chain.

    ``chat``: a chat model that accepts ``input_audio`` (``/chat/completions``).
    ``stt``: a dedicated speech-to-text model (``/audio/transcriptions``).
    """

    model: str
    engine: Engine = "chat"
    #: Ask an ``stt`` model to label who speaks (see ``engines.DIARIZATION``); the text then reads ``Speaker 1: ...``.
    diarize: bool = False


@dataclass(frozen=True)
class Answer:
    """What one model returned for one piece."""

    text: str
    language: str = ""
    cost_usd: Decimal = Decimal("0")
    #: The model stopped at its token limit; the text is cut short.
    truncated: bool = False


@dataclass(frozen=True)
class Segment:
    """One transcribed piece. ``model`` is the one that answered; ``cost_usd`` is
    everything spent on the piece, refused attempts included."""

    start_s: float
    end_s: float
    text: str
    language: str
    model: str
    cost_usd: Decimal


@dataclass(frozen=True)
class Gap:
    """A stretch of the recording nobody transcribed, and why."""

    start_s: float
    end_s: float
    reason: GapReason
    detail: str = ""
    #: True when time may still mend it (``failed``); a ``blocked`` gap will not heal.
    retryable: bool = False
    #: Charged for the attempts that ended here: a refusal is often billed.
    cost_usd: Decimal = Decimal("0")


@dataclass(frozen=True)
class Policy:
    """How hard to try. The defaults suit a background job, not a web request."""

    chunk_s: float = 300.0
    #: A blocked piece is halved while each half stays at least this long.
    floor_s: float = 60.0
    max_depth: int = 3
    #: Passes over the not-yet-blocked entries when a fault is transient.
    rounds: int = 4
    pause_s: float = 5.0
    #: Characters of earlier text handed to the next piece so a cut word is not repeated.
    context_chars: int = 400


@dataclass
class Result:
    segments: list[Segment] = field(default_factory=list)
    gaps: list[Gap] = field(default_factory=list)
    cost_usd: Decimal = Decimal("0")

    @property
    def text(self) -> str:
        return "\n\n".join(s.text for s in self.segments if s.text)

    @property
    def language(self) -> str:
        counts = Counter(s.language for s in self.segments if s.language)
        return counts.most_common(1)[0][0] if counts else ""

    @property
    def models(self) -> list[str]:
        return list(dict.fromkeys(s.model for s in self.segments if s.model))

    @property
    def complete(self) -> bool:
        return not self.gaps
