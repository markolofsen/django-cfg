import { isTopicName } from '../protocol';
import { createRealtimeStore } from '../store';
import { DEFAULT_BACKOFF } from './socket/backoff';
import { Connection } from './socket/connection';
import { browserWake, globalSocketFactory, systemClock } from './socket/environment';
import { Subscriptions } from './subscriptions';
import { toWireHandler, topicName } from './typed-topic';

import type { RealtimeIssue, ReportedIssue } from './issues';

import type { RealtimeStore } from '../store';
import type { BackoffPolicy } from './socket/backoff';
import type { Clock, SocketFactory, TimerHandle, WakeSource } from './socket/environment';
import type { EventMeta } from './subscriptions';
import type { InvalidEventHandler, TopicRef, TypedTopicHandler } from './typed-topic';

export interface RealtimeClientOptions {
  /** `ws(s)://…/ws`. A function is read at each connect, so it may depend on `location`. */
  url: string | (() => string);
  /** Sent as the first `auth` frame when it returns a token; the cookie goes with the handshake anyway. */
  getToken?: () => string | null;
  /** Defaults to `globalThis.WebSocket`. */
  WebSocket?: SocketFactory;
  clock?: Clock;
  random?: () => number;
  wake?: WakeSource;
  backoff?: BackoffPolicy;
  /** Close the socket this long after the last topic leaves. */
  idleCloseMs?: number;
  /** Keep a topic this long after its last subscriber leaves. */
  unsubscribeDelayMs?: number;
  /** Give up on a socket that has not said `hello` within this time. */
  helloTimeoutMs?: number;
  /** No `pong` within this time after a `ping` means the path is dead. */
  pongTimeoutMs?: number;
  /** On 1012 the first retry waits a random 0..this. */
  restartSpreadMs?: number;
  /** A gap's `onGap` waits a random 0..this. */
  gapJitterMs?: number;
  /**
   * On close 4419 (credentials expired or revoked): refresh the token over HTTP
   * and resolve whether a session is left. Without it, 4419 stops like 4401.
   */
  refreshCredentials?: () => Promise<boolean>;
  frameLimit?: number;
  /** Check each event against its typed topic's schema (development). Default `false`. */
  validateEvents?: boolean;
  /** An event failed its schema while `validateEvents` is on. Default: report it as an `invalid_event` issue. */
  onInvalidEvent?: InvalidEventHandler;
  /**
   * A real problem: a terminal close, 4500, a run of failed handshakes, a
   * refused topic, a protocol error, an event that failed its schema. Normal
   * reconnects are not reported. Default: `console.warn`.
   */
  onIssue?: (issue: ReportedIssue) => void;
  /** A handler threw. Default: `console.error`. */
  onHandlerError?: (error: unknown, topic: string) => void;
}

export interface RealtimeClient {
  readonly store: RealtimeStore;
  /**
   * Start receiving a topic, by name or as a typed topic from the generated
   * `realtime.ts` (whose event type types `data`). The first subscription opens
   * the socket; the returned function releases this one (idempotent). Throws on
   * a name the protocol cannot carry: a programming error, not a refusal.
   */
  subscribe<E = unknown>(
    topic: TopicRef<E>,
    handler: TypedTopicHandler<E> | ((data: E, meta: EventMeta) => void),
  ): () => void;
  /** Login or logout: retry refused topics, leave `stopped`, reconnect an open socket with the new identity. */
  authChanged(): void;
  /** Credentials may have changed (a refreshed token): retry if `stopped`, otherwise nothing. */
  resume(): void;
  /** Skip the remaining backoff. */
  retryNow(): void;
  /** The live connection's id, for the `X-Realtime-Cid` request header; `null` while not live. */
  getCid(): string | null;
  dispose(): void;
}

export const DEFAULT_IDLE_CLOSE_MS = 30_000;
export const DEFAULT_UNSUBSCRIBE_DELAY_MS = 1_500;
export const DEFAULT_HELLO_TIMEOUT_MS = 10_000;
export const DEFAULT_PONG_TIMEOUT_MS = 10_000;
export const DEFAULT_RESTART_SPREAD_MS = 5_000;
export const DEFAULT_GAP_JITTER_MS = 2_000;

