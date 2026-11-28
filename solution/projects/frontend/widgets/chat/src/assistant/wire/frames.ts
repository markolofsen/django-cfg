/**
 * The assistant SSE vocabulary, one version of it: `run`, `status`, `text_delta`, `ui_payload`, `done`, `error`, each as `data: {json with type}\n\n`.
 * The only file that knows the frame shapes. A host's structured parts travel as `ui_payload` `{kind, data}` and are drawn by the host's renderer for that kind.
 * `reasoning_delta` / `reasoning_end` and `trace_step` are optional layers: a host that never emits them is unaffected.
 * An unknown `type` is ignored and a malformed frame is dropped: the contract is forward compatible.
 */

import { decodeStep, type TraceStep } from './trace';

export type Phase = 'thinking' | 'searching' | 'answering';
export type StreamErrorCode = 'unavailable' | 'timeout' | 'failed';

/** The version `run` carries; a decoder that does not know a version still reads the fields it knows. */
export const WIRE_VERSION = 1;

export type Frame =
  | { type: 'run'; version: number; thread_id: string; message_id: string; client_id: string | null; seq: number | null }
  | { type: 'status'; phase: Phase }
  | { type: 'text_delta'; delta: string }
  | { type: 'reasoning_delta'; delta: string }
  | { type: 'reasoning_end'; elapsed_ms: number | null; tokens: number | null }
  | { type: 'trace_step'; event_seq: number | null; step: TraceStep }
  | { type: 'ui_payload'; kind: string; data: unknown }
  | { type: 'done'; finish_reason: string | null; tokens_in: number | null; tokens_out: number | null; cost_usd: number | null; replayed: boolean }
  | { type: 'error'; code: StreamErrorCode; message: string; retryable: boolean };

const PHASES: readonly string[] = ['thinking', 'searching', 'answering'];
const ERROR_CODES: readonly string[] = ['unavailable', 'timeout', 'failed'];

const isRecord = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null && !Array.isArray(value);
const str = (value: unknown): value is string => typeof value === 'string';
const num = (value: unknown): number | null => (typeof value === 'number' && Number.isFinite(value) ? value : null);

/** A known, well-formed frame, or null. */
export function decodeFrame(raw: unknown): Frame | null {
  if (!isRecord(raw)) return null;
  switch (raw.type) {
    case 'run':
      return str(raw.thread_id) && str(raw.message_id)
        ? { type: 'run', version: num(raw.version) ?? WIRE_VERSION, thread_id: raw.thread_id, message_id: raw.message_id, client_id: str(raw.client_id) ? raw.client_id : null, seq: num(raw.seq) }
        : null;
    case 'status':
      return str(raw.phase) && PHASES.includes(raw.phase) ? { type: 'status', phase: raw.phase as Phase } : null;
    case 'text_delta':
      return str(raw.delta) ? { type: 'text_delta', delta: raw.delta } : null;
    case 'reasoning_delta':
      return str(raw.delta) ? { type: 'reasoning_delta', delta: raw.delta } : null;
    case 'reasoning_end':
      return { type: 'reasoning_end', elapsed_ms: num(raw.elapsed_ms), tokens: num(raw.tokens) };
    case 'trace_step': {
      const eventSeq = num(raw.event_seq);
      const step = decodeStep(raw.step, eventSeq ?? undefined);
      return step === null ? null : { type: 'trace_step', event_seq: eventSeq, step };
    }
    case 'ui_payload':
      return str(raw.kind) && raw.kind !== '' && 'data' in raw ? { type: 'ui_payload', kind: raw.kind, data: raw.data } : null;
    case 'done':
      return {
        type: 'done',
        finish_reason: str(raw.finish_reason) ? raw.finish_reason : null,
        tokens_in: num(raw.tokens_in),
        tokens_out: num(raw.tokens_out),
        cost_usd: num(raw.cost_usd),
        replayed: raw.replayed === true,
      };
    case 'error':
      return str(raw.code) && ERROR_CODES.includes(raw.code) && str(raw.message)
        ? { type: 'error', code: raw.code as StreamErrorCode, message: raw.message, retryable: raw.retryable !== false }
        : null;
    default:
      return null;
  }
}

/** What the host says about the next turn (applies to that turn only): the page on screen, a selection, anything its server reads. The package never looks inside. */
export type ChatContext = Record<string, unknown>;

/** The idle limit above the server's 15 s ping; a silent stream past it is treated as lost. */
export const IDLE_MS = 45_000;
