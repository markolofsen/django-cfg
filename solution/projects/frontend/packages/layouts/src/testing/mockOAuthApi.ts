// Storybook / test-only. The one place that fakes the OAuth network for stories:
// `GET /oauth/providers/`, `POST /oauth/<provider>/authorize/` and
// `POST /oauth/<provider>/callback/`, answered at the `fetch` level so the real
// generated client, `useOAuthProviders` and `useOAuthLogin` all run unchanged.
// Any other request is refused, so no story can reach a real backend.

import { CFG_KEYS, cfgStorage } from '@djangocfg/api/storage';
import type { OAuthFailureCode, OAuthProviderId } from '@djangocfg/api/auth';

/** Codes the backend returns in `{ error }` (the closed set of the OpenAPI enum). */
export type OAuthServerErrorCode = Exclude<OAuthFailureCode, 'cancelled' | 'unknown_provider'>;

/** HTTP status per code, from the backend contract table. Exhaustive: a new code fails typecheck. */
const STATUS: Record<OAuthServerErrorCode, number> = {
  oauth_disabled: 503,
  github_oauth_disabled: 503,
  origin_not_allowed: 400,
  missing_redirect_uri: 400,
  invalid_state: 400,
  oauth_exchange_failed: 400,
  invalid_id_token: 400,
  email_missing: 400,
  email_not_verified: 400,
  hosted_domain_not_allowed: 403,
  account_inactive: 403,
  link_not_allowed: 403,
  rate_limited: 429,
  provider_unavailable: 502,
  server_error: 500,
  not_found: 404,
};

/** Every code the server can answer with, for parametrised stories. */
export const OAUTH_SERVER_ERROR_CODES = Object.keys(STATUS) as OAuthServerErrorCode[];

export interface OAuthApiScript {
  /** The enabled providers in display order; `pending` never answers, `unavailable` fails the request. */
  providers?: readonly OAuthProviderId[] | 'pending' | 'unavailable';
  /** `ok` returns the provider URL and a state; `pending` never answers; a code answers with that error. */
  authorize?: 'ok' | 'pending' | OAuthServerErrorCode;
  /** `ok` returns a session; `pending` never answers; a code answers with that error. */
  callback?: 'ok' | 'pending' | OAuthServerErrorCode;
  isNewUser?: boolean;
}

export interface OAuthApiCall {
  method: string;
  path: string;
  provider?: OAuthProviderId;
  body?: unknown;
}

export interface OAuthApiMock {
  /** Every request the page made, in order. */
  readonly calls: readonly OAuthApiCall[];
  /** Requests nothing here answers; always empty in a healthy story. */
  readonly unexpected: readonly string[];
  /** Full-page navigations the page attempted (cancelled, so the story stays put). */
  readonly navigations: readonly string[];
  /** Change the answers mid-story. */
  set(patch: OAuthApiScript): void;
}

export interface OAuthApiSeed {
  /** The `state` this browser stored when it started a flow (what a returning callback is checked against). */
  state?: string;
  provider?: OAuthProviderId;
  /** The back-url a route guard saved before sending the visitor to sign in. */
  savedRedirect?: string;
}

const PROVIDER_NAMES: Record<OAuthProviderId, string> = { github: 'GitHub', google: 'Google' };

const PROVIDER_URLS: Record<OAuthProviderId, string> = {
  github: 'https://github.com/login/oauth/authorize',
  google: 'https://accounts.google.com/o/oauth2/v2/auth',
};

/** The state the mocked `authorize` hands out. */
export const mockOAuthState = (provider: OAuthProviderId): string => `mock-state-${provider}`;

const ROUTE = /\/oauth\/(?:(providers)|(github|google)\/(authorize|callback))\/?$/;

const json = (status: number, body: unknown): Response =>
  new Response(JSON.stringify(body), { status, headers: { 'Content-Type': 'application/json' } });

const failure = (code: OAuthServerErrorCode): Response =>
  json(STATUS[code], { error: code, error_description: `Mock server answered ${code}.` });

const NEVER = new Promise<Response>(() => {});

let active: OAuthApiMock | null = null;

/** The mock a story's `beforeEach` installed. */
export const getOAuthApiMock = (): OAuthApiMock => {
  if (!active) throw new Error('mockOAuthApi: no mock is installed; add `beforeEach: oauthApiMock({...})` to the story.');
  return active;
};

/**
 * Write what a returning visitor would have in this browser.
 * Safe to call again (a remounted story starts from a known storage).
 */
