import type { Offset, RealtimeUser, SubErrorCode } from '../protocol';

/**
 * - `idle`: no socket, none wanted (no subscriptions, or closed after the idle delay).
 * - `connecting`: the first attempt after `idle`, until `hello`.
 * - `live`: `hello` received; subscriptions flow.
 * - `reconnecting`: the socket dropped; waiting out the backoff or retrying.
 * - `stopped`: the server refused us (4401, 4403, 4429); no retry until auth changes.
 */
export type ConnectionPhase = 'idle' | 'connecting' | 'live' | 'reconnecting' | 'stopped';

export interface CloseInfo {
  code: number;
  reason: string;
}

export interface ConnectionState {
  phase: ConnectionPhase;
  /** Failed attempts since the last `hello`. */
  attempt: number;
  /** Epoch ms of the next scheduled attempt while `reconnecting`, else `null`. */
  retryAt: number | null;
  user: RealtimeUser;
  /** The live connection's id from `hello`, else `null`. */
  cid: string | null;
  lastClose: CloseInfo | null;
}

/**
 * - `pending`: wanted, `sub` not yet confirmed (or the socket is down).
 * - `live`: `sub_ok` received on the current socket.
 * - `refused`: `sub_err`; not retried until the auth state changes.
 * - `leaving`: no subscriber left; unsubscribes when the grace delay ends.
 */
export type TopicStatus = 'pending' | 'live' | 'refused' | 'leaving';

export interface TopicState {
  status: TopicStatus;
  /** Last offset seen (a `msg`, or the head from `sub_ok`); the next `since`. */
  offset: Offset | null;
  subscribers: number;
  refusal: SubErrorCode | null;
  received: number;
  gaps: number;
}

export interface FrameRecord {
  id: number;
  at: number;
  direction: 'in' | 'out';
  op: string;
  topic: string | null;
  /** The frame as text, truncated, with any token redacted. */
  text: string;
}

export interface RealtimeSnapshot {
  connection: ConnectionState;
  topics: Readonly<Record<string, TopicState>>;
  frames: readonly FrameRecord[];
}

export const IDLE_CONNECTION: ConnectionState = {
  phase: 'idle',
  attempt: 0,
  retryAt: null,
  user: null,
  cid: null,
  lastClose: null,
};

/** Also the server snapshot: SSR renders as if no socket exists. */
export const IDLE_SNAPSHOT: RealtimeSnapshot = {
  connection: IDLE_CONNECTION,
  topics: {},
  frames: [],
};
