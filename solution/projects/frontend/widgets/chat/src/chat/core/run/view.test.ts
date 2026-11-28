import { describe, expect, it } from "vitest";

import { step } from "../../ui/run/stories/steps";
import type { MessagePart } from "../conversation/parts";
import { selectRun, stepTitle } from "./view";

const kindWord = (kind: string) => `<${kind}>`;
const text: MessagePart = { type: "text", id: "t", text: "hi" };

describe("selectRun", () => {
  it("counts the tool calls and reads ok when all went well", () => {
    const view = selectRun([step("s1"), step("s2"), step("s3", { kind: "usage", name: "usage" })]);
    expect(view.counts).toMatchObject({ tools: 2, ok: 2, failed: 0, running: 0 });
    expect(view.status).toBe("ok");
    expect(view.steps).toHaveLength(3);
  });

  it("is running while any step is open, and names it as the current one", () => {
    const view = selectRun([step("s1"), step("s2", { status: "running", label: "Reading 3 emails" })]);
    expect(view.status).toBe("running");
    expect(view.current?.meta.label).toBe("Reading 3 emails");
  });

  // MUTANT: count only `error` as failed -> a timeout reads as a quiet success.
  it("counts error, timeout and denied as failed, and a stop as cancelled", () => {
    const view = selectRun([step("s1", { status: "timeout" }), step("s2", { status: "denied" }), step("s3", { status: "cancelled" })]);
    expect(view.counts).toMatchObject({ failed: 2, cancelled: 1 });
    expect(view.status).toBe("error");
    expect(selectRun([step("s1"), step("s2", { status: "cancelled" })]).status).toBe("cancelled");
  });

  it("skips parts that are not steps, and reads a plain tool part with no trace meta", () => {
    const plain: MessagePart = { type: "tool", id: "c", toolName: "mcp__srv__read", toolState: { state: "output-error", input: {}, error: "x" } };
    const view = selectRun([text, plain]);
    expect(view.steps.map((s) => s.status)).toEqual(["error"]);
  });

  it("takes the total from the server's offsets, not from a client clock", () => {
    const view = selectRun([step("s1", { started_ms: 100, duration_ms: 400 }), step("s2", { started_ms: 500, duration_ms: 1500 })]);
    expect(view.totalMs).toBe(1900);
    expect(selectRun([step("s1", { duration_ms: 300 }), step("s2", { duration_ms: 200 })]).totalMs).toBe(500);
    expect(selectRun([step("s1")]).totalMs).toBeUndefined();
  });
});

describe("stepTitle", () => {
  it("prefers the host's map, then the server's label, then the readable tool name, then the kind", () => {
    const s = selectRun([step("s1", { name: "mcp__srv__kb_search", label: "Searching" })]).steps[0]!;
    expect(stepTitle(s, { "mcp__srv__kb_search": "Looking it up" }, kindWord)).toBe("Looking it up");
    expect(stepTitle(s, undefined, kindWord)).toBe("Searching");
    const bare = selectRun([step("s1", { name: "mcp__srv__kb_search" })]).steps[0]!;
    expect(stepTitle(bare, undefined, kindWord)).toBe("kb_search");
    const usage = selectRun([step("s1", { kind: "usage", name: undefined })]).steps[0]!;
    expect(stepTitle(usage, undefined, kindWord)).toBe("<usage>");
  });
});
