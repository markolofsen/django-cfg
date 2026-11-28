/**
 * TraceStep v1, as the server sends it (the `trace_step` frame and the stored `trace`
 * document) and as the widget's shared step model reads it.
 *
 * Tolerant and fail closed. A key it does not know is ignored; a malformed step is
 * dropped; an unknown `status` reads as `skipped` (neutral); an unknown or absent
 * `redaction` reads as `omitted`, and an `omitted` step keeps NO detail even if the
 * server sent some: the arguments, result, purpose, query and sources are dropped
 * here, so nothing downstream can show more than the server meant to.
 *
 * The step is turned into the part types the chat already draws: a tool step is a
 * `ToolPart`, a thought a `ReasoningPart`, everything else a `trace` data part. The
 * step list is derived from the parts, never kept twice.
 */

import type { DataPart, MessagePart, ReasoningPart, StepMeta, StepRedaction, StepRef, StepStatus, StepTokens, ToolPart } from '../../chat/core';
import { traceDataPart, type TraceData } from '../../chat/core';

/** One decoded step. */
export interface TraceStep {
  stepId: string;
  seq: number;
  kind: string;
  name?: string;
  meta: StepMeta;
}

const STATUSES: readonly string[] = ['running', 'ok', 'error', 'timeout', 'skipped', 'cancelled', 'denied'];
const REDACTIONS: readonly string[] = ['none', 'masked', 'omitted'];

const MAX_ARGS = 32;
const MAX_REFS = 20;
const MAX_TEXT = 500;
const MAX_PREVIEW = 2000;

const isRecord = (value: unknown): value is Record<string, unknown> => typeof value === 'object' && value !== null && !Array.isArray(value);
const text = (value: unknown, max = MAX_TEXT): string | undefined => (typeof value === 'string' && value !== '' ? value.slice(0, max) : undefined);
const count = (value: unknown): number | undefined => (typeof value === 'number' && Number.isFinite(value) && value >= 0 ? value : undefined);

function tokensOf(raw: unknown): StepTokens | undefined {
  if (!isRecord(raw)) return undefined;
  const tokens: { -readonly [K in keyof StepTokens]: StepTokens[K] } = {};
  for (const key of ['input', 'output', 'reasoning', 'cached'] as const) {
    const n = count(raw[key]);
    if (n !== undefined) tokens[key] = n;
  }
  return Object.keys(tokens).length === 0 ? undefined : tokens;
}

function refsOf(raw: unknown): StepRef[] | undefined {
  if (!Array.isArray(raw)) return undefined;
  const refs: StepRef[] = [];
  for (const item of raw.slice(0, MAX_REFS)) {
    if (!isRecord(item)) continue;
    const kind = text(item.kind, 40);
    const id = text(item.id, 200);
    if (kind === undefined || id === undefined) continue;
    const title = text(item.title, 200);
    refs.push(title === undefined ? { kind, id } : { kind, id, title });
  }
  return refs.length === 0 ? undefined : refs;
}

function argsOf(raw: unknown): Record<string, unknown> | undefined {
  if (!isRecord(raw)) return undefined;
  return Object.fromEntries(Object.entries(raw).slice(0, MAX_ARGS));
}

