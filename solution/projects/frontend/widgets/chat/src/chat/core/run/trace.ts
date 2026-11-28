/**
 * Trace steps that are neither a thought nor a tool call, as `data` parts.
 *
 * A model request, a usage line, an error, a note ("2 steps were not kept"): each
 * is a `data` part of kind `trace`, so the reducer needs no branch for them and a
 * host that draws nothing for the kind loses nothing. Thoughts and tool calls keep
 * their own part types (the existing renderers draw them) and carry the same
 * {@link StepMeta}.
 */

import type { DataPart, MessagePart, StepMeta, StepStatus } from "../conversation/parts";

export const TRACE_KIND = "trace";

/** The payload of a `trace` data part. */
export interface TraceData {
  /** `model`, `usage`, `error`, `approval`, `handoff`, `guardrail`, `source`, `note`; an unknown kind is drawn as a plain row. */
  readonly kind: string;
  /** The model or tool the step is about. */
  readonly name?: string;
  /** A `note` that steps were dropped: how many. */
  readonly omitted?: number;
  readonly meta: StepMeta;
}

const isRecord = (value: unknown): value is Record<string, unknown> =>
  typeof value === "object" && value !== null && !Array.isArray(value);

/** The payload of a `trace` part, or null when it is not one (a malformed payload is never drawn). */
export function readTraceData(part: MessagePart): TraceData | null {
  if (part.type !== "data" || part.kind !== TRACE_KIND) return null;
  const { data } = part;
  if (!isRecord(data) || typeof data.kind !== "string" || !isRecord(data.meta)) return null;
  return data as unknown as TraceData;
}

export function traceDataPart(id: string, data: TraceData): DataPart {
  return { type: "data", id, kind: TRACE_KIND, data };
}

/** The trace detail of any part that can carry some. */
export function stepMetaOf(part: MessagePart): StepMeta | undefined {
  if (part.type === "tool" || part.type === "reasoning") return part.meta;
  return readTraceData(part)?.meta;
}

/** A step that has not reached an outcome. */
export const isOpenStatus = (status: StepStatus | undefined): boolean =>
  status === "running" || status === "pending";
