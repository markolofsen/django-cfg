"""Pipeline runner — split into focused modules.

Public surface is just ``run_pipeline``; everything else is private to
the runner package.

Layout:

* ``orchestrator`` — top-level driver, spec cache, parallel fan-out.
* ``dispatch`` — per-target dispatch + tool selection.
* ``cache_keys`` — fingerprint helpers for the per-target cache.
* ``ts_wrapper`` — TS-target post-processing (wrapper layer, stale-root
  cleanup).
* ``paths`` — small filesystem helpers (project root, publish to
  consumer, mirror to tmp).
"""

from __future__ import annotations

from .orchestrator import run_pipeline

__all__ = ["run_pipeline"]
