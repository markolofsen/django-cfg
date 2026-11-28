/**
 * External-controlled engine — for backends that own the entire
 * record / decode / transcribe pipeline (Wails / Tauri / native
 * sidecar). The frontend exposes "start" and "stop" verbs to the
 * native layer, which then pushes a single `final` (or rolling
 * `partial`s + `final`) back through events.
 *
 * Use this when:
 *   - Audio capture lives outside the browser (cmdop_go OS-wide
 *     hotkey, system audio device claims, etc.).
 *   - Transcription runs on the backend (whisper.cpp, Vosk, custom
 *     ONNX) and the browser never sees the raw audio.
 *
 * Compared to `createHttpEngine`/`createWebSocketEngine`:
 *   - No `MediaRecorder` / `getUserMedia` involvement.
 *   - `isSupported` defaults to `true` (the host knows whether the
 *     native side is present — let it gate via `supported`).
 *   - No `MediaStream` to expose, so the VU meter falls through to
 *     the host's own level event (cmdop wires it via a separate hook).
 */

import { newSegmentId } from '../ids';
import { sttLogger } from '../logger';
import { createEngineBus } from './index';
import type {
  EngineStartOptions,
  RecognitionEngine,
  RecognitionError,
  Unsub,
} from '../../types';

export interface ExternalEngineHandle {
  /**
   * Push an interim transcript fragment. Wrapped into a `partial`
   * event with a generated segment id. Subsequent calls before
   * `emitFinal` mutate the same interim segment.
   */
  emitPartial(text: string): void;
  /**
   * Push the final transcript. Closes the current segment. With the
   * default `closeOnFinal`, also closes the whole session.
   */
  emitFinal(text: string, confidence?: number): void;
  /** Surface a backend error. Engine transitions to `closed`. */
  emitError(err: RecognitionError): void;
  /**
   * Notify the engine that the native side actually started capturing.
   * Flips status to `listening`. Call from a backend `recording`
   * event. Optional — see `autoMarkListening`.
   */
  markListening(): void;
}

export interface ExternalEngineOptions {
  /** Stable engine id for telemetry / UI badge. */
  id?: string;
  /**
   * Whether the host believes the native side is available. Wire to
   * a Wails ping / Tauri capability check. Defaults to `true`.
   */
  supported?: boolean;
  /** Ask the backend to start capture. */
  onStart: (opts: EngineStartOptions) => Promise<void> | void;
  /** Ask the backend to stop capture (and finalise the buffer). */
  onStop: () => Promise<void> | void;
  /**
   * Optional hard cancel — `onStop` may finalise, while `onAbort`
   * discards. Falls back to `onStop` when omitted.
   */
  onAbort?: () => Promise<void> | void;
  /**
   * Subscribe to backend events. Called once per `start()`. The host
   * wires its native event source (Wails `EventsOn`, Tauri
   * `appWindow.listen`, …) and uses the supplied `handle` to push
   * transcript fragments through the engine bus.
   *
   * Must return an unsubscribe function so the engine can detach on
   * teardown.
   */
  subscribe: (handle: ExternalEngineHandle) => Unsub;
  /**
   * If `true` (default), the engine flips state to `listening` right
   * after `onStart` resolves. Set `false` and call
   * `handle.markListening()` explicitly when you want to wait for the
   * native side to confirm the capture session opened.
   */
  autoMarkListening?: boolean;
  /**
   * If `true` (default), the engine closes the whole session right
   * after the first `emitFinal` — the common single-shot case (one
   * recording → one transcript, e.g. cmdop Wails push-to-talk).
   *
   * Set `false` for rolling backends that emit many partial/final
   * pairs within a single capture session (Deepgram-style streaming).
   * The session then stays `listening` after each `emitFinal` and only
   * closes on an explicit `stop()` / `abort()` or `emitError`.
   */
  closeOnFinal?: boolean;
}

