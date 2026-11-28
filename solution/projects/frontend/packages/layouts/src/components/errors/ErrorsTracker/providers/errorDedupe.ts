import type { ErrorDetail } from '../types';

/**
 * Generate unique ID for error
 */
let errorIdCounter = 0;
export function generateErrorId(type: string): string {
  return `${type}-error-${Date.now()}-${++errorIdCounter}`;
}

/**
 * Generate deduplication key for error
 * Used to prevent duplicate toasts for the same error
 */
function getErrorDedupeKey(detail: ErrorDetail): string {
  switch (detail.type) {
    case 'validation':
      return `validation:${detail.path}:${detail.method}`;
    case 'cors':
      return `cors:${detail.url}`;
    case 'network':
      return `network:${detail.url}:${detail.statusCode || 'unknown'}`;
    case 'runtime':
      return `runtime:${detail.source}:${detail.message.slice(0, 50)}`;
    default:
      return `unknown:${Date.now()}`;
  }
}

/** Deduplication window in ms - same errors within this window are ignored */
const DEDUPE_WINDOW_MS = 5000;

/** Max entries in deduplication map before forced cleanup */
const DEDUPE_MAX_ENTRIES = 50;

/** Map to track recent errors for deduplication (browser-only) */
let recentErrors: Map<string, number> | null = null;

function getRecentErrorsMap(): Map<string, number> {
  // Lazy init - only create in browser
  if (typeof window === 'undefined') {
    // Return dummy map for SSR (won't persist)
    return new Map();
  }
  if (!recentErrors) {
    recentErrors = new Map();
  }
  return recentErrors;
}

/**
 * Check if error should be shown (not a duplicate)
 * Returns true if error should be shown, false if it's a duplicate
 */
export function shouldShowError(detail: ErrorDetail): boolean {
  const map = getRecentErrorsMap();
  const key = getErrorDedupeKey(detail);
  const now = Date.now();
  const lastSeen = map.get(key);

  // Clean up old entries when map gets too large
  if (map.size > DEDUPE_MAX_ENTRIES) {
    for (const [k, timestamp] of map.entries()) {
      if (now - timestamp > DEDUPE_WINDOW_MS) {
        map.delete(k);
      }
    }
    // If still too large after cleanup, clear oldest half
    if (map.size > DEDUPE_MAX_ENTRIES) {
      const entries = Array.from(map.entries())
        .sort((a, b) => a[1] - b[1])
        .slice(0, Math.floor(map.size / 2));
      for (const [k] of entries) {
        map.delete(k);
      }
    }
  }

  // Check if we've seen this error recently
  if (lastSeen && now - lastSeen < DEDUPE_WINDOW_MS) {
    return false; // Duplicate, don't show
  }

  // Mark as seen
  map.set(key, now);
  return true;
}

/** Throttle production toasts — max 1 per type within this window */
const PROD_TOAST_THROTTLE_MS = 3000;
let lastProdToastByType: Map<string, number> | null = null;

export function shouldThrottleProdToast(type: string): boolean {
  if (typeof window === 'undefined') return false;
  if (!lastProdToastByType) lastProdToastByType = new Map();
  const now = Date.now();
  const last = lastProdToastByType.get(type);
  if (last && now - last < PROD_TOAST_THROTTLE_MS) return true;
  lastProdToastByType.set(type, now);
  return false;
}
