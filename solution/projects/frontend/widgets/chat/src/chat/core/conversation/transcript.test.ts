import { describe, expect, it } from "vitest";

import type { StreamChunk } from "./chunks";
import { isTextPart, isToolPart, type ChatMessage } from "./parts";
import { emptyTranscript, receiveMessage, reduceAll, selectMessages } from "./transcript";

/** Drive a whole turn and return the single message it produced. */
function run(chunks: readonly StreamChunk[]): ChatMessage {
  const messages = selectMessages(reduceAll(emptyTranscript, chunks));
  const first = messages[0];
  if (first === undefined) throw new Error("no message produced");
  return first;
}

const start: StreamChunk = { type: "message-start", messageId: "m1", createdAt: 1_700_000_000_000 };

describe("text streaming", () => {
  it("accumulates deltas into one part", () => {
    const message = run([
      start,
      { type: "text-start", partId: "t1" },
      { type: "text-delta", partId: "t1", delta: "Hel" },
      { type: "text-delta", partId: "t1", delta: "lo" },
      { type: "finish" },
    ]);
    expect(message.parts.filter(isTextPart).map((p) => p.text)).toEqual(["Hello"]);
    expect(message.status).toEqual({ state: "complete" });
  });

  it("keeps interleaved text parts apart", () => {
    // The bug this guards: a reducer that appends to "the last text part"
    // merges prose written before and after a tool call into one bubble.
    const message = run([
      start,
      { type: "text-start", partId: "a" },
      { type: "text-delta", partId: "a", delta: "before" },
      { type: "tool-input-start", toolCallId: "c1", toolName: "read" },
      { type: "tool-output", toolCallId: "c1", output: "ok" },
      { type: "text-start", partId: "b" },
      { type: "text-delta", partId: "b", delta: "after" },
      { type: "finish" },
    ]);
    expect(message.parts.filter(isTextPart).map((p) => p.text)).toEqual(["before", "after"]);
    expect(message.parts.map((p) => p.type)).toEqual(["text", "tool", "text"]);
  });

  it("routes a delta to its own part when another is still open", () => {
    const message = run([
      start,
      { type: "text-start", partId: "a" },
      { type: "text-start", partId: "b" },
      { type: "text-delta", partId: "a", delta: "A" },
      { type: "text-delta", partId: "b", delta: "B" },
      { type: "finish" },
    ]);
    expect(message.parts.filter(isTextPart).map((p) => p.text)).toEqual(["A", "B"]);
  });

  it("keeps reasoning separate from text", () => {
    const message = run([
      start,
      { type: "reasoning-start", partId: "r" },
      { type: "reasoning-delta", partId: "r", delta: "thinking" },
      { type: "text-start", partId: "t" },
      { type: "text-delta", partId: "t", delta: "answer" },
      { type: "finish" },
    ]);
    expect(message.parts.map((p) => p.type)).toEqual(["reasoning", "text"]);
  });
});

describe("tool-call lifecycle", () => {
  it("walks input-streaming to output-available", () => {
    const message = run([
      start,
      { type: "tool-input-start", toolCallId: "c1", toolName: "bash" },
      { type: "tool-input-delta", toolCallId: "c1", delta: '{"cmd"' },
      { type: "tool-input-delta", toolCallId: "c1", delta: ':"ls"}' },
      { type: "tool-input-available", toolCallId: "c1", input: { cmd: "ls" } },
      { type: "tool-output", toolCallId: "c1", output: "a.txt" },
      { type: "finish" },
    ]);
    const tool = message.parts.find(isToolPart);
    expect(tool?.toolState).toEqual({
      state: "output-available",
      input: { cmd: "ls" },
      output: "a.txt",
    });
  });

  it("carries the input through into the error state", () => {
    // Losing the input on failure is what makes a failed tool call
    // undiagnosable in the UI — you see that it broke, not what it ran.
    const message = run([
      start,
      { type: "tool-input-start", toolCallId: "c1", toolName: "bash" },
      { type: "tool-input-available", toolCallId: "c1", input: { cmd: "nope" } },
      { type: "tool-error", toolCallId: "c1", error: "exit 127" },
      { type: "finish" },
    ]);
    expect(message.parts.find(isToolPart)?.toolState).toEqual({
      state: "output-error",
      input: { cmd: "nope" },
      error: "exit 127",
    });
  });

  it("keeps two concurrent tool calls distinct", () => {
    const message = run([
      start,
      { type: "tool-input-start", toolCallId: "c1", toolName: "read" },
      { type: "tool-input-start", toolCallId: "c2", toolName: "grep" },
      { type: "tool-output", toolCallId: "c2", output: "second" },
      { type: "tool-output", toolCallId: "c1", output: "first" },
      { type: "finish" },
    ]);
    const outputs = message.parts
      .filter(isToolPart)
      .map((p) => (p.toolState.state === "output-available" ? p.toolState.output : null));
    expect(outputs).toEqual(["first", "second"]);
  });

  it("ignores output for an unknown tool call", () => {
    const message = run([
      start,
      { type: "text-start", partId: "t" },
      { type: "text-delta", partId: "t", delta: "hi" },
      { type: "tool-output", toolCallId: "ghost", output: "x" },
      { type: "finish" },
    ]);
    expect(message.parts).toHaveLength(1);
  });
});

