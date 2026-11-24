"""progenitor Rust codegen wrapper.

Install: `cargo install cargo-progenitor --locked`.

progenitor (Oxide) reads an OpenAPI 3.0.x document and writes a whole Cargo
crate: typed models (via typify, serde) and an async `reqwest` client with
one builder-style method per operation. It is the Rust counterpart of ogen.
django-cfg emits 3.1, so the sliced spec is first lowered to the 3.0 shapes
progenitor's `openapiv3` parser accepts (``progenitor_spec``), and the crate
gets a hand-off module, ``src/django.rs``, that wires the base URL, the
Bearer token and the API key (see ``openapi_processor/rust``).
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import tomllib

from ...pipeline.errors import (
    ToolExecutionError,
    ToolNotInstalledError,
)

#: The progenitor this generator is written against: its spec limits, CLI flags and output layout.
#: Bump it together with the lowering in this module and `tests/unit/test_progenitor.py`.
PROGENITOR_VERSION = "0.17.0"
INSTALL_HINT = f"cargo install cargo-progenitor --version {PROGENITOR_VERSION} --locked"


@dataclass(slots=True)
class ProgenitorResult:
    output_dir: Path
    crate_name: str
    files: list[Path]


def find_binary() -> str | None:
    found = shutil.which("cargo-progenitor")
    if found:
        return found
    cargo_home = os.environ.get("CARGO_HOME") or str(Path(os.environ.get("HOME", "")) / ".cargo")
    candidate = Path(cargo_home) / "bin" / "cargo-progenitor"
    if candidate.is_file() and os.access(candidate, os.X_OK):
        return str(candidate)
    return None


def check() -> str | None:
    return None if find_binary() else INSTALL_HINT


def crate_name_for(out_dir: Path, explicit: str | None = None) -> str:
    """The Cargo package name: ``explicit``, else the output folder's name kebab-cased."""
    raw = explicit or out_dir.name
    name = re.sub(r"[^a-z0-9]+", "-", raw.lower()).strip("-")
    if not name or name[0].isdigit():
        name = f"api-{name}".rstrip("-")
    return name


# ── 3.1 → 3.0 lowering ───────────────────────────────────────────────

_NULL = {"type": "null"}


def _resolve(member: dict, schemas: dict) -> dict:
    if "$ref" in member:
        return schemas.get(member["$ref"].rsplit("/", 1)[-1], {})
    return member


def _blank_only(schema: dict) -> bool:
    return schema.get("maxLength") == 0 or schema.get("enum") == [""]


def _lower(node: Any, schemas: dict) -> None:
    """Rewrite, in place, the 3.1 constructs django-cfg emits that `openapiv3` refuses.

    * ``oneOf`` whose non-null branches are all strings → one string schema.
      drf-spectacular and the django-cfg enum hook emit them for blank-able
      fields (``oneOf [$ref Enum, {"enum": [""]}, null]``, and
      ``oneOf [{"format": "uri"}, {"maxLength": 0}]`` for
      ``URLField(blank=True)``). typify would turn them into an untagged enum
      of two `String` variants that cannot be told apart; one string with the
      merged enum accepts the same values.
    * ``oneOf``/``anyOf`` with a ``{"type": "null"}`` branch → the rest plus
      ``nullable: true`` (a lone ``$ref`` goes into ``allOf``, since a ``$ref``
      ignores its siblings).
    * ``type: [X, "null"]`` → ``type: X, nullable: true``.
    * ``const`` → a one-value ``enum``; ``examples`` → ``example``.
    * numeric ``exclusiveMinimum``/``exclusiveMaximum`` → the 3.0 boolean form.
    """
    if isinstance(node, list):
        for value in node:
            _lower(value, schemas)
        return
    if not isinstance(node, dict):
        return

    types = node.get("type")
    if isinstance(types, list):
        non_null = [t for t in types if t != "null"]
        if "null" in types:
            node["nullable"] = True
        node["type"] = non_null[0] if len(non_null) == 1 else non_null
        if not non_null:
            node.pop("type")

    for key in ("oneOf", "anyOf"):
        branches = node.get(key)
        if not isinstance(branches, list) or not branches:
            continue
        nullable = any(b == _NULL for b in branches)
        rest = [b for b in branches if b != _NULL]
        strings = [_resolve(b, schemas) for b in rest]
        if len(rest) > 1 and all(s.get("type") == "string" for s in strings):
            node.pop(key)
            node["type"] = "string"
            if all(isinstance(s.get("enum"), list) for s in strings):
                node["enum"] = list(dict.fromkeys(x for s in strings for x in s["enum"]))
            else:
                formats = {s.get("format") for s in strings if not _blank_only(s)}
                if len(formats) == 1 and None not in formats:
                    node["format"] = formats.pop()
        elif nullable and len(rest) == 1:
            node.pop(key)
            survivor = rest[0]
            if "$ref" in survivor:
                node["allOf"] = [survivor]
            else:
                for k, v in survivor.items():
                    node.setdefault(k, v)
        elif nullable:
            node[key] = rest
        else:
            continue
        if nullable:
            node["nullable"] = True
            if isinstance(node.get("enum"), list) and None not in node["enum"]:
                node["enum"].append(None)

    if "const" in node:
        node["enum"] = [node.pop("const")]
    if isinstance(node.get("examples"), list):
        examples = node.pop("examples")
        if examples and "example" not in node:
            node["example"] = examples[0]
    for bound, flag in (("exclusiveMinimum", "minimum"), ("exclusiveMaximum", "maximum")):
        value = node.get(bound)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            node[flag] = value
            node[bound] = True

    for key, value in node.items():
        if key == "example":
            continue
        if key in ("properties", "patternProperties") and isinstance(value, dict):
            # A map of field name → schema: a field may be called `const` or `type`.
            for schema in value.values():
                _lower(schema, schemas)
        else:
            _lower(value, schemas)


