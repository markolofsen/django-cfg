"""Emit a single `events.ts` next to Hey API output.

This generator is IR-free: the emitted file's shape is fixed (event names
+ interceptor wiring) and depends only on `./client.gen` being present —
which it always is for Hey API targets.
"""

from __future__ import annotations

from pathlib import Path

from .template import EVENTS_TS


def generate_events(out_dir: Path) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "events.ts"
    path.write_text(EVENTS_TS, encoding="utf-8")
    return [path]
