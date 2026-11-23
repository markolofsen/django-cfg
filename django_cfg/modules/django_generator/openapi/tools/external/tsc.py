"""``tsc --noEmit`` over a generated TypeScript tree: the type-check gate.

The tree is checked as if it were already in its final folder, because its
imports are written for that place. The Orval runtime shim can import a
handwritten runtime by a relative path computed from the consumer folder
(``dispatch._dispatch_tool``), and bare imports (``zod``,
``@tanstack/react-query``, ``@djangocfg/api``) resolve through the consumer's
``node_modules``. A staged tree sits one folder deeper
(``.<name>.djcfg-stage-<id>/<name>``), where such a relative import misses. So
the gate copies the tree to a sibling of the final folder,
``.<name>.djcfg-tsc-<id>``, at the same depth, checks that copy and deletes
it. Neither the staged tree nor the final folder is touched.

Settings. The nearest ``tsconfig.json`` above the final folder is extended, so
the tree is held to the rules its consumer type-checks with. Only the input
list and the emit options are overridden. Without a ``tsconfig.json``, a strict
bundler-style default applies.

What fails. A diagnostic located in the generated tree fails the gate, and so
does one with no location (a configuration error). Diagnostics in files the
tree imports, such as the handwritten runtime, are counted and do not fail
generation: they belong to the consumer's own type-check. A runtime that stops
exporting what the shim re-exports still fails here, because that error is
reported in the shim.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import threading
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from ...pipeline.errors import ToolExecutionError, ToolNotInstalledError

#: Set to ``1`` to generate without the type-check (see the generator README).
SKIP_ENV = "DJANGO_CFG_GEN_SKIP_TYPECHECK"

PROBE_MARK = ".djcfg-tsc-"
_MAX_SHOWN = 20
_TIMEOUT_S = 600

# Targets run on a thread pool. One tsc at a time keeps a run with several
# TypeScript targets from holding several compilers in memory at once.
_LOCK = threading.Lock()

# Used only when no tsconfig.json exists above the final folder.
_DEFAULT_OPTIONS: dict[str, object] = {
    "strict": True,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "esModuleInterop": True,
    "resolveJsonModule": True,
    "isolatedModules": True,
}

# Always applied on top: check, never write anything.
_PROBE_OPTIONS: dict[str, object] = {
    "noEmit": True,
    "incremental": False,
    "composite": False,
    "declaration": False,
    "declarationMap": False,
    "sourceMap": False,
    "emitDeclarationOnly": False,
    "skipLibCheck": True,
}

_LOCATED = re.compile(r"^(?P<file>.+?)\((?P<line>\d+),(?P<col>\d+)\): error (?P<code>TS\d+): (?P<msg>.*)$")
_GLOBAL = re.compile(r"^error (?P<code>TS\d+): (?P<msg>.*)$")


@dataclass(slots=True)
class TypecheckResult:
    """What a passing check saw. ``outside`` counts diagnostics in imported files, which do not fail it."""

    files: int
    outside: int = 0
    errors: list[str] = field(default_factory=list)


def is_skipped() -> bool:
    return os.environ.get(SKIP_ENV, "").strip().lower() in {"1", "true", "yes"}


def find_tsc(start: Path) -> Path | None:
    """The TypeScript compiler the consumer would use: the nearest ``node_modules/typescript`` above ``start``."""
    for directory in (start, *start.parents):
        candidate = directory / "node_modules" / "typescript" / "bin" / "tsc"
        if candidate.is_file():
            return candidate
    return None


def find_tsconfig(start: Path) -> Path | None:
    for directory in (start, *start.parents):
        candidate = directory / "tsconfig.json"
        if candidate.is_file():
            return candidate
    return None


def typecheck(tree: Path, *, final: Path, tsc: Path | None = None) -> TypecheckResult:
    """Type-check ``tree`` as if it lived at ``final``. Raises on a type error in the tree.

    ``tree`` and ``final`` may be the same folder (checking a tree in place).
    """
    tree = Path(tree).resolve()
    final = Path(final)
    # Resolved, so the paths tsc prints relative to its working directory
    # compare with ours on a symlinked temp dir (macOS /var -> /private/var).
    parent = final.parent.resolve()
    final = parent / final.name

    sources = sorted(
        p.relative_to(tree).as_posix()
        for p in tree.rglob("*")
        if p.is_file() and p.suffix in {".ts", ".tsx"}
    )
    if not sources:
        return TypecheckResult(files=0)

    compiler = tsc or find_tsc(parent)
    if compiler is None:
        raise ToolNotInstalledError(
            f"cannot type-check {final}: no node_modules/typescript above it. Install the frontend "
            f"workspace dependencies, or set {SKIP_ENV}=1 to generate without the type-check."
        )
    node = shutil.which("node")
    if node is None:
        raise ToolNotInstalledError(f"cannot type-check {final}: node is not on PATH")

    probe = parent / f".{final.name}{PROBE_MARK}{uuid.uuid4().hex[:8]}"
    try:
        shutil.copytree(tree, probe, symlinks=True)
        base = find_tsconfig(parent)
        config: dict[str, object] = {
            "compilerOptions": {**({} if base else _DEFAULT_OPTIONS), **_PROBE_OPTIONS},
            "files": sources,
            "include": [],
        }
        if base is not None:
            config = {"extends": str(base), **config}
        config_path = probe / "tsconfig.djcfg-typecheck.json"
        config_path.write_text(json.dumps(config, indent=2), encoding="utf-8")
        with _LOCK:
            proc = subprocess.run(
                [node, str(compiler), "--project", str(config_path), "--pretty", "false"],
                cwd=parent,
                capture_output=True,
                text=True,
                timeout=_TIMEOUT_S,
            )
        result = _classify(proc.stdout, cwd=parent, probe=probe, files=len(sources))
    except subprocess.TimeoutExpired as exc:
        raise ToolExecutionError(f"tsc did not finish in {_TIMEOUT_S}s on {final}") from exc
    except OSError as exc:
        raise ToolExecutionError(f"cannot type-check {final}: {exc}") from exc
    finally:
        shutil.rmtree(probe, ignore_errors=True)

    if result.errors:
        shown = "\n  ".join(result.errors[:_MAX_SHOWN])
        more = f"\n  ... and {len(result.errors) - _MAX_SHOWN} more" if len(result.errors) > _MAX_SHOWN else ""
        raise ToolExecutionError(
            f"the generated TypeScript in {final} does not type-check "
            f"({len(result.errors)} error(s), tsc {compiler}); nothing was written:\n  {shown}{more}\n"
            f"Fix the generator, the OpenAPI schema or the runtime the tree imports. To inspect the tree, "
            f"regenerate with {SKIP_ENV}=1 and run the consumer's `tsc --noEmit`."
        )
    if proc.returncode != 0 and not result.outside:
        detail = (proc.stderr or proc.stdout or "").strip()[-2000:]
        raise ToolExecutionError(
            f"tsc exited {proc.returncode} on {final} without a diagnostic: {detail or 'no output'}"
        )
    return result


def _classify(stdout: str, *, cwd: Path, probe: Path, files: int) -> TypecheckResult:
    """Sort tsc's ``--pretty false`` lines into errors in the tree, global errors and errors elsewhere."""
    result = TypecheckResult(files=files)
    current: list[str] | None = None  # the entry continuation lines belong to; None = ignored
    for raw in stdout.splitlines():
        line = raw.rstrip()
        located = _LOCATED.match(line)
        if located:
            where = Path(os.path.normpath(cwd / located["file"]))
            try:
                inside = where.relative_to(probe).as_posix()
            except ValueError:
                result.outside += 1
                current = None
                continue
            result.errors.append(
                f"{inside}({located['line']},{located['col']}): error {located['code']}: {located['msg']}"
            )
            current = result.errors
            continue
        unlocated = _GLOBAL.match(line)
        if unlocated:
            result.errors.append(f"error {unlocated['code']}: {unlocated['msg']}")
            current = result.errors
            continue
        if current is not None and line.strip():
            current[-1] += "\n    " + line.strip()
    return result


__all__ = [
    "PROBE_MARK",
    "SKIP_ENV",
    "TypecheckResult",
    "find_tsc",
    "find_tsconfig",
    "is_skipped",
    "typecheck",
]
