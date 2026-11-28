/**
 * Shared setup for the generated-client smoke suite (see `vitest.smoke.config.ts`).
 *
 * Every case starts like a freshly loaded page: no runtime slot on `globalThis`, no cookie, no storage, no
 * `NEXT_PUBLIC_*` in the process environment, and fresh modules. It then loads one generated group
 * (`cfg-accounts-profile`) and the runtime that group's shim resolves to.
 */
import { vi } from 'vitest';

import { SMOKE_BUILD_ENV } from './env';

export const ENV_ORIGIN = SMOKE_BUILD_ENV.NEXT_PUBLIC_API_URL;
export const CONFIGURED_ORIGIN = 'https://api.configured.test';
export const PROFILE_PATH = '/cfg/accounts/profile/';
export const REFRESH_PATH = '/cfg/accounts/token/refresh/';

/** A body that satisfies the generated `User` schema. */
export const USER = {
  id: 7,
  email: 'ada@example.test',
  first_name: 'Ada',
  last_name: null,
  full_name: 'Ada',
  initials: 'A',
  display_username: 'ada',
  company: null,
  phone: null,
  position: null,
  language: 'de',
  timezone: null,
  avatar: null,
  is_staff: false,
  is_superuser: false,
  date_joined: '2026-01-01T00:00:00+00:00',
  last_login: null,
  unanswered_messages_count: 0,
  api_key: null,
};

/** The same user as a server would send it with one field the contract does not allow (`id` is an int). */
export const USER_OFF_CONTRACT = { ...USER, id: 'seven' };

export const json = (body: unknown, status = 200): Response =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json' } });

/** `TypeError` is what `fetch` rejects with when the host cannot be reached. */
export const unreachable = (): TypeError => new TypeError('fetch failed');

type Reply = Response | Error;

/** Stub `fetch` with one reply per expected request; a request beyond them rejects. */
export function stubFetch(...replies: Reply[]) {
  const queue = [...replies];
  const fetchMock = vi.fn(async (_input: RequestInfo | URL, _init?: RequestInit): Promise<Response> => {
    const next = queue.shift();
    if (next === undefined) throw new Error('smoke: a request nobody expected');
    if (next instanceof Error) throw next;
    return next;
  });
  vi.stubGlobal('fetch', fetchMock);
  return fetchMock;
}

export type FetchMock = ReturnType<typeof stubFetch>;

export const requestUrl = (fetchMock: FetchMock, index: number): string =>
  String(fetchMock.mock.calls[index]?.[0]);

export const requestInit = (fetchMock: FetchMock, index: number): RequestInit =>
  fetchMock.mock.calls[index]?.[1] ?? {};

export const requestHeaders = (fetchMock: FetchMock, index: number): Headers =>
  new Headers(requestInit(fetchMock, index).headers);

/** Forget everything a previous case left behind. */
export function resetPage(): void {
  vi.unstubAllGlobals();
  for (const name of Object.keys(process.env)) {
    if (name.startsWith('NEXT_PUBLIC_')) delete process.env[name];
  }
  // Runtime state shared through `globalThis[Symbol.for('djangocfg.*')]` (API origin, realtime cid, and any
  // store moved there later) outlives `vi.resetModules()`.
  const slots = globalThis as unknown as Record<symbol, unknown>;
  for (const symbol of Object.getOwnPropertySymbols(slots)) {
    if (symbol.description?.startsWith('djangocfg.')) delete slots[symbol];
  }
  // Browser pages only. Node 25+ has a global `localStorage` of its own, which the server cases must not touch.
  if (typeof document !== 'undefined') {
    for (const cookie of document.cookie.split(';')) {
      const name = cookie.split('=')[0]?.trim();
      if (name) document.cookie = `${name}=; Max-Age=0; Path=/`;
    }
    window.localStorage.clear();
    window.sessionStorage.clear();
  }
  vi.resetModules();
}

/** One generated group and the runtime its shim resolves to, as fresh modules. */
export async function loadClient() {
  const group = await import('../src/_api/generated/endpoints/cfg-accounts-profile/cfg-accounts-profile');
  const runtime = await import('../src/runtime');
  // Through the public API as well, so the reset holds wherever the store keeps its state.
  runtime.auth.clearSession();
  runtime.auth.setLocale?.(null);
  return { ...group, ...runtime };
}