/** A step the server sent, or null when it is not one this reader can use. */
export function decodeStep(raw: unknown, eventSeq?: number): TraceStep | null {
  if (!isRecord(raw)) return null;
  const stepId = text(raw.step_id, 64);
  const kind = text(raw.kind, 32);
  if (stepId === undefined || kind === undefined) return null;

  const status: StepStatus = typeof raw.status === 'string' && STATUSES.includes(raw.status) ? (raw.status as StepStatus) : 'skipped';
  const redaction: StepRedaction = typeof raw.redaction === 'string' && REDACTIONS.includes(raw.redaction) ? (raw.redaction as StepRedaction) : 'omitted';
  const detail = redaction !== 'omitted';
  const result = isRecord(raw.result) ? raw.result : undefined;
  const error = isRecord(raw.error) ? raw.error : undefined;

  const meta: { -readonly [K in keyof StepMeta]: StepMeta[K] } = { status, redaction };
  const put = <K extends keyof StepMeta>(key: K, value: StepMeta[K] | undefined): void => {
    if (value !== undefined) meta[key] = value;
  };
  put('role', text(raw.role, 32));
  put('label', text(raw.label, 200));
  put('summary', text(raw.summary, 300));
  put('startedMs', count(raw.started_ms));
  put('durationMs', count(raw.duration_ms));
  put('parentId', text(raw.parent_id, 64));
  put('errorCode', error === undefined ? undefined : text(error.code, 64));
  if (error !== undefined && typeof error.retryable === 'boolean') meta.retryable = error.retryable;
  put('tokens', tokensOf(raw.tokens));
  put('costUsd', count(raw.cost_usd));
  put('eventSeq', eventSeq);
  if (detail) {
    put('purpose', text(raw.purpose));
    put('query', text(raw.query));
    put('argsView', argsOf(raw.args));
    put('argsBytes', count(raw.args_size));
    put('sources', refsOf(raw.refs));
    if (result !== undefined) {
      put('resultView', text(result.preview, MAX_PREVIEW));
      put('resultBytes', count(result.size));
      if (typeof result.truncated === 'boolean') meta.truncated = result.truncated;
    }
  }
  const name = text(raw.name, 120);
  return { stepId, seq: count(raw.seq) ?? 0, kind, ...(name === undefined ? {} : { name }), meta };
}

const CLOSED_AS_ERROR: readonly StepStatus[] = ['error', 'timeout', 'denied', 'cancelled'];

/** The part a step is drawn as; `id` is stable across the step's `running` and settled frames. */
export function stepPart(messageId: string, step: TraceStep): ToolPart | ReasoningPart | DataPart {
  const id = `${messageId}:${step.stepId}`;
  const { meta } = step;
  const status = meta.status ?? 'skipped';

  if (step.kind === 'tool') {
    const input = meta.argsView;
    const toolName = step.name ?? meta.label ?? 'tool';
    if (status === 'running' || status === 'pending') return { type: 'tool', id, toolName, toolState: { state: 'input-available', input }, meta };
    if (CLOSED_AS_ERROR.includes(status)) return { type: 'tool', id, toolName, toolState: { state: 'output-error', input, error: '' }, meta };
    return { type: 'tool', id, toolName, toolState: { state: 'output-available', input, output: meta.resultView }, meta };
  }

  if (step.kind === 'reasoning') {
    const tokens = meta.tokens?.reasoning;
    return {
      type: 'reasoning',
      id,
      text: '',
      streaming: status === 'running',
      ...(tokens === undefined ? {} : { tokens }),
      ...(meta.durationMs !== undefined && meta.durationMs > 0 ? { elapsedMs: meta.durationMs } : {}),
      // The words never leave the server in a trace; the live `reasoning_delta` text is a separate part.
      meta: { ...meta, hidden: true },
    };
  }

  const data: TraceData = { kind: step.kind, ...(step.name === undefined ? {} : { name: step.name }), meta };
  return traceDataPart(id, data);
}

/** A stored `trace` document as the history endpoint returns it (read by `fromStored`). */
export interface StoredTrace {
  v?: number;
  status?: string;
  steps_count?: number;
  truncated?: boolean;
  steps?: unknown[];
}

/**
 * The parts a stored trace restores, in the order the steps started, with every
 * step the document records closed: a stored snapshot is not running. A document
 * that dropped steps (its own cap) ends with a `note` saying how many.
 */
export function storedTraceParts(messageId: string, trace: StoredTrace | null | undefined): MessagePart[] {
  if (!isRecord(trace) || !Array.isArray(trace.steps)) return [];
  const steps = trace.steps.flatMap((raw) => {
    const step = decodeStep(raw);
    return step === null ? [] : [step];
  });
  steps.sort((a, b) => a.seq - b.seq);
  const parts: MessagePart[] = steps.map((step) =>
    stepPart(messageId, step.meta.status === 'running' ? { ...step, meta: { ...step.meta, status: 'cancelled' } } : step),
  );
  const total = count(trace.steps_count);
  if (total !== undefined && total > steps.length) {
    parts.push(traceDataPart(`${messageId}:trace-omitted`, { kind: 'note', name: 'truncated', omitted: total - steps.length, meta: { status: 'ok', redaction: 'omitted' } }));
  }
  return parts;
}
