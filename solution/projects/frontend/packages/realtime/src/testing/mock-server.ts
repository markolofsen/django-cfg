import { CloseCode, PROTOCOL_VERSION, isTopicName } from '../protocol';
import { MockSocket } from './mock-socket';

import type { SocketFactory } from '../client';
import type { Offset, RealtimeUser, ServerFrame, SubErrorCode } from '../protocol';
import type { MockSocketPeer } from './mock-socket';

export interface MockServerOptions {
  /** Client keepalive interval announced in `hello`, seconds. Default 25. */
  ping?: number;
  /** Messages kept per topic; older ones are trimmed. Default 100. */
  history?: number;
  /** Resolve an `auth` token to a user; `undefined` refuses it with 4401. Default: the token is the user id. */
  authenticate?: (token: string) => RealtimeUser | undefined;
  /** The user a socket gets from its cookie when it sends no `auth`. Default `null` (anonymous). */
  cookieUser?: RealtimeUser;
  /** Close anonymous sockets with 4401. */
  requireUser?: boolean;
  /** Refuse a subscription with a `sub_err` code, or allow it with `null`. */
  authorize?: (topic: string, user: RealtimeUser) => SubErrorCode | null;
}

export interface ReceivedFrame {
  connection: number;
  frame: Record<string, unknown>;
}

export interface MockServer {
  /** Pass to `createRealtimeClient({ WebSocket })`. */
  readonly WebSocket: SocketFactory;
  readonly url: string;
  /** Open sockets that said `hello`. */
  readonly connections: number;
  /** The `cid` of each open socket, oldest first. */
  readonly cids: readonly string[];
  /** Every frame clients sent, in order. */
  readonly received: readonly ReceivedFrame[];
  /** With `originCid`, the message carries `origin_cid` and that connection does not receive it. */
  publish(topic: string, data: unknown, options?: { originCid?: string }): Offset;
  head(topic: string): Offset;
  /** Keep only the last `keep` messages of a topic, so an older `since` is not recovered. */
  trim(topic: string, keep: number): void;
  /**
   * History lost (a Redis flush): the topic starts a new epoch, so every older
   * `since` is not recovered, and every live subscriber gets a repeated
   * `sub_ok{recovered:false}` with the new head, as the server sends it.
   */
  bumpEpoch(topic: string): void;
  subscribers(topic: string): number;
  /** Every socket closed with 1012. History survives unless `loseHistory` (then every topic gets a new epoch). */
  restart(options?: { loseHistory?: boolean }): void;
  /** The network went away: every socket closes with 1006. */
  drop(): void;
  closeAll(code: number, reason?: string): void;
  /** Send a raw text frame to every open socket (malformed frames, hand-made `sub_ok`s). */
  sendRaw(text: string): void;
  /** Refuse new handshakes with this close code, or accept them again with `null`. */
  refuse(code: number | null): void;
  /** Stop answering `ping`, to simulate a half-dead link. */
  answerPings(on: boolean): void;
  setCookieUser(user: RealtimeUser): void;
  /** Notified after anything above changes (for stories). */
  subscribe(listener: () => void): () => void;
}

interface TopicLog {
  epoch: number;
  seq: number;
  entries: { seq: number; offset: Offset; data: unknown }[];
}

