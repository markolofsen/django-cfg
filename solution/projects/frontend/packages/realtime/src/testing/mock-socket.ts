import type { SocketLike } from '../client';

export const SOCKET_CONNECTING = 0;
export const SOCKET_OPEN = 1;
export const SOCKET_CLOSED = 3;

export interface MockSocketPeer {
  /** The client opened a socket; the peer answers `open` or a close code. */
  accept(socket: MockSocket): void;
  receive(socket: MockSocket, text: string): void;
  /** The client closed; the peer forgets the socket. */
  release(socket: MockSocket): void;
}

/**
 * A browser-shaped socket wired to an in-memory peer. Events are delivered in
 * a microtask, as a real socket delivers them after the current task.
 */
export class MockSocket implements SocketLike {
  readyState = SOCKET_CONNECTING;
  onopen: ((ev: { type: 'open' }) => void) | null = null;
  onmessage: ((ev: { data: string }) => void) | null = null;
  onclose: ((ev: { code: number; reason: string }) => void) | null = null;
  onerror: ((ev: { type: 'error' }) => void) | null = null;

  constructor(
    readonly url: string,
    private readonly peer: MockSocketPeer,
  ) {
    queueMicrotask(() => {
      if (this.readyState === SOCKET_CONNECTING) this.peer.accept(this);
    });
  }

  send(text: string): void {
    if (this.readyState !== SOCKET_OPEN) throw new Error('MockSocket.send on a socket that is not open');
    this.peer.receive(this, text);
  }

  close(code = 1005, reason = ''): void {
    if (this.readyState === SOCKET_CLOSED) return;
    this.readyState = SOCKET_CLOSED;
    this.peer.release(this);
    queueMicrotask(() => this.onclose?.({ code, reason }));
  }

  /** Peer side: complete the handshake. */
  serverOpen(): void {
    if (this.readyState !== SOCKET_CONNECTING) return;
    this.readyState = SOCKET_OPEN;
    this.onopen?.({ type: 'open' });
  }

  /** Peer side: deliver a frame. */
  serverSend(text: string): void {
    if (this.readyState !== SOCKET_OPEN) return;
    queueMicrotask(() => {
      if (this.readyState === SOCKET_OPEN) this.onmessage?.({ data: text });
    });
  }

  /** Peer side: close with a code (a refused handshake closes a socket that never opened). */
  serverClose(code: number, reason = ''): void {
    if (this.readyState === SOCKET_CLOSED) return;
    this.readyState = SOCKET_CLOSED;
    queueMicrotask(() => {
      if (code === 1006) this.onerror?.({ type: 'error' });
      this.onclose?.({ code, reason });
    });
  }
}
