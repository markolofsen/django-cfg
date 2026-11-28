'use client';

import { useSyncExternalStore } from 'react';

import { IDLE_SNAPSHOT } from '../store';
import { useRealtimeClient } from './context';

import type { ConnectionState, RealtimeSnapshot } from '../store';

const noSubscription = () => () => {};
const selectConnection = (s: RealtimeSnapshot): ConnectionState => s.connection;

/**
 * Read the realtime store. Without a selector: the connection state.
 *
 * A selector must return a value already in the snapshot (`s.topics[t]`,
 * `s.frames`), never a new object or array: the snapshot shares structure, a
 * fresh object would re-render on every frame.
 */
export function useRealtimeState(): ConnectionState;
export function useRealtimeState<T>(selector: (snapshot: RealtimeSnapshot) => T): T;
export function useRealtimeState<T>(selector?: (snapshot: RealtimeSnapshot) => T): T | ConnectionState {
  const store = useRealtimeClient()?.store ?? null;
  const select = selector ?? selectConnection;
  return useSyncExternalStore(
    store === null ? noSubscription : store.subscribe,
    () => select(store === null ? IDLE_SNAPSHOT : store.getSnapshot()),
    () => select(IDLE_SNAPSHOT),
  );
}