MULTIPART = "multipart/form-data"
_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")


def multipart_operations(spec: dict) -> list[tuple[str, str, dict]]:
    """``(path, method, operation)`` for every operation whose body is only ``multipart/form-data``."""
    found = []
    for path, item in (spec.get("paths") or {}).items():
        for method in _METHODS:
            op = item.get(method) if isinstance(item, dict) else None
            content = ((op or {}).get("requestBody") or {}).get("content") or {}
            if list(content) == [MULTIPART]:
                found.append((path, method, op))
    return found


def _drop_multipart(spec: dict) -> None:
    """progenitor refuses ``multipart/form-data``.

    A body that also has another media type keeps only the others. An operation
    whose body is multipart only is left out of progenitor's spec; the Rust
    post-processor writes its method by hand (``openapi_processor/rust``).
    """
    for path, method, _ in multipart_operations(spec):
        spec["paths"][path].pop(method)
        if not any(m in spec["paths"][path] for m in _METHODS):
            spec["paths"].pop(path)
    for item in (spec.get("paths") or {}).values():
        for method in _METHODS:
            content = ((item.get(method) or {}).get("requestBody") or {}).get("content")
            if isinstance(content, dict):
                content.pop(MULTIPART, None)


ERROR_BODY = "ApiErrorBody"
_SHAPE_KEYS = ("$ref", "type", "properties", "items", "allOf", "oneOf", "anyOf", "enum", "additionalProperties")


def _response_schemas(responses: dict, codes: list[str]) -> list[dict]:
    return [
        media["schema"]
        for code in codes
        for media in ((responses[code] or {}).get("content") or {}).values()
        if isinstance(media, dict) and isinstance(media.get("schema"), dict)
    ]


def _one_response_type(spec: dict) -> None:
    """progenitor asserts one success type and one error type per operation.

    drf-spectacular's ``OpenApiResponse(description=...)`` without a serializer
    becomes ``schema: {"description": "..."}``: any JSON, yet every such schema
    is a distinct type to typify. The text moves to the response's own
    ``description`` and the schema becomes ``{}`` (``serde_json::Value``). Error
    responses whose types still differ all become ``{}``: the client returns
    the body as JSON. Two different success types are a contract progenitor
    cannot express, so that fails, named.
    """
    for path, item in (spec.get("paths") or {}).items():
        for method in _METHODS:
            op = item.get(method) if isinstance(item, dict) else None
            responses = (op or {}).get("responses")
            if not isinstance(responses, dict):
                continue
            for response in responses.values():
                for media in ((response or {}).get("content") or {}).values():
                    schema = media.get("schema") if isinstance(media, dict) else None
                    if isinstance(schema, dict) and not any(k in schema for k in _SHAPE_KEYS):
                        if schema.get("description") and not response.get("description"):
                            response["description"] = schema["description"]
                        media["schema"] = {}
            success = [c for c in responses if c.startswith("2") or c == "default"]
            errors = [c for c in responses if c[0] in "45" or c == "default"]
            error_schemas = _response_schemas(responses, errors)
            distinct = {json.dumps(s, sort_keys=True) for s in error_schemas}
            if len(distinct) > 1 or (len(error_schemas) > 1 and "$ref" not in error_schemas[0]):
                # progenitor names an inline response schema per status, so even
                # identical inline bodies are distinct types: point them at one component.
                spec.setdefault("components", {}).setdefault("schemas", {})[ERROR_BODY] = {
                    "description": "An error body whose shape differs by status: the JSON as sent."
                }
                for schema in error_schemas:
                    schema.clear()
                    schema["$ref"] = f"#/components/schemas/{ERROR_BODY}"
            if len({json.dumps(s, sort_keys=True) for s in _response_schemas(responses, success)}) > 1:
                raise ToolExecutionError(
                    f"{method.upper()} {path} answers with more than one success type; progenitor (Rust) "
                    "takes one per operation. Give the view one 2xx serializer."
                )


