'use client';

/**
 * useSession — reactive session snapshot from the generated auth store.
 *
 * The ONE way to answer "am I logged in" in React. The store owns the
 * semantics (JWT `exp`-aware, refresh-token-aware) and pushes changes on
 * token writes, refresh success/failure, expiry (internal timer), and
 * cross-tab / cross-store sync. No polling, no ticks.
 */

import { useSyncExternalStore } from 'react';

import { auth } from '../../runtime/auth';

import type { SessionSnapshot, SessionStatus } from '../../runtime/auth';

export type { SessionSnapshot, SessionStatus };

export function useSession(): SessionSnapshot {
  return useSyncExternalStore(auth.subscribe, auth.getSnapshot, auth.getServerSnapshot);
}
