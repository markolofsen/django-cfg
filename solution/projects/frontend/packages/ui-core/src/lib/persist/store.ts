'use client';

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { CFG_KEYS } from '@djangocfg/api/storage';

/**
 * Centralized UI-state persistence for ui-core components.
 *
 * Layout: `state[scope][key] = value`. Scopes namespace different
 * categories (e.g. `'drawer-size'`, `'tabs'`, `'accordion'`) so keys
 * never collide across components.
 *
 * One localStorage entry serves all components — single migration
 * surface, single «reset all UI preferences» button.
 */
type ScopeMap = Record<string, Record<string, unknown>>;

interface UIPersistStore {
  state: ScopeMap;
  set: (scope: string, key: string, value: unknown) => void;
  get: <T>(scope: string, key: string) => T | undefined;
  remove: (scope: string, key: string) => void;
  clearScope: (scope: string) => void;
  clearAll: () => void;
  /** DevTools/inspection: snapshot of all scopes. */
  getAll: () => ScopeMap;
  /** DevTools/inspection: list scope names. */
  listScopes: () => string[];
}

const noopStorage = {
  getItem: () => null,
  setItem: () => undefined,
  removeItem: () => undefined,
};

export const useUIPersistStore = create<UIPersistStore>()(
  persist(
    (set, get) => ({
      state: {},
      set: (scope, key, value) => {
        set((s) => ({
          state: {
            ...s.state,
            [scope]: { ...s.state[scope], [key]: value },
          },
        }));
      },
      get: <T,>(scope: string, key: string) =>
        get().state[scope]?.[key] as T | undefined,
      remove: (scope, key) => {
        set((s) => {
          const scoped = s.state[scope];
          if (!scoped || !(key in scoped)) return s;
          const { [key]: _removed, ...rest } = scoped;
          return { state: { ...s.state, [scope]: rest } };
        });
      },
      clearScope: (scope) => {
        set((s) => {
          if (!(scope in s.state)) return s;
          const { [scope]: _removed, ...rest } = s.state;
          return { state: rest };
        });
      },
      clearAll: () => set({ state: {} }),
      getAll: () => get().state,
      listScopes: () => Object.keys(get().state),
    }),
    {
      name: CFG_KEYS.uiState.key,
      version: 1,
      storage: createJSONStorage(() =>
        typeof window !== 'undefined' ? window.localStorage : noopStorage,
      ),
      // Components hydrate explicitly on mount via `useUIPersistedState`.
      skipHydration: true,
    },
  ),
);
