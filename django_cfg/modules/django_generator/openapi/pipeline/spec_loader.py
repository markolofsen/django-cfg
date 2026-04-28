"""Load global OpenAPI 3.1 spec from drf-spectacular.

Two modes:
  - "in_process" (default): SchemaGenerator.get_schema() — fast, no subprocess.
  - "subprocess": `manage.py spectacular --file <out>` — fallback when in-process
    boot leaks state (e.g. mid-test).

Returns a Python dict ready for postprocessing.

Schema-name collisions are detected here, not in postprocess: drf-spectacular
emits warnings to stderr at generation time but silently keeps only one
component, so the post-load spec is already lossy. We capture stderr,
look for the diagnostic pattern, and abort with a clear error.
"""

from __future__ import annotations

import io
import json
import re
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr
from pathlib import Path
from typing import Any, Literal

from .errors import SpecLoadError

LoadMode = Literal["in_process", "subprocess"]

_COLLISION_RE = re.compile(
    r'Encountered 2 components with identical names "(?P<name>[^"]+)"'
    r' and different identities (?P<a>.+?) and (?P<b>.+?)\. ',
)


def load_spec(*, mode: LoadMode = "in_process") -> dict[str, Any]:
    if mode == "in_process":
        return _load_in_process()
    if mode == "subprocess":
        return _load_subprocess()
    raise SpecLoadError(f"unknown mode: {mode}")


def _load_in_process() -> dict[str, Any]:
    try:
        from drf_spectacular.generators import SchemaGenerator
    except ImportError as e:
        raise SpecLoadError("drf-spectacular not installed") from e

    buf = io.StringIO()
    try:
        with redirect_stderr(buf):
            generator = SchemaGenerator()
            schema = generator.get_schema(request=None, public=True)
    except Exception as e:
        raise SpecLoadError(f"drf-spectacular failed: {type(e).__name__}: {e}") from e
    finally:
        # Forward captured warnings so the user still sees them.
        sys.stderr.write(buf.getvalue())

    _check_collisions(buf.getvalue())

    if not isinstance(schema, dict):
        raise SpecLoadError(f"unexpected schema type: {type(schema).__name__}")
    return schema


def _load_subprocess() -> dict[str, Any]:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        out = Path(tmp.name)
    try:
        proc = subprocess.run(
            [sys.executable, "manage.py", "spectacular",
             "--file", str(out), "--format", "openapi-json"],
            capture_output=True,
            text=True,
        )
        sys.stderr.write(proc.stderr)
        if proc.returncode != 0:
            raise SpecLoadError(
                f"manage.py spectacular failed (exit {proc.returncode}):\n{proc.stderr}"
            )
        _check_collisions(proc.stderr)
        text = out.read_text(encoding="utf-8")
        return json.loads(text)
    finally:
        out.unlink(missing_ok=True)


def _check_collisions(stderr_text: str) -> None:
    """Abort if drf-spectacular reported schema-name collisions.

    Each collision in stderr means two distinct serializer classes (across
    Django apps) share a final OpenAPI component name. drf-spectacular keeps
    only one of them silently — the generated spec is lossy and unsafe to
    feed downstream tools.
    """
    seen: dict[str, set[str]] = {}
    for m in _COLLISION_RE.finditer(stderr_text):
        name = m.group("name")
        # Strip "<class '...'>" wrapping to keep messages readable.
        identities = seen.setdefault(name, set())
        for raw in (m.group("a"), m.group("b")):
            cleaned = raw.strip().removeprefix("<class '").removesuffix("'>")
            identities.add(cleaned)

    if not seen:
        return

    lines = []
    for name, identities in sorted(seen.items()):
        lines.append(f"  • {name}")
        for ident in sorted(identities):
            lines.append(f"      from {ident}")

    raise SpecLoadError(
        "Schema-name collision detected — drf-spectacular cannot emit a valid "
        "spec when two serializer classes resolve to the same component name:\n"
        + "\n".join(lines)
        + "\n\nFix: rename one of the conflicting serializer classes "
          "(or set its `Meta.ref_name`) so each component name is unique."
    )


__all__ = ["load_spec", "LoadMode"]
