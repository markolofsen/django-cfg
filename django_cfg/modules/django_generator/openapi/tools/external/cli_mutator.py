"""Render the standalone, stateless Fetch transport for CLI clients."""

from __future__ import annotations


def render_cli_mutator(*, auth_mode: str = "default") -> str:
    """Return import-free TypeScript; callers supply the API origin per request."""
    if auth_mode not in ("default", "public"):
        raise ValueError(f"Unsupported auth_mode: {auth_mode!r}")
    return _TRANSPORT.replace("__PUBLIC_AUTH__", "true" if auth_mode == "public" else "false")


_TRANSPORT = r'''// Generated standalone CLI transport. No shared authentication state.
export type ApiClientErrorKind = 'config' | 'network' | 'http' | 'invalid_json' | 'validation';

export class ApiClientError extends Error {
  readonly kind: ApiClientErrorKind;
  readonly status: number | undefined;
  readonly data: unknown;
  override readonly cause: unknown;

  constructor(
    kind: ApiClientErrorKind,
    message: string,
    details: { status?: number; data?: unknown; cause?: unknown } = {},
  ) {
    super(message);
    this.name = 'ApiClientError';
    this.kind = kind;
    this.status = details.status;
    this.data = details.data;
    this.cause = details.cause;
  }
}

export interface DjangoRequestInit extends RequestInit {
  /** Required at runtime: an explicit HTTP(S) origin, with no path. */
  baseUrl?: string;
  auth?: 'none';
  schema?: { parse(value: unknown): unknown };
  /** Accepted for generated operations; this transport never refreshes. */
  skipAuthRefresh?: boolean;
  /** Accepted for generated operations; baseUrl is always used directly. */
  origin?: 'direct';
}

export type ErrorType<_Error> = ApiClientError;
export type BodyType<BodyData> = BodyData;

function resolveRequestUrl(url: string, baseUrl: string | undefined): string {
  try {
    if (typeof baseUrl !== 'string' || baseUrl !== baseUrl.trim() || !/^https?:\/\/[^/?#@\\\s]+\/?$/i.test(baseUrl)) {
      throw new Error('baseUrl must be an explicit HTTP(S) origin without credentials, path, query or hash');
    }
    const base = new URL(baseUrl);
    if (base.username || base.password || base.pathname !== '/' || base.search || base.hash) {
      throw new Error('baseUrl must contain only an HTTP(S) origin');
    }
    if (typeof url !== 'string' || !url.startsWith('/') || url.startsWith('//') || /[\\\u0000-\u0020\u007f]/.test(url)) {
      throw new Error('url must be a relative path starting with /, not //');
    }
    const resolved = new URL(url, base);
    if (resolved.origin !== base.origin) {
      throw new Error('Request URL must stay on baseUrl origin');
    }
    return resolved.href;
  } catch (cause) {
    throw new ApiClientError('config', 'Invalid CLI request URL or baseUrl', { cause });
  }
}

function rethrowAbort(cause: unknown, signal: AbortSignal | null | undefined): void {
  signal?.throwIfAborted();
  if (cause !== null && typeof cause === 'object' && 'name' in cause && cause.name === 'AbortError') {
    throw cause;
  }
}

export const djangoFetch = async <T>(url: string, options?: DjangoRequestInit): Promise<T> => {
  const { baseUrl, auth, schema, skipAuthRefresh, origin, ...request } = options ?? {};
  // These flags carry no state or side effects in a CLI client.
  void skipAuthRefresh;
  void origin;
  const requestUrl = resolveRequestUrl(url, baseUrl);
  let headers: Headers;
  try {
    headers = new Headers(request.headers);
  } catch (cause) {
    throw new ApiClientError('config', 'Invalid CLI request headers', { cause });
  }
  if (__PUBLIC_AUTH__ || auth === 'none') {
    headers.delete('Authorization');
    headers.delete('Cookie');
    request.credentials = 'omit';
  }

  let response: Response;
  let text: string;
  try {
    request.signal?.throwIfAborted();
    response = await fetch(requestUrl, { ...request, headers });
    request.signal?.throwIfAborted();
    text = response.status === 204 || request.method?.toUpperCase() === 'HEAD' ? '' : await response.text();
    request.signal?.throwIfAborted();
  } catch (cause) {
    rethrowAbort(cause, request.signal);
    throw new ApiClientError('network', 'CLI request or response body failed', { cause });
  }

  let data: unknown;
  // HEAD and 204 deliberately have no JSON body. Other successes must be JSON.
  const empty = response.status === 204 || request.method?.toUpperCase() === 'HEAD';
  if (!empty) {
    try {
      data = JSON.parse(text);
    } catch (cause) {
      if (response.ok) {
        throw new ApiClientError('invalid_json', 'Response was not valid JSON', {
          status: response.status, data: text, cause,
        });
      }
      data = text;
    }
  }
  if (!response.ok) {
    throw new ApiClientError('http', `HTTP ${response.status}`, { status: response.status, data });
  }
  if (schema !== undefined) {
    try {
      data = schema.parse(data);
    } catch (cause) {
      throw new ApiClientError('validation', 'Response schema validation failed', {
        status: response.status, data, cause,
      });
    }
  }
  return data as T;
};
'''


__all__ = ["render_cli_mutator"]
