/**
 * HTTP engine — records audio with MediaRecorder and POSTs each chunk to
 * a host-supplied URL. The host owns response parsing via `parse()`, so
 * this engine works with OpenAI Whisper REST, custom Django/FastAPI
 * endpoints, or anything else that takes audio and returns text.
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

export interface HttpEngineParseResult {
  text: string;
  isFinal: boolean;
  /** Optional engine-provided confidence 0..1. */
  confidence?: number;
}

export interface HttpEngineOptions {
  /** Endpoint URL. Receives `POST` with the audio chunk as the body. */
  url: string | ((language: string) => string);
  /** Per-request headers, awaited each chunk so tokens can be refreshed. */
  headers?: () => Promise<Record<string, string>> | Record<string, string>;
  /** Chunk emission interval, ms. Default 750 — long enough for useful audio. */
  chunkMs?: number;
  /** Preferred MIME for the encoder. Probed against `MediaRecorder` support. */
  mime?: string;
  /** Parse the engine response — return null/undefined to skip emit. */
  parse: (
    resp: Response,
  ) => Promise<HttpEngineParseResult | null | undefined> | HttpEngineParseResult | null | undefined;
  /** Stable engine id for telemetry / UI badge. Default 'http'. */
  id?: string;
}

export function createHttpEngine(opts: HttpEngineOptions): RecognitionEngine {
  const bus = createEngineBus();
  let capture: MicCaptureHandle | null = null;
  let currentSegmentId: string | null = null;
  let ctrl: AbortController | null = null;
  let stopping = false;

  async function sendChunk(blob: Blob, language: string): Promise<void> {
    if (stopping) return;
    const url = typeof opts.url === 'function' ? opts.url(language) : opts.url;
    const headers = (await opts.headers?.()) ?? {};
    try {
      const resp = await fetch(url, {
        method: 'POST',
        headers,
        body: blob,
        signal: ctrl?.signal,
      });
      if (!resp.ok) {
        bus.emit('error', {
          code: 'network',
          message: `STT endpoint returned ${resp.status}`,
        });
        return;
      }
      const parsed = await opts.parse(resp);
      if (!parsed || !parsed.text) return;
      if (!currentSegmentId) currentSegmentId = newSegmentId();
      if (parsed.isFinal) {
        bus.emit('final', parsed.text, currentSegmentId, parsed.confidence);
        currentSegmentId = null;
      } else {
        bus.emit('partial', parsed.text, currentSegmentId);
      }
    } catch (cause) {
      if ((cause as { name?: string })?.name === 'AbortError') return;
      sttLogger.warn('[http] chunk send failed', cause);
      bus.emit('error', {
        code: 'network',
        message: 'Failed to deliver audio chunk to STT endpoint.',
        cause,
      });
    }
  }

  return {
    id: opts.id ?? 'http',
    isSupported:
      typeof navigator !== 'undefined' &&
      !!navigator.mediaDevices?.getUserMedia &&
      typeof MediaRecorder !== 'undefined',
    on(event, cb): Unsub {
      return bus.on(event, cb);
    },
    async start(start: EngineStartOptions): Promise<void> {
      if (capture) return;
      stopping = false;
      ctrl = new AbortController();
      bus.emit('state', 'connecting');
      try {
        capture = await startMicCapture({
          deviceId: start.deviceId,
          mime: opts.mime,
          chunkMs: opts.chunkMs ?? 750,
          onChunk: (chunk) => {
            void sendChunk(chunk, start.language);
          },
          onError: (err) => bus.emit('error', err),
        });
        bus.emit('state', 'listening');
      } catch (cause) {
        const err = cause as RecognitionError;
        bus.emit('error', err);
        bus.emit('state', 'error');
        throw err;
      }

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
      ctrl?.abort();
      ctrl = null;
      await capture?.stop();
      capture = null;
      currentSegmentId = null;
      bus.emit('state', 'closed');
    },
    abort(): void {
      stopping = true;
      ctrl?.abort();
      ctrl = null;
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
