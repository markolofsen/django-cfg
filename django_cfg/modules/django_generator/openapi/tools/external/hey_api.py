"""@hey-api/openapi-ts CLI wrapper. Requires Node 18+ + npx on PATH.

Uses Hey API's native `operations.strategy: 'byTags'` to group SDK methods
by OpenAPI tag — emits one container class per tag (`AccountsSdk`,
`ProfilesSdk`, …) sharing a single `types.gen.ts` (no schema duplication).

We pass the config via a JS file because CLI flags don't expose nested
plugin options.
"""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from ...pipeline.errors import ToolExecutionError, ToolNotInstalledError

INSTALL_HINT = "ensure node + npx are on PATH (Node 18+)"

# `latest`, by owner decision (2026-08-16): the generator tracks upstream rather
# than being bumped by hand.
#
# The cost is stated plainly because it was once the reason for a pin (W2.1): a
# new hey-api release can change SDK/type naming, enum output, or file layout,
# so two runs of the SAME spec on different days can produce different files.
# The generated tree is committed, so that shows up as a diff nobody wrote —
# review it as a real change, not as noise, and re-verify the clients when it
# appears.
HEY_API_VERSION = "latest"


@dataclass(slots=True)
class HeyApiResult:
    output_dir: Path
    files: list[Path]


def check() -> str | None:
    return None if shutil.which("npx") else INSTALL_HINT


def generate(
    spec_path: Path,
    out_dir: Path,
    *,
    client: str = "fetch",
    plugins: list[str] | None = None,
    sdk_strategy: str = "byTags",
) -> HeyApiResult:
    """Generate Hey API client.

    Args:
      spec_path: OpenAPI 3.x spec (already sliced by caller if needed).
      out_dir: destination — wiped + recreated.
      client: Hey API client variant ("fetch", "axios", "next", …).
      plugins: extra plugins (e.g. ["zod"]); we always include @hey-api/sdk.
      sdk_strategy: SDK grouping — "byTags" | "single" | "flat".
        - byTags (default): one class per OpenAPI tag, shared types.gen.ts.
        - single: one class for all ops.
        - flat: tree-shakeable functions (no classes).
    """
    if shutil.which("npx") is None:
        raise ToolNotInstalledError(f"npx not found on PATH. {INSTALL_HINT}")

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    config_path = _write_config(spec_path, out_dir, client, plugins, sdk_strategy)

    cmd = ["npx", "-y", f"@hey-api/openapi-ts@{HEY_API_VERSION}", "-f", str(config_path)]
    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        raise ToolExecutionError(f"hey-api exit {e.returncode}: {e.stderr}") from e
    finally:
        # Always wipe the temp config — even on failure — so neither the next
        # run nor the user's source tree carries stale build artefacts.
        config_path.unlink(missing_ok=True)

    _normalize_whitespace_only_lines(out_dir)
    files = sorted(p for p in out_dir.rglob("*") if p.is_file())
    return HeyApiResult(output_dir=out_dir, files=files)


def _normalize_whitespace_only_lines(output: Path) -> None:
    """Remove indentation from otherwise-empty generated text lines.

    Hey API emits spaces on some separator lines in ``sdk.gen.ts`` (seen in
    0.99.0; the version now floats, so this stays defensive rather than
    tracking one release).
    Normalizing those lines keeps generated output friendly to ``git diff
    --check`` without touching non-empty lines, where trailing whitespace can
    be meaningful inside a TypeScript template literal.
    """
    paths = (output,) if output.is_file() else output.rglob("*")
    for path in paths:
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        normalized = "\n".join("" if line.isspace() else line for line in text.split("\n"))
        if normalized != text:
            path.write_text(normalized, encoding="utf-8")


def _write_config(
    spec_path: Path,
    out_dir: Path,
    client: str,
    extra_plugins: list[str] | None,
    sdk_strategy: str,
) -> Path:
    """Emit a Hey API config (.mjs) capturing nested plugin options.

    Lives next to the cached spec (under `.cache/runs/<target>/`) so it
    never pollutes the user's frontend tree, even if cleanup is skipped
    by an OS interrupt.
    """
    config_path = spec_path.parent / "heyapi.config.mjs"
    plugin_lines: list[str] = [
        f"  '@hey-api/client-{client}',",
        # `enums: { enabled, mode: 'typescript' }` materializes string-enum
        # schemas as `export enum <Op><Field>` — so consumers can use the
        # runtime constants (e.g. `EventType.JS_ERROR`) instead of inlined
        # string-literal unions.
        "  { name: '@hey-api/typescript', enums: { enabled: true, mode: 'typescript' } },",
        f"  {{ name: '@hey-api/sdk', operations: {{ strategy: '{sdk_strategy}' }} }},",
    ]
    for p in extra_plugins or []:
        plugin_lines.append(f"  '{p}',")

    body = (
        "export default {\n"
        f"  input: {_js_str(str(spec_path))},\n"
        f"  output: {_js_str(str(out_dir))},\n"
        "  plugins: [\n"
        + "\n".join(plugin_lines)
        + "\n  ],\n"
        "};\n"
    )
    config_path.write_text(body, encoding="utf-8")
    return config_path


def _js_str(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"
