'use client';

import { useEffect, useSyncExternalStore } from 'react';

/**
 * Module-level store of every hotkey that registered itself with a
 * `description`. Lets you render a `?` cheat-sheet without prop-drilling.
 */
export interface RegisteredHotkey {
  /** Key combo (raw string passed to `useHotkey` — format with `formatHotkey()` for display). */
  combo: string;
  /** Human-readable purpose. */
  description: string;
  /** Optional scope label for grouping (e.g. `'chat'`, `'global'`). */
  scope?: string;
}

const registry = new Map<symbol, RegisteredHotkey>();
const listeners = new Set<() => void>();

function notify() {
  for (const cb of listeners) cb();
}

/**
 * Register a hotkey entry while a component is mounted. Internal —
 * called by `useHotkey` when a `description` is provided.
 */
export function registerHotkey(entry: RegisteredHotkey): () => void {
  const key = Symbol(entry.combo);
  registry.set(key, entry);
  notify();
  return () => {
    registry.delete(key);
    notify();
  };
}

/** Read the live list of registered hotkeys. SSR-safe. */
export function useHotkeyHelp(): RegisteredHotkey[] {
  return useSyncExternalStore(
    (cb) => {
      listeners.add(cb);
      return () => {
        listeners.delete(cb);
      };
    },
    () => Array.from(registry.values()),
    () => [],
  );
}

/** Imperative read for non-React consumers (debug panels, etc.). */
export function getRegisteredHotkeys(): RegisteredHotkey[] {
  return Array.from(registry.values());
}

/**
 * Hook variant — call alongside `useHotkey` when the binding lives
 * outside the hook (e.g. raw `window.addEventListener` consumers that
 * still want to appear in the cheat sheet).
 */
export function useRegisterHotkey(entry: RegisteredHotkey | null): void {
  // Registration is keyed on the entry's FIELDS, not its identity: callers pass
  // an inline object, so depending on `entry` would unregister and re-register
  // on every render and notify every cheat-sheet subscriber each time.
  const { combo, description, scope } = entry ?? {};

  useEffect(() => {
    if (!combo || !description) return;
    return registerHotkey({ combo, description, scope });
  }, [combo, description, scope]);
}