export const seedOAuthBrowser = ({ state, provider, savedRedirect }: OAuthApiSeed): void => {
  cfgStorage.remove(CFG_KEYS.oauthState.key);
  cfgStorage.remove(CFG_KEYS.oauthProvider.key);
  if (state) cfgStorage.write(CFG_KEYS.oauthState.key, state);
  if (provider) cfgStorage.write(CFG_KEYS.oauthProvider.key, provider);
  if (savedRedirect !== undefined) {
    // The redirect manager stores its value JSON-encoded.
    window.sessionStorage.setItem(CFG_KEYS.redirectUrl.key, JSON.stringify(savedRedirect));
  }
};

interface NavigationEventLike extends Event {
  destination: { url: string; sameDocument: boolean };
}
interface NavigationLike {
  addEventListener(type: 'navigate', listener: (event: NavigationEventLike) => void): void;
  removeEventListener(type: 'navigate', listener: (event: NavigationEventLike) => void): void;
}

/**
 * Install the fake OAuth network for one story and capture full-page
 * navigations (the redirect to the provider, the redirect after sign-in) so the
 * iframe is never navigated away. Returns the story cleanup.
 */
const install = (initial: OAuthApiScript): (() => void) => {
  const script: OAuthApiScript = { providers: [], authorize: 'ok', callback: 'ok', ...initial };
  const calls: OAuthApiCall[] = [];
  const unexpected: string[] = [];
  const navigations: string[] = [];

  const mock: OAuthApiMock = {
    calls,
    unexpected,
    navigations,
    set: (patch) => {
      Object.assign(script, patch);
    },
  };

  const originalFetch = globalThis.fetch;
  globalThis.fetch = async (input, init) => {
    const request = new Request(input, init);
    const path = new URL(request.url).pathname;
    const match = ROUTE.exec(path);
    if (!match) {
      unexpected.push(`${request.method} ${request.url}`);
      throw new TypeError(`mockOAuthApi: unexpected request ${request.method} ${request.url}`);
    }

    const [, providersRoute, providerId, action] = match;
    const provider = providerId as OAuthProviderId | undefined;
    const body = request.method === 'POST' ? await request.clone().json().catch(() => undefined) : undefined;
    calls.push({ method: request.method, path, provider, body });

    if (providersRoute) {
      if (script.providers === 'pending') return NEVER;
      if (script.providers === 'unavailable') return failure('server_error');
      return json(200, {
        providers: (script.providers ?? []).map((id) => ({ id, name: PROVIDER_NAMES[id], icon: id })),
      });
    }

    if (action === 'authorize') {
      if (script.authorize === 'pending') return NEVER;
      if (script.authorize !== 'ok' && script.authorize) return failure(script.authorize);
      const state = mockOAuthState(provider!);
      return json(200, { authorization_url: `${PROVIDER_URLS[provider!]}?client_id=mock&state=${state}`, state });
    }

    if (script.callback === 'pending') return NEVER;
    if (script.callback !== 'ok' && script.callback) return failure(script.callback);
    return json(200, {
      requires_2fa: false,
      access: 'mock-access-token',
      refresh: 'mock-refresh-token',
      user: { id: 1, email: 'jane.cooper@example.com' },
      is_new_user: script.isNewUser ?? false,
      is_new_connection: false,
    });
  };

  const navigation = (window as unknown as { navigation?: NavigationLike }).navigation;
  const onNavigate = (event: NavigationEventLike) => {
    // `replaceState` and hash changes stay in the document; only a real page change is held back.
    if (event.destination.sameDocument) return;
    navigations.push(event.destination.url);
    if (event.cancelable) event.preventDefault();
  };
  navigation?.addEventListener('navigate', onNavigate);

  // The auth hooks log every failure they handle (`api:auth` tag). A story that
  // drives a failure on purpose would trip the console gate with the very line
  // that proves the flow ran, so this one tag is dropped while the mock is on.
  const restoreConsole = (['error', 'warn'] as const).map((method) => {
    const previous = console[method];
    console[method] = (...args: unknown[]) => {
      if (typeof args[0] === 'string' && args[0].includes('api:auth')) return;
      previous.apply(console, args);
    };
    return () => {
      console[method] = previous;
    };
  });

  active = mock;
  return () => {
    for (const restore of restoreConsole) restore();
    navigation?.removeEventListener('navigate', onNavigate);
    globalThis.fetch = originalFetch;
    active = null;
  };
};

/**
 * A story `beforeEach`: fakes the OAuth endpoints with `script` and optionally
 * seeds this browser's storage.
 *
 * ```ts
 * beforeEach: oauthApiMock({ providers: ['google'] }),
 * ```
 */
export const oauthApiMock =
  (script: OAuthApiScript = {}, seed?: OAuthApiSeed) =>
  (): (() => void) => {
    if (seed) seedOAuthBrowser(seed);
    return install(script);
  };
