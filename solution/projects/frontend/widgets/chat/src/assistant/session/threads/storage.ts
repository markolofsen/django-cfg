'use client';

import { useMemo } from 'react';

import type { SessionStorage } from './sessions';

/** The last used session id in a Storage (default `localStorage`). Never throws: remembering is a convenience (private mode, a full quota, SSR). */
export function createSessionStorage(key: string, backing?: Pick<Storage, 'getItem' | 'setItem' | 'removeItem'>): SessionStorage {
  const store = () => backing ?? (typeof localStorage === 'undefined' ? null : localStorage);
  return {
    read: () => {
      try {
        return store()?.getItem(key) ?? null;
      } catch {
        return null;
      }
    },
    write: (id) => {
      try {
        if (id) store()?.setItem(key, id);
        else store()?.removeItem(key);
      } catch {
        // see above
      }
    },
  };
}

/** A stable `SessionStorage` for `useSession({ storage })`: the key should be namespaced to the app (and to the account if accounts share a browser). */
export function useRememberedSession(key: string): SessionStorage {
  return useMemo(() => createSessionStorage(key), [key]);
}
