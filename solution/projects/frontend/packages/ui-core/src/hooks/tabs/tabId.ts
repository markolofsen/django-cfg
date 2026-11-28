import { CFG_KEYS } from '@djangocfg/api/storage';
/**
 * Stable per-tab identifier. Persisted in sessionStorage so a single
 * tab keeps its id across in-tab reloads (Cmd-R) but a new tab gets a
 * fresh one. Falls back to an in-memory id when sessionStorage is
 * unavailable (private mode, sandboxed iframes, SSR).
 *
 * The id includes `performance.timeOrigin` so leader election can
 * prefer the longest-lived tab without an extra "born_at" field —
 * lexicographic ordering of the id matches age ordering closely enough
 * for our purposes (ties broken by random suffix).
 */

const KEY = CFG_KEYS.uiTabId.key;

let cached: string | null = null;

function makeId(): string {
  const origin = typeof performance !== 'undefined' ? performance.timeOrigin : Date.now();
  const rand = Math.random().toString(36).slice(2, 10);
  // Zero-padded so string compare matches numeric compare.
  return `${Math.floor(origin).toString(10).padStart(16, '0')}-${rand}`;
}

export function getTabId(): string {
  if (cached) return cached;
  if (typeof sessionStorage === 'undefined') {
    cached = makeId();
    return cached;
  }
  try {
    const existing = sessionStorage.getItem(KEY);
    if (existing) {
      cached = existing;
      return existing;
    }
    const next = makeId();
    sessionStorage.setItem(KEY, next);
    cached = next;
    return next;
  } catch {
    cached = makeId();
    return cached;
  }
}
