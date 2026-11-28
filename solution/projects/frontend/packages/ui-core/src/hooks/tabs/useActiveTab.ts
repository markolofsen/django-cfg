'use client';

import { useEffect } from 'react';
import { useShallow } from 'zustand/react/shallow';

import {
  ensureActiveTabCoordinator,
  useActiveTabStore,
} from './activeTabStore';

export interface UseActiveTabReturn {
  /** Stable id for this tab. Survives in-tab reload, dies with the tab. */
  tabId: string;
  /** True while the user has focus on this tab. */
  isActive: boolean;
  /** True when this tab is the elected leader across all open app tabs. */
  isLeader: boolean;
  /** Current leader id (may be this tab or another). */
  leaderId: string;
}

/**
 * Subscribe to cross-tab state: focus + leader election.
 *
 * Use cases:
 *   - Only the leader mutates `document.title` / favicon to avoid all
 *     open tabs blinking in unison.
 *   - Only the leader holds a websocket; followers consume snapshots
 *     via broadcast.
 *   - `isActive` for "the user is watching this exact tab" gating.
 *
 * The coordinator is shared across every consumer in the app — calling
 * the hook in multiple components costs only a store subscription.
 */
export function useActiveTab(): UseActiveTabReturn {
  useEffect(() => {
    ensureActiveTabCoordinator();
  }, []);

  return useActiveTabStore(
    useShallow((s) => ({
      tabId: s.tabId,
      isActive: s.isActive,
      isLeader: s.isLeader,
      leaderId: s.leaderId,
    })),
  );
}

/** Subscribe to just the `isActive` flag — no leader-election reads. */
export function useIsTabActive(): boolean {
  useEffect(() => {
    ensureActiveTabCoordinator();
  }, []);
  return useActiveTabStore((s) => s.isActive);
}

/** Subscribe to just the `isLeader` flag. */
export function useIsTabLeader(): boolean {
  useEffect(() => {
    ensureActiveTabCoordinator();
  }, []);
  return useActiveTabStore((s) => s.isLeader);
}
