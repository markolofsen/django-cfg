'use client';

import * as React from 'react';

import { useUIPersistedState } from '../../../lib/persist';

const SCOPE = 'tabs';

export interface UseTabsStateOptions<T extends string = string> {
  /**
   * Whitelist of allowed tab values. If the persisted value is not in
   * this list, falls back to default. Pass when you don't want a stale
   * value (e.g. tab renamed/removed) to leak through.
   */
  allowed?: readonly T[];
}

export interface UseTabsStateResult<T extends string = string> {
  /** Current tab value (default until hydrated, or if stored value is no longer allowed). */
  tab: T;
  /** Persist new tab value. Wire to `<Tabs onValueChange={...}>`. */
  setTab: (next: T) => void;
  /** Remove the persisted entry. */
  reset: () => void;
}

/**
 * Persist Tabs `value` between sessions.
 *
 * @example
 * const { tab, setTab } = useTabsState('settings-page', 'general', { allowed: ['general', 'appearance', 'advanced'] });
 * <Tabs value={tab} onValueChange={setTab}>...</Tabs>
 */
export function useTabsState<T extends string = string>(
  key: string,
  defaultTab: T,
  options: UseTabsStateOptions<T> = {},
): UseTabsStateResult<T> {
  const { allowed } = options;
  const sanitize = React.useCallback(
    (raw: T) => {
      if (typeof raw !== 'string') return undefined;
      if (allowed && !allowed.includes(raw)) return undefined;
      return raw;
    },
    [allowed],
  );

  const { value, setValue, reset } = useUIPersistedState<T>(
    SCOPE,
    key,
    defaultTab,
    { sanitize },
  );

  return { tab: value, setTab: setValue, reset };
}
