import type { ZodError } from 'zod';

type Body = Record<string, unknown>;

/** The text of a DRF error item: a string, or an object carrying a `message` string. */
const itemText = (item: unknown): string | null => {
  if (typeof item === 'string') return item.trim() ? item : null;
  if (item && typeof item === 'object' && typeof (item as Body).message === 'string') {
    const message = (item as Body).message as string;
    return message.trim() ? message : null;
  }
  return null;
};

/** A string, or an array of error items joined with ", "; `null` when it holds no text. */
const textOf = (value: unknown): string | null => {
  if (Array.isArray(value)) {
    const parts = value.map(itemText).filter((part): part is string => part !== null);
    return parts.length ? parts.join(', ') : null;
  }
  return itemText(value);
};

/**
 * Text the server wrote for the whole request, in order: DRF `detail` (a string or an array), django-cfg's
 * `error` and `message`, then DRF `non_field_errors`.
 */
const serverText = (body: Body | null): string | null => {
  if (!body) return null;
  for (const key of ['detail', 'error', 'message', 'non_field_errors']) {
    const text = textOf(body[key]);
    if (text) return text;
  }
  return null;
};

/** DRF field errors: `field_errors` when the body nests them there, else every array-valued key but `detail`. */
const collectFieldErrors = (body: Body | null): Record<string, string[]> => {
  if (!body) return {};
  const source = body.field_errors && typeof body.field_errors === 'object' && !Array.isArray(body.field_errors)
    ? body.field_errors as Body
    : body;
  const out: Record<string, string[]> = {};
  for (const [key, value] of Object.entries(source)) {
    if (key === 'detail' || !Array.isArray(value)) continue;
    const messages = value.map(itemText).filter((part): part is string => part !== null);
    if (messages.length) out[key] = messages;
  }
  return out;
};

export class APIError extends Error {
  readonly name = 'APIError';
  readonly statusCode: number;
  readonly statusText: string;
  readonly response: unknown;
  readonly url: string;
  /** Field name to its messages, as DRF reports them (`non_field_errors` included). */
  readonly fieldErrors: Record<string, string[]>;
  /** 403 only (H1.5). A 401 is `isAuthError`. */
  readonly isPermissionError: boolean;

  constructor(
    statusCode: number,
    response: unknown,
    url: string,
    message?: string,
    statusText = '',
  ) {
    const body = response && typeof response === 'object' && !Array.isArray(response) ? response as Body : null;
    // The generic form restates the status line; `formatAuthError` recognises it and shows its own copy instead.
    super(message ?? serverText(body) ?? `HTTP ${statusCode}: ${statusText}`.trimEnd());
    this.statusCode = statusCode;
    this.statusText = statusText;
    this.response = response;
    this.url = url;
    this.fieldErrors = collectFieldErrors(body);
    this.isPermissionError = statusCode === 403;
  }

  get details(): Record<string, unknown> | null {
    return this.response && typeof this.response === 'object'
      ? this.response as Record<string, unknown>
      : null;
  }

  /**
   * One sentence for the UI (H1.4): DRF `detail` (string or array), `error`, `message`, `non_field_errors`, then the
   * first field error as `field: message`, then `message` (an explicit one, or the generic `HTTP <status>:`).
   */
  get errorMessage(): string {
    const body = this.details && !Array.isArray(this.details) ? this.details as Body : null;
    const text = serverText(body);
    if (text) return text;
    const [field, messages] = Object.entries(this.fieldErrors).find(([key]) => key !== 'non_field_errors') ?? [];
    if (field && messages?.length) return `${field}: ${messages.join(', ')}`;
    return this.message;
  }

  get isValidationError(): boolean {
    return this.statusCode === 400 || Object.keys(this.fieldErrors).length > 0;
  }

  get isAuthError(): boolean {
    return this.statusCode === 401;
  }

  get isNotFoundError(): boolean {
    return this.statusCode === 404;
  }

  get isServerError(): boolean {
    return this.statusCode >= 500 && this.statusCode < 600;
  }
}

export class NetworkError extends Error {
  readonly name = 'NetworkError';
  readonly url: string;
  readonly originalError: Error | undefined;

  constructor(message = 'Network request failed', options?: ErrorOptions, url = '') {
    super(message, options);
    this.url = url;
    this.originalError = options?.cause instanceof Error ? options.cause : undefined;
  }
}

/** Raised before fetch when a generated relative operation has no API origin. */
export class APIConfigurationError extends Error {
  readonly name = 'APIConfigurationError';

  constructor(message = 'API origin is not configured') {
    super(message);
  }
}

/**
 * Everything a generated operation can reject with:
 * - `APIError`: the API answered with a non-2xx status, or a 2xx body that is not JSON where a schema expects it;
 * - `NetworkError`: the request (or the session refresh it needed) did not reach the API;
 * - `APIConfigurationError`: no API origin is configured for the request;
 * - `ZodError`: the response missed its schema, only with `validation: 'strict'`;
 * - `DOMException`: the caller's own abort (`AbortError`, or `TimeoutError` from `AbortSignal.timeout`),
 *   rethrown unchanged.
 */
export type ApiClientError = APIError | NetworkError | APIConfigurationError | ZodError | DOMException;

/** Answers of the refresh endpoint that mean the refresh token is dead. */
const TERMINAL_REFRESH_STATUSES = new Set([400, 401, 403]);

/**
 * Whether a failed session refresh leaves the session in place (H0.7): the API was not reached (`NetworkError`),
 * no origin is configured (`APIConfigurationError`), the refresh was aborted, or the refresh endpoint answered
 * something other than 400/401/403 (a 5xx, a 404 from a misrouted proxy). Anything else, including a plain `Error`
 * from a custom refresh handler, ends the session.
 *
 * Checked by `name`, not `instanceof`: the in-flight refresh is shared by every copy of this module in the page,
 * so the error may be an instance of another copy's class.
 */
export function isTransientRefreshError(error: unknown): boolean {
  if (!error || typeof error !== 'object') return false;
  const { name, statusCode } = error as { name?: unknown; statusCode?: unknown };
  if (name === 'NetworkError' || name === 'APIConfigurationError' || name === 'AbortError') return true;
  return name === 'APIError' && typeof statusCode === 'number' && !TERMINAL_REFRESH_STATUSES.has(statusCode);
}
