"""Per-group `class API` + `index.ts` renderers.

The wrapper layer is intentionally thin. The *real* auth/baseUrl wiring
lives in `helpers/auth.ts` (one global `auth` object + ONE request
interceptor on the shared `client`, installed as a side-effect when
`client.gen.ts` loads). The per-group `class API` exists for ergonomic
reasons only — it lets consumers write `apiAccounts.accounts.X(...)`
instead of `Accounts.X(...)`. All `API` instances share the same global
auth; per-group token isolation isn't possible (one HTTP client) and
was never honored in practice.

Each group dir gets:
  - `api.ts`     — `class API` (proxy to global `auth` + SDK class refs)
  - `index.ts`   — barrel re-exporting `API`, SDK classes, helpers
"""

from __future__ import annotations

import logging
import re
from dataclasses import dataclass

_log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# Reserved type names in the top-level barrel
# ─────────────────────────────────────────────────────────────────────────────
# The top-level `index.ts` re-exports these symbols from `helpers/`:
#
#   export { auth, type Auth } from './helpers/auth';
#
# The `type Auth` alias means **any OpenAPI tag whose Hey-API SDK class
# would also be named `Auth`** collides — TypeScript can't merge a type
# alias and a class under the same exported name.
#
# Same story for any future helper-side type aliases. Add them here.
#
# Resolution policy in `render_target_index_ts(...)`:
#   1. If a colliding tag is encountered, log a WARNING (visible in
#      `make gen` output) so callers learn about it.
#   2. Re-export the SDK class with the alias defined below — barrel
#      stays compilable. Consumers that need the original name can
#      import directly from `./_<group>` (e.g. `import { Auth } from
#      '@api-server/_auth'`).
#   3. The cleanest long-term fix is to rename the OpenAPI tag on the
#      backend (FastAPI / DRF) so the SDK class doesn't collide. Tags
#      like `auth` → `authentication` cost nothing and remove the rule
#      from this list entirely.
_BARREL_TYPE_RESERVED: dict[str, str] = {
    # SDK class name → re-export alias
    "Auth": "AuthSDK",
}

# SDK names we deliberately drop from the top-level barrel (no alias —
# they live behind their own per-group import only). "Cfg" is an
# internal helper namespace consumers don't reach for at top level.
_BARREL_SDK_DROPPED: frozenset[str] = frozenset({"Cfg"})


@dataclass(frozen=True)
class GroupSpec:
    """One Hey API SDK class to mount on the group's `class API`."""

    sdk_class: str   # e.g. "OAuth", "Accounts", "TotpSetup"
    dir_name: str    # e.g. "cfg_accounts"

    @property
    def prop_name(self) -> str:
        """JS-safe property name: lower-camel of the SDK class."""
        if not self.sdk_class:
            return self.dir_name
        return self.sdk_class[0].lower() + self.sdk_class[1:]


@dataclass(frozen=True)
class OpRoute:
    """One operation routing entry for the response zod-validator."""

    method: str         # "GET" / "POST" / …
    path: str           # "/apix/profiles/profiles/{id}/"
    schema: str | None  # "UserProfile" / None


