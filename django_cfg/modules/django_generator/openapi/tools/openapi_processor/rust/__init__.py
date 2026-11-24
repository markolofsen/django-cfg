"""Rust post-processor for progenitor output.

Adds ``src/django.rs`` to the generated crate: a ``DjangoClient`` builder that
resolves the base URL (explicit, else ``<CRATE>_BASE_URL``), sends the Bearer
token and the ``X-Api-Key`` header, and hands back progenitor's ``Client``.
"""

from .tool import RustWrapperResult, generate

__all__ = ["RustWrapperResult", "generate"]
