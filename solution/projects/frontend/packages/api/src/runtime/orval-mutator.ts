import * as zod from 'zod';

import { resolveApiUrl } from './api-origin';
import { auth, getRealtimeCid } from './auth';
import { APIConfigurationError, APIError, NetworkError, isTransientRefreshError } from './errors';
import { storeTrace, tracePath } from './store-trace';
import { dispatchValidationError } from './validation-events';
import { reportRequestFailure } from './request-diagnostics';

export type BodyType<BodyData> = BodyData;
export type ErrorType<Error> = Error;

/**
 * `RequestInit` plus the per-operation flags the generator emits through Orval `requestOptions` (H2.4). Callers
 * can pass them too; a caller's value wins over the generated one.
 */
export type DjangoRequestInit = RequestInit & {
  /** Response schema. A miss is reported, and the data returned, unless `validation` is `'strict'`. */
  schema?: zod.ZodTypeAny;
  /**
   * A sign-in step (the generator sets it on the 7 of them). No refresh first, no refresh on a 401, and a 401 never
   * expires the session: it is a credential refusal, returned to the caller as an `APIError`.
   */
  skipAuthRefresh?: boolean;
  /**
   * `'none'`: a public operation. No `Authorization` header from the store, no refresh on a 401, and a 401 never
   * expires the session. An `Authorization` header passed in `headers` is still sent.
   */
  auth?: 'none';
  /** `'direct'`: send to the API host (`NEXT_PUBLIC_API_URL` or the explicit origin), never the proxy or static mode. */
  origin?: 'direct';
  /**
   * `'report'` (default): a schema miss dispatches `zod-validation-error` and returns the data as the server sent
   * it. `'strict'`: the miss rejects with the `ZodError`.
   */
  validation?: 'strict' | 'report';
};

const parseBody = async (response: Response): Promise<{ body: unknown; json: boolean }> => {
  if ([204, 205, 304].includes(response.status)) return { body: undefined, json: false };
  const text = await response.text();
  if (!text) return { body: undefined, json: false };
  const type = response.headers.get('content-type') ?? '';
  if (type.includes('json')) {
    try { return { body: JSON.parse(text), json: true }; } catch { return { body: text, json: false }; }
  }
  return { body: text, json: false };
};

const isAbortError = (error: unknown): boolean =>
  Boolean(error && typeof error === 'object' && (error as { name?: unknown }).name === 'AbortError');

