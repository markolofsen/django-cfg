"""TS-target post-processing — wrapper layer + stale-root cleanup.

Hey API writes one self-contained SDK per OpenAPI tag. The wrapper
layer (``api.ts``, ``index.ts``, ``_shared/``) sits next to those
sub-SDKs to give consumers a stable import path that survives
re-slicing. This module exposes:

* ``clean_stale_root`` — sweep leftovers from a previous flat (single
  SDK) layout when a target moves to per-group layout.
* ``run_ts_wrapper`` — emit the ``class API`` wrapper. Failure isn't
  fatal: the wrapper is purely additive, consumers can fall back to
  importing from ``generated/<group>/`` directly.
* ``ts_extras_list`` — translate config booleans into the ``extras``
  list ts_extras consumes (``zod``, ``hooks``, ``events``).
"""

from __future__ import annotations

import shutil
from pathlib import Path

from ..config import GenerationTarget, OpenAPIConfig
from ...tools.ts_extras.wrapper import generate as generate_ts_wrapper

# Files emitted by the wrapper itself (or the per-target conventions
# we maintain by hand). They survive ``clean_stale_root``; everything
# else at target root that isn't a per-group folder gets swept.
_TS_ROOT_KEEP = {
    "_shared",
    "index.ts",
    ".cache",
    ".gitignore",
}


def clean_stale_root(target_root: Path, groups: list[str]) -> None:
    """Remove leftover artifacts at the per-group target root.

    When a TS target switches to per-group layout
    (``<root>/<group>/``), the previous single-SDK output (``client/``,
    ``core/``, ``hooks/``, ``schemas/``, ``sdk.gen.ts``,
    ``types.gen.ts`` …) lingers at the root. Hey API only writes inside
    group subdirs and the wrapper layer only writes its own files, so
    nothing cleans the stale single-SDK files. Sweep them here.

    Keeps: known wrapper files, the per-group sub-dirs themselves, and
    dotfiles.
    """
    if not target_root.exists():
        return
    keep = _TS_ROOT_KEEP | set(groups)
    for entry in target_root.iterdir():
        if entry.name in keep or entry.name.startswith("."):
            continue
        if entry.is_dir():
            shutil.rmtree(entry, ignore_errors=True)
        else:
            try:
                entry.unlink()
            except OSError:
                pass


def run_ts_wrapper(target: GenerationTarget, out_root: Path) -> None:
    """Emit the legacy-compatible ``class API`` wrapper for a TS target.

    Best-effort — wrapper failures are not fatal. The wrapper proxies
    into Hey API SDK classes; if it can't be emitted, callers just
    import from the per-group barrels directly.
    """
    try:
        generate_ts_wrapper(Path(out_root))
    except Exception:  # noqa: BLE001 — wrapper is non-critical
        return


def ts_extras_list(config: OpenAPIConfig) -> list[str]:
    extras: list[str] = []
    if config.generate_zod_schemas:
        extras.append("zod")
    if config.generate_swr_hooks:
        extras.append("hooks")
    if config.generate_events_bridge:
        extras.append("events")
    return extras


__all__ = ["clean_stale_root", "run_ts_wrapper", "ts_extras_list"]
