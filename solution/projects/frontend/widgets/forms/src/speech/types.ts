/**
 * Public types for the SpeechRecognition tool.
 *
 * Design: a small `RecognitionEngine` interface lets consumers plug in
 * any STT backend (browser Web Speech, Deepgram, Whisper, custom WS).
 * The hooks/UI never depend on a specific engine.
 */

export type RecognitionStatus =
  | 'idle'
  | 'starting'
  | 'listening'
  | 'stopping'
  | 'error';

export type EngineState =
  | 'idle'
  | 'connecting'
  | 'listening'
  | 'closing'
  | 'closed'
  | 'error';

export type RecognitionErrorCode =
  | 'unsupported'
  | 'permission-denied'
  | 'no-microphone'
  | 'network'
  | 'aborted'
  | 'no-speech'
  | 'language'
  | 'engine'
  | 'unknown';

export interface RecognitionError {
  code: RecognitionErrorCode;
  message: string;
  cause?: unknown;
}

export interface Segment {
  id: string;
  text: string;
  isFinal: boolean;
  /** Engine-provided confidence 0..1 if available. */
  confidence?: number;
  /** ms since session start. */
  startedAt: number;
  endedAt?: number;
  /** Pass-through metadata from custom engines (diarization, lang, …). */
  metadata?: Record<string, unknown>;
}

export interface Transcript {
  /** Latest interim text (not yet final). Empty string when none. */
  interim: string;
  /** Concatenated final text (all segments joined with " "). */
  final: string;
  /** Full segment list including the trailing interim segment if any. */
  segments: Segment[];
}

// ── engine contract ────────────────────────────────────────────────────────

export interface EngineStartOptions {
  language: string;
  /** Whether the engine should emit partial/interim results. */
  interim: boolean;
  deviceId?: string;
  signal?: AbortSignal;
}

export type EngineEventMap = {
  partial: (text: string, segmentId: string) => void;
  final: (text: string, segmentId: string, confidence?: number) => void;
  error: (err: RecognitionError) => void;
  state: (state: EngineState) => void;
};

export type Unsub = () => void;

export interface RecognitionEngine {
  readonly id: string;
  readonly isSupported: boolean;
  /**
   * Whether this engine captures audio through the browser microphone
   * (`navigator.mediaDevices.getUserMedia`). `true` (default when
   * omitted) for the browser-native engines — Web Speech, HTTP and
   * WebSocket all open a `getUserMedia` stream. `false` for engines
   * that own capture outside the browser (`createExternalEngine` —
   * Wails / Tauri / native whisper sidecar), so consumers must NOT gate
   * them on `getUserMedia` being present.
   */
  readonly usesMicrophone?: boolean;
  start(opts: EngineStartOptions): Promise<void>;
  stop(): Promise<void>;
  abort(): void;
  on<K extends keyof EngineEventMap>(event: K, cb: EngineEventMap[K]): Unsub;
  /**
   * Optional — engines that capture mic audio themselves (HTTP / WS)
   * may expose the active `MediaStream` so consumers can wire up a
   * VU meter or waveform without owning a second `getUserMedia` call.
   */
  getStream?(): MediaStream | null;
}

// ── hook config ────────────────────────────────────────────────────────────

export interface AutoStopOptions {
  /** Stop after this many ms of silence (RMS below threshold). */
  silenceMs?: number;
  /** Hard cap on session length. */
  maxMs?: number;
  /** RMS threshold below which we count "silence". 0..1. Default 0.02. */
  silenceThreshold?: number;
}

export interface UseSpeechRecognitionConfig {
  engine?: RecognitionEngine;
  language?: string;
  interim?: boolean;
  deviceId?: string;
  autoStop?: AutoStopOptions;
  onFinal?: (text: string, segment: Segment) => void;
  onPartial?: (text: string, segment: Segment) => void;
  onError?: (err: RecognitionError) => void;
  onStart?: () => void;
  onStop?: () => void;
}

export interface UseSpeechRecognitionReturn {
  status: RecognitionStatus;
  isSupported: boolean;
  transcript: Transcript;
  error: RecognitionError | null;
  /** RMS level 0..1 for VU-meters. */
  level: number;
  start(): Promise<void>;
  stop(): Promise<void>;
  abort(): void;
  toggle(): Promise<void>;
  reset(): void;
}