/**
 * Wraps a backend-driven STT pipeline into the standard
 * `RecognitionEngine` shape so it works with `useSpeechRecognition`,
 * `VoiceComposerSlot`, and every other piece of the SpeechRecognition
 * tool.
 *
 * Example (cmdop Wails):
 *
 * ```ts
 * import { EventsOn } from '@runtime';
 * import * as VoiceService from '@bindings/desktop/services/voice/service';
 *
 * const engine = createExternalEngine({
 *   id: 'wails-whisper',
 *   onStart: () => VoiceService.StartRecordingForChat(),
 *   onStop: () => VoiceService.StopRecordingForChat(),
 *   subscribe: (handle) => {
 *     const offText = EventsOn('voice:chat-text', (p) => {
 *       if (p?.error) handle.emitError({ code: 'engine', message: p.error });
 *       else if (p?.text) handle.emitFinal(p.text);
 *       else handle.emitError({ code: 'no-speech', message: '' });
 *     });
 *     const offState = EventsOn('voice:state', (s) => {
 *       if (s.state === 'recording' || s.state === 'streaming') {
 *         handle.markListening();
 *       }
 *       if (s.partial) handle.emitPartial(s.partial);
 *     });
 *     return () => { offText(); offState(); };
 *   },
 * });
 * ```
 */
export function createExternalEngine(
  opts: ExternalEngineOptions,
): RecognitionEngine {
  const bus = createEngineBus();
  const closeOnFinal = opts.closeOnFinal ?? true;
  let currentSegmentId: string | null = null;
  let unsubscribe: Unsub | null = null;
  let running = false;

  function teardown(): void {
    unsubscribe?.();
    unsubscribe = null;
    currentSegmentId = null;
    running = false;
  }

  const handle: ExternalEngineHandle = {
    emitPartial(text: string): void {
      if (!running) return;
      if (!currentSegmentId) currentSegmentId = newSegmentId();
      bus.emit('partial', text, currentSegmentId);
    },
    emitFinal(text: string, confidence?: number): void {
      if (!running) return;
      const id = currentSegmentId ?? newSegmentId();
      bus.emit('final', text, id, confidence);
      // Single-shot engines (default) go idle right after their final —
      // close the session so consumers' `onStop` fires without a
      // separate `stop()` call. Rolling engines keep the session open
      // and just reset the segment so the next partial starts fresh.
      if (closeOnFinal) {
        bus.emit('state', 'closed');
        teardown();
      } else {
        currentSegmentId = null;
      }
    },
    emitError(err: RecognitionError): void {
      bus.emit('error', err);
      bus.emit('state', 'closed');
      teardown();
    },
    markListening(): void {
      if (!running) return;
      bus.emit('state', 'listening');
    },
  };

  return {
    id: opts.id ?? 'external',
    isSupported: opts.supported ?? true,
    // Capture happens outside the browser (native / sidecar), so this
    // engine must never be gated on `navigator.mediaDevices.getUserMedia`
    // — that API is absent in many host shells (Wails WKWebView) and in
    // headless / non-secure contexts, yet the engine works fine there.
    usesMicrophone: false,
    on(event, cb): Unsub {
      return bus.on(event, cb);
    },
    async start(start: EngineStartOptions): Promise<void> {
      if (running) return;
      running = true;
      bus.emit('state', 'connecting');
      // Subscribe before the native side starts so we never miss the
      // first event (some backends emit `recording` synchronously).
      unsubscribe = opts.subscribe(handle);
      try {
        await opts.onStart(start);
      } catch (cause) {
        const err: RecognitionError = {
          code: 'engine',
          message: 'External engine failed to start.',
          cause,
        };
        bus.emit('error', err);
        bus.emit('state', 'closed');
        teardown();
        throw err;
      }
      if (opts.autoMarkListening !== false) {
        bus.emit('state', 'listening');
      }
      // `once`: the listener is never removed explicitly, so a caller
      // reusing one AbortController across start/stop cycles stacked a
      // new one per start and aborted them all at once.
      start.signal?.addEventListener(
        'abort',
        () => {
          this.abort();
        },
        { once: true },
      );
    },
    async stop(): Promise<void> {
      if (!running) return;
      bus.emit('state', 'closing');
      try {
        await opts.onStop();
      } catch (cause) {
        sttLogger.warn('[external] onStop threw', cause);
      }
      // Note: we DO NOT flip to `closed` here — most external engines
      // need a roundtrip (transcribe + LLM rewrite) before the final
      // text arrives. `emitFinal` / `emitError` are responsible for
      // closing the session.
    },
    abort(): void {
      if (!running) return;
      bus.emit('state', 'closing');
      const stopper = opts.onAbort ?? opts.onStop;
      Promise.resolve(stopper()).catch((cause) => {
        sttLogger.warn('[external] abort hook threw', cause);
      });
      bus.emit('state', 'closed');
      teardown();
    },
  };
}