def _ts_string(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


_PATH_PARAM_RE = re.compile(r"\{[^}]+\}")


def _path_to_regex(path: str) -> str:
    escaped = re.escape(path).replace("\\{", "{").replace("\\}", "}")
    pattern = _PATH_PARAM_RE.sub("[^/]+", escaped)
    pattern = pattern.rstrip("/") + "/?"
    return f"^{pattern}$"


def render_group_api_ts(
    *,
    groups: list[GroupSpec],
    routes: list[OpRoute] | None = None,
    access_key: str = "cfg.access_token",  # kept for signature compat
    refresh_key: str = "cfg.refresh_token",
) -> str:
    """Render `<group>/api.ts` — thin proxy over the global `auth` store."""

    del access_key, refresh_key  # auth keys live in helpers/auth.ts now

    routes = routes or []

    sdk_imports = "\n".join(
        f"import {{ {g.sdk_class} }} from '../sdk.gen';" for g in groups
    )
    sdk_props = "\n".join(
        f"  readonly {g.prop_name} = {g.sdk_class};" for g in groups
    )
    sdk_reexports = ", ".join(g.sdk_class for g in groups)

    # Optional response zod-validation block (only if routes carry schemas).
    used_schemas = sorted({r.schema for r in routes if r.schema})
    if used_schemas:
        schema_imports = (
            "import type { ZodTypeAny } from 'zod';\n"
            "import {\n"
            + ",\n".join(f"  {s}Schema" for s in used_schemas)
            + ",\n} from './schemas';\n"
            "import { dispatchValidationError } from '../helpers/validation-events';\n"
            "import { client } from '../client.gen';"
        )
        route_entries = ",\n".join(
            (
                f"  {{ method: '{r.method}', "
                f"re: new RegExp({_ts_string(_path_to_regex(r.path))}), "
                f"schema: {r.schema}Schema, "
                f"path: {_ts_string(r.path)} }}"
            )
            for r in routes
            if r.schema
        )
        validator_block = f"""\

interface ValidationRoute {{
  method: string;
  re: RegExp;
  schema: ZodTypeAny;
  path: string;
}}
const VALIDATION_ROUTES: ReadonlyArray<ValidationRoute> = [
{route_entries}
];

// Side-effect: install one response validator per group module load.
// Multiple group modules each install their own; routes are scoped by
// regex so validators don't double-fire.
client.interceptors.response.use(async (response, request) => {{
  if (!response.ok) return response;
  const ct = response.headers.get('content-type') || '';
  if (!ct.includes('application/json')) return response;
  const url = new URL(request.url);
  const method = request.method.toUpperCase();
  const route = VALIDATION_ROUTES.find(
    (r) => r.method === method && r.re.test(url.pathname),
  );
  if (!route) return response;
  let payload: unknown;
  try {{ payload = await response.clone().json(); }} catch {{ return response; }}
  const result = route.schema.safeParse(payload);
  if (!result.success) {{
    dispatchValidationError({{
      operation: `${{method}} ${{route.path}}`,
      path: route.path,
      method,
      error: result.error,
      response: payload,
      timestamp: new Date(),
    }});
  }}
  return response;
}});
"""
    else:
        schema_imports = ""
        validator_block = ""

    return f'''\
// AUTO-GENERATED by django_generator / ts_extras.wrapper
// Thin per-group proxy over the global `auth` store. All actual auth
// wiring lives in `helpers/auth.ts` (one interceptor, one source of
// truth). DO NOT EDIT — re-run `make gen`.

import {{ auth }} from '../helpers/auth';
import {{ APILogger, type LoggerConfig }} from '../helpers/logger';

{sdk_imports}
{schema_imports}
{validator_block}

export interface APIOptions {{
  /** Logger config (defaults to dev-only). */
  logger?: Partial<LoggerConfig>;
  /** Locale for `Accept-Language`. If omitted, auto-detected from cookie/navigator. */
  locale?: string;
  /** API key sent as `X-API-Key`. Falls back to NEXT_PUBLIC_API_KEY. */
  apiKey?: string;
  /** Send Django session/CSRF cookies cross-origin. Defaults to true. */
  withCredentials?: boolean;
}}

/**
 * Per-group ergonomic facade.
 *
 * Calling `setToken/setApiKey/setLocale/setBaseUrl` proxies to the
 * global `auth` store — the change applies to **every** group's API
 * instance because they share the same HTTP client and interceptor.
 *
 * Use the global `auth` object directly when you don't need a group
 * facade: `import {{ auth }} from '@your/api'; auth.setToken(jwt);`
 */
export class API {{
  readonly logger: APILogger;

{sdk_props}

  constructor(_baseUrl?: string, opts: APIOptions = {{}}) {{
    this.logger = new APILogger(opts.logger);
    if (_baseUrl) auth.setBaseUrl(_baseUrl);
    if (opts.locale !== undefined) auth.setLocale(opts.locale);
    if (opts.apiKey !== undefined) auth.setApiKey(opts.apiKey);
    if (opts.withCredentials !== undefined) auth.setWithCredentials(opts.withCredentials);
  }}

  // ── Base URL ────────────────────────────────────────────────────────────
  getBaseUrl(): string {{ return auth.getBaseUrl(); }}
  setBaseUrl(url: string): void {{ auth.setBaseUrl(url); }}

  // ── Tokens ──────────────────────────────────────────────────────────────
  getToken(): string | null {{ return auth.getToken(); }}
  setToken(token: string | null): void {{ auth.setToken(token); }}
  getRefreshToken(): string | null {{ return auth.getRefreshToken(); }}
  setRefreshToken(token: string | null): void {{ auth.setRefreshToken(token); }}
  clearToken(): void {{ auth.clearTokens(); }}
  isAuthenticated(): boolean {{ return auth.isAuthenticated(); }}

  // ── Locale / API key ────────────────────────────────────────────────────
  getLocale(): string | null {{ return auth.getLocale(); }}
  setLocale(locale: string | null): void {{ auth.setLocale(locale); }}
  getApiKey(): string | null {{ return auth.getApiKey(); }}
  setApiKey(key: string | null): void {{ auth.setApiKey(key); }}

  // ── 401 handling ────────────────────────────────────────────────────────
  /** Fired only on terminal 401 (after refresh+retry path is exhausted). */
  onUnauthorized(cb: ((response: Response) => void) | null): void {{
    auth.onUnauthorized(cb);
  }}
  /** Provide a refresh strategy. See `auth.setRefreshHandler` for the contract. */
  setRefreshHandler(
    fn: ((refreshToken: string) => Promise<{{ access: string; refresh?: string }} | null>) | null,
  ): void {{
    auth.setRefreshHandler(fn);
  }}
}}

export {{ {sdk_reexports} }};
export {{ auth }};
'''


def render_target_index_ts(*, groups_by_dir: list[tuple[str, list[GroupSpec]]]) -> str:
    """Render `<target>/index.ts` — top-level barrel.

    Exports:
      • Global `auth` (the one anyone should reach for).
      • `<group>Api` singletons (kept for legacy ergonomics — they all
        proxy to the same `auth`).
      • Per-group wrapper classes (`<Group>API`) for tests/SSR.
      • Hey API SDK classes (one per OpenAPI tag) for direct use.
    """

    def _camel(name: str) -> str:
        parts = re.split(r"[_\-]+", name)
        head, *tail = parts
        return head + "".join(p.capitalize() for p in tail)

    def _alias(name: str) -> str:
        return "".join(p.capitalize() for p in re.split(r"[_\-]+", name) if p)

    imports = "\n".join(
        f"import {{ API as {_alias(d)}API }} from './{d}';"
        for d, _ in groups_by_dir
    )
    singletons = "\n".join(
        f"export const {_camel(d)}Api = new {_alias(d)}API();"
        for d, _ in groups_by_dir
    )
    api_class_reexports = "\n".join(
        f"export {{ API as {_alias(d)}API }} from './{d}';"
        for d, _ in groups_by_dir
    )

    # See `_BARREL_TYPE_RESERVED` / `_BARREL_SDK_DROPPED` at module
    # top for the policy + rationale.
    seen: set[str] = set()
    sdk_class_reexports_lines: list[str] = []
    for d, specs in groups_by_dir:
        names: list[str] = []
        for s in specs:
            if s.sdk_class in _BARREL_SDK_DROPPED:
                continue
            if s.sdk_class in seen:
                continue
            seen.add(s.sdk_class)
            if s.sdk_class in _BARREL_TYPE_RESERVED:
                alias = _BARREL_TYPE_RESERVED[s.sdk_class]
                _log.warning(
                    "ts_extras.wrapper: SDK class %r collides with a "
                    "reserved name in the top-level barrel — re-exporting "
                    "as %r. Direct import still works "
                    "(`import { %s } from '<api>/_%s'`). To remove this "
                    "warning, rename the OpenAPI tag on the backend so "
                    "the generated SDK class no longer collides.",
                    s.sdk_class, alias, s.sdk_class, d,
                )
                names.append(f"{s.sdk_class} as {alias}")
            else:
                names.append(s.sdk_class)
        if names:
            sdk_class_reexports_lines.append(
                f"export {{ {', '.join(names)} }} from './{d}';"
            )
    sdk_class_reexports = "\n".join(sdk_class_reexports_lines)

    return f'''\
// AUTO-GENERATED by django_generator / ts_extras.wrapper
// Top-level barrel — global `auth` + per-group facades.
// DO NOT EDIT — re-run `make gen`.

// Side-effect: ensure auth interceptor is installed even if consumers
// only ever import this barrel (it'll also load via client.gen.ts).
import './helpers/auth';

// Global auth/config store — single source of truth.
export {{ auth, type Auth }} from './helpers/auth';

{imports}

// Singletons for ergonomic access (`import {{ apiAccounts }} from '@your/api'`).
// All instances share the same global `auth` store.
{singletons}

// Per-group wrapper classes (e.g. for tests / SSR isolation of options).
{api_class_reexports}

// Hey API SDK classes — one per OpenAPI tag. Lets consumers call
// `Centrifugo.cfgCentrifugoAuthTokenRetrieve({{...}})` directly.
//
// NOTE: classes whose name would collide with a barrel-level type
// alias (e.g. `Auth`, which is also `type Auth = typeof auth`) are
// re-exported under a `*SDK` suffix here. The original name is still
// available via the per-group import: `import {{ Auth }} from
// '<api>/_auth'`. To remove the alias, rename the OpenAPI tag on the
// backend so the SDK class doesn't collide.
{sdk_class_reexports}

// Generated DTO / schema types (Hey API). The per-group barrels each
// re-export these too; surfacing them at the top level lets consumers
// `import {{ FleetSummary }} from '<api>'` without reaching into a
// group subpath.
export type * from './types.gen';

// Shared utilities (errors, storage adapters, logger).
export * from './helpers';
'''


def render_group_index_ts(*, groups: list[GroupSpec]) -> str:
    """Render `<group>/index.ts` — barrel for the group package."""

    sdk_reexports = ", ".join(g.sdk_class for g in groups)

    return f'''\
// AUTO-GENERATED by django_generator / ts_extras.wrapper
// Group barrel. DO NOT EDIT — re-run `make gen`.

// Wrapper class + per-group SDK re-exports + global auth.
export {{ API, type APIOptions, auth, {sdk_reexports} }} from './api';

// Shared utilities.
export {{
  type StorageAdapter,
  LocalStorageAdapter,
  MemoryStorageAdapter,
  CookieStorageAdapter,
  APIError,
  NetworkError,
  APILogger,
  defaultLogger,
  type LoggerConfig,
  type RequestLog,
  type ResponseLog,
  type ErrorLog,
  dispatchValidationError,
  onValidationError,
  formatZodError,
  type ValidationErrorDetail,
  type ValidationErrorEvent,
}} from '../helpers';

// Generated artifacts (Hey API).
export type * from '../types.gen';
'''
