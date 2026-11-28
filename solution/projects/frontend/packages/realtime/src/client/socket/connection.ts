import { CloseCode, PROTOCOL_VERSION, isTerminalClose, parseFrame } from '../../protocol';
import { UNREACHABLE_AFTER_ATTEMPTS, isReportedClose } from '../issues';
import { backoffDelay } from './backoff';

import type { ClientFrame, HelloFrame, ServerFrame } from '../../protocol';
import type { CloseInfo, ConnectionPhase, RealtimeStore } from '../../store';
import type { IssueSink } from '../issues';
import type { BackoffPolicy } from './backoff';
import type { Clock, SocketFactory, SocketLike, TimerHandle, WakeSource } from './environment';

export interface ConnectionOptions {
  url: () => string;
  socketFactory: () => SocketFactory | null;
  getToken: () => string | null;
  clock: Clock;
  random: () => number;
  wake: WakeSource;
  store: RealtimeStore;
  helloTimeoutMs: number;
  /** No `pong` within this time after a `ping`: the path is dead. */
  pongTimeoutMs: number;
  /** After 1011, 1012 or 1013 the first retry waits a random 0..this, so tabs do not return in one burst. */
  restartSpreadMs: number;
  backoff: BackoffPolicy;
  /** On 4419: refresh the credential over HTTP; resolves whether a session is left. */
  refreshCredentials: (() => Promise<boolean>) | null;
  report: IssueSink;
  onLive(hello: HelloFrame): void;
  onFrame(frame: ServerFrame): void;
  onDown(): void;
}

const FRAME_TEXT_LIMIT = 300;
/** Server-wide drops (keepalive, restart, slow-consumer shedding): spread the first retry so tabs do not return at once. */
const SPREAD_CLOSE_CODES: ReadonlySet<number> = new Set([
  CloseCode.keepaliveTimeout,
  CloseCode.serviceRestart,
  CloseCode.slowConsumer,
]);
/** 4429 means other tabs may hold this user's slots: retry slowly. */
const LIMIT_FLOOR_MS = 30_000;
/** The attempt counter resets only after this much time live, so a server closing right after `hello` is not retried at 2 Hz. */
const STABLE_AFTER_MS = 10_000;
/** Our own close code for a socket we abandon; the server never sees it on a dead link. */
const CLIENT_CLOSE = 1000;

type TimerName = 'retryTimer' | 'helloTimer' | 'pingTimer' | 'pongTimer' | 'stableTimer';

function frameTopic(frame: ClientFrame | ServerFrame): string | null {
  return 'topic' in frame ? frame.topic : null;
}

function readCode(ev: { code?: unknown; reason?: unknown }): CloseInfo {
  return {
    code: typeof ev.code === 'number' ? ev.code : 1006,
    reason: typeof ev.reason === 'string' ? ev.reason : '',
  };
}

/**
 * One socket's lifecycle: connect, `auth`, `hello`, keepalive, the close-code
 * policy and the backoff. Knows nothing about topics; it hands `hello` and the
 * frames after it to its owner.
 *
 * Writes the `connection` slice and the frame log of the store.
 */
export class Connection {
  private socket: SocketLike | null = null;
  private wanted = false;
  private stopped = false;
  private live = false;
  /** Failures since the connection was last stable; drives the backoff. */
  private attempt = 0;
  /** Attempts in a row that ended without `hello`; drives the "unreachable" issue. */
  private failedHandshakes = 0;
  /** Bumped by every reset, so a credential refresh that resolves late cannot revive an old attempt. */
  private generation = 0;
  private retryTimer: TimerHandle | null = null;
  private helloTimer: TimerHandle | null = null;
  private pingTimer: TimerHandle | null = null;
  private pongTimer: TimerHandle | null = null;
  private stableTimer: TimerHandle | null = null;
  private detachWake: (() => void) | null = null;

  constructor(private readonly o: ConnectionOptions) {}

  /** A socket is wanted: connect unless already connected or stopped. */
  open(): void {
    if (this.wanted) return;
    this.wanted = true;
    this.detachWake = this.o.wake(() => this.wakeUp());
    if (!this.stopped) this.connect();
  }

  /** No socket is wanted: close it and cancel any retry. A `stopped` state survives. */
  close(): void {
    if (!this.wanted) return;
    this.wanted = false;
    this.detachWake?.();
    this.detachWake = null;
    this.attempt = 0;
    this.failedHandshakes = 0;
    this.reset(this.stopped ? 'stopped' : 'idle');
  }

