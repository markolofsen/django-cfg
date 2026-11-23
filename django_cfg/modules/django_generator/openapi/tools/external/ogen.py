"""ogen Go codegen wrapper.

Install: `go install github.com/ogen-go/ogen/cmd/ogen@latest`.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ...pipeline.errors import (
    ToolExecutionError,
    ToolNotInstalledError,
)

INSTALL_HINT = "go install github.com/ogen-go/ogen/cmd/ogen@latest"


@dataclass(slots=True)
class OgenResult:
    output_dir: Path
    files: list[Path]


def find_binary() -> str | None:
    found = shutil.which("ogen")
    if found:
        return found
    home = os.environ.get("HOME", "")
    candidates = [
        Path(os.environ.get("GOPATH", "")) / "bin" / "ogen",
        Path(home) / "go" / "bin" / "ogen",
    ]
    for c in candidates:
        if c.is_file() and os.access(c, os.X_OK):
            return str(c)
    return None


def check() -> str | None:
    return None if find_binary() else INSTALL_HINT


def _string_branch(member: dict, schemas: dict) -> dict | None:
    """The string schema a `oneOf` member stands for (`$ref` resolved), else None."""
    if "$ref" in member:
        member = schemas.get(member["$ref"].rsplit("/", 1)[-1], {})
    return member if member.get("type") == "string" else None


def _blank_only(schema: dict) -> bool:
    """A branch that admits only the empty string."""
    return schema.get("maxLength") == 0 or schema.get("enum") == [""]


def _merge_string_unions(node: object, schemas: dict) -> int:
    """Collapse every `oneOf` whose branches are all strings (plus an optional null).

    drf-spectacular and the django-cfg hooks emit such unions for blank-able
    fields: `oneOf [$ref Enum, {"enum": [""]}, null]` for a choice, and
    `oneOf [{"format": "uri"}, {"maxLength": 0}]` for `URLField(blank=True)`.
    ogen cannot tell two string branches apart ("discriminator inference not
    implemented") and, with `ignore_not_implemented`, drops the whole operation
    and every schema only it used. One string schema accepts the same values:
    the merged enum when every branch is an enum, else a plain string. ogen
    names an inline enum after the field (`<Schema><Field>`), as the Go clients
    did before Orval.
    """
    merged = 0
    if isinstance(node, dict):
        branches = node.get("oneOf")
        if isinstance(branches, list) and branches:
            nullable = any(b == {"type": "null"} for b in branches)
            rest = [_string_branch(b, schemas) for b in branches if b != {"type": "null"}]
            if len(rest) > 1 and all(r is not None for r in rest):
                node.pop("oneOf")
                node["type"] = ["string", "null"] if nullable else "string"
                if all(isinstance(r.get("enum"), list) for r in rest):
                    enum = list(dict.fromkeys(x for r in rest for x in r["enum"]))
                    node["enum"] = enum + ([None] if nullable else [])
                else:
                    # `URLField(blank=True)`: keep the real branch's format (Go `url.URL`),
                    # the blank branch adds only "" and Go's url.Parse("") accepts it.
                    formats = {r.get("format") for r in rest if not _blank_only(r)}
                    if len(formats) == 1 and None not in formats:
                        node["format"] = formats.pop()
                merged += 1
        for value in node.values():
            merged += _merge_string_unions(value, schemas)
    elif isinstance(node, list):
        for value in node:
            merged += _merge_string_unions(value, schemas)
    return merged


def ogen_spec(spec_path: Path) -> Path:
    """Write the spec ogen reads: the same contract, string unions inlined."""
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    schemas = spec.get("components", {}).get("schemas", {})
    _merge_string_unions(spec.get("paths", {}), schemas)
    for schema in schemas.values():
        _merge_string_unions(schema, schemas)
    out = spec_path.with_name(spec_path.stem + ".ogen.json")
    out.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    return out


_SKIPPED_RE = re.compile(r"Skipping operation\s+(\{.*\})")


def generate(spec_path: Path, out_dir: Path, *, package: str = "api") -> OgenResult:
    binary = find_binary()
    if binary is None:
        raise ToolNotInstalledError(f"ogen not found on PATH. Install: {INSTALL_HINT}")

    if out_dir.exists():
        for child in out_dir.iterdir():
            if child.is_dir():
                shutil.rmtree(child)
            else:
                child.unlink()
    else:
        out_dir.mkdir(parents=True)

    # Drop unsupported OpenAPI features (e.g. "complex defaults") rather
    # than failing the whole target. drf-spectacular emits constructs
    # ogen cannot model — letting ogen skip them keeps the rest of the
    # client compilable. Written as a sibling to the spec so it isn't
    # confused for project-scoped config.
    config_path = spec_path.parent / ".ogen.yml"
    config_path.write_text(
        "generator:\n"
        "  ignore_not_implemented:\n"
        "    - all\n",
        encoding="utf-8",
    )

    cmd = [
        binary,
        "--config", str(config_path),
        "--target", str(out_dir),
        "--package", package,
        "--clean",
        str(ogen_spec(spec_path)),
    ]
    try:
        run = subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise ToolExecutionError(f"ogen exit {e.returncode}: {e.stderr}") from e

    # `ignore_not_implemented` keeps a target alive past one exotic schema, but a
    # skipped operation is a client without that call and without its types: the
    # Go code that uses them stops compiling, far from the cause. Fail here.
    skipped = _SKIPPED_RE.findall(run.stdout + run.stderr)
    if skipped:
        raise ToolExecutionError(
            f"ogen skipped {len(skipped)} operation(s), the Go client would lack them: "
            + "; ".join(skipped[:5])
        )

    files = sorted(p for p in out_dir.rglob("*.go") if p.is_file())
    return OgenResult(output_dir=out_dir, files=files)