describe("terminal states", () => {
  it("marks a failed turn failed, not complete", () => {
    // A failure rendered as an ordinary reply looks like the agent said it.
    const message = run([
      start,
      { type: "text-start", partId: "t" },
      { type: "text-delta", partId: "t", delta: "partial" },
      { type: "error", message: "upstream 502" },
    ]);
    expect(message.status).toEqual({ state: "failed", message: "upstream 502" });
  });

  it("distinguishes interrupted from failed", () => {
    const message = run([start, { type: "interrupted" }]);
    expect(message.status).toEqual({ state: "interrupted" });
  });

  it("stops routing chunks after a turn ends", () => {
    const message = run([
      start,
      { type: "text-start", partId: "t" },
      { type: "text-delta", partId: "t", delta: "done" },
      { type: "finish" },
      { type: "text-delta", partId: "t", delta: " LATE" },
    ]);
    expect(message.parts.filter(isTextPart).map((p) => p.text)).toEqual(["done"]);
  });
});

describe("reset", () => {
  it("discards the abandoned fragment instead of appending to it", () => {
    // Server event 15: the agent re-issues the turn after a mid-stream cut.
    // Ignoring it renders the fragment twice, which reads as the agent
    // repeating itself.
    const message = run([
      start,
      { type: "text-start", partId: "t1" },
      { type: "text-delta", partId: "t1", delta: "abandoned half-sen" },
      { type: "reset" },
      { type: "text-start", partId: "t2" },
      { type: "text-delta", partId: "t2", delta: "the real answer" },
      { type: "finish" },
    ]);
    expect(message.parts.filter(isTextPart).map((p) => p.text)).toEqual(["the real answer"]);
  });

  it("drops tool parts from the abandoned attempt too", () => {
    const message = run([
      start,
      { type: "tool-input-start", toolCallId: "c1", toolName: "read" },
      { type: "tool-output", toolCallId: "c1", output: "stale" },
      { type: "reset" },
      { type: "text-start", partId: "t" },
      { type: "text-delta", partId: "t", delta: "retry" },
      { type: "finish" },
    ]);
    expect(message.parts.map((p) => p.type)).toEqual(["text"]);
  });
});

describe("part identity", () => {
  it("gives every part a stable id survivable across a reset", () => {
    // React keys on these. An array index cannot serve: reset empties the
    // array, so index 0 legitimately becomes a different part.
    const message = run([
      start,
      { type: "text-start", partId: "t1" },
      { type: "reset" },
      { type: "text-start", partId: "t2" },
      { type: "finish" },
    ]);
    const ids = message.parts.map((p) => p.id);
    expect(ids).toEqual(["t2"]);
    expect(new Set(ids).size).toBe(ids.length);
  });
});

describe("stray chunks", () => {
  it("drops chunks that arrive with no message in flight", () => {
    // Deliberately NOT auto-opening a message: silent recovery hides an
    // adapter that forgot message-start and yields a plausible-but-wrong
    // transcript.
    const state = reduceAll(emptyTranscript, [
      { type: "text-start", partId: "t" },
      { type: "text-delta", partId: "t", delta: "orphan" },
    ]);
    expect(selectMessages(state)).toEqual([]);
  });
});

