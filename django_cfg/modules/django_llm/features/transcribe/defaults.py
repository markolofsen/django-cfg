"""The default chain. Data, not logic: change it without touching the runner.

Measured 2026-11-05 on a real 10-minute Russian piece that ``google/gemini-2.5-flash``
refused with ``PROHIBITED_CONTENT`` (cost of that one piece, seconds):

    google/gemini-2.5-flash-lite   BLOCKED (same filter as 2.5-flash)
    qwen/qwen3.8-omni-flash        ok   $0.0015  25 s
    openai/gpt-audio-mini          ok   $0.0077  17 s
    google/gemini-3.5-flash-lite   ok   $0.0088   8 s
    google/gemini-3.1-flash-lite   ok   $0.0096   9 s
    google/gemini-3-flash-preview  ok   $0.0183  10 s
    mistralai/voxtral-small-24b    429 twice (upstream rate limit)
    nvidia/nemotron-3-nano-omni    unusable (130 s, unreadable answer)
    /audio/transcriptions          not served by the router (404)

So the chain is cheapest first, with a different vendor in each step, because
filters differ by vendor. ``gemini-2.5-*`` is left out: it blocks what 3.x passes.
"""

from __future__ import annotations

from ...catalog.tasks import TRANSCRIBE_MODELS
from .models import ChainEntry

#: Derived from the task table (``catalog/tasks.py``), which owns the slugs.
DEFAULT_CHAIN: tuple[ChainEntry, ...] = tuple(ChainEntry(m) for m in TRANSCRIBE_MODELS)
