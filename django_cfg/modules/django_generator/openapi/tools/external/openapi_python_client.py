"""openapi-python-client CLI wrapper.

Prefer `uvx` (zero-install on PATH); fall back to direct binary if available.
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

INSTALL_HINT = (
    "pip install openapi-python-client  (or: uv tool install openapi-python-client)"
)


@dataclass(slots=True)
class OpenAPIPyResult:
    output_dir: Path
    files: list[Path]


def _resolve_invocation() -> list[str] | None:
    if shutil.which("uvx"):
        return ["uvx", "openapi-python-client"]
    if shutil.which("openapi-python-client"):
        return ["openapi-python-client"]
    return None


def check() -> str | None:
    return None if _resolve_invocation() else INSTALL_HINT


def generate(
    spec_path: Path,
    out_dir: Path,
    *,
    package_name: str | None = None,
) -> OpenAPIPyResult:
    invoke = _resolve_invocation()
    if invoke is None:
        raise ToolNotInstalledError(
            f"openapi-python-client not found on PATH. {INSTALL_HINT}"
        )

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        *invoke, "generate",
        "--path", str(spec_path),
        "--output-path", str(out_dir),
        "--meta", "none",
        "--overwrite",
    ]
    try:
        if package_name:
            cmd += ["--config", "/dev/stdin"]
            config = f"package_name_override: {package_name}\n"
            subprocess.run(cmd, check=True, input=config, text=True, capture_output=True)
        else:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise ToolExecutionError(
            f"openapi-python-client exit {e.returncode}: {e.stderr}"
        ) from e

    files = sorted(p for p in out_dir.rglob("*.py") if p.is_file())
    return OpenAPIPyResult(output_dir=out_dir, files=files)
