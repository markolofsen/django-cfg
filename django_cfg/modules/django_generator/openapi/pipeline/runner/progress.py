"""Progress printer for the runner.

Each target prints a single line as it finishes:

    ✓ go-cli-3                12.34s   (cached)
    ✓ typescript-web-0         8.21s
    ✗ swift_codable-mobile-2   3.10s   ToolExecutionError: ...

A header announces the spec-load step (cache hit / miss + ms) so a
slow drf-spectacular render is visible. A footer prints the run total
and the slowest target — useful when chasing wallclock regressions.

Output goes to stderr to keep stdout clean for tooling that captures
generated paths or names. Set ``DJANGO_CFG_GEN_QUIET=1`` to silence.
"""

from __future__ import annotations

import os
import sys
import time
from threading import Lock

_lock = Lock()
_GREEN = "\033[32m"
_RED = "\033[31m"
_DIM = "\033[2m"
_RESET = "\033[0m"


def is_quiet() -> bool:
    return os.environ.get("DJANGO_CFG_GEN_QUIET") in {"1", "true", "yes"}


def _color(code: str, text: str) -> str:
    if not _supports_color():
        return text
    return f"{code}{text}{_RESET}"


def _supports_color() -> bool:
    """Coarse TTY check — good enough for a build tool."""
    if os.environ.get("NO_COLOR"):
        return False
    return sys.stderr.isatty()


def print_spec_status(*, cache_hit: bool, elapsed_s: float) -> None:
    if is_quiet():
        return
    label = "cache" if cache_hit else "render"
    line = f"  spec       {elapsed_s:6.2f}s   ({label})"
    with _lock:
        sys.stderr.write(line + "\n")
        sys.stderr.flush()


def print_target_result(
    name: str,
    *,
    ok: bool,
    elapsed_s: float,
    cache_hit: bool,
    error: str | None = None,
) -> None:
    if is_quiet():
        return
    mark = _color(_GREEN, "✓") if ok else _color(_RED, "✗")
    cached = _color(_DIM, "(cached)") if cache_hit and ok else ""
    err_part = f"  {error}" if error else ""
    # Pad name to a stable width so columns align across targets.
    line = f"  {mark} {name:<32} {elapsed_s:6.2f}s   {cached}{err_part}".rstrip()
    with _lock:
        sys.stderr.write(line + "\n")
        sys.stderr.flush()


def print_run_summary(
    *,
    total_s: float,
    timings: dict[str, float],
    cache_hits: dict[str, bool],
) -> None:
    """Optional one-line summary at the end of the run.

    Skipped when only one target ran (the per-target line already
    carries the timing) or when quiet mode is on.
    """
    if is_quiet():
        return
    target_timings = {
        n: t for n, t in timings.items() if not n.startswith("__")
    }
    if not target_timings:
        return
    slowest = max(target_timings.items(), key=lambda kv: kv[1])
    n_cached = sum(1 for n, hit in cache_hits.items()
                   if hit and not n.startswith("__"))
    n_total = len(target_timings)
    cache_note = f"{n_cached}/{n_total} cached" if n_total else ""
    parts = [f"total {total_s:.2f}s",
             f"slowest {slowest[0]} {slowest[1]:.2f}s"]
    if cache_note:
        parts.append(cache_note)
    line = "  " + _color(_DIM, " · ".join(parts))
    with _lock:
        sys.stderr.write(line + "\n")
        sys.stderr.flush()


def now() -> float:
    """Monotonic seconds — used by the orchestrator for elapsed timing."""
    return time.perf_counter()


__all__ = [
    "is_quiet",
    "now",
    "print_run_summary",
    "print_spec_status",
    "print_target_result",
]