def progenitor_spec(spec_path: Path) -> Path:
    """Write the spec progenitor reads: the same contract in OpenAPI 3.0.3 shapes."""
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    spec["openapi"] = "3.0.3"
    spec.pop("webhooks", None)
    spec.pop("jsonSchemaDialect", None)
    for key in [k for k in spec if k.startswith("x-")]:
        spec.pop(key)  # x-realtime & co.: not part of the REST contract
    _drop_multipart(spec)
    _one_response_type(spec)
    schemas = spec.get("components", {}).get("schemas", {})
    _lower(spec.get("paths", {}), schemas)
    for schema in schemas.values():
        _lower(schema, schemas)
    out = spec_path.with_name(spec_path.stem + ".progenitor.json")
    out.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return out


# ── Run ──────────────────────────────────────────────────────────────


def _client_version(cargo: Path) -> str | None:
    """The ``progenitor-client`` version a crate depends on: the generator's own, as the CLI has no ``--version``."""
    try:
        spec = tomllib.loads(cargo.read_text(encoding="utf-8")).get("dependencies", {}).get("progenitor-client")
    except (OSError, tomllib.TOMLDecodeError):
        return None
    version = spec.get("version") if isinstance(spec, dict) else spec
    return str(version).lstrip("=^~ ") if version else None

_RUSTFMT_SHIM = """#!/bin/sh
# django-cfg: cargo-progenitor asks rustfmt for two nightly-only options
# (wrap_comments, normalize_doc_attributes) and stops on a stable rustfmt.
# Stable formats the same code without them; drop the flag, keep the rest.
for arg; do
  shift
  [ "$arg" = "--unstable-features" ] || set -- "$@" "$arg"
done
exec "{rustfmt}" "$@"
"""


def _rustfmt(work_dir: Path) -> str:
    """The rustfmt cargo-progenitor runs: ``$RUSTFMT``, a nightly one, else a shim over stable."""
    explicit = os.environ.get("RUSTFMT")
    if explicit:
        return explicit
    rustup = shutil.which("rustup") or str(Path(os.environ.get("HOME", "")) / ".cargo" / "bin" / "rustup")
    try:
        nightly = subprocess.run(
            [rustup, "which", "--toolchain", "nightly", "rustfmt"], capture_output=True, text=True, check=True
        ).stdout.strip()
        if nightly:
            return nightly
    except (OSError, subprocess.CalledProcessError):
        pass
    stable = shutil.which("rustfmt") or str(Path(os.environ.get("HOME", "")) / ".cargo" / "bin" / "rustfmt")
    if not Path(stable).is_file():
        raise ToolNotInstalledError("rustfmt not found. Install: rustup component add rustfmt")
    shim = work_dir / "rustfmt-stable.sh"
    shim.write_text(_RUSTFMT_SHIM.format(rustfmt=stable), encoding="utf-8")
    shim.chmod(0o755)
    return str(shim)



def generate(
    spec_path: Path,
    out_dir: Path,
    *,
    crate_name: str,
    crate_version: str = "0.1.0",
) -> ProgenitorResult:
    binary = find_binary()
    if binary is None:
        raise ToolNotInstalledError(f"cargo-progenitor not found on PATH. Install: {INSTALL_HINT}")

    if out_dir.exists():
        for child in out_dir.iterdir():
            if child.name == "target":
                continue  # cargo's build cache of the consumer: not ours, and costly to rebuild
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        out_dir.mkdir(parents=True)

    cmd = [
        binary,
        "progenitor",
        "--input", str(progenitor_spec(spec_path)),
        "--output", str(out_dir),
        "--name", crate_name,
        "--version", crate_version,
        "--interface", "builder",
        "--tags", "merged",
        "--license-name", "MIT",
    ]
    env = {**os.environ, "RUSTFMT": _rustfmt(spec_path.parent)}
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True, env=env)
    except subprocess.CalledProcessError as e:
        detail = (e.stderr or e.stdout or "").strip()
        raise ToolExecutionError(f"progenitor exit {e.returncode}: {detail[-2000:]}") from e

    installed = _client_version(out_dir / "Cargo.toml")
    if installed != PROGENITOR_VERSION:
        raise ToolNotInstalledError(
            f"cargo-progenitor {installed or '?'} is installed, django-cfg is written against {PROGENITOR_VERSION}. "
            f"Install: {INSTALL_HINT}"
        )

    files = sorted(p for p in out_dir.rglob("*") if p.is_file() and "target" not in p.relative_to(out_dir).parts)
    return ProgenitorResult(output_dir=out_dir, crate_name=crate_name, files=files)
