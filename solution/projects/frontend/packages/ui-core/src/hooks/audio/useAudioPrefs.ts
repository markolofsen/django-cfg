'use client';

/**
 * Persistent audio preferences (volume / mute / per-event toggles).
 *
 * One zustand store per `storageKey` — instances with different keys
 * persist independently (chat / alerts / per-product). Cross-tab sync
 * via the `storage` event ships with zustand's persist middleware.
 */

import { create, type StoreApi, type UseBoundStore } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

export interface AudioPrefsState<E extends string = string> {
  /** 0..1 master volume. */
  volume: number;
  /** Master mute (overrides per-event toggles). */
  muted: boolean;
  /** Per-event opt-out — `false` silences a single trigger. */
  enabled: Partial<Record<E, boolean>>;
  setVolume: (v: number) => void;
  setMuted: (m: boolean) => void;
  setEventEnabled: (event: E, enabled: boolean) => void;
}

const clamp01 = (v: number): number => {
  if (!Number.isFinite(v)) return 1;
  return v < 0 ? 0 : v > 1 ? 1 : v;
};

/**
 * Per-key registry so repeated calls with the same `storageKey` return
 * the same store instance — necessary for cross-component state sharing
 * (e.g. ChatHeader audio toggle + ChatLauncher bus reading the same key).
 *
 * `E` is phantom — nothing at runtime restricts which event names the store
 * accepts, so one instance serves callers that name different event unions.
 * The store is therefore built and stored at the widest instantiation, and
 * every narrower `AudioPrefsState<E>` is assignable from it.
 */
const registry = new Map<string, UseBoundStore<StoreApi<AudioPrefsState<string>>>>();

export function createAudioPrefsStore<E extends string = string>(
  storageKey: string,
): UseBoundStore<StoreApi<AudioPrefsState<E>>> {
  const cached = registry.get(storageKey);
  if (cached) return cached;

  const store = create<AudioPrefsState<string>>()(
    persist(
      (set) => ({
        volume: 1,
        muted: false,
        enabled: {},
        setVolume: (v) => set({ volume: clamp01(v) }),
        setMuted: (m) => set({ muted: !!m }),
        setEventEnabled: (event, enabled) =>
          set((s) => ({ enabled: { ...s.enabled, [event]: enabled } })),
      }),
      {
        name: storageKey,
        storage: createJSONStorage(() => {
          if (typeof window === 'undefined') {
            return {
              getItem: () => null,
              setItem: () => undefined,
              removeItem: () => undefined,
            };
          }
          return window.localStorage;
        }),
        partialize: (s) => ({ volume: s.volume, muted: s.muted, enabled: s.enabled }),
        version: 1,
      },
    ),
  );

  registry.set(storageKey, store);
  return store;
}

/**
 * React hook helper — returns the persisted prefs store hook for a given
 * `storageKey`. Callers can use it as a normal zustand hook with selectors.
 *
 * @example
 * ```ts
 * const usePrefs = useAudioPrefs<'sent' | 'received'>('myapp.audio');
 * const muted = usePrefs((s) => s.muted);
 * ```
 */
export function useAudioPrefs<E extends string = string>(
  storageKey: string,
): UseBoundStore<StoreApi<AudioPrefsState<E>>> {
  return createAudioPrefsStore<E>(storageKey);
}
