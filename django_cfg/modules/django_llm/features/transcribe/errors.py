"""What can go wrong when one model is asked to transcribe one piece of audio.

The split matters more than the names: a *block* is the model's decision and
repeats on the same audio; a *transient* fault is time's; a *fatal* one is the
account's. They are handled three different ways (see ``runner``).
"""

from __future__ import annotations

from decimal import Decimal


class TranscribeError(Exception):
    """Base for every failure of the transcribe plane.

    ``cost_usd``: what the provider charged for this call anyway. A refused call
    is often billed, so the runner adds it to the total instead of dropping it.
    """

    def __init__(self, message: str = "", cost_usd: Decimal = Decimal("0")):
        super().__init__(message)
        self.cost_usd = cost_usd


class ContentBlocked(TranscribeError):
    """The model refused this audio under its content policy.

    Deterministic: asking the same model again for the same audio gets the same
    answer. The next entry of the chain, or a smaller piece, may pass.
    """


class Transient(TranscribeError):
    """A fault that time can mend: rate limit, upstream 5xx, a dropped connection."""


class ModelUnavailable(TranscribeError):
    """This model cannot serve the request (unknown id, bad answer shape). Skip it."""


class Fatal(TranscribeError):
    """No model will help: no key (401) or no credit (402). Stop at once."""


class NothingTranscribed(TranscribeError):
    """Every piece ended as a gap: there is no text to return."""
