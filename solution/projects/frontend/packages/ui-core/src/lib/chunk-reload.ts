/**
 * Stale-chunk recovery.
 *
 * After a deploy the old tab still points at hashed `/_next/static/...` assets
 * that no longer exist. The next lazy import / route navigation fails with a
 * ChunkLoadError (or a cancelled fetch), which is a transient condition, not an
 * app bug. The right response is ONE hard reload, not the crash screen.
 *
 * Single implementation for the whole stack: `Boundary` (render errors),
 * `UiProviders` (window `error` / `unhandledrejection`) and `ErrorLayout`
 * (`global-error.tsx`) all call into this module. Loop guard: a timestamp in
 * `sessionStorage`; a second chunk failure inside the window shows the real
 * fallback. Without a usable `sessionStorage` we never auto-reload (a reload
 * would lose any in-memory guard and could loop).
 */

export const CHUNK_RELOAD_STORAGE_KEY = 'djangocfg:chunk-reload-at';
/** Minimum gap between two automatic reloads in one tab session. */
export const CHUNK_RELOAD_WINDOW_MS = 30_000;

const CHUNK_MESSAGE_PATTERNS: RegExp[] = [
  /loading chunk [\w./-]+ failed/i, // webpack
  /loading css chunk [\w./-]+ failed/i, // webpack CSS chunk
  /failed to fetch dynamically imported module/i, // Chrome / Turbopack
  /error loading dynamically imported module/i, // Firefox
  /importing a module script failed/i, // Safari
  /unable to preload css/i, // Vite
];

const STATIC_ASSET_RE = /\/_next\/static\//;
const FETCH_FAILURE_RE = /failed to fetch|load failed|networkerror|aborted|canceled|cancelled|signal is aborted/i;

function asText(value: unknown): { name: string; message: string; stack: string } {
  if (value && typeof value === 'object') {
    const v = value as { name?: unknown; message?: unknown; stack?: unknown };
    return {
      name: typeof v.name === 'string' ? v.name : '',
      message: typeof v.message === 'string' ? v.message : '',
      stack: typeof v.stack === 'string' ? v.stack : '',
    };
  }
  return { name: '', message: typeof value === 'string' ? value : '', stack: '' };
}

/**
 * True when `error` is the signature of a missing/cancelled build asset:
 * ChunkLoadError, "Loading chunk N failed", "Loading CSS chunk", dynamic import
 * failures, or a failed/aborted fetch that names a `/_next/static/` URL.
 */
export function isChunkLoadError(error: unknown): boolean {
  const { name, message, stack } = asText(error);
  if (name === 'ChunkLoadError') return true;
  if (CHUNK_MESSAGE_PATTERNS.some((re) => re.test(message))) return true;
  // Generic network-ish failure only counts when it concerns a build asset.
  if (FETCH_FAILURE_RE.test(`${name} ${message}`) && STATIC_ASSET_RE.test(`${message} ${stack}`)) {
    return true;
  }
  return false;
}

/** Resource-load `error` event from a `<script>`/`<link>` pointing at `/_next/static/`. */
export function isStaticAssetLoadEvent(event: Event): boolean {
  const target = event.target as { tagName?: string; src?: string; href?: string } | null;
  if (!target || typeof target.tagName !== 'string') return false;
  const tag = target.tagName.toUpperCase();
  if (tag !== 'SCRIPT' && tag !== 'LINK') return false;
  return STATIC_ASSET_RE.test(target.src || target.href || '');
}

function readStamp(): number | null | 'unavailable' {
  try {
    const raw = window.sessionStorage.getItem(CHUNK_RELOAD_STORAGE_KEY);
    if (!raw) return null;
    const n = Number(raw);
    return Number.isFinite(n) ? n : null;
  } catch {
    return 'unavailable';
  }
}

/** Read-only check: would an automatic reload be allowed right now? */
export function canAutoReloadForChunk(now: number = Date.now()): boolean {
  if (typeof window === 'undefined') return false;
  const stamp = readStamp();
  if (stamp === 'unavailable') return false;
  return stamp === null || now - stamp > CHUNK_RELOAD_WINDOW_MS || now < stamp;
}

/**
 * Reload once if the guard allows. Returns true when a reload was triggered
 * (callers should render nothing meanwhile), false when the guard blocked it
 * (callers show their normal error UI).
 */
export function reloadForChunkError(now: number = Date.now()): boolean {
  if (!canAutoReloadForChunk(now)) return false;
  try {
    window.sessionStorage.setItem(CHUNK_RELOAD_STORAGE_KEY, String(now));
  } catch {
    return false;
  }
  window.location.reload();
  return true;
}

/**
 * Install window-level listeners that catch chunk failures outside React
 * (route-change imports, failed `<script>`/`<link>` tags, rejected promises).
 * Idempotent; returns a cleanup function.
 */
export function installChunkReloadListeners(): () => void {
  if (typeof window === 'undefined') return () => {};
  const w = window as unknown as { __djangocfgChunkReload?: boolean };
  if (w.__djangocfgChunkReload) return () => {};
  w.__djangocfgChunkReload = true;

  const onError = (event: Event) => {
    if (event instanceof ErrorEvent ? isChunkLoadError(event.error ?? event.message) : isStaticAssetLoadEvent(event)) {
      reloadForChunkError();
    }
  };
  const onRejection = (event: PromiseRejectionEvent) => {
    if (isChunkLoadError(event.reason)) reloadForChunkError();
  };
  // capture=true: resource errors do not bubble.
  window.addEventListener('error', onError, true);
  window.addEventListener('unhandledrejection', onRejection);
  return () => {
    window.removeEventListener('error', onError, true);
    window.removeEventListener('unhandledrejection', onRejection);
    w.__djangocfgChunkReload = false;
  };
}
