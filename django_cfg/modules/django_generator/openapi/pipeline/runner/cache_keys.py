"""Cache-key builders for ``_run_single``.

Two pieces:

* ``target_signature`` — extra inputs that affect output but aren't
  captured by the sliced-spec hash (target name, tool, group set,
  ``out_dir``). ``out_dir`` matters because hey-api / ts_extras embed
  the path inside generated source.

* ``target_cache_slot`` — the on-disk slot name used by
  ``cache.restore_target_output`` / ``store_target_output``. Multi-group
  targets reuse the slot once per group, so we keep groups in the slot
  too.
"""

from __future__ import annotations

from pathlib import Path

from ..config import GenerationTarget


def target_cache_slot(target: GenerationTarget, groups: list[str]) -> str:
    suffix = "+".join(sorted(groups)) or "_all"
    return f"{target.name}__{suffix}"


def target_signature(
    target: GenerationTarget,
    groups: list[str],
    out_dir: Path,
) -> str:
    return "|".join((
        target.name,
        target.tool,
        "+".join(sorted(groups)),
        out_dir.as_posix(),
    ))


__all__ = ["target_cache_slot", "target_signature"]
