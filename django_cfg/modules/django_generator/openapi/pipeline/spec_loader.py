"""Load global OpenAPI 3.1 spec from drf-spectacular.

Two modes:
  - "in_process" (default): SchemaGenerator.get_schema() — fast, no subprocess.
  - "subprocess": `manage.py spectacular --file <out>` — fallback when in-process
    boot leaks state (e.g. mid-test).

Returns a Python dict ready for postprocessing.

Every schema is validated before it can reach an external generator.  The
in-process path mirrors ``manage.py spectacular --validate --fail-on-warn``;
the subprocess path invokes those exact flags.  Set
``DJANGO_CFG_GEN_ALLOW_SCHEMA_WARNINGS=1`` only as a temporary migration
escape hatch for a project that has not yet cleaned up its schema warnings.

Schema-name collisions are detected here, not in postprocess: drf-spectacular
emits warnings to stderr at generation time but silently keeps only one
component, so the post-load spec is already lossy. We capture stderr,
look for the diagnostic pattern, and abort with a clear error.
"""

from __future__ import annotations

import ast
import io
import json
import os
import re
import subprocess
import sys
import tempfile
from contextlib import redirect_stderr
from pathlib import Path
from typing import Any, Literal

from .errors import SpecLoadError

LoadMode = Literal["in_process", "subprocess"]

_ALLOW_SCHEMA_WARNINGS = "DJANGO_CFG_GEN_ALLOW_SCHEMA_WARNINGS"

_COLLISION_RE = re.compile(
    r'Encountered 2 components with identical names "(?P<name>[^"]+)"'
    r' and different identities (?P<a>.+?) and (?P<b>.+?)\. ',
)
# drf_spectacular.plumbing.sanitize_result_object: it renames every operation after the first one.
_OPERATION_ID_COLLISION_RE = re.compile(
    r'operationId "(?P<id>[^"]+)" has collisions (?P<locations>\[.*?\])\. resolving with numeral suffixes\.'
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

    # drf-spectacular keeps warning state globally.  A previous management
    # command in the same interpreter must not poison this generation run.
    try:
        from drf_spectacular.drainage import reset_generator_stats

        reset_generator_stats()
    except ImportError:  # pragma: no cover - old drf-spectacular fallback
        pass

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
    _check_operation_id_collisions(buf.getvalue())

    if not isinstance(schema, dict):
        raise SpecLoadError(f"unexpected schema type: {type(schema).__name__}")

    _validate_schema(schema, warning_output=buf.getvalue())
    return schema


def _load_subprocess() -> dict[str, Any]:
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        out = Path(tmp.name)
    try:
        command = [
            sys.executable,
            "manage.py",
            "spectacular",
            "--file",
            str(out),
            "--format",
            "openapi-json",
        ]
        if not _allow_schema_warnings():
            command.extend(["--validate", "--fail-on-warn"])
        proc = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )
        sys.stderr.write(proc.stderr)
        # Before the exit code: with --fail-on-warn a collision also fails the command, and these name the fix.
        _check_collisions(proc.stderr)
        _check_operation_id_collisions(proc.stderr)
        if proc.returncode != 0:
            raise SpecLoadError(
                f"manage.py spectacular failed (exit {proc.returncode}):\n{proc.stderr}"
            )
        text = out.read_text(encoding="utf-8")
        schema = json.loads(text)
        # Older drf-spectacular releases may not understand the CLI flags.
        # Keep the loaded document protected by the same in-process gate.
        _validate_schema(schema, warning_output=proc.stderr, check_warnings=False)
        return schema
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


def _check_operation_id_collisions(stderr_text: str) -> None:
    """Abort if drf-spectacular gave two operations the same operationId.

    It does not fail: it appends ``_2``, ``_3`` in URL order and warns. The generated function and hook names then
    depend on route order, and a new route can rename an existing client call. Refused even with the schema-warning
    escape hatch, like a schema-name collision.
    """
    found: dict[str, list[tuple[str, str]]] = {}
    for m in _OPERATION_ID_COLLISION_RE.finditer(stderr_text):
        try:
            locations = ast.literal_eval(m.group("locations"))
        except (ValueError, SyntaxError):
            locations = []
        found.setdefault(m.group("id"), [])
        for item in locations:
            if isinstance(item, (list, tuple)) and len(item) == 2 and tuple(item) not in found[m.group("id")]:
                found[m.group("id")].append((str(item[0]), str(item[1])))
    if not found:
        return
    from .views import describe

    blocks = []
    for operation_id, locations in sorted(found.items()):
        lines = [f'  • operationId "{operation_id}" is claimed by:']
        lines += [f"      - {describe(path, method)}" for path, method in sorted(locations)] or ["      - (locations not reported)"]
        blocks.append("\n".join(lines))
    raise SpecLoadError(
        "operationId collision: drf-spectacular renames all but the first of these with a numeral suffix "
        "(`_2`, `_3`, in URL order), so the generated client names would depend on route order:\n"
        + "\n".join(blocks)
        + '\n\nFix: give each one its own id with `@extend_schema(operation_id="<unique_id>")` on the view method '
        "(for a viewset action, on the action), or rename one of the routes."
    )


def _allow_schema_warnings() -> bool:
    """Return whether the temporary warning escape hatch is enabled."""
    return os.environ.get(_ALLOW_SCHEMA_WARNINGS, "").strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _validate_schema(
    schema: dict[str, Any], *, warning_output: str = "", check_warnings: bool = True
) -> None:
    """Apply drf-spectacular's schema and warning gates before codegen."""
    try:
        from drf_spectacular.validation import validate_schema

        validate_schema(schema)
    except Exception as exc:  # noqa: BLE001 - preserve validator diagnostics
        raise SpecLoadError(
            "drf-spectacular OpenAPI validation failed before client generation: "
            f"{type(exc).__name__}: {exc}"
        ) from exc

    if not check_warnings or _allow_schema_warnings():
        return

    try:
        from drf_spectacular.drainage import GENERATOR_STATS
    except ImportError:  # pragma: no cover - old drf-spectacular fallback
        GENERATOR_STATS = None

    if GENERATOR_STATS:
        details = warning_output.strip()
        suffix = f"\n{details}" if details else ""
        raise SpecLoadError(
            "drf-spectacular emitted warnings/errors; refusing to generate "
            "clients from an ambiguous contract. Fix the schema or set "
            f"{_ALLOW_SCHEMA_WARNINGS}=1 temporarily.{suffix}"
        )


__all__ = ["load_spec", "LoadMode"]
