/**
 * The runtime's mutable state, held on `globalThis` so every copy of this module in a page shares it (H0.5).
 *
 * The published package bundles the runtime into each entry (`index`, `auth`, `clients`, `hooks`), and an app
 * can load the ESM and CJS builds or two installs side by side. Module-level variables would give each copy its
 * own session, handlers and origin: a sign-in through `@djangocfg/api/auth` would never reach the root
 * `djangoFetch`. Each slot is created once, by whichever copy runs first, and reused by every other copy.
 *
 * Two slots, both defined here:
 * - `djangocfg.api.auth`: session, transport overrides, handlers, refresh single-flight;
 * - `djangocfg.api.runtime`: the API origin set by `configureApi` / `setApiOrigin` (kept under its existing
 *   name, so a copy that already writes it stays in step).
 *
 * The realtime connection id keeps its own slot (`djangocfg.realtime.cid`, see `auth.ts`).
 */

import type { RefreshResult, SessionSnapshot } from './auth';

export type RefreshHandler = (refreshToken: string) => Promise<RefreshResult>;
export type Listener = () => void;
export type CookieDomainPolicy = 'auto' | string | false;

export interface SharedAuthState {
  /** Raw token cookie values as this page last saw them; `null` until the first browser read. */
  cookieSeen: { access: string | null; refresh: string | null } | null;
  accessToken: string | null;
  refreshToken: string | null;
  /** Persisted API key (`setApiKeyPersist`, localStorage). */
  apiKey: string | null;
  /** In-memory API key for this page (`setApiKey`); wins over the persisted one. */
  apiKeyOverride: string | null;
  locale: string | null;
  timezone: string | null;
  clientId: string | null;
  withCredentials: boolean;
  /** `undefined` until a copy calls `setCookieDomain`; then every copy writes token cookies under it. */
  cookieDomain: CookieDomainPolicy | undefined;
  refreshHandler: RefreshHandler | null;
  refreshInflight: Promise<string | null> | null;
  unauthorized: (() => void) | null;
  expiryListeners: Set<Listener>;
  listeners: Set<Listener>;
  /** Replaced only when the session changes, so `useSyncExternalStore` sees a stable value (React #185). */
  snapshot: SessionSnapshot;
  serverSnapshot: SessionSnapshot;
  notifyQueued: boolean;
  /** The page's `storage` / focus / visibility / `cookieStore` listeners are installed (once per page). */
  syncInstalled: boolean;
  /** Timer that re-reads the session at the next token `exp` while someone is subscribed. */
  expiryTimer: ReturnType<typeof setTimeout> | null;
  /**
   * A token the server just issued already looked expired by this device's clock: `exp` is not trusted on this
   * page, so tokens count by presence and no request refreshes ahead of a 401.
   */
  clockSkewed: boolean;
  /** Warnings already given (`setStorageMode`), so each shows once per page. */
  warned: string[];
}

export interface ApiOriginSlot {
  /** Explicit origin from `configureApi` / `setApiOrigin`: an absolute URL, a same-origin prefix or `''`. */
  origin?: string | null;
  /** Fallback opt-in for same-origin relative requests when nothing else is configured. */
  allowRelative?: boolean;
  /** Invalid values already warned about, so a render-time `configureApi` warns once per value. */
  warned?: string[];
}

const AUTH_SLOT = Symbol.for('djangocfg.api.auth');
const ORIGIN_SLOT = Symbol.for('djangocfg.api.runtime');

const ANONYMOUS: SessionSnapshot = { status: 'anonymous', isAuthenticated: false, accessToken: null };

function defaults(): SharedAuthState {
  return {
    cookieSeen: null,
    accessToken: null,
    refreshToken: null,
    apiKey: null,
    apiKeyOverride: null,
    locale: null,
    timezone: null,
    clientId: null,
    withCredentials: true,
    cookieDomain: undefined,
    refreshHandler: null,
    refreshInflight: null,
    unauthorized: null,
    expiryListeners: new Set(),
    listeners: new Set(),
    snapshot: { ...ANONYMOUS },
    serverSnapshot: { ...ANONYMOUS },
    notifyQueued: false,
    syncInstalled: false,
    expiryTimer: null,
    clockSkewed: false,
    warned: [],
  };
}

const slots = () => globalThis as unknown as Record<symbol, unknown>;
/** Slot objects this copy has already checked, so the shape check runs once per copy and slot. */
const adopted = new WeakSet<object>();

/**
 * The shared auth state. `onCreate` runs once per page, for the copy that creates the slot (it loads the stored
 * session). A slot created by another package version gets any field it lacks.
 */
export function sharedAuthState(onCreate?: (state: SharedAuthState) => void): SharedAuthState {
  const holder = slots();
  const existing = holder[AUTH_SLOT];
  if (existing && typeof existing === 'object') {
    if (!adopted.has(existing)) {
      const target = existing as Record<string, unknown>;
      for (const [key, value] of Object.entries(defaults())) if (!(key in target)) target[key] = value;
      adopted.add(existing);
    }
    return existing as SharedAuthState;
  }
  const created = defaults();
  holder[AUTH_SLOT] = created;
  adopted.add(created);
  onCreate?.(created);
  return created;
}

export function apiOriginSlot(): ApiOriginSlot {
  const holder = slots();
  const existing = holder[ORIGIN_SLOT];
  if (existing && typeof existing === 'object') return existing as ApiOriginSlot;
  const created: ApiOriginSlot = {};
  holder[ORIGIN_SLOT] = created;
  return created;
}
