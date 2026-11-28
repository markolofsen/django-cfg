/**
 * Shared mic capture used by the HTTP and WebSocket engines.
 *
 * Probes the browser for a working `MediaRecorder` MIME type and emits
 * `Blob` chunks on a steady interval. Picks the first supported MIME in
 * order: `audio/webm;codecs=opus` → `audio/ogg;codecs=opus` →
 * `audio/mp4;codecs=mp4a`. Falls back to engine default if none match.
 *
 * The capture also exposes the raw `MediaStream` so callers can wire up
 * an `AnalyserNode` for the level meter without owning a second copy.
 */

import { sttLogger } from '../logger';
import type { RecognitionError } from '../../types';

const PREFERRED_MIMES = [
  'audio/webm;codecs=opus',
  'audio/ogg;codecs=opus',
  'audio/mp4;codecs=mp4a',
  'audio/webm',
];

export function pickMime(preferred?: string): string | undefined {
  if (typeof MediaRecorder === 'undefined') return undefined;
  const candidates = preferred ? [preferred, ...PREFERRED_MIMES] : PREFERRED_MIMES;
  for (const mime of candidates) {
    if (MediaRecorder.isTypeSupported(mime)) return mime;
  }
  return undefined;
}

export interface MicCaptureOptions {
  deviceId?: string;
  /** Override probed MIME — useful when the backend expects a specific codec. */
  mime?: string;
  /** Chunk emission interval, ms. Default 250. */
  chunkMs?: number;
  onChunk: (chunk: Blob) => void;
  onError?: (err: RecognitionError) => void;
}

export interface MicCaptureHandle {
  readonly stream: MediaStream;
  readonly mime: string | undefined;
  stop(): Promise<void>;
}

function toErr(code: RecognitionError['code'], message: string, cause?: unknown): RecognitionError {
  return { code, message, cause };
}

export async function startMicCapture(
  opts: MicCaptureOptions,
): Promise<MicCaptureHandle> {
  if (typeof navigator === 'undefined' || !navigator.mediaDevices?.getUserMedia) {
    throw toErr('unsupported', 'getUserMedia is not available in this environment.');
  }
  if (typeof MediaRecorder === 'undefined') {
    throw toErr('unsupported', 'MediaRecorder is not available in this environment.');
  }

  let stream: MediaStream;
  try {
    stream = await navigator.mediaDevices.getUserMedia({
      audio: opts.deviceId ? { deviceId: { exact: opts.deviceId } } : true,
      video: false,
    });
  } catch (cause) {
    const name = (cause as { name?: string })?.name;
    if (name === 'NotAllowedError' || name === 'SecurityError') {
      throw toErr('permission-denied', 'Microphone permission denied.', cause);
    }
    if (name === 'NotFoundError' || name === 'OverconstrainedError') {
      throw toErr('no-microphone', 'No microphone found matching the constraints.', cause);
    }
    throw toErr('unknown', 'Failed to access microphone.', cause);
  }

  const mime = pickMime(opts.mime);
  const rec = mime ? new MediaRecorder(stream, { mimeType: mime }) : new MediaRecorder(stream);

  rec.ondataavailable = (e) => {
    if (e.data && e.data.size > 0) opts.onChunk(e.data);
  };
  rec.onerror = (e) => {
    const err = toErr('engine', 'MediaRecorder error.', e);
    sttLogger.warn('[capture] recorder error', e);
    opts.onError?.(err);
  };

  rec.start(opts.chunkMs ?? 250);

  return {
    stream,
    mime: mime ?? rec.mimeType,
    async stop() {
      const done = new Promise<void>((resolve) => {
        rec.addEventListener('stop', () => resolve(), { once: true });
      });
      if (rec.state !== 'inactive') rec.stop();
      stream.getTracks().forEach((t) => t.stop());
      await done;
    },
  };
}
