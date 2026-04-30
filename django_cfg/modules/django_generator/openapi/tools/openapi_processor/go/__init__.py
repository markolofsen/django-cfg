"""Go post-processor for ogen output.

Generates a convenience ``wrapper.go`` alongside ogen's ``oas_*.gen.go``
files.  The wrapper implements ``SecuritySource`` (JWT bearer token),
provides a ``DjangoClient`` struct with functional options, and exposes
``WithToken``, ``WithBaseURL``, ``WithEnv``, and ``WithAPIKey``.
"""

from .tool import GoWrapperResult, generate

__all__ = ["GoWrapperResult", "generate"]
