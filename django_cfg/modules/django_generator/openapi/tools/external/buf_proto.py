"""buf generate wrapper. Fans out a proto/ tree to N language outputs.

Install: `brew install bufbuild/buf/buf`. Apple's Swift plugins are local
binaries — install via `brew install swift-protobuf grpc-swift`.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ...pipeline.errors import (
    ToolExecutionError,
    ToolNotInstalledError,
)

INSTALL_HINT = "brew install bufbuild/buf/buf"

_PLUGIN_ALIASES: dict[str, str] = {
    "go": "buf.build/protocolbuffers/go",
    "go-grpc": "buf.build/grpc/go",
    "connect-go": "buf.build/connectrpc/go",
    "es": "buf.build/bufbuild/es",
    "connect-es": "buf.build/connectrpc/es",
    "swift": "local:protoc-gen-swift",
    "grpc-swift": "local:protoc-gen-grpc-swift-2",
}


@dataclass(slots=True)
class BufResult:
    output_dir: Path
    files: list[Path]


def check() -> str | None:
    return None if shutil.which("buf") else INSTALL_HINT


def _normalize_plugin(p: str) -> str:
    return _PLUGIN_ALIASES.get(p, p)


def _build_template(
    out_dir: Path,
    plugins: list[str],
    plugin_options: dict[str, list[str]],
) -> dict[str, object]:
    items: list[dict[str, object]] = []
    for alias in plugins:
        canonical = _normalize_plugin(alias)
        if canonical.startswith("local:"):
            entry: dict[str, object] = {
                "local": canonical.removeprefix("local:"),
                "out": str(out_dir),
            }
        else:
            entry = {"remote": canonical, "out": str(out_dir)}
        opts = plugin_options.get(alias) or plugin_options.get(canonical)
        if opts:
            entry["opt"] = list(opts)
        items.append(entry)
    return {"version": "v2", "plugins": items}


def generate(
    proto_dir: Path,
    out_dir: Path,
    *,
    plugins: list[str],
    plugin_options: dict[str, list[str]] | None = None,
    cache_dir: Path | None = None,
) -> BufResult:
    if shutil.which("buf") is None:
        raise ToolNotInstalledError(f"buf not found. Install: {INSTALL_HINT}")
    if not proto_dir.is_dir():
        raise ToolExecutionError(f"proto source dir not found: {proto_dir}")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    template = _build_template(out_dir, plugins, plugin_options or {})
    cache = cache_dir or (out_dir.parent / ".buf_cache")
    cache.mkdir(parents=True, exist_ok=True)
    template_path = cache / "buf.gen.json"
    template_path.write_text(json.dumps(template, indent=2))

    cmd = ["buf", "generate", str(proto_dir), "--template", str(template_path)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise ToolExecutionError(f"buf exit {e.returncode}: {e.stderr}") from e

    files = sorted(p for p in out_dir.rglob("*") if p.is_file())
    return BufResult(output_dir=out_dir, files=files)
