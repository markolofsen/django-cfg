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


def _clean_identity(raw: str) -> str:
    """Strip ``<class '...'>`` wrapping to keep messages readable."""
    return raw.strip().removeprefix("<class '").removesuffix("'>")


def _suggest_ref_name(identity: str) -> str | None:
    """Derive a unique ``ref_name`` suggestion from a serializer identity.

    ``identity`` looks like ``billing.serializers.SubscribeSerializer``. We
    prefix the serializer's base name (``Serializer`` suffix stripped) with the
    PascalCased leading module segment (the Django app label):

        billing.serializers.SubscribeSerializer  ->  BillingSubscribe

    Returns ``None`` when the heuristic cannot produce a sensible name (e.g. the
    identity has no module path), so the caller can fall back to a placeholder.
    """
    parts = identity.split(".")
    if len(parts) < 2:
        return None

    class_name = parts[-1]
    app_segment = parts[0]
    if not class_name or not app_segment:
        return None

    base_name = class_name
    for suffix in ("Serializer", "Request", "Response"):
        if base_name.endswith(suffix) and base_name != suffix:
            base_name = base_name[: -len(suffix)]
            break

    app_pascal = "".join(w[:1].upper() + w[1:] for w in re.split(r"[_\-]+", app_segment) if w)
    if not app_pascal or not base_name:
        return None

    # Avoid double-prefixing when the base name already starts with the app.
    if base_name.lower().startswith(app_pascal.lower()):
        return base_name
    return f"{app_pascal}{base_name}"


def _serializer_class_name(identity: str) -> str:
    """Best-effort serializer class name from a dotted identity."""
    tail = identity.rsplit(".", 1)[-1]
    return tail or "YourSerializer"


def _fix_snippet(identity: str) -> str:
    """Render a copy-paste ``Meta.ref_name`` snippet for one serializer."""
    cls = _serializer_class_name(identity)
    suggested = _suggest_ref_name(identity)
    if suggested is None:
        ref = '"<UniqueComponentName>"  # replace with a globally-unique name'
    else:
        ref = f'"{suggested}"'
    return (
        f"        # in {identity}\n"
        f"        class {cls}(...):\n"
        f"            class Meta:\n"
        f"                ref_name = {ref}"
    )


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
        identities = seen.setdefault(name, set())
        for raw in (m.group("a"), m.group("b")):
            identities.add(_clean_identity(raw))

    if not seen:
        return

    blocks: list[str] = []
    for name, identities in sorted(seen.items()):
        block = [f"  • component \"{name}\" is claimed by:"]
        for ident in sorted(identities):
            block.append(f"      - {ident}")
        block.append("    Pick a unique `ref_name` for at least one of them, e.g.:")
        for ident in sorted(identities):
            block.append(_fix_snippet(ident))
        blocks.append("\n".join(block))

    raise SpecLoadError(
        "Schema-name collision detected — drf-spectacular cannot emit a valid "
        "spec when two serializer classes resolve to the same component name:\n"
        + "\n\n".join(blocks)
        + "\n\nFix: rename one of the conflicting serializer classes (or set its "
          "`Meta.ref_name` as shown above) so each component name is unique."
    )


__all__ = ["load_spec", "LoadMode"]
