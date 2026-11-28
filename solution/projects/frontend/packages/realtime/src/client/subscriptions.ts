import { isReportedRefusal } from './issues';
import { backoffDelay } from './socket/backoff';

import type { ClientFrame, Offset, ServerFrame, SubErrorCode } from '../protocol';
import type { RealtimeStore, TopicStatus } from '../store';
import type { IssueSink } from './issues';
import type { BackoffPolicy } from './socket/backoff';
import type { Clock, TimerHandle } from './socket/environment';

export interface EventMeta {
  topic: string;
  offset: Offset;
  /** The connection whose request caused this publication, when it said so. */
  originCid: string | null;
}

export interface TopicHandler {
  onEvent(data: unknown, meta: EventMeta): void;
  /** History no longer reaches our last offset (trimmed, or a new epoch): refetch the topic's data. */
  onGap?(topic: string): void;
  /** The server refused the subscription (`sub_err`). Not retried until the auth state changes; `timeout` is retried. */
  onRefused?(code: SubErrorCode, topic: string): void;
  /**
   * This handler's subscription is live from the head, without a replay: an
   * event published between the caller's own read and now was not delivered.
   * Called once per handler. A cache that refetches on change refetches here.
   */
  onLive?(topic: string): void;
}

export interface SubscriptionsOptions {
  store: RealtimeStore;
  clock: Clock;
  send(frame: ClientFrame): boolean;
  leaveDelayMs: number;
  random: () => number;
  backoff: BackoffPolicy;
  /** A gap's refetch waits a random 0..this, so a reconnect wave does not hit the API at once. */
  gapJitterMs: number;
  onEmpty(): void;
  onHandlerError(error: unknown, topic: string): void;
  report: IssueSink;
}

/** Where the subscription stands on the current socket. */
type Wire = 'none' | 'sent' | 'confirmed';

interface Entry {
  topic: string;
  handlers: Set<TopicHandler>;
  offset: Offset | null;
  wire: Wire;
  subId: number | null;
  /** The pending `sub` carried `since`. */
  sentSince: boolean;
  refusal: SubErrorCode | null;
  leaveTimer: TimerHandle | null;
  retryTimer: TimerHandle | null;
  gapTimer: TimerHandle | null;
  /** `sub_err: timeout` answers in a row, for the retry backoff. */
  timeouts: number;
  /** Handlers already told `onLive`, or that joined a replay and need not be. */
  settled: WeakSet<TopicHandler>;
  /**
   * A `sub_ok recovered:false` set the offset to the head; the `msg` that
   * revealed the new epoch may follow with that same offset and must be delivered.
   */
  acceptHead: boolean;
  received: number;
  gaps: number;
}

function statusOf(entry: Entry): TopicStatus {
  if (entry.refusal !== null) return 'refused';
  if (entry.handlers.size === 0) return 'leaving';
  return entry.wire === 'confirmed' ? 'live' : 'pending';
}

/**
 * Reference-counted topics over one connection. Keeps each topic's last
 * offset so a reconnect resubscribes with `since`, and delays the unsubscribe
 * so a StrictMode remount or a route change does not cost a round trip.
 *
 * Writes the `topics` slice of the store.
 */
export class Subscriptions {
  private readonly entries = new Map<string, Entry>();
  private nextId = 1;

  constructor(private readonly o: SubscriptionsOptions) {}

  get size(): number {
    return this.entries.size;
  }

  add(topic: string, handler: TopicHandler): () => void {
    let entry = this.entries.get(topic);
    if (entry === undefined) {
      entry = {
        topic,
        handlers: new Set(),
        offset: null,
        wire: 'none',
        subId: null,
        sentSince: false,
        refusal: null,
        leaveTimer: null,
        retryTimer: null,
        gapTimer: null,
        timeouts: 0,
        settled: new WeakSet(),
        acceptHead: false,
        received: 0,
        gaps: 0,
      };
      this.entries.set(topic, entry);
    }
    if (entry.leaveTimer !== null) {
      this.o.clock.clearTimeout(entry.leaveTimer);
      entry.leaveTimer = null;
    }
    entry.handlers.add(handler);
    if (entry.wire === 'none' && entry.refusal === null) this.sendSub(entry, entry.offset);
    this.publish(entry);
    // Joining a topic that is already live: this handler missed everything before now.
    if (entry.wire === 'confirmed') this.settle(entry, handler, true);

    const owned = entry;
    let removed = false;
    return () => {
      if (removed) return;
      removed = true;
      owned.handlers.delete(handler);
      if (owned.handlers.size > 0) {
        this.publish(owned);
        return;
      }
      owned.leaveTimer = this.o.clock.setTimeout(() => this.leave(owned), this.o.leaveDelayMs);
      this.publish(owned);
    };
  }

  /**
   * A new socket said `hello`: resubscribe with each topic's offset. A reconnect
   * that lands on another server process is not a gap; only `recovered:false` is.
   */
  connected(): void {
    for (const entry of this.entries.values()) {
      entry.wire = 'none';
      this.clearRetry(entry);
      if (entry.handlers.size === 0 || entry.refusal !== null) continue;
      this.sendSub(entry, entry.offset);
      this.publish(entry);
    }
  }

  disconnected(): void {
    for (const entry of this.entries.values()) {
      this.clearRetry(entry);
      if (entry.wire === 'none') continue;
      entry.wire = 'none';
      this.publish(entry);
    }
  }

  /** The auth state changed: what was forbidden may be allowed now. */
  forgiveRefusals(): void {
    for (const entry of this.entries.values()) {
      if (entry.refusal === null) continue;
      entry.refusal = null;
      this.publish(entry);
    }
  }

