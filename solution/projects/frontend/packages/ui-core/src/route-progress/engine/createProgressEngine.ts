/**
 * The progress state machine, free of DOM and React. The numbers (start jump, step size by
 * band, the 0.994 cap) follow the model of `nprogress` 0.2.0 (MIT, see ../NOTICE); the code
 * is ours: one timer for trickling, one for the ceiling, one for the fade-out.
 */

import type { ProgressEngine, ProgressEngineOptions, ProgressState } from './types';

const IDLE: ProgressState = Object.freeze({ phase: 'idle', value: 0 });
const CAP = 0.994;

/** Step size by how far the bar already is. */
function stepFor(value: number): number {
  if (value < 0.2) return 0.1;
  if (value < 0.5) return 0.04;
  if (value < 0.8) return 0.02;
  if (value < 0.99) return 0.005;
  return 0;
}

export function createProgressEngine(options: ProgressEngineOptions = {}): ProgressEngine {
  const { minimum = 0.08, trickleMs = 200, maxMs = 15000, finishMs = 400 } = options;

  let state: ProgressState = IDLE;
  const listeners = new Set<() => void>();
  let trickleTimer: ReturnType<typeof setInterval> | undefined;
  let ceilingTimer: ReturnType<typeof setTimeout> | undefined;
  let finishTimer: ReturnType<typeof setTimeout> | undefined;

  const emit = (next: ProgressState) => {
    state = next;
    listeners.forEach((l) => l());
  };

  const clearTimers = () => {
    clearInterval(trickleTimer);
    clearTimeout(ceilingTimer);
    clearTimeout(finishTimer);
    trickleTimer = ceilingTimer = finishTimer = undefined;
  };

  const set = (value: number) => {
    if (state.phase !== 'running') return;
    const next = Math.min(CAP, Math.max(0, value));
    if (next !== state.value) emit({ phase: 'running', value: next });
  };

  const inc = (amount?: number) => {
    if (state.phase !== 'running') return;
    set(state.value + (amount ?? stepFor(state.value)));
  };

  const done = () => {
    if (state.phase !== 'running') return;
    clearTimers();
    emit({ phase: 'finishing', value: 1 });
    finishTimer = setTimeout(() => {
      finishTimer = undefined;
      emit(IDLE);
    }, finishMs);
  };

  return {
    getState: () => state,
    subscribe(listener) {
      listeners.add(listener);
      return () => {
        listeners.delete(listener);
      };
    },
    start() {
      if (state.phase === 'running') return;
      clearTimers();
      emit({ phase: 'running', value: minimum });
      trickleTimer = setInterval(() => inc(), trickleMs);
      ceilingTimer = setTimeout(done, maxMs);
    },
    set,
    inc,
    done,
    cancel() {
      if (state === IDLE) return;
      clearTimers();
      emit(IDLE);
    },
  };
}
