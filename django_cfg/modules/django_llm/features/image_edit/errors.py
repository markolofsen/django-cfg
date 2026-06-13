"""Exception hierarchy for image-edit calls.

Separated out so callers can ``except NoImageReturnedError`` without
pulling the whole client module + httpx into their import graph (e.g.
a Django signal that just wants to type a refusal handler).
"""

from __future__ import annotations


class ImageEditError(Exception):
    """Base for any image-edit transport or response failure.

    Use this when the call itself blew up — HTTP error, malformed
    response, missing API key, etc. For the specific case where the
    model *answered* but emitted no image (a soft refusal), raise
    :class:`NoImageReturnedError` instead so the caller can persist
    the refusal as a terminal outcome rather than a transient error.
    """


class NoImageReturnedError(ImageEditError):
    """Model produced a text response but no image bytes.

    Sign of a safety-classifier refusal on the provider side. The
    model usually emits a short explanation (e.g. "I'm just a language
    model and can't help with that.") that the caller surfaces as the
    refusal reason without retrying the call.

    Args:
        message: Short human-readable reason — typically
            ``"Model returned no image bytes"``.
        model_text: The model's own caption / explanation pulled from
            the response's text payload. Empty string when the model
            refused silently.
    """

    def __init__(self, message: str, *, model_text: str = ""):
        super().__init__(message)
        self.model_text = model_text
