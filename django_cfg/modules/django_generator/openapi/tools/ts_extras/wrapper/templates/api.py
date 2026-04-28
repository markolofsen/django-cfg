"""Per-group `class API` + `index.ts` renderers.

Each group dir gets:
  - `api.ts` — self-contained `class API` over the group's Hey API client/SDK
  - `index.ts` — barrel re-exporting `API`, shared adapters, errors, logger

Shared utilities (`storage`, `errors`, `logger`, `validation-events`) live in
`<target>/_shared/` and are imported via `'../_shared'` from each group.
"""

from __future__ import annotations

import re
from dataclasses import dataclass


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
    """One operation routing entry for the response zod-validator.

    `schema` is the OpenAPI schema name (without `Schema` suffix) for
    the 200/201/202 response. `None` means "no validation" (operation
    has no JSON response body or body schema is inline).
    """

    method: str         # "GET" / "POST" / …
    path: str           # "/apix/profiles/profiles/{id}/"
    schema: str | None  # "UserProfile" / None


def _ts_string(value: str) -> str:
    """JSON-encode a Python string for safe embedding in TS source.

    Single quotes preferred to match the rest of the generated style.
    """
    escaped = value.replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


_PATH_PARAM_RE = re.compile(r"\{[^}]+\}")


def _path_to_regex(path: str) -> str:
    """Convert OpenAPI path template to a JS regex source.

    `/apix/profiles/{id}/` → `^/apix/profiles/[^/]+/?$`
    Trailing slash is optional to tolerate Django's APPEND_SLASH +
    redirect quirks.
    """
    escaped = re.escape(path).replace("\\{", "{").replace("\\}", "}")
    pattern = _PATH_PARAM_RE.sub("[^/]+", escaped)
    pattern = pattern.rstrip("/") + "/?"
    return f"^{pattern}$"


