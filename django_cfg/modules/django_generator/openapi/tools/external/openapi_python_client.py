"""openapi-python-client CLI wrapper.

Use an exact uvx package version; direct binaries must report that same version.
"""

from __future__ import annotations

import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ...pipeline.errors import (
    ToolExecutionError,
    ToolNotInstalledError,
)

VERSION = "0.28.4"
INSTALL_HINT = f"install openapi-python-client=={VERSION} (or use uvx with that exact version)"


@dataclass(slots=True)
class OpenAPIPyResult:
    output_dir: Path
    files: list[Path]


def _resolve_invocation() -> list[str] | None:
    if shutil.which("uvx"):
        return ["uvx", "--from", f"openapi-python-client=={VERSION}", "openapi-python-client"]
    binary = shutil.which("openapi-python-client")
    if binary:
        try:
            result = subprocess.run([binary, "--version"], capture_output=True, text=True, timeout=10)  # noqa: S603 -- resolved generator executable, fixed argument, no shell
            version = re.search(r"\b\d+\.\d+\.\d+(?:[a-zA-Z0-9.+-]*)?", result.stdout)
            if result.returncode == 0 and version and version.group() == VERSION:
                return [binary]
        except (OSError, subprocess.SubprocessError):
            pass
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
            subprocess.run(cmd, check=True, input=config, text=True, capture_output=True)  # noqa: S603 -- fixed generator argv and path arguments, no shell
        else:
            subprocess.run(cmd, check=True, capture_output=True, text=True)  # noqa: S603 -- fixed generator argv and path arguments, no shell
    except subprocess.CalledProcessError as e:
        raise ToolExecutionError(
            f"openapi-python-client exit {e.returncode}: {e.stderr}"
        ) from e

    files = sorted(p for p in out_dir.rglob("*.py") if p.is_file())
    return OpenAPIPyResult(output_dir=out_dir, files=files)
