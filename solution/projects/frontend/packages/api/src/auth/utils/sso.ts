/**
 * One sign-in host for a family of subdomains (pure, no React, no `window`).
 *
 * `auth={{ sso: { host: 'reforms.ai' } }}` (or `NEXT_PUBLIC_AUTH_HOST=reforms.ai`) turns it on:
 * every other host of the same registrable domain sends a signed-out visitor to
 * `https://reforms.ai/auth?next=<where they were>`, and the auth host sends them back.
 * The session itself is the shared cookie pair (`cfg.auth.*` on `.reforms.ai`), nothing new.
 *
 * The one security decision here is `safeNext`: `next` is attacker-controlled (a link in a mail
 * or a chat), so only `https://<apex or a subdomain of it>/path` and a plain path survive.
 * The Python twin is `django_cfg.core.site.safe_next_url`; keep the rules identical.
 */

export interface SsoConfig {
  /** The dedicated sign-in host: `auth.reforms.ai` or `https://auth.reforms.ai`. No path, no credentials. Every other host of the apex (the public `reforms.ai` too) is a follower. */
  authHost?: string;
  /** Label of the derived host when `authHost` is not given: `auth` → `auth.<apex of NEXT_PUBLIC_SITE_URL>`. */
  authLabel?: string;
  /** Alias of `authHost`. */
  host?: string;
  /** Sign-in page path on that host. Default `/auth`. */
  path?: string;
  /** Cookie `Domain` override. Default: detected by the browser (`'auto'`). */
  cookieDomain?: string;
}

export type SsoOffReason =
  | 'not-configured'
  | 'invalid-host'
  /** The page is not on the apex of `host` (localhost, an IP, a preview URL): the old per-host sign-in is used. */
  | 'outside-apex';

export interface SsoState {
  enabled: boolean;
  /** Current host is the sign-in host itself: it renders the form. */
  isAuthHost: boolean;
  /** `https://reforms.ai`, or null when off. */
  authOrigin: string | null;
  authPath: string;
  /** Registrable domain all `next` targets must belong to. */
  apex: string | null;
  reason?: SsoOffReason;
}

const OFF: SsoState = { enabled: false, isAuthHost: false, authOrigin: null, authPath: '/auth', apex: null };

// Mirrors `core/site.py`: shared hosts whose own subdomains belong to different people.
const SHARED_SUFFIXES = new Set([
  'vercel.app', 'netlify.app', 'github.io', 'gitlab.io', 'pages.dev', 'workers.dev', 'herokuapp.com',
  'onrender.com', 'fly.dev', 'ngrok.io', 'ngrok-free.app', 'trycloudflare.com', 'web.app',
  'firebaseapp.com', 'azurewebsites.net', 'cloudfront.net', 'amazonaws.com', 'appspot.com',
  'repl.co', 'glitch.me', 'surge.sh', 'railway.app', 'up.railway.app', 'nip.io', 'sslip.io',
]);
const SECOND_LEVEL = new Set(['co', 'com', 'org', 'net', 'gov', 'edu', 'ac', 'or', 'ne', 'go', 'gob', 'mil']);
const IPV4 = /^\d{1,3}(\.\d{1,3}){3}$/;
const HOST_LABEL = /^[a-z0-9]([a-z0-9-]*[a-z0-9])?$/;

/** `my.reforms.ai` → `reforms.ai`. Null for an IP, `localhost`, a single label or a bare public suffix. */
export function registrableDomain(host: string): string | null {
  const h = (host || '').trim().replace(/^\.+|\.+$/g, '').toLowerCase();
  if (!h || h.includes(':') || IPV4.test(h)) return null;
  const labels = h.split('.');
  if (labels.length < 2 || !labels.every((l) => HOST_LABEL.test(l))) return null;
  const lastTwo = labels.slice(-2).join('.');
  const lastThree = labels.slice(-3).join('.');
  if (SHARED_SUFFIXES.has(lastTwo) || SHARED_SUFFIXES.has(lastThree)) {
    const n = SHARED_SUFFIXES.has(lastThree) ? 3 : 2;
    return labels.length > n ? labels.slice(-(n + 1)).join('.') : null;
  }
  const tld = labels[labels.length - 1] ?? '';
  if (tld.length === 2 && SECOND_LEVEL.has(labels[labels.length - 2] ?? '')) {
    return labels.length >= 3 ? lastThree : null;
  }
  return lastTwo;
}

/**
 * The sign-in host nobody had to write down: `auth.` + the registrable domain of the site URL
 * (`NEXT_PUBLIC_SITE_URL=https://my.reforms.ai` → `auth.reforms.ai`). Null for localhost, an IP or a bad URL.
 */
