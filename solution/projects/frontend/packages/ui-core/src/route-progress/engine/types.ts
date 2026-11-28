export type ProgressPhase = 'idle' | 'running' | 'finishing';

/** Immutable snapshot: a new object on every change, so it can feed `useSyncExternalStore`. */
export interface ProgressState {
  phase: ProgressPhase;
  /** 0..1. The bar's width while `running`; 1 while `finishing`; 0 when `idle`. */
  value: number;
}

export interface ProgressEngineOptions {
  /** Where the bar jumps to on `start()`. Default 0.08. */
  minimum?: number;
  /** Delay between automatic steps, ms. Default 200. */
  trickleMs?: number;
  /** Ceiling: a run that was never finished ends by itself after this many ms. Default 15000. */
  maxMs?: number;
  /** How long the full bar stays before it goes idle (the fade-out), ms. Default 400. */
  finishMs?: number;
}

export interface ProgressEngine {
  getState(): ProgressState;
  subscribe(listener: () => void): () => void;
  /** Begin a run. Starting while running keeps the current value. */
  start(): void;
  /** Jump to `value` (clamped to 0..0.994) while running. */
  set(value: number): void;
  /** Move forward by `amount`, or by the step for the current band. */
  inc(amount?: number): void;
  /** Finish: fill the bar, then go idle after `finishMs`. No-op when idle. */
  done(): void;
  /** Drop the run at once, without the fill. */
  cancel(): void;
}
