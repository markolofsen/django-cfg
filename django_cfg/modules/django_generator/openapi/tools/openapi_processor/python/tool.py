"""python-extras entry point.

Walks an openapi-python-client output directory and applies a chain of
in-place fixers (see ``fixes.py``). Designed to run *after*
openapi-python-client has finished writing files into ``out_dir``.

Usage:
    from openapi_processor.python.tool import generate
    result = generate(out_dir=Path("..."))
    print(result.fixed_files)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .fixes import fix_enum_value_none_guard, fix_unset_import


@dataclass(slots=True)
class PythonExtrasResult:
    out_dir: Path
    fixed_files: list[Path] = field(default_factory=list)


# All fixers run in order. Each returns (new_text, changed). The file is
# rewritten only if at least one fixer reports a change.
_FIXERS = (fix_unset_import, fix_enum_value_none_guard)


def generate(out_dir: Path) -> PythonExtrasResult:
    """Apply post-process fixers to every .py file under ``out_dir``."""
    fixed: list[Path] = []
    for py_file in out_dir.rglob("*.py"):
        if not py_file.is_file():
            continue
        original = py_file.read_text(encoding="utf-8")
        text = original
        changed_any = False
        for fixer in _FIXERS:
            text, changed = fixer(text)
            changed_any = changed_any or changed
        if changed_any and text != original:
            py_file.write_text(text, encoding="utf-8")
            fixed.append(py_file)
    return PythonExtrasResult(out_dir=out_dir, fixed_files=fixed)


__all__ = ["PythonExtrasResult", "generate"]