const pathOf = (url: string): string => {
  try { return new URL(url).pathname; } catch { return url.split(/[?#]/, 1)[0] ?? url; }
};

/**
 * The error the original request rejects with when its refresh failed but the session stays (H0.7). Rebuilt as
 * this copy's class, because the shared in-flight refresh may have been started by another copy.
 */
const transientRefreshFailure = (error: unknown, requestUrl: string): Error => {
  const { name, message, statusCode, response, url, statusText } = error as {
    name?: string; message?: string; statusCode?: number; response?: unknown; url?: string; statusText?: string;
  };
  if (name === 'APIConfigurationError') return new APIConfigurationError(message);
  if (name === 'APIError' && typeof statusCode === 'number') {
    return new APIError(statusCode, response, url ?? requestUrl, message, statusText ?? '');
  }
  if (name === 'AbortError') return error as Error;
  return new NetworkError('Session refresh could not reach the API', { cause: error }, requestUrl);
};

const executeRequest = async <T>(url: string, options: DjangoRequestInit): Promise<T> => {
  const {
    schema,
    skipAuthRefresh,
    auth: authMode,
    origin,
    validation,
    ...requestInit
  } = options;
  // The operation's own flags decide first (H1.3): a public operation or a sign-in step neither refreshes nor
  // expires the session. The URL is not read for this; the generator marks the operations.
  const isPublic = authMode === 'none';
  const sessionNeutral = isPublic || skipAuthRefresh === true;
  const requestUrl = resolveApiUrl(url, { origin });
  const mayRefresh = !sessionNeutral && !requestUrl.includes('/token/refresh/');
  const headers = new Headers(requestInit.headers);
  const callerAuthorization = headers.has('Authorization');

  // Refresh first (H1.1): an access token the store knows has expired would only earn a 401, so a live refresh
  // token mints a new one before the request goes out. Not for a sign-in step (`mayRefresh` is false there): a
  // refused refresh would expire the session (and redirect) while the user is signing in.
  let refreshFailed = false;
  if (mayRefresh && !callerAuthorization && auth.needsRefresh()) {
    try {
      await auth.refreshNow();
    } catch (error) {
      if (isTransientRefreshError(error)) throw transientRefreshFailure(error, requestUrl);
      // The session is gone and its listeners were told; the request goes out without a token.
      refreshFailed = true;
    }
  }

  const transportHeaders = auth.clientHeaders();
  for (const [key, value] of Object.entries(transportHeaders)) {
    if (isPublic && key === 'Authorization') continue;
    if (!headers.has(key)) headers.set(key, value);
  }
  const method = (requestInit.method ?? 'GET').toUpperCase();
  if (!['GET', 'HEAD', 'OPTIONS'].includes(method) && !headers.has('X-Realtime-Cid')) {
    const cid = getRealtimeCid();
    if (cid) headers.set('X-Realtime-Cid', cid);
  }

  const perform = async (): Promise<{ response: Response; body: unknown; json: boolean }> => {
    let response: Response;
    try {
      response = await fetch(requestUrl, {
        ...requestInit,
        headers,
        credentials: requestInit.credentials ?? (auth.getWithCredentials() ? 'include' : 'same-origin'),
      });
      const { body, json } = await parseBody(response);
      return { response, body, json };
    } catch (error) {
      // Body-stream failures matter too. Preserve the caller's original
      // abort reason, including an explicit AbortSignal.timeout().
      if (requestInit.signal?.aborted || isAbortError(error)) throw error;
      throw new NetworkError('Network request failed', { cause: error }, requestUrl);
    }
  };

  let result = await perform();
  if (result.response.status === 401 && mayRefresh && !refreshFailed) {
    let refreshed: string | null = null;
    try {
      refreshed = await auth.refreshNow();
    } catch (error) {
      // The refresh could not say whether the token is dead (network, configuration, a 5xx): the session stays
      // and the request fails with that cause, not with a 401 that reads as "signed out".
      if (isTransientRefreshError(error)) throw transientRefreshFailure(error, requestUrl);
      // refreshNow() has already cleared the session and notified listeners;
      // preserve the original 401 as the endpoint error for the caller.
      refreshFailed = true;
    }
    if (refreshed) {
      headers.set('Authorization', `Bearer ${refreshed}`);
      result = await perform();
    }
  }

  if (result.response.status === 401 && !refreshFailed) {
    if (sessionNeutral) {
      // A refusal from a sign-in step or a public operation is a credential error, not a dead session.
      storeTrace('401.passthrough', { path: tracePath(requestUrl) });
    } else {
      // Any stored token counts here, live or not: the server has just refused it.
      const hadSession = Boolean(auth.getToken() || auth.getRefreshToken());
      if (hadSession) {
        storeTrace('store.expire', { why: '401', path: tracePath(requestUrl) });
        auth.clearSession();
        auth.notifySessionExpired();
      }
      auth.notifyUnauthorized();
    }
  }

  if (!result.response.ok) {
    throw new APIError(result.response.status, result.body, requestUrl, undefined, result.response.statusText);
  }

  if (schema && result.body !== undefined) {
    const parsed = schema.safeParse(result.body);
    if (parsed.success) return parsed.data as T;

    const path = pathOf(requestUrl);
    // A 2xx page that is not JSON (an SPA fallback, a WAF or CDN page) is a transport problem, not schema drift
    // (audit E7): report it as the response it was.
    if (!result.json) {
      const type = result.response.headers.get('content-type') || 'no content type';
      throw new APIError(
        result.response.status,
        result.body,
        requestUrl,
        `Expected a JSON response from ${method} ${path}, received ${type}`,
        result.response.statusText,
      );
    }

    dispatchValidationError({
      operation: `${method} ${path}`,
      path,
      method,
      error: parsed.error,
      response: result.body,
      timestamp: new Date(),
    });
    if (validation === 'strict') throw parsed.error;
    // Soft Zod (H0.6, owner decision 2026-11-23): the page keeps the data the server sent.
    return result.body as T;
  }
  return result.body as T;
};

/** Report final failures once; a successfully recovered 401 is not an error. */
export const djangoFetch = async <T>(url: string, options: DjangoRequestInit = {}): Promise<T> => {
  try {
    return await executeRequest<T>(url, options);
  } catch (error) {
    const isTimeout = Boolean(error && typeof error === 'object' &&
      (error as { name?: unknown }).name === 'TimeoutError');
    if (isTimeout || (!options.signal?.aborted && !isAbortError(error))) {
      reportRequestFailure(error, (options.method ?? 'GET').toUpperCase(), url);
    }
    throw error;
  }
};
