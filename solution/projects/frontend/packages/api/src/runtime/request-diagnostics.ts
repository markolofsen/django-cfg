/** Browser diagnostics shared by every generated client, independent of React. */

import { APIError, APIConfigurationError, NetworkError } from './errors';

let sequence = 0;

/** A reference identifies an occurrence, not the monitoring fingerprint. */
export function diagnosticReference(): string {
  try {
    if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
      return `ERR-${crypto.randomUUID().replace(/-/g, '').slice(0, 12).toUpperCase()}`;
    }
  } catch { /* use the clock fallback */ }
  return `ERR-${Date.now().toString(36).toUpperCase()}-${(++sequence).toString(36).toUpperCase()}`;
}

/** Keep the endpoint, never URL userinfo, query parameters or fragments. */
export function diagnosticUrl(value: string): string {
  try {
    const parsed = value.startsWith('//') ? new URL(value, window.location.href) : new URL(value);
    if (parsed.protocol === 'http:' || parsed.protocol === 'https:') {
      return (parsed.origin + parsed.pathname).slice(0, 400);
    }
    return '[non-http URL]';
  } catch {
    return value.startsWith('//') || /^https?:/i.test(value)
      ? '[invalid URL]' : value.split(/[?#]/, 1)[0]!.slice(0, 400);
  }
}

export function printDiagnostic(
  source: 'validation' | 'request', reference: string, method: string,
  url: string, diagnostic: string, level: 'warn' | 'error' = 'error',
): void {
  if (typeof window === 'undefined') return;
  try {
    console[level](`[DjangoCFG:${source}] ${reference} ${method} ${diagnosticUrl(url)}: ${diagnostic}`);
  } catch { /* Observability must never change the request result. */ }
}

interface RequestDiagnostic {
  reference: string;
  url: string;
  method: string;
  error: string;
  statusCode?: number;
  possibly_cors?: boolean;
  timestamp: Date;
}

/**
 * Report only the final failure of an operation. Ordinary HTTP client refusals
 * belong to the calling form/auth flow; they get a console line, not a global
 * toast or another monitoring alert. Never log exception messages, raw bodies,
 * headers or input values. Browser fetch cannot prove that CORS caused a failure.
 */
export function reportRequestFailure(error: unknown, method: string, url: string): void {
  if (typeof window === 'undefined') return;
  try {
    let detail: string;
    let statusCode: number | undefined;
    let possiblyCors = false;
    let endpoint = url;
    if (error instanceof APIError) {
      statusCode = error.statusCode;
      endpoint = error.url || url;
      if (statusCode >= 200 && statusCode < 300) {
        detail = `HTTP ${statusCode}: response was not valid JSON`;
      } else {
        detail = `HTTP ${statusCode}`;
        const fields = Object.keys(error.fieldErrors);
        // DRF keys can be supplied by the server; only field-shaped names.
        const names = fields.slice(0, 12).map(key =>
          /^[a-zA-Z_][a-zA-Z0-9_-]{0,63}$/.test(key) ? key : '[key]');
        if (names.length) detail += `; field errors: ${names.join(', ')}${fields.length > 12 ? ', …' : ''}`;
      }
    } else if (error instanceof NetworkError) {
      endpoint = error.url || url;
      // A generated operation preserves its own public NetworkError.url on a
      // failed refresh. Use the nested transport error for the diagnostic.
      const cause = error.originalError as (Error & { url?: unknown }) | undefined;
      if (cause?.name === 'NetworkError' && typeof cause.url === 'string' && cause.url) {
        endpoint = cause.url;
      }
      try {
        possiblyCors = new URL(endpoint, window.location.href).origin !== window.location.origin;
      } catch { /* no usable origin */ }
      detail = possiblyCors
        ? 'Cross-origin network request failed (possible CORS, DNS, TLS or connection failure)'
        : 'Network request failed (connection or response stream)';
    } else if (error instanceof APIConfigurationError) {
      detail = 'API origin is not configured';
    } else if (error && typeof error === 'object' && (error as { name?: unknown }).name === 'TimeoutError') {
      detail = 'Request timed out';
    } else {
      // Strict Zod is already reported by the validation-event path.
      // Unknown JS exceptions are not transport errors.
      return;
    }
    // A transient refresh failure may carry the refresh endpoint rather
    // than the operation URL. The refresh request is always POST.
    if (endpoint !== url && /\/token\/refresh\/?$/.test(diagnosticUrl(endpoint))) method = 'POST';
    const expectedRefusal = statusCode !== undefined && statusCode >= 400 && statusCode < 500;
    const reference = diagnosticReference();
    const safeUrl = diagnosticUrl(endpoint);
    printDiagnostic('request', reference, method, safeUrl, detail, expectedRefusal ? 'warn' : 'error');
    if (!expectedRefusal && typeof CustomEvent !== 'undefined') {
      const event: RequestDiagnostic = {
        reference, url: safeUrl, method, error: detail, statusCode,
        ...(possiblyCors && { possibly_cors: true }),
        timestamp: new Date(),
      };
      window.dispatchEvent(new CustomEvent<RequestDiagnostic>('network-error', { detail: event }));
    }
  } catch { /* Never replace the original failure. */ }
}
