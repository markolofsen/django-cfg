/**
 * Close what a turn left open.
 *
 * A thought is sealed by the next part opening, a call by its result. When the
 * turn ends first (Stop, a lost stream, a failed run, even a `finish` that
 * arrived before the last result) nothing else will ever say so, and the part
 * would read as running for as long as the transcript lives.
 *
 * Open calls become `output-error` with `meta.status: "cancelled"`, never a
 * failure verdict: the reader sees "Stopped", and the turn's own status says why
 * it ended. The type keeps its four states, so no renderer learns a fifth.
 */

import type { ChatMessage, MessagePart, ToolPart } from "./parts";
import { isOpenStatus, readTraceData, traceDataPart } from "../run/trace";

function settlePart(part: MessagePart): MessagePart {
  if (part.type === "reasoning") {
    const stepOpen = part.meta !== undefined && isOpenStatus(part.meta.status);
    if (part.streaming !== true && !stepOpen) return part;
    return { ...part, streaming: false, ...(stepOpen ? { meta: { ...part.meta, status: "cancelled" as const } } : {}) };
  }
  if (part.type === "tool") return settleTool(part);
  const trace = readTraceData(part);
  if (trace !== null && isOpenStatus(trace.meta.status)) {
    return traceDataPart(part.id, { ...trace, meta: { ...trace.meta, status: "cancelled" } });
  }
  return part;
}

function settleTool(part: ToolPart): ToolPart {
  const { toolState } = part;
  if (toolState.state !== "input-streaming" && toolState.state !== "input-available") return part;
  return {
    ...part,
    toolState: {
      state: "output-error",
      input: toolState.state === "input-available" ? toolState.input : undefined,
      error: "",
    },
    meta: { ...part.meta, status: "cancelled" },
  };
}

/** The message with every open part closed; the same object when nothing was open. */
export function settleOpenParts(message: ChatMessage): ChatMessage {
  let changed = false;
  const parts = message.parts.map((part) => {
    const next = settlePart(part);
    if (next !== part) changed = true;
    return next;
  });
  return changed ? { ...message, parts } : message;
}
