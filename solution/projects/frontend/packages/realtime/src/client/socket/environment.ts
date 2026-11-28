/**
 * What the client needs from its host, injectable so the core runs in node
 * tests and stories with no browser: a WebSocket constructor, timers, and a
 * "the network or the page came back" signal.
 */

/**
 * The part of `WebSocket` the client uses. Handlers take `never` so that the
 * browser `WebSocket` (whose handlers expect DOM events) and the in-memory mock
 * both fit; the client narrows every event it receives.
 */
export interface SocketLike {
  readonly readyState: number;
  send(data: string): void;
  close(code?: number, reason?: string): void;
  onopen: ((ev: never) => void) | null;
  onmessage: ((ev: never) => void) | null;
  onclose: ((ev: never) => void) | null;
  onerror: ((ev: never) => void) | null;
}

export type SocketFactory = new (url: string) => SocketLike;

export type TimerHandle = ReturnType<typeof setTimeout>;

export interface Clock {
  now(): number;
  setTimeout(fn: () => void, ms: number): TimerHandle;
  clearTimeout(handle: TimerHandle): void;
}

/** Read `globalThis` at call time, so fake timers installed after import still apply. */
export const systemClock: Clock = {
  now: () => Date.now(),
  setTimeout: (fn, ms) => globalThis.setTimeout(fn, ms),
  clearTimeout: (handle) => globalThis.clearTimeout(handle),
};

/** Calls `onWake` when a retry is worth trying now; returns the detach function. */
export type WakeSource = (onWake: () => void) => () => void;

interface EventTargetLike {
  addEventListener(type: string, listener: () => void): void;
  removeEventListener(type: string, listener: () => void): void;
}

function hasEvents(value: unknown): value is EventTargetLike {
  return (
    typeof value === 'object' &&
    value !== null &&
    'addEventListener' in value &&
    typeof value.addEventListener === 'function' &&
    'removeEventListener' in value &&
    typeof value.removeEventListener === 'function'
  );
}

/** `online` on the window, and the page becoming visible. A no-op outside a browser. */
export const browserWake: WakeSource = (onWake) => {
  const win: unknown = globalThis;
  const doc: unknown = 'document' in globalThis ? globalThis.document : undefined;
  const onVisible = () => {
    if (hasEvents(doc) && 'visibilityState' in doc && doc.visibilityState === 'visible') onWake();
  };
  if (hasEvents(win)) win.addEventListener('online', onWake);
  if (hasEvents(doc)) doc.addEventListener('visibilitychange', onVisible);
  return () => {
    if (hasEvents(win)) win.removeEventListener('online', onWake);
    if (hasEvents(doc)) doc.removeEventListener('visibilitychange', onVisible);
  };
};

/** The host's `WebSocket`, or `null` where there is none (SSR, old runtimes). */
export function globalSocketFactory(): SocketFactory | null {
  if (!('WebSocket' in globalThis) || typeof globalThis.WebSocket !== 'function') return null;
  return globalThis.WebSocket;
}
