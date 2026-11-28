/**
 * Wire protocol v1: the frame shapes and close codes.
 *
 * The contract is owned by django-cfg's `django_realtime/protocol.py`; this file
 * mirrors it for the browser and nothing else may restate it. A field added
 * there is added here in the same change.
 */

export const PROTOCOL_VERSION = 1;

/** Opaque per-topic position (`"<epoch>:<seq>"` on the wire). The client compares offsets for equality only. */
export type Offset = string;

/** A user id as the server states it in `hello`, or `null` for anonymous. */
export type RealtimeUser = string | number | null;

export type SubErrorCode = 'forbidden' | 'unknown_topic' | 'invalid' | 'limit' | 'timeout';

export type ClientFrame =
  | { op: 'auth'; token?: string }
  | { op: 'sub'; id: number; topic: string; since?: Offset }
  | { op: 'unsub'; topic: string }
  | { op: 'ping' };

export interface HelloFrame {
  op: 'hello';
  v: number;
  user: RealtimeUser;
  /** Seconds between the client's keepalive pings. */
  ping: number;
  /** This connection's id; sent back as `X-Realtime-Cid` so a mutation's echo can be told apart. */
  cid: string;
}

export interface SubOkFrame {
  op: 'sub_ok';
  id: number;
  topic: string;
  /** Current head; `null` is tolerated for a topic that has no history yet. */
  offset: Offset | null;
  /** Present only when the `sub` carried `since`. */
  recovered?: boolean;
}

export interface SubErrFrame {
  op: 'sub_err';
  id: number;
  topic: string;
  code: SubErrorCode;
}

export interface MsgFrame {
  op: 'msg';
  topic: string;
  offset: Offset;
  data: unknown;
  /** The connection whose request caused this publication, when it sent `X-Realtime-Cid`. */
  origin_cid?: string;
}

export interface ErrorFrame {
  op: 'error';
  code: string;
  detail?: string;
}

export type ServerFrame =
  | HelloFrame
  | SubOkFrame
  | SubErrFrame
  | MsgFrame
  | ErrorFrame
  | { op: 'pong' };

export const CloseCode = {
  authFailed: 4401,
  originRefused: 4403,
  authTimeout: 4408,
  /** The presented credential was refused, or revoked: refresh the token, then reconnect at once. */
  credentialsExpired: 4419,
  /** Connection limit, or an inbound frame flood: retry with a long backoff (other tabs may hold the slots). */
  connectionLimit: 4429,
  serverError: 4500,
  keepaliveTimeout: 1011,
  serviceRestart: 1012,
  /** The server shed a client that fell behind; reconnect and replay. */
  slowConsumer: 1013,
} as const;

/** Retrying these cannot succeed until the auth state changes or the page reloads. */
const TERMINAL_CLOSE_CODES: ReadonlySet<number> = new Set([CloseCode.authFailed, CloseCode.originRefused]);

export function isTerminalClose(code: number): boolean {
  return TERMINAL_CLOSE_CODES.has(code);
}

const TOPIC_PATTERN = /^[a-z0-9_.-]+(:[A-Za-z0-9_.-]+)*$/;

export function isTopicName(value: string): boolean {
  return TOPIC_PATTERN.test(value);
}