  /** The identity changed: leave `stopped` and, if a socket is wanted, open a fresh one now. */
  restart(): void {
    this.stopped = false;
    this.attempt = 0;
    this.failedHandshakes = 0;
    this.reset('idle');
    if (this.wanted) this.connect();
  }

  /** Retry a `stopped` connection, e.g. after a token refresh. No-op otherwise. */
  resume(): void {
    if (this.stopped) this.restart();
  }

  /** Skip the remaining backoff (network back, page visible, a manual retry). */
  wakeUp(): void {
    if (!this.wanted || this.retryTimer === null) return;
    this.connect();
  }

  send(frame: ClientFrame): boolean {
    if (!this.live || this.socket === null) return false;
    this.transmit(this.socket, frame);
    return true;
  }

  private transmit(socket: SocketLike, frame: ClientFrame): void {
    const text = JSON.stringify(frame);
    socket.send(text);
    if (!this.o.store.recordingFrames) return;
    const shown = frame.op === 'auth' && frame.token ? JSON.stringify({ op: 'auth', token: '[redacted]' }) : text;
    this.record('out', frame.op, frameTopic(frame), shown);
  }

  private record(direction: 'in' | 'out', op: string, topic: string | null, text: string): void {
    if (!this.o.store.recordingFrames) return;
    this.o.store.recordFrame({
      at: this.o.clock.now(),
      direction,
      op,
      topic,
      text: text.length > FRAME_TEXT_LIMIT ? `${text.slice(0, FRAME_TEXT_LIMIT)}…` : text,
    });
  }

  private connect(): void {
    this.clearTimer('retryTimer');
    const Factory = this.o.socketFactory();
    if (Factory === null) {
      this.stop({ code: 0, reason: 'no WebSocket in this environment' });
      return;
    }
    let url: string;
    try {
      url = this.o.url();
      new URL(url);
    } catch (error) {
      // A misconfigured URL is not a transport failure: retrying cannot fix it.
      this.stop({ code: 0, reason: `bad realtime URL: ${error instanceof Error ? error.message : String(error)}` });
      return;
    }
    this.o.store.setConnection({ phase: this.attempt === 0 ? 'connecting' : 'reconnecting', retryAt: null });
    let socket: SocketLike;
    try {
      socket = new Factory(url);
    } catch (error) {
      this.handleDown({ code: 1006, reason: error instanceof Error ? error.message : 'connect failed' });
      return;
    }
    this.socket = socket;
    // Covers a handshake that never completes as well as a server that never says hello.
    this.helloTimer = this.o.clock.setTimeout(() => this.abandon('no hello'), this.o.helloTimeoutMs);

    socket.onopen = () => {
      // Always first: without a token it tells the server to settle on the cookie now, not after its auth window.
      const token = this.o.getToken();
      this.transmit(socket, token ? { op: 'auth', token } : { op: 'auth' });
    };
    socket.onmessage = (ev: { data?: unknown }) => {
      if (this.socket === socket) this.receive(ev.data);
    };
    socket.onclose = (ev: { code?: unknown; reason?: unknown }) => {
      if (this.socket === socket) this.handleDown(readCode(ev));
    };
    socket.onerror = () => {
      // A close event follows every error; that is where the policy runs.
    };
  }

  private receive(data: unknown): void {
    if (typeof data !== 'string') {
      this.record('in', '?', null, '[binary frame ignored]');
      return;
    }
    const parsed = parseFrame(data);
    if (!parsed.ok) {
      this.record('in', '?', null, `${parsed.reason}: ${data}`);
      this.o.report({ kind: 'protocol', code: 'unparseable', detail: parsed.reason });
      return;
    }
    const frame = parsed.frame;
    this.record('in', frame.op, frameTopic(frame), data);

    switch (frame.op) {
      case 'hello':
        this.onHello(frame);
        return;
      case 'pong':
        this.clearTimer('pongTimer');
        return;
      case 'error':
        this.o.report({ kind: 'protocol', code: frame.code, detail: frame.detail ?? null });
        return;
      default:
        if (this.live) this.o.onFrame(frame);
    }
  }

  private onHello(hello: HelloFrame): void {
    this.clearTimer('helloTimer');
    if (hello.v !== PROTOCOL_VERSION) {
      this.reset('stopped');
      this.stop({ code: 0, reason: `server speaks protocol v${hello.v}, client v${PROTOCOL_VERSION}` });
      return;
    }
    this.live = true;
    this.failedHandshakes = 0;
    this.stableTimer = this.o.clock.setTimeout(() => {
      this.stableTimer = null;
      this.attempt = 0;
      this.o.store.setConnection({ attempt: 0 });
    }, STABLE_AFTER_MS);
    this.schedulePing(hello.ping * 1000);
    this.o.store.setConnection({ phase: 'live', retryAt: null, user: hello.user, cid: hello.cid });
    this.o.onLive(hello);
  }

