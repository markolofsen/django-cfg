import { IDLE_SNAPSHOT } from './snapshot';

import type { ConnectionState, FrameRecord, RealtimeSnapshot, TopicState } from './snapshot';

export const DEFAULT_FRAME_LIMIT = 50;

/**
 * The read model of one realtime client: connection state, per-topic status
 * and offsets, the last frames. Immutable snapshots with structural sharing, so
 * a selector returning `snapshot.connection` keeps its identity until the
 * connection itself changes (`useSyncExternalStore`-ready).
 *
 * Written only by the client that owns it: the connection writes `connection`
 * and `frames`, the subscription registry writes `topics`.
 */
export interface RealtimeStore {
  getSnapshot(): RealtimeSnapshot;
  subscribe(listener: () => void): () => void;
  setConnection(patch: Partial<ConnectionState>): void;
  setTopic(topic: string, state: TopicState | null): void;
  /** True while something shows frames (a debug panel); the connection skips the log otherwise. */
  readonly recordingFrames: boolean;
  /** Start keeping the frame log until the returned function is called; reference-counted. */
  retainFrames(): () => void;
  recordFrame(frame: Omit<FrameRecord, 'id'>): void;
}

export function createRealtimeStore(frameLimit = DEFAULT_FRAME_LIMIT): RealtimeStore {
  let snapshot = IDLE_SNAPSHOT;
  let frameId = 0;
  let frameReaders = 0;
  const listeners = new Set<() => void>();

  function commit(next: RealtimeSnapshot): void {
    snapshot = next;
    // Copied first: a listener unsubscribing another must not skip it for this change.
    for (const listener of [...listeners]) listener();
  }

  return {
    getSnapshot: () => snapshot,
    subscribe(listener) {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },
    setConnection(patch) {
      const current = snapshot.connection;
      const next: ConnectionState = { ...current, ...patch };
      const changed =
        next.phase !== current.phase ||
        next.attempt !== current.attempt ||
        next.retryAt !== current.retryAt ||
        next.user !== current.user ||
        next.cid !== current.cid ||
        next.lastClose !== current.lastClose;
      if (!changed) return;
      commit({ ...snapshot, connection: next });
    },
    setTopic(topic, state) {
      if (state === null) {
        if (!(topic in snapshot.topics)) return;
        const rest = { ...snapshot.topics };
        delete rest[topic];
        commit({ ...snapshot, topics: rest });
        return;
      }
      commit({ ...snapshot, topics: { ...snapshot.topics, [topic]: state } });
    },
    get recordingFrames() {
      return frameReaders > 0;
    },
    retainFrames() {
      frameReaders += 1;
      let released = false;
      return () => {
        if (released) return;
        released = true;
        frameReaders -= 1;
      };
    },
    recordFrame(frame) {
      if (frameReaders === 0) return;
      frameId += 1;
      const frames = [...snapshot.frames, { ...frame, id: frameId }];
      commit({ ...snapshot, frames: frames.length > frameLimit ? frames.slice(-frameLimit) : frames });
    },
  };
}
