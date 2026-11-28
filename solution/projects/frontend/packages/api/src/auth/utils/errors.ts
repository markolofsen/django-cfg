/** Read a property off an unknown value without asserting its shape. */
const prop = (value: unknown, key: string): unknown =>
  typeof value === 'object' && value !== null
    ? (value as Record<string, unknown>)[key]
    : undefined;

/**
 * The transport's own fallback message, e.g. `HTTP 404: ` or `HTTP 500: Boom`.
 *
 * `APIError` builds this when the caller supplies no message of its own
 * (`_api/generated/helpers/errors.ts`), so it is never server prose — it is the
 * status line restated. Under HTTP/2 `statusText` is empty, which is how a bare
 * `HTTP 404:` (and `HTTP 0:` for a response that never arrived) reached a sign-in form and told the user nothing at all.
 */
const TRANSPORT_FALLBACK = /^HTTP \d{1,3}:\s*/;

/**
 * Translation keys for the copy this module can choose.
 *
 * Every one already exists, translated, in all 17 locales of `@djangocfg/i18n`
 * — `api.errors.*` for transport conditions and `ui.errors.*` for the ones a
 * person can act on. Nothing is added here: a second key saying "Server is
 * unavailable" in a namespace of its own would be a second owner of the same
 * sentence, and the one that loses is whichever the caller did not use.
 *
 * A 404 maps to `serverUnavailable`, not to `ui.errors.notFound` ("Not found"):
 * on a sign-in POST the missing thing is the ENDPOINT, which tells the visitor
 * nothing about a page and everything about the service being down.
 */
export const AUTH_ERROR_KEYS = {
  invalidCredentials: 'ui.errors.unauthorized',
  rateLimited: 'api.errors.rateLimited',
  serverUnavailable: 'api.errors.serverUnavailable',
  networkError: 'api.errors.networkError',
  generic: 'ui.errors.generic',
} as const;

export type AuthErrorKey = (typeof AUTH_ERROR_KEYS)[keyof typeof AUTH_ERROR_KEYS];

/**
 * English copy for each key, so a caller without a translator still renders a
 * sentence. The catalogue is authoritative; this is the offline twin.
 */
const FALLBACK_COPY: Record<AuthErrorKey, string> = {
  [AUTH_ERROR_KEYS.invalidCredentials]: 'Please sign in to continue',
  [AUTH_ERROR_KEYS.rateLimited]: 'Too many requests. Please wait.',
  [AUTH_ERROR_KEYS.serverUnavailable]: 'Server is unavailable',
  [AUTH_ERROR_KEYS.networkError]: 'Network error',
  [AUTH_ERROR_KEYS.generic]: 'Something went wrong',
};

/** Map a status code to the key whose copy explains it. */
const keyForStatus = (status: number | undefined): AuthErrorKey => {
  if (status === undefined) return AUTH_ERROR_KEYS.generic;
  // 0 is "no response at all": the network dropped, CORS refused (a proxy answering 404 while the API restarts carries
  // no CORS headers, so the browser reports it as 0), or the request was blocked. Not a server verdict.
  if (status === 0) return AUTH_ERROR_KEYS.networkError;
  if (status === 401 || status === 403) return AUTH_ERROR_KEYS.invalidCredentials;
  // A 404 here is a missing endpoint, not a missing page — see AUTH_ERROR_KEYS.
  if (status === 404) return AUTH_ERROR_KEYS.serverUnavailable;
  if (status === 429) return AUTH_ERROR_KEYS.rateLimited;
  if (status >= 500) return AUTH_ERROR_KEYS.serverUnavailable;
  return AUTH_ERROR_KEYS.generic;
};

/** What the auth layer decided to show, and why. */
export interface AuthErrorCopy {
  /** Ready-to-render text: server prose, or this module's English fallback. */
  message: string;
  /**
   * Set only when `message` came from `FALLBACK_COPY`. A caller holding a
   * translator renders `t(key)` instead; server prose carries no key because
   * the backend already chose the words and the locale.
   */
  key?: AuthErrorKey;
}

/**
 * Decide what a failed auth call should say.
 *
 * Order: text the SERVER wrote, then copy chosen from the status code, then a
 * generic sentence. Server prose wins because the backend knows the specific
 * reason ("This code has expired") that a status code cannot express.
 *
 * Each candidate is checked to be a string before it is returned. Under the
 * previous `any` the check was only that the property was truthy, so a DRF
 * field-error object (`{detail: {email: [...]}}`) reached the UI as
 * "[object Object]" — an error message that tells the user nothing.
 *
 * `HTTP <code>:` strings are rejected on the way through. They are the
 * transport restating its own status line, not prose anyone wrote to be read,
 * and treating them as a message is what put a bare `HTTP 404:` under a
 * sign-in field. The code itself stays useful — `logAuthFailure` puts it in
 * the console, where diagnosis belongs.
 */
export const resolveAuthError = (error: unknown, fallback?: string): AuthErrorCopy => {
  if (typeof error === 'string' && error && !TRANSPORT_FALLBACK.test(error)) {
    return { message: error };
  }

  const candidates = [
    prop(error, 'message'),
    prop(error, 'detail'),
    prop(prop(error, 'response'), 'error'),
    prop(prop(error, 'response'), 'detail'),
    prop(prop(error, 'response'), 'message'),
    prop(prop(prop(error, 'response'), 'data'), 'detail'),
  ];

  for (const candidate of candidates) {
    if (typeof candidate === 'string' && candidate && !TRANSPORT_FALLBACK.test(candidate)) {
      return { message: candidate };
    }
  }

  // Both spellings are read: `statusCode` is what `APIError` declares, while a
  // Response-shaped rejection reaching here from outside the interceptor
  // carries `status`.
  const rawStatus = prop(error, 'statusCode') ?? prop(error, 'status');
  const status = typeof rawStatus === 'number' ? rawStatus : undefined;

  // A caller's own fallback only applies where the status says nothing; a 404
  // must not be reported as "Failed to send the code".
  if (status === undefined && fallback) {
    return { message: fallback };
  }

  const key = keyForStatus(status);
  return { message: FALLBACK_COPY[key], key };
};

/**
 * `resolveAuthError` for callers that only want the string.
 *
 * Kept because most call sites store a plain `error` string in form state and
 * have no translator to hand.
 */
export const formatAuthError = (error: unknown, fallback?: string): string =>
  resolveAuthError(error, fallback).message;

/**
 * Log a failed auth call at the level its cause deserves.
 *
 * A 4xx on an auth endpoint is the USER getting it wrong — a mistyped OTP, an
 * expired code, a bad password. It is the endpoint working. Logged through
 * `console.error` it became a production alert: `@djangocfg/devtools` captures
 * `console.error` as an `ERROR` event, so every typo raised "❌ Error" in
 * Telegram, complete with consola's `%c` CSS in the message body. Real faults
 * drown in that.
 *
 * 5xx, a network failure and a broken response contract stay at `error`:
 * nobody can fix those by retyping, and they are what the alert is for.
 *
 * Both `statusCode` (what `APIError` declares) and `status` are read, because
 * a Response-shaped rejection can reach here from code that does not go
 * through the interceptor.
 */
export const logAuthFailure = (
  log: { warn: (...args: unknown[]) => void; error: (...args: unknown[]) => void },
  message: string,
  error: unknown,
): void => {
  const code = prop(error, 'statusCode') ?? prop(error, 'status');
  const isClientError = typeof code === 'number' && code >= 400 && code < 500;
  if (isClientError) {
    log.warn(message, error);
    return;
  }
  log.error(message, error);
};