export function createRealtimeClient(options: RealtimeClientOptions): RealtimeClient {
  const clock = options.clock ?? systemClock;
  const store = createRealtimeStore(options.frameLimit);
  const idleCloseMs = options.idleCloseMs ?? DEFAULT_IDLE_CLOSE_MS;
  const url = options.url;
  const resolveUrl = typeof url === 'function' ? url : () => url;
  const onHandlerError =
    options.onHandlerError ??
    ((error: unknown, topic: string) => console.error(`[realtime] handler for ${topic} threw`, error));

  const random = options.random ?? Math.random;
  const backoff = options.backoff ?? DEFAULT_BACKOFF;
  const validateEvents = options.validateEvents ?? false;
  const onIssue = options.onIssue ?? ((issue: ReportedIssue) => console.warn('[realtime]', issue));
  const report = (issue: RealtimeIssue) => {
    try {
      onIssue({ ...issue, cid: store.getSnapshot().connection.cid });
    } catch {
      // Reporting must never break the socket.
    }
  };
  const onInvalidEvent: InvalidEventHandler =
    options.onInvalidEvent ??
    ((topic, error) =>
      report({ kind: 'invalid_event', topic, message: error instanceof Error ? error.message : String(error) }));
  let idleTimer: TimerHandle | null = null;
  let disposed = false;

  const connection: Connection = new Connection({
    url: resolveUrl,
    socketFactory: () => options.WebSocket ?? globalSocketFactory(),
    getToken: options.getToken ?? (() => null),
    clock,
    random,
    wake: options.wake ?? browserWake,
    store,
    helloTimeoutMs: options.helloTimeoutMs ?? DEFAULT_HELLO_TIMEOUT_MS,
    pongTimeoutMs: options.pongTimeoutMs ?? DEFAULT_PONG_TIMEOUT_MS,
    restartSpreadMs: options.restartSpreadMs ?? DEFAULT_RESTART_SPREAD_MS,
    backoff,
    refreshCredentials: options.refreshCredentials ?? null,
    report,
    onLive: () => subscriptions.connected(),
    onFrame: (frame) => subscriptions.handle(frame),
    onDown: () => subscriptions.disconnected(),
  });

  const subscriptions: Subscriptions = new Subscriptions({
    store,
    clock,
    send: (frame) => connection.send(frame),
    leaveDelayMs: options.unsubscribeDelayMs ?? DEFAULT_UNSUBSCRIBE_DELAY_MS,
    random,
    backoff,
    gapJitterMs: options.gapJitterMs ?? DEFAULT_GAP_JITTER_MS,
    onHandlerError,
    report,
    onEmpty() {
      if (idleTimer !== null) clock.clearTimeout(idleTimer);
      idleTimer = clock.setTimeout(() => {
        idleTimer = null;
        if (subscriptions.size === 0) connection.close();
      }, idleCloseMs);
    },
  });

  return {
    store,
    subscribe(topic, handler) {
      if (disposed) throw new Error('[realtime] subscribe() on a disposed client');
      const name = topicName(topic);
      if (!isTopicName(name)) throw new Error(`[realtime] invalid topic name ${JSON.stringify(name)}`);
      const typed = typeof handler === 'function' ? { onEvent: handler } : handler;
      const wire = toWireHandler(topic, typed, validateEvents, onInvalidEvent);
      if (idleTimer !== null) {
        clock.clearTimeout(idleTimer);
        idleTimer = null;
      }
      const release = subscriptions.add(name, wire);
      connection.open();
      return release;
    },
    authChanged() {
      if (disposed) return;
      subscriptions.forgiveRefusals();
      connection.restart();
    },
    resume() {
      if (disposed || store.getSnapshot().connection.phase !== 'stopped') return;
      subscriptions.forgiveRefusals();
      connection.resume();
    },
    retryNow() {
      connection.wakeUp();
    },
    getCid: () => store.getSnapshot().connection.cid,
    dispose() {
      if (disposed) return;
      disposed = true;
      if (idleTimer !== null) clock.clearTimeout(idleTimer);
      subscriptions.clear();
      connection.close();
    },
  };
}
