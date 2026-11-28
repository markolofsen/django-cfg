'use client';

import * as React from 'react';

import { useUIPersistedState } from '../../../lib/persist';

const SCOPE_WIDTH = 'drawer-size:width';
const SCOPE_HEIGHT = 'drawer-size:height';

export interface UseDrawerSizeOptions {
  /** Which axis to read/write. `'width'` for left/right, `'height'` for top/bottom. */
  axis?: 'width' | 'height';
  /** Clamp loaded value into these bounds (recommended). */
  min?: number;
  max?: number;
}

export interface UseDrawerSizeResult {
  /** Persisted size in px, or `undefined` if nothing stored / not yet hydrated. */
  size: number | undefined;
  /** Persist a new size. */
  setSize: (size: number) => void;
  /** Remove the persisted entry for this key. */
  reset: () => void;
}

/**
 * Hook that wires a Drawer to centralized persisted UI state.
 *
 * Width and height live in separate scopes, so the same `key` can be
 * reused across directions without one axis overwriting the other.
 *
 * @example
 * const drawer = useDrawerSize('settings', { min: 320, max: 900 });
 * <DrawerContent
 *   resizable
 *   resizedSize={drawer.size}
 *   onSizeChange={drawer.setSize}
 * />
 */
export function useDrawerSize(
  key: string,
  options: UseDrawerSizeOptions = {},
): UseDrawerSizeResult {
  const { axis = 'width', min, max } = options;
  const scope = axis === 'height' ? SCOPE_HEIGHT : SCOPE_WIDTH;

  const sanitize = React.useCallback(
    (raw: number) => {
      if (typeof raw !== 'number' || !Number.isFinite(raw)) return undefined;
      let v = raw;
      if (min != null) v = Math.max(v, min);
      if (max != null) v = Math.min(v, max);
      return v;
    },
    [min, max],
  );

  const persisted = useUIPersistedState<number | undefined>(
    scope,
    key,
    undefined,
    { sanitize: (raw) => (raw == null ? undefined : sanitize(raw)) },
  );

  return {
    size: persisted.value,
    setSize: persisted.setValue,
    reset: persisted.reset,
  };
}