  private schedulePing(intervalMs: number): void {
    if (!(intervalMs > 0)) return;
    this.pingTimer = this.o.clock.setTimeout(() => {
      this.pingTimer = null;
      if (this.socket === null || !this.live) return;
      this.transmit(this.socket, { op: 'ping' });
      if (this.pongTimer === null) {
        this.pongTimer = this.o.clock.setTimeout(() => this.abandon('pong timeout'), this.o.pongTimeoutMs);
      }
      this.schedulePing(intervalMs);
    }, intervalMs);
  }

  /** Give up on the current socket without waiting for a close event a dead link may never deliver. */
  private abandon(reason: string): void {
    this.handleDown({ code: 1006, reason });
  }

  private handleDown(close: CloseInfo): void {
    const hadHello = this.live;
    // Before the reset, while the connection id is still known.
    if (isReportedClose(close.code)) this.o.report({ kind: 'closed', code: close.code, reason: close.reason });
    this.reset('reconnecting');
    this.o.store.setConnection({ lastClose: close });

    if (!this.wanted) {
      this.o.store.setConnection({ phase: 'idle', attempt: 0, retryAt: null });
      return;
    }
    if (isTerminalClose(close.code)) {
      this.stop(close, false);
      return;
    }
    if (close.code === CloseCode.credentialsExpired) {
      this.refreshThenConnect(close);
      return;
    }
    if (!hadHello) {
      this.failedHandshakes += 1;
      if (this.failedHandshakes === UNREACHABLE_AFTER_ATTEMPTS) {
        this.o.report({ kind: 'unreachable', attempts: this.failedHandshakes, lastCode: close.code, lastReason: close.reason });
      }
    }
    this.attempt += 1;
    this.scheduleRetry(close.code);
  }

  private scheduleRetry(code: number): void {
    const jitter = backoffDelay(this.attempt, this.o.random, this.o.backoff);
    let delay = jitter;
    if (code === CloseCode.connectionLimit) delay = LIMIT_FLOOR_MS + jitter;
    else if (SPREAD_CLOSE_CODES.has(code) && this.attempt === 1) delay = this.o.random() * this.o.restartSpreadMs;
    this.retryTimer = this.o.clock.setTimeout(() => this.connect(), delay);
    this.o.store.setConnection({
      phase: 'reconnecting',
      attempt: this.attempt,
      retryAt: this.o.clock.now() + delay,
    });
  }

  /** 4419: the credential is stale or refused, not the network. Refresh it and reconnect at once; no session left means stop. */
  private refreshThenConnect(close: CloseInfo): void {
    const refresh = this.o.refreshCredentials;
    if (refresh === null) {
      this.stop(close, false);
      return;
    }
    const generation = this.generation;
    this.o.store.setConnection({ phase: 'reconnecting', retryAt: null });
    const settle = (hasSession: boolean) => {
      if (generation !== this.generation || !this.wanted || this.stopped || this.socket !== null) return;
      if (hasSession) this.connect();
      else this.stop(close, false);
    };
    refresh().then(settle, () => settle(false));
  }

  /** `report` is false where the close was already reported, or is not a problem (4419 with no session left). */
  private stop(close: CloseInfo, report = true): void {
    this.stopped = true;
    this.clearTimer('retryTimer');
    if (report) this.o.report({ kind: 'closed', code: close.code, reason: close.reason });
    this.o.store.setConnection({ phase: 'stopped', retryAt: null, lastClose: close });
  }

  /**
   * The one way a socket ends: detach and close it so its late events cannot
   * reach us, cancel every timer, tell the owner, and publish `phase`.
   */
  private reset(phase: ConnectionPhase): void {
    for (const name of ['retryTimer', 'helloTimer', 'pingTimer', 'pongTimer', 'stableTimer'] as const) this.clearTimer(name);
    this.generation += 1;
    const socket = this.socket;
    this.socket = null;
    this.live = false;
    if (socket !== null) {
      socket.onopen = null;
      socket.onmessage = null;
      socket.onclose = null;
      socket.onerror = null;
      try {
        socket.close(CLIENT_CLOSE);
      } catch {
        // Closing a socket that is already closing throws in some runtimes; it is gone either way.
      }
    }
    this.o.onDown();
    this.o.store.setConnection({ phase, cid: null, retryAt: null });
  }

  private clearTimer(name: TimerName): void {
    const handle = this[name];
    if (handle !== null) this.o.clock.clearTimeout(handle);
    this[name] = null;
  }
}
