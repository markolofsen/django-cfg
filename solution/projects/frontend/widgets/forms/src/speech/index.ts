/**
 * @djangocfg/widget-forms/speech-recognition
 *
 * Decomposed Speech-to-Text tool. Default backend is the browser Web
 * Speech API; custom engines can be plugged in for cloud or self-hosted
 * STT (Deepgram, Whisper, AssemblyAI, custom WebSocket).
 */

'use client';

export type {
  AutoStopOptions,
  EngineEventMap,
  EngineStartOptions,
  EngineState,
  RecognitionEngine,
  RecognitionError,
  RecognitionErrorCode,
  RecognitionStatus,
  Segment,
  Transcript,
  Unsub,
  UseSpeechRecognitionConfig,
  UseSpeechRecognitionReturn,
} from './types';

export {
  EMPTY_TRANSCRIPT,
  buildTranscript,
  joinFinal,
  newSegmentId,
  normaliseFinal,
} from './core';

export { createEngineBus } from './core/engine';
export { createWebSpeechEngine } from './core/engine/webspeech';
export type { WebSpeechEngineOptions } from './core/engine/webspeech';
export { createHttpEngine } from './core/engine/http';
export type {
  HttpEngineOptions,
  HttpEngineParseResult,
} from './core/engine/http';
export { createWebSocketEngine } from './core/engine/websocket';
export type {
  WebSocketEngineOptions,
  WsParsedEvent,
} from './core/engine/websocket';
export { createExternalEngine } from './core/engine/external';
export type {
  ExternalEngineHandle,
  ExternalEngineOptions,
} from './core/engine/external';
export { pickMime, startMicCapture } from './core/engine/mediarecorder';
export type {
  MicCaptureHandle,
  MicCaptureOptions,
} from './core/engine/mediarecorder';

export * from './hooks';
export * from './components';
export * from './widgets';
export * from './context';
// Dev logger — namespaced, runtime opt-in via localStorage.
// Enable from devtools: `localStorage['cfg.forms.speech_debug'] = '1'`.
export {
  getSpeechLogger,
  sttLogger,
  type SpeechLogger,
  type SpeechLogScope,
} from './core/logger';

export { LazyDictationField } from './lazy';
export { useSpeechPrefs } from './store';
export type { SpeechPrefs } from './store';
export { DEFAULT_VOICE_SOUNDS } from './core/audio/defaults';
export type { VoiceSoundEvent } from './core/audio/defaults';
