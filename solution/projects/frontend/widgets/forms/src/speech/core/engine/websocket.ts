/**
 * WebSocket engine — pushes recorded audio frames over a persistent socket
 * and parses server responses through a host-supplied `parseMessage`
 * callback. Works with Deepgram / AssemblyAI realtime endpoints or any
 * custom gateway that speaks JSON or binary frames.
 *
 * Reconnect: simple exponential backoff capped at 5 s; the engine emits
 * `state: 'connecting'` between attempts so UIs can show "reconnecting…".
 */

import { newSegmentId } from '../ids';
import { sttLogger } from '../logger';
import { createEngineBus } from './index';
import { startMicCapture, type MicCaptureHandle } from './mediarecorder';
import type {
  EngineStartOptions,
  RecognitionEngine,
  RecognitionError,
  Unsub,
} from '../../types';

export type WsParsedEvent =
  | { kind: 'partial'; text: string; segmentId?: string; confidence?: number }
  | { kind: 'final'; text: string; segmentId?: string; confidence?: number }
  | { kind: 'error'; error: RecognitionError }
  | { kind: 'ignore' };

export interface WebSocketEngineOptions {
  url: string | ((language: string) => Promise<string> | string);
  protocols?: string[];
  /** Chunk emission interval, ms. Default 250 for realtime feel. */
  chunkMs?: number;
  mime?: string;
  /** Parse one frame (string or binary) into our normalised event shape. */
  parseMessage: (data: string | ArrayBuffer) => WsParsedEvent;
  /** Stable engine id for telemetry / UI badge. Default 'websocket'. */
  id?: string;
  /** Max reconnect attempts before giving up. Default 5. */
  maxReconnect?: number;
}

const MIN_BACKOFF = 250;
const MAX_BACKOFF = 5000;

export function createWebSocketEngine(
  opts: WebSocketEngineOptions,
): RecognitionEngine {
  const bus = createEngineBus();
  let socket: WebSocket | null = null;
  let capture: MicCaptureHandle | null = null;
  let currentSegmentId: string | null = null;
  let stopping = false;
  let attempts = 0;

  function emitParsed(parsed: WsParsedEvent): void {
    switch (parsed.kind) {
      case 'partial': {
        const id = parsed.segmentId ?? currentSegmentId ?? newSegmentId();
        currentSegmentId = id;
        bus.emit('partial', parsed.text, id);
        return;
      }
      case 'final': {
        const id = parsed.segmentId ?? currentSegmentId ?? newSegmentId();
        bus.emit('final', parsed.text, id, parsed.confidence);
        currentSegmentId = null;
        return;
      }
      case 'error':
        bus.emit('error', parsed.error);
        return;
      case 'ignore':
      default:
        return;
    }
  }

  async function openSocket(language: string): Promise<WebSocket> {
    const url =
      typeof opts.url === 'function' ? await opts.url(language) : opts.url;
    const ws = new WebSocket(url, opts.protocols);
    ws.binaryType = 'arraybuffer';
    return ws;
  }

  async function connect(start: EngineStartOptions): Promise<void> {
    if (stopping) return;
    bus.emit('state', 'connecting');
    let ws: WebSocket;
    try {
      ws = await openSocket(start.language);
    } catch (cause) {
      bus.emit('error', {
        code: 'network',
        message: 'Failed to open STT socket.',
        cause,
      });
      return;
    }
    socket = ws;

    ws.onopen = () => {
      attempts = 0;
      bus.emit('state', 'listening');
    };
    ws.onmessage = (e) => {
      try {
        const parsed = opts.parseMessage(e.data as string | ArrayBuffer);
        emitParsed(parsed);
      } catch (cause) {
        sttLogger.warn('[ws] parseMessage threw', cause);
      }
    };
    ws.onerror = () => {
      bus.emit('error', { code: 'network', message: 'STT socket error.' });
    };
    ws.onclose = () => {
      socket = null;
      if (stopping) {
        bus.emit('state', 'closed');
        return;
      }
      attempts += 1;
      const max = opts.maxReconnect ?? 5;
      if (attempts > max) {
        bus.emit('error', {
          code: 'network',
          message: `STT socket closed; gave up after ${max} attempts.`,
        });
        bus.emit('state', 'closed');
        return;
      }
      const delay = Math.min(MIN_BACKOFF * 2 ** (attempts - 1), MAX_BACKOFF);
      setTimeout(() => {
        void connect(start);
      }, delay);
    };
  }

  return {
    id: opts.id ?? 'websocket',
    isSupported:
      typeof WebSocket !== 'undefined' &&
      typeof navigator !== 'undefined' &&
      !!navigator.mediaDevices?.getUserMedia &&
      typeof MediaRecorder !== 'undefined',
    on(event, cb): Unsub {
      return bus.on(event, cb);
    },
    async start(start: EngineStartOptions): Promise<void> {
      if (capture) return;
      stopping = false;
      attempts = 0;
      try {
        capture = await startMicCapture({
          deviceId: start.deviceId,
          mime: opts.mime,
          chunkMs: opts.chunkMs ?? 250,
          onChunk: (chunk) => {
            if (socket?.readyState === WebSocket.OPEN) {
              chunk
                .arrayBuffer()
                .then((buf) => socket?.send(buf))
                .catch((cause) => sttLogger.warn('[ws] send failed', cause));
            }
          },
          onError: (err) => bus.emit('error', err),
        });
      } catch (cause) {
        const err = cause as RecognitionError;
        bus.emit('error', err);
        bus.emit('state', 'error');
        throw err;
      }
      await connect(start);
      // `once`: the listener is never removed explicitly, so a caller
      // reusing one AbortController across start/stop cycles stacked a
      // new one per start and aborted them all at once.
      start.signal?.addEventListener(
        'abort',
        () => {
          void this.stop();
        },
        { once: true },
      );
    },
    async stop(): Promise<void> {
      stopping = true;
      bus.emit('state', 'closing');
      try {
        socket?.close(1000, 'client-stop');
      } catch {
        // ignore
      }
      socket = null;
      await capture?.stop();
      capture = null;
      currentSegmentId = null;
      bus.emit('state', 'closed');
    },
    abort(): void {
      stopping = true;
      try {
        socket?.close(4000, 'client-abort');
      } catch {
        // ignore
      }
      socket = null;
      capture?.stop().catch(() => undefined);
      capture = null;
      currentSegmentId = null;
      bus.emit('state', 'closed');
    },
    getStream(): MediaStream | null {
      return capture?.stream ?? null;
    },
  };
}