  handle(frame: ServerFrame): void {
    switch (frame.op) {
      case 'sub_ok': {
        const entry = this.entries.get(frame.topic);
        if (entry === undefined || entry.subId !== frame.id) return;
        entry.wire = 'confirmed';
        entry.timeouts = 0;
        // With a recovered `since` the replay that follows advances the offset; otherwise start at the head.
        if (!(entry.sentSince && frame.recovered === true) && frame.offset !== null) entry.offset = frame.offset;
        const gap = frame.recovered === false;
        if (gap) {
          entry.gaps += 1;
          entry.acceptHead = true;
        }
        this.publish(entry);
        for (const handler of [...entry.handlers]) this.settle(entry, handler, !entry.sentSince);
        if (gap) this.scheduleGap(entry);
        return;
      }
      case 'sub_err': {
        const entry = this.entries.get(frame.topic);
        if (entry === undefined || entry.subId !== frame.id) return;
        entry.wire = 'none';
        if (frame.code === 'timeout') {
          this.scheduleRetry(entry);
          this.publish(entry);
          return;
        }
        entry.refusal = frame.code;
        if (isReportedRefusal(frame.code)) this.o.report({ kind: 'refused', topic: entry.topic, code: frame.code });
        this.publish(entry);
        this.dispatch(entry, (h) => h.onRefused?.(frame.code, entry.topic));
        return;
      }
      case 'msg': {
        const entry = this.entries.get(frame.topic);
        if (entry === undefined || entry.refusal !== null) return;
        if (frame.offset === entry.offset && !entry.acceptHead) return;
        entry.acceptHead = false;
        entry.offset = frame.offset;
        entry.received += 1;
        this.publish(entry);
        const meta: EventMeta = { topic: frame.topic, offset: frame.offset, originCid: frame.origin_cid ?? null };
        this.dispatch(entry, (h) => h.onEvent(frame.data, meta));
        return;
      }
      default:
        return;
    }
  }

  clear(): void {
    for (const entry of this.entries.values()) {
      if (entry.leaveTimer !== null) this.o.clock.clearTimeout(entry.leaveTimer);
      if (entry.gapTimer !== null) this.o.clock.clearTimeout(entry.gapTimer);
      this.clearRetry(entry);
      this.o.store.setTopic(entry.topic, null);
    }
    this.entries.clear();
  }

  private sendSub(entry: Entry, since: Offset | null): void {
    const id = this.nextId;
    const frame: ClientFrame = since === null ? { op: 'sub', id, topic: entry.topic } : { op: 'sub', id, topic: entry.topic, since };
    if (!this.o.send(frame)) return;
    this.nextId += 1;
    entry.subId = id;
    entry.sentSince = since !== null;
    entry.wire = 'sent';
  }

  /** Mark a handler as caught up; `notify` tells it its subscription started without a replay. */
  private settle(entry: Entry, handler: TopicHandler, notify: boolean): void {
    if (entry.settled.has(handler)) return;
    entry.settled.add(handler);
    if (!notify || handler.onLive === undefined) return;
    try {
      handler.onLive(entry.topic);
    } catch (error) {
      this.o.onHandlerError(error, entry.topic);
    }
  }

  private scheduleRetry(entry: Entry): void {
    this.clearRetry(entry);
    entry.timeouts += 1;
    const delay = backoffDelay(entry.timeouts, this.o.random, this.o.backoff);
    entry.retryTimer = this.o.clock.setTimeout(() => {
      entry.retryTimer = null;
      if (this.entries.get(entry.topic) !== entry || entry.handlers.size === 0) return;
      if (entry.wire === 'none' && entry.refusal === null) this.sendSub(entry, entry.offset);
      this.publish(entry);
    }, delay);
  }

  private clearRetry(entry: Entry): void {
    if (entry.retryTimer !== null) this.o.clock.clearTimeout(entry.retryTimer);
    entry.retryTimer = null;
  }

  /** One refetch per gap, jittered; a second gap before it runs folds into the same refetch. */
  private scheduleGap(entry: Entry): void {
    if (entry.gapTimer !== null) return;
    entry.gapTimer = this.o.clock.setTimeout(() => {
      entry.gapTimer = null;
      if (this.entries.get(entry.topic) !== entry) return;
      this.dispatch(entry, (h) => h.onGap?.(entry.topic));
    }, this.o.random() * this.o.gapJitterMs);
  }

  private leave(entry: Entry): void {
    entry.leaveTimer = null;
    if (entry.handlers.size > 0 || this.entries.get(entry.topic) !== entry) return;
    this.clearRetry(entry);
    if (entry.gapTimer !== null) this.o.clock.clearTimeout(entry.gapTimer);
    entry.gapTimer = null;
    if (entry.wire !== 'none') this.o.send({ op: 'unsub', topic: entry.topic });
    this.entries.delete(entry.topic);
    this.o.store.setTopic(entry.topic, null);
    if (this.entries.size === 0) this.o.onEmpty();
  }

  /** Handlers are copied first: one unsubscribing another mid-dispatch must not skip it. */
  private dispatch(entry: Entry, call: (handler: TopicHandler) => void): void {
    for (const handler of [...entry.handlers]) {
      try {
        call(handler);
      } catch (error) {
        this.o.onHandlerError(error, entry.topic);
      }
    }
  }

  private publish(entry: Entry): void {
    this.o.store.setTopic(entry.topic, {
      status: statusOf(entry),
      offset: entry.offset,
      subscribers: entry.handlers.size,
      refusal: entry.refusal,
      received: entry.received,
      gaps: entry.gaps,
    });
  }
}
