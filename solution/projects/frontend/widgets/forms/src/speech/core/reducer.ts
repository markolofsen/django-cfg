import { newSegmentId } from './ids';
import type {
  RecognitionError,
  RecognitionStatus,
  Segment,
} from '../types';

export interface RecognitionState {
  status: RecognitionStatus;
  segments: Segment[];
  error: RecognitionError | null;
  startedAt: number | null;
}

export const INITIAL_STATE: RecognitionState = {
  status: 'idle',
  segments: [],
  error: null,
  startedAt: null,
};

export type RecognitionAction =
  | { type: 'START' }
  | { type: 'STARTED' }
  | { type: 'STOP' }
  | { type: 'STOPPED' }
  | { type: 'ABORT' }
  | {
      type: 'PARTIAL';
      text: string;
      segmentId: string;
      confidence?: number;
    }
  | {
      type: 'FINAL';
      text: string;
      segmentId: string;
      confidence?: number;
    }
  | { type: 'ERROR'; error: RecognitionError }
  | { type: 'RESET' };

function nowSinceStart(state: RecognitionState): number {
  return state.startedAt ? Date.now() - state.startedAt : 0;
}

function upsertSegment(
  segments: Segment[],
  patch: Segment,
): Segment[] {
  const idx = segments.findIndex((s) => s.id === patch.id);
  if (idx === -1) return [...segments, patch];
  const next = segments.slice();
  next[idx] = { ...next[idx], ...patch };
  return next;
}

export function reducer(
  state: RecognitionState,
  action: RecognitionAction,
): RecognitionState {
  switch (action.type) {
    case 'START':
      return {
        ...state,
        status: 'starting',
        error: null,
        startedAt: Date.now(),
      };
    case 'STARTED':
      return { ...state, status: 'listening' };
    case 'STOP':
      return { ...state, status: 'stopping' };
    case 'STOPPED':
    case 'ABORT':
      return { ...state, status: 'idle' };
    case 'PARTIAL': {
      const seg: Segment = {
        id: action.segmentId,
        text: action.text,
        isFinal: false,
        confidence: action.confidence,
        startedAt: nowSinceStart(state),
      };
      return { ...state, segments: upsertSegment(state.segments, seg) };
    }
    case 'FINAL': {
      const seg: Segment = {
        id: action.segmentId || newSegmentId(),
        text: action.text,
        isFinal: true,
        confidence: action.confidence,
        startedAt: nowSinceStart(state),
        endedAt: nowSinceStart(state),
      };
      return { ...state, segments: upsertSegment(state.segments, seg) };
    }
    case 'ERROR':
      return { ...state, status: 'error', error: action.error };
    case 'RESET':
      return { ...INITIAL_STATE };
    default:
      return state;
  }
}