describe("whole parts (file, data)", () => {
  const plan = (step: string) => ({
    type: "data" as const,
    part: { type: "data" as const, id: "plan-current", kind: "plan", data: { step } },
  });

  it("REPLACES a data part that arrives again under the same id", () => {
    // The server revises its plan in place under a stable id and re-sends it on
    // every step. Appending stacks one card per step; the transport's own
    // accumulator is replace-by-id for this reason.
    const message = run([start, plan("one"), plan("two"), { type: "finish" }]);
    expect(message.parts).toHaveLength(1);
    expect(message.parts[0]).toMatchObject({ data: { step: "two" } });
  });

  it("keeps a replaced part in its ORIGINAL position", () => {
    // A card that jumps to the end on each revision makes a different claim
    // about when the agent authored it.
    const message = run([
      start,
      plan("one"),
      { type: "text-start", partId: "t" },
      { type: "text-delta", partId: "t", delta: "after" },
      plan("two"),
      { type: "finish" },
    ]);
    expect(message.parts.map((p) => p.type)).toEqual(["data", "text"]);
    expect(message.parts[0]).toMatchObject({ data: { step: "two" } });
  });

  it("keeps distinct ids as distinct parts", () => {
    const message = run([
      start,
      plan("one"),
      { type: "data", part: { type: "data", id: "notice-1", kind: "notice", data: {} } },
      { type: "finish" },
    ]);
    expect(message.parts).toHaveLength(2);
  });

  it("does NOT let a repeated text-start wipe the text under that id", () => {
    // The boundary of the replace rule. `text-start` creates an EMPTY part that
    // deltas fill, so replacing on a repeat would erase what already arrived —
    // strictly worse than the duplicate empty part it would prevent.
    const message = run([
      start,
      { type: "text-start", partId: "t1" },
      { type: "text-delta", partId: "t1", delta: "kept" },
      { type: "text-start", partId: "t1" },
      { type: "finish" },
    ]);
    expect(message.parts.filter(isTextPart).map((p) => p.text)).toContain("kept");
  });
});


describe("reasoning-end", () => {
  function thinkOnce(end: Record<string, unknown>): ChatMessage {
    return run([
      start,
      { type: "reasoning-start", partId: "r" },
      { type: "reasoning-delta", partId: "r", delta: "weighing it" },
      { type: "reasoning-end", partId: "r", ...end } as StreamChunk,
    ]);
  }

  it("seals the block and keeps what the engine measured", () => {
    expect(thinkOnce({ elapsedMs: 4200 }).parts[0]).toMatchObject({
      type: "reasoning",
      streaming: false,
      elapsedMs: 4200,
    });
  });

  // A block still marked streaming reads as a stalled turn forever. Its own end
  // is the only chunk that can settle it: the next part opening cannot, because
  // a turn may answer with a tool call or with nothing at all.
  it("marks a block streaming until its own end arrives", () => {
    const message = run([start, { type: "reasoning-start", partId: "r" }]);
    expect(message.parts[0]).toMatchObject({ streaming: true });
  });

  // Absent must stay absent: a zero would claim the model thought for no time.
  it("does not invent a measurement", () => {
    const part = thinkOnce({}).parts[0];
    expect(part).toMatchObject({ streaming: false });
    expect(part).not.toHaveProperty("elapsedMs");
    expect(part).not.toHaveProperty("tokens");
  });

  it("carries a token count for an engine that strips the words", () => {
    expect(thinkOnce({ tokens: 812 }).parts[0]).toMatchObject({ tokens: 812 });
  });

  // An end for a block that never opened would append an empty disclosure.
  it("ignores an end with no matching block", () => {
    const message = run([
      start,
      { type: "reasoning-end", partId: "ghost", elapsedMs: 10 } as StreamChunk,
    ]);
    expect(message.parts).toEqual([]);
  });
});

describe("receiveMessage", () => {
  const other = (id: string): ChatMessage => ({
    id,
    role: "user",
    parts: [{ type: "text", id: `${id}:t`, text: id }],
    status: { state: "complete" },
    createdAt: 1,
    from: "other",
  });

  it("appends a new message and keeps the streaming id", () => {
    const streaming = reduceAll(emptyTranscript, [
      start,
      { type: "text-start", partId: "t1" },
      { type: "text-delta", partId: "t1", delta: "hi" },
    ]);

    const next = receiveMessage(streaming, other("r1"));

    expect(next.ids).toEqual(["m1", "r1"]);
    expect(next.streamingId).toBe("m1");
    // The stream keeps writing into its own message afterwards.
    const after = reduceAll(next, [{ type: "text-delta", partId: "t1", delta: "!" }]);
    const text = after.byId["m1"]?.parts.filter(isTextPart).map((p) => p.text);
    expect(text).toEqual(["hi!"]);
  });

  it("refuses a copy of the message that is streaming", () => {
    const streaming = reduceAll(emptyTranscript, [start]);
    expect(receiveMessage(streaming, other("m1"))).toBe(streaming);
  });

  it("replaces a settled message by id and keeps its place", () => {
    let state = receiveMessage(emptyTranscript, other("a"));
    state = receiveMessage(state, other("b"));
    const revised = { ...other("a"), parts: [{ type: "text", id: "a:t", text: "edited" } as const] };

    state = receiveMessage(state, revised);

    expect(state.ids).toEqual(["a", "b"]);
    expect(state.byId["a"]).toBe(revised);
  });
});
