import { describe, expect, it } from "vitest";

import { step } from "../../ui/run/stories/steps";
import type { MessagePart } from "../conversation/parts";
import { planRuns } from "./segment";

const text = (id: string): MessagePart => ({ type: "text", id, text: id });
const card: MessagePart = { type: "data", id: "d", kind: "citations", data: {} };

describe("planRuns", () => {
  it("makes one run of adjacent steps, thoughts and tool calls, and keeps the text between runs", () => {
    const thought: MessagePart = { type: "reasoning", id: "r", text: "", streaming: false };
    const items = planRuns([thought, step("s1"), text("a"), step("s2"), card, step("s3")]);
    expect(items.map((i) => (i.kind === "run" ? `run:${i.part.parts.length}` : i.part.id))).toEqual(["run:2", "a", "run:1", "d", "run:1"]);
  });

  it("an ordinary card is never a step", () => {
    expect(planRuns([card]).map((i) => i.kind)).toEqual(["part"]);
  });

  // MUTANT: build a new RunPart on every call -> a delta in the answer re-renders every settled run above it.
  it("reuses the run while its parts are the same objects, and replaces it when one changes", () => {
    const a = step("s1");
    const b = step("s2");
    const first = planRuns([a, b])[0]!.part;
    expect(planRuns([a, b, text("t")])[0]!.part).toBe(first);
    expect(planRuns([a, step("s2", { status: "error" })])[0]!.part).not.toBe(first);
  });
});
