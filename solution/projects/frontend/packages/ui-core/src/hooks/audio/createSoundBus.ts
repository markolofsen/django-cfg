'use client';

/**
 * Generic notification-sound bus.
 *
 * Lifted from `ui-tools/chat/core/audio/audioBus` and generalised over an
 * arbitrary event-key type so any feature (chat, presence, alerts, …)
 * can reuse the same Safari unlock + multi-fire-safe playback infra.
 *
 * Pitfalls this addresses:
 *   - Safari needs a user-gesture transaction to unlock playback. We
 *     pre-allocate an `<audio>` per cached URL and play() each (muted)
 *     during the unlock event so the whole bus lifts at once.
 *   - Rapid play() calls on the same element cancel each other — we
 *     clone a fresh `HTMLAudioElement` per fire (HTTP cache reuses the
 *     underlying bytes for free).
 *   - SSR safety: all DOM access is gated; module imports never touch
 *     `window`.
 *   - `play()` returns a Promise — we attach `.catch()` everywhere so
 *     blocked-autoplay warnings don't reach the console.
 */

export interface SoundBusOptions<E extends string> {
  /** Map an event key to a sound URL. `false`/missing silences the event. */
  sounds: Partial<Record<E, string | false>>;
  /**
   * Volume 0..1 used for the next `play()` call. Receives the event so
   * callers can scale per-event (e.g. quieter error sounds).
   */
  getVolume: (event?: E) => number;
  /** Master mute. Read on every play. */
  getMuted: () => boolean;
  /** Per-event predicate. Return `false` to suppress one event. */
  isEnabled: (event: E) => boolean;
}

export interface SoundBus<E extends string> {
  play: (event: E) => void;
  preload: (event: E) => void;
  unlock: () => void;
  isUnlocked: () => boolean;
  subscribeUnlock: (cb: (unlocked: boolean) => void) => () => void;
  setSounds: (sounds: Partial<Record<E, string | false>>) => void;
  dispose: () => void;
}

// One unlock state per tab — first gesture inside ANY bus unlocks every
// bus. Matches AudioPlayer's ADR-004 "global per tab" rule.
let unlocked = false;
const unlockListeners = new Set<(v: boolean) => void>();

function setUnlocked(value: boolean) {
  if (unlocked === value) return;
  unlocked = value;
  for (const cb of unlockListeners) cb(value);
}

/** Test helper — resets unlock state between tests. */
export function _resetUnlockForTesting(): void {
  unlocked = false;
  unlockListeners.clear();
}

export function createSoundBus<E extends string>(
  options: SoundBusOptions<E>,
): SoundBus<E> {
  if (typeof window === 'undefined') return noopBus<E>();

  let sounds = options.sounds;
  const cache = new Map<string, HTMLAudioElement>();

  const getOrCreate = (url: string): HTMLAudioElement => {
    const hit = cache.get(url);
    if (hit) return hit;
    const el = new Audio(url);
    el.preload = 'auto';
    el.crossOrigin = 'anonymous';
    cache.set(url, el);
    return el;
  };

  const resolveUrl = (event: E): string | null => {
    const v = sounds[event];
    if (!v) return null;
    return v;
  };

  const play = (event: E) => {
    if (options.getMuted()) return;
    if (!options.isEnabled(event)) return;
    const url = resolveUrl(event);
    if (!url) return;

    getOrCreate(url);
    const fresh = new Audio(url);
    fresh.preload = 'auto';
    fresh.volume = clamp01(options.getVolume(event));
    const p = fresh.play();
    if (p && typeof p.catch === 'function') {
      p.catch(() => {
        // Browser blocked playback (no gesture yet) — ignore.
      });
    }
  };

  const preload = (event: E) => {
    const url = resolveUrl(event);
    if (!url) return;
    const el = getOrCreate(url);
    try {
      el.load();
    } catch {
      // ignore
    }
  };

  const unlock = () => {
    if (unlocked) return;
    for (const el of cache.values()) {
      const wasMuted = el.muted;
      el.muted = true;
      const p = el.play();
      if (p && typeof p.then === 'function') {
        p.then(() => {
          el.pause();
          el.currentTime = 0;
          el.muted = wasMuted;
        }).catch(() => {
          el.muted = wasMuted;
        });
      } else {
        el.pause();
        el.muted = wasMuted;
      }
    }
    setUnlocked(true);
  };

  return {
    play,
    preload,
    unlock,
    isUnlocked: () => unlocked,
    subscribeUnlock(cb) {
      unlockListeners.add(cb);
      return () => unlockListeners.delete(cb);
    },
    setSounds(next) {
      sounds = next;
    },
    dispose() {
      cache.clear();
    },
  };
}

function clamp01(v: number): number {
  if (!Number.isFinite(v)) return 1;
  return v < 0 ? 0 : v > 1 ? 1 : v;
}

function noopBus<E extends string>(): SoundBus<E> {
  return {
    play: () => undefined,
    preload: () => undefined,
    unlock: () => undefined,
    isUnlocked: () => false,
    subscribeUnlock: () => () => undefined,
    setSounds: () => undefined,
    dispose: () => undefined,
  };
}