interface Peer {
  id: number;
  cid: string;
  socket: MockSocket;
  user: RealtimeUser;
  helloSent: boolean;
  /** Topic → the `sub` id that subscribed it, which a repeated `sub_ok` carries. */
  topics: Map<string, number>;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

/**
 * Protocol v1 in memory, for unit tests and stories: `"<epoch>:<seq>"`
 * offsets, history with trimming and epoch changes (`recovered:false`),
 * `origin_cid` with sender skip, close codes, `ping`/`pong`.
 * Not a reference for the server; django-cfg's own tests own that.
 */
export function createMockServer(options: MockServerOptions = {}): MockServer {
  const historyLimit = options.history ?? 100;
  const authenticate = options.authenticate ?? ((token: string) => token);
  const authorize = options.authorize ?? (() => null);
  let nextEpoch = 1;
  let cookieUser: RealtimeUser = options.cookieUser ?? null;
  let refuseCode: number | null = null;
  let pongs = true;
  let nextPeerId = 1;

  const logs = new Map<string, TopicLog>();
  const peers = new Map<MockSocket, Peer>();
  const received: ReceivedFrame[] = [];
  const listeners = new Set<() => void>();

  const changed = () => {
    for (const listener of [...listeners]) listener();
  };
  const logOf = (topic: string): TopicLog => {
    let log = logs.get(topic);
    if (log === undefined) {
      log = { epoch: nextEpoch++, seq: 0, entries: [] };
      logs.set(topic, log);
    }
    return log;
  };
  const headOf = (log: TopicLog): Offset => `${log.epoch}:${log.seq}`;
  const send = (peer: Peer, frame: ServerFrame) => peer.socket.serverSend(JSON.stringify(frame));

  function sendHello(peer: Peer): void {
    peer.helloSent = true;
    send(peer, { op: 'hello', v: PROTOCOL_VERSION, user: peer.user, ping: options.ping ?? 25, cid: peer.cid });
    changed();
  }

  /** Recovered when `since` is of this epoch and no older than the message before the first one kept. */
  function replay(log: TopicLog, since: Offset): { recovered: boolean; items: TopicLog['entries'] } {
    const [epoch, seqText] = since.split(':');
    const seq = Number(seqText);
    if (Number(epoch) !== log.epoch || !Number.isInteger(seq) || seq > log.seq) return { recovered: false, items: [] };
    const firstKept = log.entries[0]?.seq ?? log.seq + 1;
    if (seq < firstKept - 1) return { recovered: false, items: [] };
    return { recovered: true, items: log.entries.filter((e) => e.seq > seq) };
  }

  function onSub(peer: Peer, f: Record<string, unknown>): void {
    const id = typeof f.id === 'number' ? f.id : -1;
    const topic = typeof f.topic === 'string' ? f.topic : '';
    if (!isTopicName(topic)) {
      send(peer, { op: 'sub_err', id, topic, code: 'invalid' });
      return;
    }
    const refusal = authorize(topic, peer.user);
    if (refusal !== null) {
      send(peer, { op: 'sub_err', id, topic, code: refusal });
      return;
    }
    peer.topics.set(topic, id);
    const log = logOf(topic);
    if (typeof f.since !== 'string') {
      send(peer, { op: 'sub_ok', id, topic, offset: headOf(log) });
    } else {
      const { recovered, items } = replay(log, f.since);
      send(peer, { op: 'sub_ok', id, topic, offset: headOf(log), recovered });
      for (const item of items) send(peer, { op: 'msg', topic, offset: item.offset, data: item.data });
    }
    changed();
  }

  const peerApi: MockSocketPeer = {
    accept(socket) {
      if (refuseCode !== null) {
        socket.serverClose(refuseCode, 'refused by mock server');
        return;
      }
      const id = nextPeerId++;
      const peer: Peer = { id, cid: `c${id}`, socket, user: null, helloSent: false, topics: new Map() };
      peers.set(socket, peer);
      // The client sends `auth` from its open handler, synchronously, so it is handled before this returns.
      socket.serverOpen();
      if (peer.helloSent || !peers.has(socket)) return;
      peer.user = cookieUser;
      if (options.requireUser && peer.user === null) {
        peers.delete(socket);
        socket.serverClose(CloseCode.authFailed, 'authentication required');
        return;
      }
      sendHello(peer);
    },
    receive(socket, text) {
      const peer = peers.get(socket);
      if (peer === undefined) return;
      let raw: unknown;
      try {
        raw = JSON.parse(text);
      } catch {
        send(peer, { op: 'error', code: 'bad_json' });
        return;
      }
      if (!isRecord(raw)) {
        send(peer, { op: 'error', code: 'bad_frame' });
        return;
      }
      received.push({ connection: peer.id, frame: raw });
      switch (raw.op) {
        case 'auth': {
          if (peer.helloSent) {
            send(peer, { op: 'error', code: 'unexpected_auth' });
            return;
          }
          // No token: settle on the cookie user, as the server does.
          if (typeof raw.token !== 'string') return;
          const user = authenticate(raw.token);
          if (user === undefined) {
            peers.delete(socket);
            socket.serverClose(CloseCode.authFailed, 'bad token');
            return;
          }
          peer.user = user;
          sendHello(peer);
          return;
        }
        case 'sub':
          onSub(peer, raw);
          return;
        case 'unsub':
          if (typeof raw.topic === 'string') peer.topics.delete(raw.topic);
          changed();
          return;
        case 'ping':
          if (pongs) send(peer, { op: 'pong' });
          return;
        default:
          send(peer, { op: 'error', code: 'unknown_op', detail: String(raw.op) });
      }
    },
    release(socket) {
      if (peers.delete(socket)) changed();
    },
  };

  class BoundSocket extends MockSocket {
    constructor(url: string) {
      super(url, peerApi);
    }
  }

  function closeAll(code: number, reason = ''): void {
    for (const [socket] of [...peers]) socket.serverClose(code, reason);
    peers.clear();
    changed();
  }

  return {
    WebSocket: BoundSocket,
    url: 'ws://mock.realtime/ws',
    get connections() {
      return [...peers.values()].filter((p) => p.helloSent).length;
    },
    get cids() {
      return [...peers.values()].filter((p) => p.helloSent).map((p) => p.cid);
    },
    received,
    publish(topic, data, publishOptions = {}) {
      const log = logOf(topic);
      log.seq += 1;
      const offset = `${log.epoch}:${log.seq}`;
      log.entries.push({ seq: log.seq, offset, data });
      if (log.entries.length > historyLimit) log.entries.splice(0, log.entries.length - historyLimit);
      const originCid = publishOptions.originCid;
      for (const peer of peers.values()) {
        if (!peer.topics.has(topic) || peer.cid === originCid) continue;
        send(peer, originCid === undefined ? { op: 'msg', topic, offset, data } : { op: 'msg', topic, offset, data, origin_cid: originCid });
      }
      changed();
      return offset;
    },
    head: (topic) => headOf(logOf(topic)),
    trim(topic, keep) {
      const log = logOf(topic);
      if (log.entries.length <= keep) return;
      log.entries.splice(0, log.entries.length - keep);
      changed();
    },
    bumpEpoch(topic) {
      const log = logOf(topic);
      log.epoch = nextEpoch++;
      log.seq = 0;
      log.entries = [];
      for (const peer of peers.values()) {
        const id = peer.topics.get(topic);
        if (id !== undefined) send(peer, { op: 'sub_ok', id, topic, offset: headOf(log), recovered: false });
      }
      changed();
    },
    subscribers: (topic) => [...peers.values()].filter((p) => p.topics.has(topic)).length,
    restart(restartOptions = {}) {
      if (restartOptions.loseHistory) logs.clear();
      closeAll(CloseCode.serviceRestart, 'server restart');
    },
    drop: () => closeAll(1006),
    sendRaw(text) {
      for (const peer of peers.values()) peer.socket.serverSend(text);
    },
    closeAll,
    refuse(code) {
      refuseCode = code;
    },
    answerPings(on) {
      pongs = on;
    },
    setCookieUser(user) {
      cookieUser = user;
    },
    subscribe(listener) {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },
  };
}
