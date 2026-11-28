'use client';

import { create } from 'zustand';

import { getTabId } from './tabId';
import { cfgStorage } from '@djangocfg/api/storage';

/**
 * Cross-tab coordination store. Singleton, lazily initialised on the
 * first hook subscription.
 *
 * Two orthogonal concepts:
 *   - `isActive` — this tab has user focus right now (visibilitychange
 *     + focus/blur).
 *   - `isLeader` — among open tabs of this app, this tab won the
 *     election. Leadership is stable; it only changes when the current
 *     leader closes/refreshes.
 *
 * Election protocol over a single BroadcastChannel:
 *   on mount:
 *     - announce HELLO with our tabId
 *     - listen for HELLO/CLAIM/BYE
 *   on HELLO from a peer:
 *     - if we think we're leader, reply CLAIM (so the newcomer learns
 *       the current leader without forcing a re-election)
 *   on CLAIM from a peer:
 *     - record their tabId in the peer set; the smallest tabId wins
 *       (tabIds are time-prefixed so smallest == oldest)
 *   on BYE (beforeunload):
 *     - remove peer; if it was the leader, re-elect locally
 *
 * Leader election runs locally on each tab from the same peer-set view,
 * so all tabs converge on the same answer without a coordinator.
 */

export type ActiveTabMessage =
  | { type: 'hello'; tabId: string }
  | { type: 'claim'; tabId: string }
  | { type: 'bye'; tabId: string };

interface ActiveTabState {
  /** Stable id for the current tab. */
  tabId: string;
  /** This tab has user focus. */
  isActive: boolean;
  /** This tab is the elected leader among open tabs. */
  isLeader: boolean;
  /** Currently elected leader id (may be this tab or another). */
  leaderId: string;
  /** All tabs we've seen, including ourselves. */
  peers: string[];
}

const CHANNEL_NAME = cfgStorage.key('ui', 'active_tab');

const initialId = getTabId();

export const useActiveTabStore = create<ActiveTabState>(() => ({
  tabId: initialId,
  isActive: typeof document !== 'undefined' ? !document.hidden : true,
  isLeader: true, // Optimistic — corrected by election on first peer HELLO.
  leaderId: initialId,
  peers: [initialId],
}));

let initialised = false;
let channel: BroadcastChannel | null = null;
let visibilityTeardown: (() => void) | null = null;

function elect(peers: string[]): string {
  // Smallest tabId wins. tabIds are time-prefixed; smallest == oldest.
  return peers.slice().sort()[0]!;
}

function applyPeers(nextPeers: string[]) {
  const me = useActiveTabStore.getState().tabId;
  const peers = Array.from(new Set([me, ...nextPeers])).sort();
  const leaderId = elect(peers);
  useActiveTabStore.setState({
    peers,
    leaderId,
    isLeader: leaderId === me,
  });
}

function post(msg: ActiveTabMessage) {
  channel?.postMessage(msg);
}

function setupVisibility(): () => void {
  if (typeof document === 'undefined') return () => {};

  const sync = () => {
    const hidden = document.hidden || (
      typeof document.hasFocus === 'function' && !document.hasFocus()
    );
    useActiveTabStore.setState({ isActive: !hidden });
  };

  sync();
  document.addEventListener('visibilitychange', sync);
  window.addEventListener('focus', sync);
  window.addEventListener('blur', sync);

  return () => {
    document.removeEventListener('visibilitychange', sync);
    window.removeEventListener('focus', sync);
    window.removeEventListener('blur', sync);
  };
}

/**
 * Idempotent — first call wires up the channel and listeners, later
 * calls are no-ops. Called automatically by `useActiveTab` on mount.
 * Exposed for hosts that want to warm the coordinator before any hook
 * subscribes (e.g. inside an app shell).
 */
export function ensureActiveTabCoordinator(): void {
  if (initialised) return;
  initialised = true;

  visibilityTeardown = setupVisibility();

  if (typeof BroadcastChannel === 'undefined') {
    // Single-tab fallback: we are trivially the leader.
    return;
  }

  channel = new BroadcastChannel(CHANNEL_NAME);
  const me = useActiveTabStore.getState().tabId;

  channel.addEventListener('message', (e) => {
    const msg = e.data as ActiveTabMessage | undefined;
    if (!msg || typeof msg !== 'object') return;

    const { peers: currentPeers } = useActiveTabStore.getState();

    if (msg.type === 'hello') {
      // Acknowledge the newcomer with a CLAIM so they learn about us.
      applyPeers([...currentPeers, msg.tabId]);
      post({ type: 'claim', tabId: me });
    } else if (msg.type === 'claim') {
      applyPeers([...currentPeers, msg.tabId]);
    } else if (msg.type === 'bye') {
      applyPeers(currentPeers.filter((id) => id !== msg.tabId));
    }
  });

  // Announce ourselves.
  post({ type: 'hello', tabId: me });

  const onUnload = () => post({ type: 'bye', tabId: me });
  window.addEventListener('beforeunload', onUnload);
  window.addEventListener('pagehide', onUnload);
}

/**
 * Tear down everything (channel, listeners). Tests only — production
 * tabs live and die with the page.
 */
export function disposeActiveTabCoordinator(): void {
  if (!initialised) return;
  initialised = false;
  channel?.close();
  channel = null;
  visibilityTeardown?.();
  visibilityTeardown = null;
}