export function deriveAuthHost(siteUrl: string | undefined | null, label = 'auth'): string | null {
  if (!siteUrl) return null;
  let host: string;
  try {
    host = new URL(siteUrl.includes('://') ? siteUrl : `https://${siteUrl}`).hostname;
  } catch {
    return null;
  }
  const apex = registrableDomain(host);
  return apex && HOST_LABEL.test(label) ? `${label}.${apex}` : null;
}

/** `reforms.ai` / `https://reforms.ai` → `{ hostname, origin }`. Anything with a path, query, credentials or port is refused. */
export function parseSsoHost(raw: string | undefined | null): { hostname: string; origin: string } | null {
  const value = (raw || '').trim();
  if (!value || /[\s\\]/.test(value)) return null;
  let url: URL;
  try {
    url = new URL(value.includes('://') ? value : `https://${value}`);
  } catch {
    return null;
  }
  if (url.protocol !== 'https:' || url.username || url.password || url.port) return null;
  if ((url.pathname !== '/' && url.pathname !== '') || url.search || url.hash) return null;
  const hostname = url.hostname.toLowerCase();
  if (!registrableDomain(hostname)) return null;
  return { hostname, origin: `https://${hostname}` };
}

/** Compare against the sign-in host's apex: `host` itself, or any subdomain of that apex. */
export function resolveSso(
  sso: SsoConfig | undefined | null,
  current: { hostname: string; protocol?: string } | null,
): SsoState {
  const hostValue = sso?.authHost || sso?.host;
  if (!sso || !hostValue) return { ...OFF, reason: 'not-configured' };
  const parsed = parseSsoHost(hostValue);
  const apex = parsed ? registrableDomain(parsed.hostname) : null;
  if (!parsed || !apex) return { ...OFF, reason: 'invalid-host' };
  const authPath = normalizeAuthPath(sso.path);
  if (!current) {
    // Server render: nothing to compare with. Report the config, never a decision.
    return { enabled: false, isAuthHost: false, authOrigin: parsed.origin, authPath, apex, reason: 'outside-apex' };
  }
  const hostname = current.hostname.toLowerCase();
  const inApex = hostname === apex || hostname.endsWith(`.${apex}`);
  if (!inApex || current.protocol === 'http:') {
    return { enabled: false, isAuthHost: false, authOrigin: null, authPath, apex, reason: 'outside-apex' };
  }
  return { enabled: true, isAuthHost: hostname === parsed.hostname, authOrigin: parsed.origin, authPath, apex };
}

function normalizeAuthPath(path: string | undefined): string {
  const p = (path || '/auth').trim();
  return p.startsWith('/') && !p.startsWith('//') && !/[\s\\]/.test(p) ? p.replace(/\/+$/, '') || '/auth' : '/auth';
}

/**
 * The one gate for a `next` value. Returns the normalized URL (absolute https, or a path) or null.
 *
 * Refused: another host, a lookalike (`evilreforms.ai`, `reforms.ai.evil.com`), `//host`, `/\host`,
 * `user@host`, `user:pass@host`, any scheme but https (`javascript:`, `data:`, `http:`), a port,
 * whitespace and control characters (including percent-encoded ones), and a target that is the
 * sign-in page itself (a nested `?next=` would bounce forever or chain to a second target).
 */
export function safeNext(raw: unknown, apex: string | null, authPath = '/auth'): string | null {
  if (typeof raw !== 'string') return null;
  const value = raw;
  if (!value || value.length > 2048) return null;
  // Controls, spaces, backslashes: browsers read `\` as `/`, so `/\evil.com` is `//evil.com`.
  // eslint-disable-next-line no-control-regex
  if (/[\u0000- \u007f-\u009f\\]/.test(value)) return null;
  if (/%(?:0[0-9a-f]|1[0-9a-f]|5c|7f)/i.test(value)) return null;
  // An encoded slash right after the first one (`/%2f…`) is `//host` once something decodes it.
  if (/^\/(?:%2f|%2e%2f)/i.test(value)) return null;

  let url: URL;
  if (value.startsWith('/')) {
    if (value.startsWith('//')) return null;
    try {
      url = new URL(value, 'https://placeholder.invalid');
    } catch {
      return null;
    }
    return isAuthTarget(url.pathname, authPath) ? null : `${url.pathname}${url.search}${url.hash}`;
  }

  if (!apex) return null;
  try {
    url = new URL(value);
  } catch {
    return null;
  }
  if (url.protocol !== 'https:' || url.username || url.password || url.port) return null;
  const host = url.hostname.toLowerCase();
  if (!(host === apex || host.endsWith(`.${apex}`))) return null;
  if (!host.split('.').every((l) => HOST_LABEL.test(l))) return null;
  if (isAuthTarget(url.pathname, authPath)) return null;
  return `https://${host}${url.pathname}${url.search}${url.hash}`;
}