def render_group_api_ts(
    *,
    groups: list[GroupSpec],
    routes: list[OpRoute] | None = None,
    access_key: str = "cfg.access_token",
    refresh_key: str = "cfg.refresh_token",
) -> str:
    """Render `<group>/api.ts` — self-contained `class API` for one group."""

    routes = routes or []

    sdk_imports = "\n".join(
        f"import {{ {g.sdk_class} }} from './sdk.gen';" for g in groups
    )
    sdk_props = "\n".join(
        f"  readonly {g.prop_name} = {g.sdk_class};" for g in groups
    )
    sdk_reexports = ", ".join(g.sdk_class for g in groups)

    # ── Auto zod-validation: route → schema map ────────────────────────
    used_schemas = sorted({r.schema for r in routes if r.schema})
    if used_schemas:
        schema_imports = (
            "import type { ZodTypeAny } from 'zod';\n"
            "import {\n"
            + ",\n".join(f"  {s}Schema" for s in used_schemas)
            + ",\n} from './schemas';\n"
            "import { dispatchValidationError } from '../_shared/validation-events';"
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
        routes_block = (
            "interface ValidationRoute {\n"
            "  method: string;\n"
            "  re: RegExp;\n"
            "  schema: ZodTypeAny;\n"
            "  path: string;\n"
            "}\n"
            "const VALIDATION_ROUTES: ReadonlyArray<ValidationRoute> = [\n"
            f"{route_entries}\n"
            "];"
        )
        response_validator = """\
    client.interceptors.response.use(async (response, request) => {
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
      try {
        payload = await response.clone().json();
      } catch {
        return response;
      }
      const result = route.schema.safeParse(payload);
      if (!result.success) {
        dispatchValidationError({
          operation: `${method} ${route.path}`,
          path: route.path,
          method,
          error: result.error,
          response: payload,
          timestamp: new Date(),
        });
      }
      return response;
    });"""
    else:
        schema_imports = ""
        routes_block = ""
        response_validator = ""

    return f'''\
// AUTO-GENERATED by django_generator / ts_extras.wrapper
// Self-contained API wrapper for this group. DO NOT EDIT — re-run `make gen`.

import {{ client }} from './client.gen';
import type {{ StorageAdapter }} from '../_shared/storage';
import {{ LocalStorageAdapter }} from '../_shared/storage';
import {{ APILogger, type LoggerConfig }} from '../_shared/logger';

{sdk_imports}
{schema_imports}

const ACCESS_KEY = '{access_key}';
const REFRESH_KEY = '{refresh_key}';

{routes_block}

/** Auto-detect locale from cookie NEXT_LOCALE or navigator.language. */
function detectLocale(): string | null {{
  try {{
    if (typeof document !== 'undefined') {{
      const m = document.cookie.match(/(?:^|;\\s*)NEXT_LOCALE=([^;]*)/);
      if (m) return decodeURIComponent(m[1]);
    }}
    if (typeof navigator !== 'undefined' && navigator.language) {{
      return navigator.language;
    }}
  }} catch {{}}
  return null;
}}

export interface APIOptions {{
  /** Override storage backend (LocalStorage by default; Memory for SSR/tests). */
  storage?: StorageAdapter;
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
 * Self-contained API wrapper for this group.
 *
 * Each group has its own client + interceptor + token store. The interceptor
 * automatically attaches:
 *   - `Authorization: Bearer <jwt>` from storage
 *   - `Accept-Language` from `opts.locale` or `NEXT_LOCALE` cookie
 *   - `X-API-Key` from `opts.apiKey` or `NEXT_PUBLIC_API_KEY`
 *   - `credentials: 'include'` for Django session/CSRF cookies (toggle via opts)
 */
export class API {{
  private baseUrl: string;
  private storage: StorageAdapter;
  private locale: string | null;
  private apiKey: string | null;
  readonly logger: APILogger;

{sdk_props}

  constructor(baseUrl: string, opts: APIOptions = {{}}) {{
    this.baseUrl = baseUrl.replace(/\\/$/, '');
    this.storage = opts.storage ?? new LocalStorageAdapter();
    this.logger = new APILogger(opts.logger);
    this.locale = opts.locale ?? null;
    this.apiKey = opts.apiKey ?? (typeof process !== 'undefined' ? (process.env?.NEXT_PUBLIC_API_KEY ?? null) : null);

    const credentials: RequestCredentials = (opts.withCredentials ?? true) ? 'include' : 'same-origin';
    client.setConfig({{ baseUrl: this.baseUrl, credentials }});

    client.interceptors.request.use((request) => {{
      const access = this.getToken();
      if (access) request.headers.set('Authorization', `Bearer ${{access}}`);

      const locale = this.locale ?? detectLocale();
      if (locale) request.headers.set('Accept-Language', locale);

      if (this.apiKey) request.headers.set('X-API-Key', this.apiKey);

      return request;
    }});

{response_validator}
  }}

  // ── Base URL ────────────────────────────────────────────────────────────
  getBaseUrl(): string {{ return this.baseUrl; }}
  setBaseUrl(url: string): void {{
    this.baseUrl = url.replace(/\\/$/, '');
    client.setConfig({{ baseUrl: this.baseUrl }});
  }}

  // ── Tokens ──────────────────────────────────────────────────────────────
  getToken(): string | null {{ return this.storage.getItem(ACCESS_KEY); }}
  setToken(token: string | null): void {{
    if (token) this.storage.setItem(ACCESS_KEY, token);
    else this.storage.removeItem(ACCESS_KEY);
  }}
  getRefreshToken(): string | null {{ return this.storage.getItem(REFRESH_KEY); }}
  setRefreshToken(token: string | null): void {{
    if (token) this.storage.setItem(REFRESH_KEY, token);
    else this.storage.removeItem(REFRESH_KEY);
  }}
  clearToken(): void {{
    this.storage.removeItem(ACCESS_KEY);
    this.storage.removeItem(REFRESH_KEY);
  }}
  isAuthenticated(): boolean {{ return this.getToken() !== null; }}

  // ── Locale / API key ────────────────────────────────────────────────────
  getLocale(): string | null {{ return this.locale ?? detectLocale(); }}
  setLocale(locale: string | null): void {{ this.locale = locale; }}
  getApiKey(): string | null {{ return this.apiKey; }}
  setApiKey(key: string | null): void {{ this.apiKey = key; }}
}}

export {{ {sdk_reexports} }};
export {{ client }};
'''


def render_target_index_ts(*, groups_by_dir: list[tuple[str, list[GroupSpec]]]) -> str:
    """Render `<target>/index.ts` — top-level barrel with Next.js singletons.

    For each per-group dir we emit:
      • An `<group>Api` singleton (baseUrl from `NEXT_PUBLIC_API_URL`).
      • Class re-exports — both the wrapper `API` and every Hey API SDK
        class (one per OpenAPI tag) so consumers can call e.g.
        `import { CentrifugoAuth } from '@djangocfg/api'` and reach
        `CentrifugoAuth.cfgCentrifugoAuthTokenRetrieve(...)` directly.
    """

    def _camel(name: str) -> str:
        # `cfg_accounts` -> `cfgAccounts`
        head, *tail = name.split("_")
        return head + "".join(p.capitalize() for p in tail)

    def _alias(name: str) -> str:
        # `cfg_accounts` -> `CfgAccounts` (TS class alias)
        return "".join(p.capitalize() for p in name.split("_"))

    imports = "\n".join(
        (
            f"import {{ API as {_alias(d)}API, "
            f"LocalStorageAdapter as {_alias(d)}Storage }} from './{d}';"
        )
        for d, _ in groups_by_dir
    )
    singletons = "\n".join(
        (
            f"export const {_camel(d)}Api = new {_alias(d)}API("
            f"baseUrl, {{ storage: new {_alias(d)}Storage() }});"
        )
        for d, _ in groups_by_dir
    )
    api_class_reexports = "\n".join(
        f"export {{ API as {_alias(d)}API }} from './{d}';"
        for d, _ in groups_by_dir
    )
    # Hey API emits one `<Tag>` class per OpenAPI tag. We re-export each
    # class at the top level, but skip the shared `Cfg` namespace tag — it
    # exists in every cfg_* group SDK (drf-spectacular stamps `["cfg", ...]`
    # on every django-cfg op via PathBasedAutoSchema), so re-exporting it
    # would collide. Consumers that need `Cfg` should import from the
    # specific group barrel (e.g. `import { Cfg } from '@djangocfg/api/...'`).
    # Slicing isn't perfectly tag-isolated: a group's sdk.gen.ts can
    # carry classes for tags that leaked from sibling groups (operations
    # referenced via shared components). Naive re-export from every
    # group produces TS2300 duplicate-identifier errors. We dedupe by
    # SDK class name — first group to expose it wins. Consumers that
    # need a class from a specific group can still import via the group
    # barrel (`from './<group>'`).
    _RESERVED_SDK = {"Cfg"}
    seen: set[str] = set()
    sdk_class_reexports_lines: list[str] = []
    for d, specs in groups_by_dir:
        names: list[str] = []
        for s in specs:
            if s.sdk_class in _RESERVED_SDK:
                continue
            if s.sdk_class in seen:
                continue
            seen.add(s.sdk_class)
            names.append(s.sdk_class)
        if names:
            sdk_class_reexports_lines.append(
                f"export {{ {', '.join(names)} }} from './{d}';"
            )
    sdk_class_reexports = "\n".join(sdk_class_reexports_lines)

    return f'''\
// AUTO-GENERATED by django_generator / ts_extras.wrapper
// Top-level barrel — one singleton API per group, baseUrl from Next.js env.
// DO NOT EDIT — re-run `make gen`.

{imports}

const isStaticBuild = process.env.NEXT_PUBLIC_STATIC_BUILD === 'true';
const baseUrl = isStaticBuild ? '' : process.env.NEXT_PUBLIC_API_URL || '';

{singletons}

// API wrapper classes — for users who need to construct their own
// instance (e.g. with MemoryStorageAdapter in SSR/tests).
{api_class_reexports}

// Hey API SDK classes — one per OpenAPI tag. Lets consumers call
// `Centrifugo.cfgCentrifugoAuthTokenRetrieve({{...}})` directly without
// going through the wrapper singleton.
{sdk_class_reexports}

// Shared utilities (errors, storage adapters, logger).
export * from './_shared';
'''


def render_group_index_ts(*, groups: list[GroupSpec]) -> str:
    """Render `<group>/index.ts` — barrel for the group package."""

    sdk_reexports = ", ".join(g.sdk_class for g in groups)

    return f'''\
// AUTO-GENERATED by django_generator / ts_extras.wrapper
// Group barrel. DO NOT EDIT — re-run `make gen`.

// Wrapper class + per-group SDK re-exports
export {{ API, type APIOptions, {sdk_reexports} }} from './api';

// Shared utilities (storage / errors / logger / validation events)
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
}} from '../_shared';

// Generated artifacts (Hey API)
export type * from './types.gen';
'''
