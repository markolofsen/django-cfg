"""TS-target post-processing — wrapper layer + stale-root cleanup.

Hey API writes a single shared SDK (``sdk.gen.ts``, ``types.gen.ts``,
``client/``, ``core/``) at the target root. The wrapper layer
(``api.ts``, ``index.ts``, ``helpers/``) is emitted next to those
files. Per-group ts_extras output (hooks, schemas) goes into
``_<group>/`` subdirs. This module exposes:

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
from ...tools.openapi_processor.ts.wrapper import generate as generate_ts_wrapper

# Files/dirs at target root that survive ``clean_stale_root``.
# hey-api SDK output (sdk.gen.ts, types.gen.ts, client/, core/) lives
# here now and must not be removed between runs.  Only stale group
# sub-dirs (old group names removed from config) get swept.
_TS_ROOT_KEEP = {
    # hey-api SDK output
    "sdk.gen.ts",
    "types.gen.ts",
    "client.gen.ts",
    "client",
    "core",
    # wrapper layer
    "helpers",
    "_shared",
    "api.ts",
    "index.ts",
    "events.ts",
    ".routes.json",
    # OpenAPI spec saved alongside generated output
    "openapi.json",
    # misc
    ".cache",
    ".gitignore",
}


def clean_stale_root(target_root: Path, groups: list[str]) -> None:
    """Remove leftover artifacts at the per-group target root.

    In the new layout hey-api writes the shared SDK into the target root
    and ts_extras writes per-group output into ``_<group>/`` subdirs.
    Stale group directories from renamed or removed groups linger between
    runs; this sweep removes them while keeping known SDK + wrapper files.

    Keeps: known hey-api + wrapper files, underscore-prefixed group
    sub-dirs (``_<group>``), bare group names (backward compat), and
    dotfiles.
    """
    if not target_root.exists():
        return
    # Keep underscore-prefixed group dirs (new layout: _<group>) as well as
    # bare group names for backward compatibility during transitions.
    keep = _TS_ROOT_KEEP | {f"_{g}" for g in groups} | set(groups)
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
