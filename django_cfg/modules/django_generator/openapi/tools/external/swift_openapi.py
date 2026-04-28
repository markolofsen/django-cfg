"""swift-openapi-generator (Apple) wrapper.

Install: `brew install apple/tap/swift-openapi-generator`.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ...pipeline.errors import (
    ToolExecutionError,
    ToolNotInstalledError,
)

INSTALL_HINT = "brew install apple/tap/swift-openapi-generator"


@dataclass(slots=True)
class SwiftOpenAPIResult:
    output_dir: Path
    files: list[Path]


def check() -> str | None:
    return None if shutil.which("swift-openapi-generator") else INSTALL_HINT


def generate(
    spec_path: Path,
    out_dir: Path,
    *,
    module_name: str = "API",
) -> SwiftOpenAPIResult:
    del module_name  # Apple's CLI doesn't accept this — module is set by SwiftPM.
    binary = shutil.which("swift-openapi-generator")
    if binary is None:
        raise ToolNotInstalledError(
            f"swift-openapi-generator not found. Install: {INSTALL_HINT}"
        )

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    cmd = [
        binary, "generate", str(spec_path),
        "--mode", "types",
        "--mode", "client",
        "--output-directory", str(out_dir),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise ToolExecutionError(
            f"swift-openapi-generator exit {e.returncode}: {e.stderr}"
        ) from e

    files = sorted(p for p in out_dir.rglob("*.swift") if p.is_file())
    return SwiftOpenAPIResult(output_dir=out_dir, files=files)
