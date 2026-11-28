import { describe, expect, it } from "vitest";

import type { StreamChunk } from "./chunks";
import type { ChatMessage, StepMeta, StepStatus, ToolPart } from "./parts";
import { readTraceData, traceDataPart } from "../run/trace";
import { emptyTranscript, reduceAll, selectMessages } from "./transcript";

const start: StreamChunk = { type: "message-start", messageId: "m1", createdAt: 1 };

function run(chunks: readonly StreamChunk[]): ChatMessage {
  const message = selectMessages(reduceAll(emptyTranscript, chunks))[0];
  if (message === undefined) throw new Error("no message");
  return message;
}
const tools = (m: ChatMessage): ToolPart[] => m.parts.filter((p): p is ToolPart => p.type === "tool");

describe("a turn that ends with a call still open", () => {
  const open: StreamChunk[] = [
    start,
    { type: "reasoning-start", partId: "r" },
    { type: "reasoning-delta", partId: "r", delta: "hm" },
    { type: "tool-input-start", toolCallId: "c1", toolName: "read" },
    { type: "tool-input-available", toolCallId: "c1", input: { a: 1 } },
  ];

  it.each([
    ["finish", { type: "finish" }, "complete"],
    ["interrupted", { type: "interrupted" }, "interrupted"],
    ["error", { type: "error", message: "boom" }, "failed"],
  ] as const)("settles the thought and the call on %s", (_name, last, status) => {
    // MUTANT: drop `settleOpenParts` from `finishWith` -> the call reads as running forever.
    const message = run([...open, last]);
    expect(message.status.state).toBe(status);
    const part = message.parts[0];
    expect(part?.type === "reasoning" && part.streaming).toBe(false);
    const call = tools(message)[0];
    expect(call?.toolState).toEqual({ state: "output-error", input: { a: 1 }, error: "" });
    // Stopped, not failed: nothing about the tool itself is known.
    expect(call?.meta?.status).toBe("cancelled");
  });

  it("leaves a call that finished alone", () => {
    const message = run([...open, { type: "tool-output", toolCallId: "c1", output: "ok" }, { type: "finish" }]);
    expect(tools(message)[0]?.toolState.state).toBe("output-available");
    expect(tools(message)[0]?.meta).toBeUndefined();
  });
});

describe("repeated and early tool chunks", () => {
  it("does not append a second part for a repeated tool-input-start", () => {
    // MUTANT: append unconditionally -> two cards for one call.
    const message = run([
      start,
      { type: "tool-input-start", toolCallId: "c1", toolName: "read" },
      { type: "tool-input-start", toolCallId: "c1", toolName: "read" },
    ]);
    expect(tools(message)).toHaveLength(1);
  });

  it("keeps the arguments after a repeated start", () => {
    const message = run([
      start,
      { type: "tool-input-start", toolCallId: "c1", toolName: "read" },
      { type: "tool-input-delta", toolCallId: "c1", delta: "abc" },
      { type: "tool-input-start", toolCallId: "c1", toolName: "read" },
    ]);
    expect(tools(message)[0]?.toolState).toEqual({ state: "input-streaming", inputText: "abc" });
  });

  it("does not duplicate a reasoning or text part on a repeated start", () => {
    const message = run([
      start,
      { type: "reasoning-start", partId: "r" },
      { type: "reasoning-delta", partId: "r", delta: "x" },
      { type: "reasoning-start", partId: "r" },
      { type: "text-start", partId: "t" },
      { type: "text-delta", partId: "t", delta: "y" },
      { type: "text-start", partId: "t" },
    ]);
    expect(message.parts.map((p) => [p.type, "text" in p ? p.text : ""])).toEqual([["reasoning", "x"], ["text", "y"]]);
  });

  it("applies an output that arrived before its start, in order", () => {
    // MUTANT: drop orphans (the old behaviour) -> the call stays input-streaming.
    const message = run([
      start,
      { type: "tool-output", toolCallId: "c1", output: "late-first" },
      { type: "tool-input-start", toolCallId: "c1", toolName: "read" },
    ]);
    expect(tools(message)[0]?.toolState).toEqual({ state: "output-available", input: undefined, output: "late-first" });
  });

  it("buffers a call's early arguments and result together", () => {
    const message = run([
      start,
      { type: "tool-input-delta", toolCallId: "c1", delta: "{}" },
      { type: "tool-input-available", toolCallId: "c1", input: { q: 1 } },
      { type: "tool-output", toolCallId: "c1", output: "done" },
      { type: "tool-input-start", toolCallId: "c1", toolName: "read" },
    ]);
    expect(tools(message)[0]?.toolState).toEqual({ state: "output-available", input: { q: 1 }, output: "done" });
  });

  it("keeps the first answer a call got", () => {
    const message = run([
      start,
      { type: "tool-input-start", toolCallId: "c1", toolName: "read" },
      { type: "tool-output", toolCallId: "c1", output: "first" },
      { type: "tool-output", toolCallId: "c1", output: "second" },
      { type: "tool-error", toolCallId: "c1", error: "late" },
    ]);
    expect(tools(message)[0]?.toolState).toMatchObject({ state: "output-available", output: "first" });
  });

  it("bounds what it holds for calls that never open", () => {
    const strays: StreamChunk[] = Array.from({ length: 40 }, (_v, i) => ({ type: "tool-output", toolCallId: `x${i}`, output: i }));
    const state = reduceAll(emptyTranscript, [start, ...strays]);
    expect(Object.keys(state.orphans ?? {}).length).toBeLessThanOrEqual(16);
  });

  it("forgets what it held when the turn ends", () => {
    const state = reduceAll(emptyTranscript, [start, { type: "tool-output", toolCallId: "ghost", output: 1 }, { type: "finish" }]);
    expect(state.orphans).toBeUndefined();
  });
});

describe("a trace step frame (upsert)", () => {
  const meta = (status: StepStatus, eventSeq?: number): StepMeta => ({ status, redaction: "none", ...(eventSeq === undefined ? {} : { eventSeq }) });
  const tool = (status: StepStatus, eventSeq?: number): StreamChunk => ({
    type: "step",
    part: { type: "tool", id: "m1:s1", toolName: "kb", toolState: status === "running" ? { state: "input-available", input: undefined } : { state: "output-available", input: undefined, output: "ok" }, meta: meta(status, eventSeq) },
  });

  it("replaces a running step in place when it settles", () => {
    const m = run([start, tool("running", 1), tool("ok", 2)]);
    expect(tools(m)).toHaveLength(1);
    expect(tools(m)[0]?.toolState.state).toBe("output-available");
  });

  // MUTANT: drop the eventSeq guard -> a replayed running frame reopens a settled step.
  it("ignores an older frame and a running frame after a settled one", () => {
    expect(tools(run([start, tool("ok", 5), tool("running", 4)]))[0]?.toolState.state).toBe("output-available");
    expect(tools(run([start, tool("ok"), tool("running")]))[0]?.toolState.state).toBe("output-available");
  });

  it("settles a still-running step and an open trace data part when the turn is interrupted", () => {
    const data: StreamChunk = { type: "step", part: traceDataPart("m1:s2", { kind: "model", meta: meta("running") }) };
    const m = run([start, tool("running"), data, { type: "interrupted" }]);
    expect(tools(m)[0]?.meta?.status).toBe("cancelled");
    const trace = m.parts.find((p) => p.type === "data");
    expect(trace && readTraceData(trace)?.meta.status).toBe("cancelled");
  });
});
