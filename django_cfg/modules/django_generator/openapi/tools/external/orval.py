"""Pinned Orval CLI wrapper for TypeScript React Query clients.

Orval is intentionally installed by the frontend workspace, not by the Python
package. The Django generator owns the OpenAPI slice and invokes the pinned
workspace binary through ``pnpm exec``. This keeps generation reproducible and
avoids the floating ``npx ...@latest`` behavior of the old Hey API wrapper.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ...pipeline.errors import ToolExecutionError, ToolNotInstalledError
from ..realtime import generate_realtime

MIN_NODE = (22, 18)
ORVAL_VERSION = "8.48.0"
INSTALL_HINT = (
    "install Node >= 22.18, pnpm, and the frontend workspace dependencies "
    f"(including orval@{ORVAL_VERSION})"
)


@dataclass(slots=True)
class OrvalResult:
    output_dir: Path
    files: list[Path]


def node_version() -> tuple[int, int] | None:
    """Return the Node major/minor on PATH, or ``None`` when unavailable."""
    node = shutil.which("node")
    if node is None:
        return None
    try:
        output = subprocess.run(
            [node, "--version"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        ).stdout.strip()
        version = output.lstrip("v").split(".")
        return int(version[0]), int(version[1])
    except (OSError, ValueError, IndexError, subprocess.SubprocessError):
        return None


def check() -> str | None:
    """Return a human-readable toolchain problem, if one is detected."""
    if shutil.which("pnpm") is None:
        return f"pnpm is not on PATH: {INSTALL_HINT}"
    version = node_version()
    if version is None:
        return f"node is not available or unreadable: {INSTALL_HINT}"
    if version < MIN_NODE:
        return f"node {version[0]}.{version[1]} is too old: {INSTALL_HINT}"
    return None


def generate(
    spec_path: Path,
    out_dir: Path,
    *,
    cwd: Path,
    mock: bool = True,
    prettier: bool = True,
    mutator_import: str | None = None,
) -> OrvalResult:
    """Generate a clean Orval React Query/Zod/MSW tree.

    ``cwd`` must be the frontend workspace containing the pinned Orval binary.
    The generated tree is intentionally disposable: endpoint files, models,
    and mocks are all emitted below ``out_dir``.
    """
    problem = check()
    if problem:
        raise ToolNotInstalledError(problem)

    if not cwd.is_dir():
        raise ToolNotInstalledError(f"Orval workspace does not exist: {cwd}")
    if not (cwd / "package.json").is_file():
        raise ToolNotInstalledError(f"Orval workspace has no package.json: {cwd}")

    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    # Orval resolves the mutator from the generated tree. Keep a tiny shim in
    # that tree so the generated imports remain valid after the Python
    # pipeline stages the tree into the consumer directory. The shim points at
    # the handwritten runtime; it is recreated on every generation and is not
    # itself the source of truth.
    mutator_path: Path | None = None
    if mutator_import:
        runtime_dir = out_dir / "runtime"
        runtime_dir.mkdir(parents=True)
        mutator_path = runtime_dir / "orval-mutator.ts"
        mutator_path.write_text(
            f"export {{ djangoFetch }} from {json.dumps(mutator_import)};\n"
            f"export type {{ BodyType, ErrorType, DjangoRequestInit }} from "
            f"{json.dumps(mutator_import)};\n",
            encoding="utf-8",
        )

    config_path = spec_path.parent / "orval.config.mjs"
    config = {
        "djangocfg": {
            "input": {"target": str(spec_path.resolve())},
            "output": {
                "mode": "tags-split",
                "target": str((out_dir / "endpoints").resolve()),
                "schemas": {
                    "path": str((out_dir / "models").resolve()),
                    "type": "zod",
                },
                "client": "react-query",
                "httpClient": "fetch",
                "mock": mock,
                "prettier": prettier,
                "override": {
                    # Orval otherwise falls back to React Query v4 when the
                    # config is run from a staging directory that has no
                    # package.json dependency metadata.
                    "query": {"version": 5},
                    "includeZodSchemaInArguments": True,
                    **(
                        {
                            "mutator": {
                                "path": str(mutator_path.resolve()),
                                "name": "djangoFetch",
                            }
                        }
                        if mutator_path is not None
                        else {}
                    ),
                    "fetch": {
                        "runtimeValidation": {"strategy": "both"},
                        "forceSuccessResponse": True,
                        "includeHttpResponseReturnType": False,
                    },
                },
            },
        }
    }
    config_path.write_text(
        "export default " + json.dumps(config, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )

    cmd = ["pnpm", "exec", "orval", "--config", str(config_path)]
    try:
        subprocess.run(
            cmd,
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or "").strip()
        raise ToolExecutionError(
            f"orval exit {exc.returncode}: {detail or 'no diagnostic output'}"
        ) from exc
    finally:
        config_path.unlink(missing_ok=True)

    # Orval intentionally ignores vendor extensions such as ``x-realtime``.
    # Render WebSocket topic builders as a separate protocol adapter beside
    # the generated REST tree, importing the Zod models Orval just produced.
    document = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    generate_realtime(document.get("x-realtime"), out_dir)

    files = sorted(path for path in out_dir.rglob("*") if path.is_file())
    if not files:
        raise ToolExecutionError("orval completed without writing generated files")
    return OrvalResult(output_dir=out_dir, files=files)


__all__ = ["ORVAL_VERSION", "OrvalResult", "check", "generate", "node_version"]
