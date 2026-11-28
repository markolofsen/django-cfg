/**
 * Default engine — wraps the browser's `SpeechRecognition` API.
 *
 * Lives behind the same `RecognitionEngine` contract every other engine
 * implements. When the browser doesn't expose `SpeechRecognition`
 * (Firefox, some mobile WebViews) `isSupported` is `false` and `start()`
 * throws an `unsupported` error.
 */

import { newSegmentId } from '../ids';
import { sttLogger } from '../logger';
import { createEngineBus } from './index';
import type {
  EngineStartOptions,
  RecognitionEngine,
  RecognitionError,
  RecognitionErrorCode,
  Unsub,
} from '../../types';

// Minimal subset of the Web Speech API we actually rely on. Browsers
// expose either `SpeechRecognition` (Edge / Safari new) or the older
// `webkitSpeechRecognition` (Chrome). Both share the same shape.
interface BrowserSpeechRecognition extends EventTarget {
  lang: string;
  interimResults: boolean;
  continuous: boolean;
  maxAlternatives: number;
  start(): void;
  stop(): void;
  abort(): void;
  onresult: ((e: BrowserSpeechRecognitionEvent) => void) | null;
  onerror: ((e: BrowserSpeechRecognitionError) => void) | null;
  onstart: (() => void) | null;
  onend: (() => void) | null;
}

interface BrowserSpeechRecognitionResult {
  isFinal: boolean;
  0: { transcript: string; confidence: number };
}

interface BrowserSpeechRecognitionEvent extends Event {
  resultIndex: number;
  results: ArrayLike<BrowserSpeechRecognitionResult>;
}

interface BrowserSpeechRecognitionError extends Event {
  error: string;
  message?: string;
}

type Ctor = new () => BrowserSpeechRecognition;

function resolveCtor(): Ctor | null {
  if (typeof window === 'undefined') return null;
  const w = window as unknown as {
    SpeechRecognition?: Ctor;
    webkitSpeechRecognition?: Ctor;
  };
  return w.SpeechRecognition ?? w.webkitSpeechRecognition ?? null;
}

const ERROR_MAP: Record<string, RecognitionErrorCode> = {
  'no-speech': 'no-speech',
  aborted: 'aborted',
  'audio-capture': 'no-microphone',
  network: 'network',
  'not-allowed': 'permission-denied',
  'service-not-allowed': 'permission-denied',
  'bad-grammar': 'engine',
  'language-not-supported': 'language',
};

export interface WebSpeechEngineOptions {
  /** Whether the underlying recognition should be continuous. Default true. */
  continuous?: boolean;
  /** Max alternatives the engine should request. Default 1. */
  maxAlternatives?: number;
}

export function createWebSpeechEngine(
  opts: WebSpeechEngineOptions = {},
): RecognitionEngine {
  const Ctor = resolveCtor();
  const bus = createEngineBus();
  let instance: BrowserSpeechRecognition | null = null;
  let currentSegmentId: string | null = null;

  function teardown(): void {
    if (!instance) return;
    instance.onresult = null;
    instance.onerror = null;
    instance.onstart = null;
    instance.onend = null;
    instance = null;
    currentSegmentId = null;
  }

  return {
    id: 'webspeech',
    isSupported: Ctor !== null,
    on(event, cb): Unsub {
      return bus.on(event, cb);
    },
    async start(start: EngineStartOptions): Promise<void> {
      if (!Ctor) {
        const err: RecognitionError = {
          code: 'unsupported',
          message: 'Web Speech API is not available in this browser.',
        };
        bus.emit('error', err);
        throw err;
      }
      if (instance) {
        sttLogger.debug('[webspeech] start() called while running — ignoring');
        return;
      }

      bus.emit('state', 'connecting');

      const rec = new Ctor();
      rec.lang = start.language;
      rec.interimResults = start.interim;
      rec.continuous = opts.continuous ?? true;
      rec.maxAlternatives = opts.maxAlternatives ?? 1;

      rec.onstart = () => {
        bus.emit('state', 'listening');
      };
      rec.onend = () => {
        // `onerror` may have already forced the close + teardown (see
        // below). Guard so a trailing `onend` doesn't emit a second
        // `closed` — which would fire `onStop` twice (double stop earcon,
        // double `onFinish`).
        if (!instance) return;
        bus.emit('state', 'closed');
        teardown();
      };
      rec.onerror = (e) => {
        const code = ERROR_MAP[e.error] ?? 'engine';
        const err: RecognitionError = {
          code,
          message: e.message || `Web Speech error: ${e.error}`,
        };
        bus.emit('error', err);
        // Chrome does NOT reliably fire `onend` after `onerror` — most
        // often on a fast press→release where `no-speech`/`aborted`
        // fires but the recognizer settles without an `onend`. Without a
        // `closed` here the consumer stays in `stopping`/`starting`
        // forever (spinner hangs, next tap is swallowed because
        // `instance` is still set). Force the close + teardown so the
        // state machine always returns to a terminal state. Guard on
        // `instance` so a late `onend` after this doesn't double-emit.
        if (instance) {
          bus.emit('state', 'closed');
          teardown();
        }
      };
      rec.onresult = (e) => {
        for (let i = e.resultIndex; i < e.results.length; i += 1) {
          const res = e.results[i];
          if (!res) continue;
          const alt = res[0];
          if (!alt) continue;
          const text = alt.transcript;
          if (!currentSegmentId) currentSegmentId = newSegmentId();
          if (res.isFinal) {
            bus.emit('final', text, currentSegmentId, alt.confidence);
            currentSegmentId = null;
          } else {
            bus.emit('partial', text, currentSegmentId);
          }
        }
      };

      if (start.signal) {
        start.signal.addEventListener('abort', () => {
          rec.abort();
        });
      }

      instance = rec;
      try {
        rec.start();
      } catch (cause) {
        const err: RecognitionError = {
          code: 'engine',
          message: 'Failed to start Web Speech recognition.',
          cause,
        };
        bus.emit('error', err);
        teardown();
        throw err;
      }
    },
    async stop(): Promise<void> {
      if (!instance) return;
      bus.emit('state', 'closing');
      instance.stop();
    },
    abort(): void {
      if (!instance) return;
      instance.abort();
    },
  };
}
