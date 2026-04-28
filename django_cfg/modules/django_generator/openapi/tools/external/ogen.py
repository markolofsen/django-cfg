"""ogen Go codegen wrapper.

Install: `go install github.com/ogen-go/ogen/cmd/ogen@latest`.
"""

from __future__ import annotations

import os
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
        str(spec_path),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise ToolExecutionError(f"ogen exit {e.returncode}: {e.stderr}") from e

    files = sorted(p for p in out_dir.rglob("*.go") if p.is_file())
    return OgenResult(output_dir=out_dir, files=files)
