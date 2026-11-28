"""Pinned Orval wrapper for TypeScript web and standalone CLI clients.

Orval is intentionally installed by the frontend workspace, not by the Python
package. The Django generator owns the OpenAPI slice and invokes the pinned
workspace binary through ``pnpm exec``. This keeps generation reproducible and
avoids the floating ``npx ...@latest`` behavior of the old Hey API wrapper.

Output hygiene (H2.9a of ``@dev/active/orval-client-hardening``):

* Every file Orval writes starts with a banner: the Orval version and the
  django-cfg contract (``info["x-cfg-contract"]``, stamped into the slice by
  ``dispatch.run_single``). The django-cfg release is left out on purpose, or
  every generated file would change on every release; it stays in the stamped
  ``openapi.json`` and in ``runtime/cfg.ts`` (``render_cfg_ts``).
* Orval reads the consumer's ``package.json``, the nearest one above the folder
  the tree is published to, for the TypeScript, TanStack Query, Zod and Faker
  versions its output depends on.
* The tree is formatted with prettier using the config a file in the consumer
  folder gets. Orval's own ``formatter`` option is not used: it resolves the
  config from where it writes, which with ``source_root`` is the Django project,
  so it applied prettier's defaults instead of the frontend's config.

The mutator (H2.5): ``runtime/orval-mutator.ts`` in the tree is a generated
two-parameter wrapper around the runtime's ``djangoFetch``, not a re-export.
Orval reads that file as text: a re-export counts as one parameter, so
operations took ``RequestInit``, hooks had no ``request`` and ``TError`` was
``unknown``. See ``render_mutator_shim``.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from django_cfg.core.contract import (
    AUTH_SIGN_IN,
    CFG_VERSION,
    CONTRACT_SINCE,
    SPEC_KEY_AUTH,
    SPEC_KEY_CONTRACT,
    SPEC_KEY_VERSION,
)

from ...pipeline.errors import (
    PostprocessError,
    SliceError,
    ToolExecutionError,
    ToolNotInstalledError,
)
from ..realtime import generate_realtime
from ..realtime.query_topics import (
    REALTIME_QUERY_FILE,
    RealtimeInvalidationError,
    invalidating_queries,
    query_option_overrides,
    render_realtime_query,
)
from .cli_mutator import render_cli_mutator

MIN_NODE = (22, 18)
ORVAL_VERSION = "8.48.0"
INSTALL_HINT = (
    "install Node >= 22.18, pnpm, and the frontend workspace dependencies "
    f"(including orval@{ORVAL_VERSION})"
)
_FORMAT_TIMEOUT_S = 300


@dataclass(slots=True)
class OrvalResult:
    output_dir: Path
    files: list[Path]
    #: What formatted the tree, for example ``prettier 3.9.10, config /…/.prettierrc``; ``None`` when it was not formatted.
    formatter: str | None = None


def node_version() -> tuple[int, int] | None:
    """Return the Node major/minor on PATH, or ``None`` when unavailable."""
    node = shutil.which("node")
    if node is None:
        return None
    try:
        output = subprocess.run(  # noqa: S603 -- resolved Node executable and fixed version argument, no shell
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


def installed_version(workspace: Path) -> str | None:
    """The orval version installed in the frontend workspace, or ``None`` when it is not installed."""
    try:
        package = json.loads((Path(workspace) / "node_modules" / "orval" / "package.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    version = package.get("version") if isinstance(package, dict) else None
    return version if isinstance(version, str) else None


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


#: The runtime package. Its root exports `djangoFetch`, `DjangoRequestInit` and `ApiClientError`.
RUNTIME_PACKAGE = "@djangocfg/api"
AUTH_MODES = ("default", "public")


@dataclass(frozen=True, slots=True)
class RuntimeImport:
    """Where the generated shim takes the runtime from.

    ``fetch`` exports ``djangoFetch`` and ``DjangoRequestInit``: the package, or a relative path to a hand-written
    ``runtime/orval-mutator.ts`` above the tree. ``errors`` exports ``ApiClientError`` when ``fetch`` does not.
    """

    fetch: str
    errors: str | None = None


def render_mutator_shim(runtime: RuntimeImport, *, auth_mode: str = "default") -> str:
    """The text of ``runtime/orval-mutator.ts``, the mutator every generated operation calls.

    Orval reads this file as text, so its shape is the contract:

    * ``djangoFetch`` takes two declared parameters. Orval then types ``options`` as ``DjangoRequestInit`` in every
      operation, gives every hook ``request``, and lets mutation hooks pass it.
    * ``export type ErrorType`` / ``export type BodyType`` are literal declarations here (Orval greps for them, a
      re-export does not count), so ``TError`` is ``ApiClientError``. The unused parameter is ``_Error``, so a consumer
      with ``noUnusedParameters`` still type-checks.
    * ``auth_mode="public"``: every call is sent with ``auth: 'none'`` after the caller's options, so no caller can
      add the session's Bearer.
    """
    if auth_mode not in AUTH_MODES:
        raise ValueError(f"auth_mode must be one of {', '.join(AUTH_MODES)}, not {auth_mode!r}")
    if runtime.errors is None:
        imports = (
            "import { djangoFetch as runtimeFetch, type ApiClientError, type DjangoRequestInit } from "
            f"{json.dumps(runtime.fetch)};\n"
        )
    else:
        imports = (
            f"import type {{ ApiClientError }} from {json.dumps(runtime.errors)};\n"
            "import { djangoFetch as runtimeFetch, type DjangoRequestInit } from "
            f"{json.dumps(runtime.fetch)};\n"
        )
    call = "runtimeFetch<T>(url, { ...options, auth: 'none' })" if auth_mode == "public" else "runtimeFetch<T>(url, options)"
    policy = (
        "// Public target: every request goes without the session (`auth: 'none'`), whatever the caller passes.\n"
        if auth_mode == "public"
        else ""
    )
    return (
        "// The Orval mutator of this tree, generated by django-cfg: do not edit, re-run `make gen`.\n"
        "// Orval reads this file as text: two declared parameters give every operation `options?: DjangoRequestInit`\n"
        "// and every hook `request`; the literal `ErrorType` and `BodyType` type `TError` and request bodies.\n"
        + imports
        + "\n"
        "export type ErrorType<_Error> = ApiClientError;\n"
        "export type BodyType<BodyData> = BodyData;\n"
        "export type { DjangoRequestInit };\n"
        "\n"
        + policy
        + f"export const djangoFetch = <T>(url: string, options?: DjangoRequestInit): Promise<T> =>\n  {call};\n"
    )


_HTTP_METHODS = ("get", "put", "post", "delete", "options", "head", "patch", "trace")
#: `override.query` for the `infinite` Target option. Candidates in priority order: django-cfg's page number, then a
#: cursor. An operation with neither query parameter gets no infinite hook.
_INFINITE_QUERY = {"useInfinite": True, "useInfiniteQueryParam": ["page", "cursor"]}


def _operations(document: dict[str, Any]):
    for path, item in (document.get("paths") or {}).items():
        if not isinstance(item, dict):
            continue
        for method in _HTTP_METHODS:
            op = item.get(method)
            if isinstance(op, dict):
                yield path, method, op


def _accepts_no_auth(op: dict[str, Any], document_security: Any) -> bool:
    """The operation takes no credentials: `security` is `[{}]` or `[]`, or absent with no document-level `security`.

    `[{"jwt": []}, {}]` is optional auth (a session is used when there is one) and does not count. An absent `security`
    inherits the document's, so it means "no auth" only when the document declares none.
    """
    security = op["security"] if "security" in op else (document_security or [])
    return isinstance(security, list) and all(requirement == {} for requirement in security)


def request_option_overrides(
    document: dict[str, Any], *, direct_origin_tags: tuple[str, ...] | list[str] = ()
) -> dict[str, dict[str, Any]]:
    """Orval ``override.operations`` / ``override.tags`` with the request flags the runtime honours (H2.4).

    Orval inlines an override's ``requestOptions`` into the generated call before the caller's ``options``
    (``djangoFetch(url, { auth: 'none', ...options, method, … })``), and merges a tag's with an operation's. Each flag
    states one fact of the spec; the runtime acts on it:

    * ``auth: 'none'`` for an operation that takes no credentials (``_accepts_no_auth``): no Bearer, no refresh, and
      its 401 never expires the session;
    * ``skipAuthRefresh: true`` for a sign-in step, marked ``x-cfg-auth: sign-in`` by its view: a 401 there is a wrong
      code or password, not an expired session;
    * ``origin: 'direct'`` for every operation of a tag in ``direct_origin_tags`` (a Target option): sent to the API
      host, never through the proxy.

    Keys are the raw spec ``operationId`` and tag. Raises on an unknown ``x-cfg-auth`` value and on a
    ``direct_origin_tags`` entry that no operation of this slice carries.
    """
    document_security = document.get("security")
    operations: dict[str, Any] = {}
    seen_tags: set[str] = set()
    for path, method, op in _operations(document):
        seen_tags.update(str(t) for t in op.get("tags") or [])
        flags: dict[str, Any] = {}
        if _accepts_no_auth(op, document_security):
            flags["auth"] = "none"
        marker = op.get(SPEC_KEY_AUTH)
        if marker is not None:
            if marker != AUTH_SIGN_IN:
                raise PostprocessError(
                    f"{method.upper()} {path} ({op.get('operationId')}): {SPEC_KEY_AUTH} is {marker!r}; the only "
                    f"value is {AUTH_SIGN_IN!r}. Fix the view's extend_schema(extensions=...): use "
                    "django_cfg.core.contract.SIGN_IN_STEP, or drop the extension"
                )
            flags["skipAuthRefresh"] = True
        if flags and op.get("operationId"):
            operations[str(op["operationId"])] = {"requestOptions": flags}
    unknown = sorted(set(direct_origin_tags) - seen_tags)
    if unknown:
        raise SliceError(
            f"direct_origin_tags names {', '.join(map(repr, unknown))}, but no operation of this target carries that "
            f"tag. Tags in the target: {', '.join(sorted(seen_tags)) or 'none'}. Fix the Target's direct_origin_tags "
            "(raw OpenAPI tags, as in the schema)"
        )
    overrides: dict[str, dict[str, Any]] = {}
    if operations:
        overrides["operations"] = dict(sorted(operations.items()))
    if direct_origin_tags:
        overrides["tags"] = {tag: {"requestOptions": {"origin": "direct"}} for tag in sorted(set(direct_origin_tags))}
    return overrides


def render_cfg_ts(info: dict[str, Any]) -> str:
    """``runtime/cfg.ts`` (H2.6): the django-cfg stamp of the slice, importable at runtime as ``CFG``.

    Read from the slice's ``info``, which ``dispatch.run_single`` stamps before Orval runs, so this file, the banner
    and the published ``openapi.json`` cannot disagree. An unstamped slice falls back to this django-cfg.
    """
    version = info.get(SPEC_KEY_VERSION) or CFG_VERSION
    contract = info.get(SPEC_KEY_CONTRACT) or CONTRACT_SINCE
    return (
        "// The django-cfg stamp of this client, generated by django-cfg: do not edit, re-run `make gen`.\n"
        "// `version`: the django-cfg that generated it. `contract`: the oldest django-cfg that serves the same\n"
        "// contract, i.e. the minimum a host must run.\n"
        f"export const CFG = {{ version: {json.dumps(str(version))}, contract: {json.dumps(str(contract))} }} as const;\n"
    )


def consumer_package_json(consumer_dir: Path) -> Path | None:
    """The ``package.json`` the consumer folder belongs to: the nearest one at or above it."""
    consumer_dir = Path(consumer_dir).resolve()
    return next(
        (d / "package.json" for d in (consumer_dir, *consumer_dir.parents) if (d / "package.json").is_file()),
        None,
    )


# The config is an ES module, not JSON, because `override.header` must be a
# function. Python writes the data as JSON; the function below is fixed text.
_CONFIG_PREAMBLE = (
    "// Orval config for one django-cfg generation run: written and deleted by\n"
    "// django_generator/openapi/tools/external/orval.py.\n"
)
_HEADER_FUNCTION = """\
// The banner on top of every file Orval writes, from the spec's `info`. Only the
// contract, not the django-cfg release: a release must not rewrite every file.
config.djangocfg.output.override.header = (info) => [
  `Generated by orval ${ORVAL_VERSION} from the django-cfg contract ${info["x-cfg-contract"] ?? "(unstamped)"}.`,
  "Do not edit: re-run `make gen`.",
];
"""


def render_config(config: dict[str, Any], *, orval_version: str) -> str:
    """The ``orval.config.mjs`` text: ``config`` as JSON plus the fixed ``override.header`` function."""
    return (
        _CONFIG_PREAMBLE
        + f"const ORVAL_VERSION = {json.dumps(orval_version)};\n"
        + "const config = "
        + json.dumps(config, ensure_ascii=False, indent=2)
        + ";\n\n"
        + _HEADER_FUNCTION
        + "\nexport default config;\n"
    )


# Formats every .ts/.tsx file of the tree as if it lived in the consumer folder:
# `resolveConfig` runs on the consumer path, so the consumer's config (and its
# overrides) apply wherever the tree was written. Through the API, not the CLI:
# the CLI silently skips files matched by `.gitignore`/`.prettierignore` in its
# cwd. `editorconfig` stays off, because an `.editorconfig` above the checkout
# is machine state. Prettier comes from the workspace, else from Orval itself.
_FORMAT_SCRIPT = r"""
const { createRequire } = require("node:module");
const fs = require("node:fs");
const path = require("node:path");
const [workspace, tree, consumer] = process.argv.slice(1);
const fromWorkspace = createRequire(path.join(workspace, "package.json"));
function loadPrettier() {
  try {
    return fromWorkspace("prettier");
  } catch {
    return createRequire(fromWorkspace.resolve("orval"))("prettier");
  }
}
(async () => {
  const prettier = loadPrettier();
  const files = fs.readdirSync(tree, { recursive: true }).filter((f) => /\.tsx?$/.test(f)).sort();
  let changed = 0;
  for (const rel of files) {
    const at = path.join(consumer, rel);
    const options = { ...(await prettier.resolveConfig(at, { editorconfig: false })), filepath: at };
    const file = path.join(tree, rel);
    const before = fs.readFileSync(file, "utf8");
    const after = await prettier.format(before, options);
    if (after !== before) {
      fs.writeFileSync(file, after);
      changed += 1;
    }
  }
  const config = await prettier.resolveConfigFile(path.join(consumer, "index.ts"));
  process.stdout.write(JSON.stringify({ version: prettier.version, config, files: files.length, changed }));
})().catch((error) => {
  process.stderr.write(String((error && error.stack) || error));
  process.exit(1);
});
"""


def format_tree(tree: Path, *, consumer_dir: Path, cwd: Path) -> str:
    """Format ``tree`` with prettier as the consumer at ``consumer_dir`` would. Returns what formatted it."""
    node = shutil.which("node")
    if node is None:
        raise ToolNotInstalledError(f"node is not on PATH: {INSTALL_HINT}")
    try:
        proc = subprocess.run(  # noqa: S603 -- fixed formatter script and path arguments, no shell
            [node, "-e", _FORMAT_SCRIPT, str(Path(cwd).resolve()), str(Path(tree).resolve()), str(Path(consumer_dir))],
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=_FORMAT_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired as exc:
        raise ToolExecutionError(f"prettier did not finish in {_FORMAT_TIMEOUT_S}s on {tree}") from exc
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()[-2000:]
        raise ToolExecutionError(f"prettier failed on the generated tree {tree}: {detail or 'no output'}")
    try:
        report = json.loads(proc.stdout)
    except ValueError as exc:
        raise ToolExecutionError(f"prettier printed no report for {tree}: {proc.stdout[-500:]!r}") from exc
    config = report.get("config") or f"none for {consumer_dir} (prettier defaults)"
    return f"prettier {report.get('version')}, config {config}"


def generate(
    spec_path: Path,
    out_dir: Path,
    *,
    cwd: Path,
    consumer_dir: Path | None = None,
    mock: bool = True,
    prettier: bool = True,
    runtime: RuntimeImport | None = None,
    auth_mode: str = "default",
    direct_origin_tags: tuple[str, ...] | list[str] = (),
    infinite: bool = False,
    profile: str = "web",
) -> OrvalResult:
    """Generate a web React Query/Zod/MSW tree or standalone CLI Fetch/Zod tree.

    ``cwd`` must be the frontend workspace containing the pinned Orval binary.
    ``consumer_dir`` is the folder the tree is published to (default
    ``out_dir``): its ``package.json`` and prettier config apply. The
    generated tree is intentionally disposable: endpoint files, models,
    and mocks are all emitted below ``out_dir``. ``runtime`` is where the
    generated mutator shim imports the runtime from; without it Orval uses
    plain ``fetch``.
    """
    if profile not in ("web", "cli"):
        raise ValueError(f"Unknown TypeScript profile: {profile!r}; choose web or cli")
    if profile == "cli" and (runtime is not None or infinite or direct_origin_tags):
        raise ValueError("CLI profile uses its standalone transport and explicit baseUrl, without runtime/infinite/direct_origin_tags")
    if auth_mode not in AUTH_MODES:
        raise ValueError(f"auth_mode must be one of {', '.join(AUTH_MODES)}")
    problem = check()
    if problem:
        raise ToolNotInstalledError(problem)

    if not cwd.is_dir():
        raise ToolNotInstalledError(f"Orval workspace does not exist: {cwd}")
    if not (cwd / "package.json").is_file():
        raise ToolNotInstalledError(f"Orval workspace has no package.json: {cwd}")

    out_dir = Path(out_dir)
    consumer = Path(consumer_dir) if consumer_dir is not None else out_dir
    document = json.loads(Path(spec_path).read_text(encoding="utf-8"))
    # Before anything is written: a bad x-cfg-auth or direct_origin_tags stops here, named, not inside Orval.
    request_overrides = request_option_overrides(document, direct_origin_tags=direct_origin_tags)
    try:
        realtime_queries = invalidating_queries(document) if profile == "web" else {}
    except RealtimeInvalidationError as exc:
        raise PostprocessError(str(exc)) from exc
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    # Orval resolves the mutator from the generated tree. The shim lives in
    # that tree so the generated imports remain valid after the Python
    # pipeline stages the tree into the consumer directory. It wraps the
    # handwritten runtime and is recreated on every generation.
    mutator_path: Path | None = None
    if runtime is not None or profile == "cli":
        runtime_dir = out_dir / "runtime"
        runtime_dir.mkdir(parents=True)
        mutator_path = runtime_dir / "orval-mutator.ts"
        mutator_path.write_text(
            render_cli_mutator(auth_mode=auth_mode) if profile == "cli" else render_mutator_shim(runtime, auth_mode=auth_mode),
            encoding="utf-8",
        )
    # H2.10: the queries marked `invalidated_by` carry their topics in `meta` (see `realtime/query_topics.py`).
    operation_overrides: dict[str, dict[str, Any]] = {
        op: dict(entry) for op, entry in (request_overrides.get("operations") or {}).items()
    } if mutator_path is not None else {}
    if realtime_queries:
        query_mutator = out_dir / "runtime" / REALTIME_QUERY_FILE
        query_mutator.parent.mkdir(parents=True, exist_ok=True)
        query_mutator.write_text(render_realtime_query(realtime_queries), encoding="utf-8")
        for op, entry in query_option_overrides(realtime_queries, str(query_mutator.resolve())).items():
            operation_overrides.setdefault(op, {}).update(entry)

    package_json = consumer_package_json(consumer)
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
                "client": "fetch" if profile == "cli" else "react-query",
                "httpClient": "fetch",
                "mock": False if profile == "cli" else mock,
                **({"packageJson": str(package_json)} if package_json is not None else {}),
                "override": {
                    # Orval takes the TanStack Query version from `packageJson`.
                    # Without one it generates v4 option types (no `Partial`,
                    # no `DataTag`), and two consumers declare no
                    # @tanstack/react-query in their nearest package.json: cmdop
                    # `apps/docs/scripts/api` and cmdop_go `cmdop-web/frontend/
                    # packages/api`. With a declared version this changes nothing.
                    # `infinite` (H2.7): `use<Op>Infinite` for every GET with a
                    # `page` or `cursor` query parameter; Orval skips the others.
                    # The page params come from the runtime (`drfPageParams`).
                    **({"query": {"version": 5, **(_INFINITE_QUERY if infinite else {})}} if profile == "web" else {}),
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
                    # Per-operation and per-tag request flags (`auth`, `skipAuthRefresh`, `origin`), from the spec.
                    # Only for the runtime: plain `fetch` takes a `RequestInit`, which has none of them. Per
                    # operation also the realtime `queryOptions` mutator (H2.10), with or without the runtime.
                    **({"operations": dict(sorted(operation_overrides.items()))} if operation_overrides else {}),
                    **(
                        {"tags": request_overrides["tags"]}
                        if mutator_path is not None and "tags" in request_overrides
                        else {}
                    ),
                },
            },
        }
    }
    config_path.write_text(
        render_config(config, orval_version=installed_version(cwd) or ORVAL_VERSION),
        encoding="utf-8",
    )

    cmd = ["pnpm", "exec", "orval", "--config", str(config_path)]
    try:
        subprocess.run(  # noqa: S603 -- pinned workspace Orval and generated config path, no shell
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
    if profile == "web":
        generate_realtime(document.get("x-realtime"), out_dir)
    (out_dir / "runtime").mkdir(exist_ok=True)
    (out_dir / "runtime" / "cfg.ts").write_text(render_cfg_ts(document.get("info") or {}), encoding="utf-8")

    files = sorted(path for path in out_dir.rglob("*") if path.is_file())
    if not files:
        raise ToolExecutionError("orval completed without writing generated files")
    formatter = format_tree(out_dir, consumer_dir=consumer, cwd=cwd) if prettier else None
    return OrvalResult(output_dir=out_dir, files=files, formatter=formatter)


__all__ = [
    "AUTH_MODES",
    "ORVAL_VERSION",
    "RUNTIME_PACKAGE",
    "OrvalResult",
    "RuntimeImport",
    "check",
    "consumer_package_json",
    "format_tree",
    "generate",
    "installed_version",
    "node_version",
    "render_cfg_ts",
    "render_config",
    "render_mutator_shim",
    "request_option_overrides",
]