function isAuthTarget(pathname: string, authPath: string): boolean {
  const norm = pathname.replace(/^\/[a-z]{2}(?=\/|$)/, '').replace(/\/+$/, '') || '/';
  return norm === authPath || norm.startsWith(`${authPath}/`);
}

/** Added by the sign-in host to the `next` it sends a signed-in visitor back to. */
export const SSO_RETURN = 'sso_ret';
/** Added by a follower that got the visitor back from the host and still sees no session. */
export const SSO_ERROR = 'sso_error';

function withParam(url: string, name: string, value: string | null): string {
  const abs = !url.startsWith('/');
  const u = new URL(url, 'https://placeholder.invalid');
  if (value === null) u.searchParams.delete(name);
  else u.searchParams.set(name, value);
  return abs ? u.href : `${u.pathname}${u.search}${u.hash}`;
}

/** `next` with the return marker: the follower can tell it was sent back by the host. */
export function markReturn(next: string): string {
  return withParam(next, SSO_RETURN, '1');
}

export function hasReturnMarker(url: string | null | undefined): boolean {
  if (!url) return false;
  try {
    return new URL(url, 'https://placeholder.invalid').searchParams.has(SSO_RETURN);
  } catch {
    return false;
  }
}

export function stripReturnMarker(url: string): string {
  return withParam(url, SSO_RETURN, null);
}

/**
 * `https://reforms.ai/auth?next=<next>`; `next` is dropped when it does not pass `safeNext`.
 *
 * `failed` = the follower was just sent back by the host and still has no session (the shared
 * cookie did not reach it). The URL then carries `sso_error=cookie`, and the host shows the form with
 * a message instead of sending the visitor back again: that is the cycle breaker.
 */
export function buildSsoLoginUrl(state: SsoState, next?: string | null, failed = false): string | null {
  if (!state.enabled || !state.authOrigin) return null;
  const base = `${state.authOrigin}${state.authPath}`;
  const checked = next ? safeNext(next, state.apex, state.authPath) : null;
  const query: string[] = [];
  if (checked) query.push(`next=${encodeURIComponent(stripReturnMarker(checked))}`);
  if (failed) query.push(`${SSO_ERROR}=cookie`);
  return query.length ? `${base}?${query.join('&')}` : base;
}

/** True when `href` is this app's own sign-in route (`/auth`, `/ru/auth/`), the thing the router rewrites. */
export function isAuthRoute(href: string, authPath: string): boolean {
  if (!href.startsWith('/') || href.startsWith('//')) return false;
  return isAuthTarget(href.split(/[?#]/)[0] ?? '', authPath);
}

// ── module-level registry: set by AuthProvider, read by the router and the middleware-free guards ──

let current: { config: SsoConfig | null } = { config: null };

/** Called by `AuthProvider` while rendering. Idempotent. */
export function configureSso(config: SsoConfig | null): void {
  current = { config };
}

/** The decision for the page the browser is on. Off on the server. */
export function getSsoState(): SsoState {
  if (typeof window === 'undefined') return resolveSso(current.config, null);
  return resolveSso(current.config, window.location);
}

export function getSsoConfig(): SsoConfig | null {
  return current.config;
}

/** The `next` value that should travel to the sign-in host for the page the user is on now. */
export function currentNextUrl(): string | null {
  if (typeof window === 'undefined') return null;
  return window.location.href;
}

let warned = false;
/** One console line, once: why SSO is off here. Silent when it is simply not configured. */
export function warnSsoOff(state: SsoState, hostname: string): void {
  if (warned || state.enabled || !state.reason || state.reason === 'not-configured') return;
  warned = true;
  const why =
    state.reason === 'outside-apex'
      ? `"${hostname}" is not under ${state.apex ?? 'the sign-in host'}, so there is no shared cookie domain. Using this host's own sign-in page (normal for localhost).`
      : 'auth.sso.host is not a valid https host name (no path, port or credentials).';
   
  console.warn(`[django-cfg] single sign-in is off: ${why}`);
}

/** Test hook. */
export function __resetSsoForTests(): void {
  current = { config: null };
  warned = false;
}
