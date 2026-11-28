/**
 * The Run block's model: what a turn DID, read from its parts.
 *
 * Headless and pure. The step list is derived from the parts (a tool call, a
 * thought, a `trace` data part), never stored a second time, so a live turn and a
 * reloaded one produce the same view. The UI reads only this.
 */

import type { MessagePart, StepMeta, StepStatus } from "../conversation/parts";
import { readableToolName } from "../tools/name";
import { isOpenStatus, readTraceData } from "./trace";

export type RunStatus = "running" | "ok" | "error" | "cancelled";

export interface RunStep {
  readonly id: string;
  /** `tool`, `reasoning`, or the kind of a trace step (`model`, `usage`, `error`, `note`, ...). */
  readonly kind: string;
  readonly status: StepStatus;
  /** The tool or model the step is about. */
  readonly name?: string;
  readonly meta: StepMeta;
  readonly part: MessagePart;
}

export interface RunCounts {
  readonly tools: number;
  readonly ok: number;
  readonly failed: number;
  readonly cancelled: number;
  readonly running: number;
}

export interface RunView {
  readonly status: RunStatus;
  /** The step in flight, when one is. */
  readonly current?: RunStep;
  readonly counts: RunCounts;
  /** Wall time of the whole run, from the server's own offsets; absent when the server sent none. */
  readonly totalMs?: number;
  readonly steps: readonly RunStep[];
  /** Steps the stored record dropped (its own cap), when it says so. */
  readonly omitted?: number;
}

/** An outcome that went wrong (not a stop: a stopped call failed at nothing known). */
export const isFailedStatus = (status: StepStatus): boolean => status === "error" || status === "timeout" || status === "denied";

/** A step the reader must not lose: it failed, it was stopped, or it is still going. */
export const isPinnedStep = (step: RunStep): boolean => isFailedStatus(step.status) || step.status === "cancelled" || isOpenStatus(step.status);

function toolStatus(part: MessagePart & { type: "tool" }): StepStatus {
  if (part.meta?.status !== undefined) return part.meta.status;
  switch (part.toolState.state) {
    case "output-available":
      return "ok";
    case "output-error":
      return "error";
    default:
      return "running";
  }
}

/** One part as a step, or null when it is not one (text, an attachment, a card). */
export function stepOf(part: MessagePart): RunStep | null {
  if (part.type === "tool") {
    const status = toolStatus(part);
    return { id: part.id, kind: "tool", status, name: part.toolName, meta: { ...part.meta, status }, part };
  }
  if (part.type === "reasoning") {
    const status = part.meta?.status ?? (part.streaming === true ? "running" : "ok");
    return { id: part.id, kind: "reasoning", status, meta: { ...part.meta, status }, part };
  }
  const trace = readTraceData(part);
  if (trace === null) return null;
  const status = trace.meta.status ?? "ok";
  return { id: part.id, kind: trace.kind, status, ...(trace.name === undefined ? {} : { name: trace.name }), meta: { ...trace.meta, status }, part };
}

function totalOf(steps: readonly RunStep[]): number | undefined {
  const timed = steps.filter((s) => s.meta.startedMs !== undefined);
  if (timed.length > 0) {
    const start = Math.min(...timed.map((s) => s.meta.startedMs ?? 0));
    const end = Math.max(...timed.map((s) => (s.meta.startedMs ?? 0) + (s.meta.durationMs ?? 0)));
    return end > start ? end - start : undefined;
  }
  const sum = steps.reduce((total, s) => total + (s.meta.durationMs ?? 0), 0);
  return sum > 0 ? sum : undefined;
}

/** The view of a run: its parts, in arrival order, summarised. Parts that are not steps are skipped. */
export function selectRun(parts: readonly MessagePart[]): RunView {
  let omitted = 0;
  const steps = parts.flatMap((part) => {
    const step = stepOf(part);
    if (step === null) return [];
    // "N steps were not kept" is a note about the record, not a step of the run.
    const dropped = readTraceData(part)?.omitted;
    if (dropped !== undefined) {
      omitted += dropped;
      return [];
    }
    return [step];
  });
  const tools = steps.filter((s) => s.kind === "tool");
  const failed = steps.filter((s) => isFailedStatus(s.status)).length;
  const counts: RunCounts = {
    tools: tools.length,
    ok: tools.filter((s) => s.status === "ok" || s.status === "skipped").length,
    failed,
    cancelled: steps.filter((s) => s.status === "cancelled").length,
    running: steps.filter((s) => isOpenStatus(s.status)).length,
  };
  const current = [...steps].reverse().find((s) => isOpenStatus(s.status));
  const status: RunStatus = counts.running > 0 ? "running" : counts.failed > 0 ? "error" : counts.cancelled > 0 ? "cancelled" : "ok";
  const totalMs = totalOf(steps);
  return { status, counts, steps, ...(omitted > 0 ? { omitted } : {}), ...(current === undefined ? {} : { current }), ...(totalMs === undefined ? {} : { totalMs }) };
}

/**
 * The words a step is called by: the host's map (by tool name), then the server's own
 * `label`, then the tool's readable name, then the kind's generic word. Never a raw
 * `mcp__` name.
 */
export function stepTitle(step: RunStep, hostLabels: Readonly<Record<string, string>> | undefined, kindWord: (kind: string) => string): string {
  const mapped = step.name === undefined ? undefined : hostLabels?.[step.name];
  if (mapped !== undefined && mapped !== "") return mapped;
  if (step.meta.label !== undefined && step.meta.label !== "") return step.meta.label;
  if (step.kind === "tool" && step.name !== undefined) return readableToolName(step.name);
  return kindWord(step.kind);
}
