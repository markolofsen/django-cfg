/**
 * Store events for the auth trace (H1.7), read in the browser with `__cfgAuth.dump()`.
 *
 * The runtime does not import `auth/trace.ts` (the reader lives in the auth layer and is installed by the package
 * entry). It forwards through `globalThis.__cfgAuthTrace`, and queues in `__cfgAuthTraceQ` until the reader
 * installs, the contract `installAuthTrace` drains. The reader drops keys that look sensitive; on top of that the
 * store passes decisions only: never a token, a cookie value or a query string.
 */

export type StoreTraceFields = Record<string, string | number | boolean | null>;

const QUEUE_LIMIT = 200;

export function storeTrace(ev: string, fields?: StoreTraceFields): void {
  if (typeof window === 'undefined') return;
  try {
    const g = globalThis as Record<string, unknown>;
    const sink = g.__cfgAuthTrace;
    if (typeof sink === 'function') {
      (sink as (ev: string, fields?: StoreTraceFields) => void)(ev, fields);
      return;
    }
    const queue = Array.isArray(g.__cfgAuthTraceQ) ? (g.__cfgAuthTraceQ as unknown[]) : (g.__cfgAuthTraceQ = []) as unknown[];
    if (queue.length < QUEUE_LIMIT) queue.push([Date.now(), ev, fields]);
  } catch {
    // Tracing never breaks auth.
  }
}

/** The path of a request URL, without query or hash (a query can carry a code). */
export function tracePath(url: string): string {
  try {
    return new URL(url, 'http://relative.invalid').pathname;
  } catch {
    return url.split(/[?#]/, 1)[0] ?? '';
  }
}
