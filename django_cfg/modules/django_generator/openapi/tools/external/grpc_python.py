"""grpc_tools.protoc wrapper — Python proto + gRPC stubs."""

from __future__ import annotations

import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

from ...pipeline.errors import (
    ToolExecutionError,
    ToolNotInstalledError,
)

INSTALL_HINT = "pip install grpcio-tools  (or: django-cfg[grpc] extra)"


@dataclass(slots=True)
class ProtoPythonResult:
    output_dir: Path
    files: list[Path]


def check() -> str | None:
    try:
        import grpc_tools.protoc  # noqa: F401
    except ImportError:
        return INSTALL_HINT
    return None


def generate(proto_dir: Path, out_dir: Path) -> ProtoPythonResult:
    if check() is not None:
        raise ToolNotInstalledError(f"grpc_tools not importable. {INSTALL_HINT}")
    if not proto_dir.is_dir():
        raise ToolExecutionError(f"proto source dir not found: {proto_dir}")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)
    (out_dir / "__init__.py").touch()

    for sub in sorted(p for p in proto_dir.rglob("*") if p.is_dir()):
        rel = sub.relative_to(proto_dir)
        mirror = out_dir / rel
        mirror.mkdir(parents=True, exist_ok=True)
        (mirror / "__init__.py").touch()

    proto_files = sorted(proto_dir.rglob("*.proto"))
    if not proto_files:
        raise ToolExecutionError(f"no .proto files under {proto_dir}")

    cmd = [
        sys.executable, "-m", "grpc_tools.protoc",
        f"-I{proto_dir}",
        f"--python_out={out_dir}",
        f"--grpc_python_out={out_dir}",
        f"--pyi_out={out_dir}",
        *(str(p) for p in proto_files),
    ]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise ToolExecutionError(f"protoc exit {e.returncode}: {e.stderr}") from e

    files = sorted(p for p in out_dir.rglob("*.py") if p.is_file())
    files += sorted(p for p in out_dir.rglob("*.pyi") if p.is_file())
    return ProtoPythonResult(output_dir=out_dir, files=files)
