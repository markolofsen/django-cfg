import { describe, expect, it } from "vitest";

import { groupParts, isGroupActive, planFold, type PartGroup } from "./group-parts";
import type { MessagePart, ToolState } from "./parts";

/** `noUncheckedIndexedAccess` is on; a missing group must fail loudly. */
function first(groups: readonly PartGroup[]): PartGroup {
  const group = groups[0];
  if (group === undefined) throw new Error("expected at least one group");
  return group;
}

const text = (id: string): MessagePart => ({ type: "text", id, text: id });
const reasoning = (id: string): MessagePart => ({ type: "reasoning", id, text: id });
const tool = (id: string, state: ToolState = { state: "output-available", input: {}, output: "" }): MessagePart => ({
  type: "tool",
  id,
  toolName: "read",
  toolState: state,
});

describe("groupParts", () => {
  it("collapses a run of adjacent tools", () => {
    const groups = groupParts([tool("a"), tool("b"), tool("c")]);
    expect(groups).toHaveLength(1);
    expect(groups[0]).toMatchObject({ kind: "run", type: "tool" });
  });

  it("never groups text — prose is the answer itself", () => {
    const groups = groupParts([text("a"), text("b")]);
    expect(groups.map((g) => g.kind)).toEqual(["single", "single"]);
  });

  it("does not merge runs separated by prose", () => {
    // Reordering to gather all tools together would misrepresent the turn:
    // "searched, then read what it found" is not "searched and read". Two
    // tools before the prose so the first group is a real run — with one it
    // would pass whether or not the split happened.
    const groups = groupParts([tool("a"), tool("b"), text("t"), tool("c"), tool("d")]);
    expect(groups.map((g) => g.kind)).toEqual(["run", "single", "run"]);
    expect(groups.filter((g) => g.kind === "run")).toHaveLength(2);
  });

  it("keeps a lone tool as a single, not a run of one", () => {
    expect(groupParts([tool("a")])[0]).toMatchObject({ kind: "single" });
  });

  it("does not merge different groupable types", () => {
    const groups = groupParts([reasoning("r"), tool("a")]);
    expect(groups.map((g) => g.kind)).toEqual(["single", "single"]);
  });

  it("keys a run on its first member so it survives growing", () => {
    // A run that gains a tool mid-stream must keep its key, or the group
    // remounts — and a remount closes whatever the user had expanded.
    const before = groupParts([tool("a"), tool("b")]);
    const after = groupParts([tool("a"), tool("b"), tool("c")]);
    expect(after[0]?.key).toBe(before[0]?.key);
  });

  it("handles an empty part list", () => {
    expect(groupParts([])).toEqual([]);
  });
});

describe("isGroupActive", () => {
  it("is active while a tool is still running", () => {
    const groups = groupParts([tool("a", { state: "input-streaming", inputText: "{" })]);
    expect(isGroupActive(first(groups))).toBe(true);
  });

  it("settles once every tool has finished", () => {
    const groups = groupParts([
      tool("a"),
      tool("b", { state: "output-error", input: {}, error: "boom" }),
    ]);
    expect(isGroupActive(first(groups))).toBe(false);
  });

  it("stays active if any member of a run is still running", () => {
    const groups = groupParts([tool("a"), tool("b", { state: "input-available", input: {} })]);
    expect(isGroupActive(first(groups))).toBe(true);
  });
});

describe("planFold", () => {
  const running = (id: string): MessagePart => tool(id, { state: "input-available", input: {} });
  const failed = (id: string): MessagePart => tool(id, { state: "output-error", input: {}, error: "x" });
  const stopped = (id: string): MessagePart => ({ ...(failed(id) as Extract<MessagePart, { type: "tool" }>), meta: { status: "cancelled" } });
  const plan = (parts: readonly MessagePart[]) => groupParts(parts).flatMap(planFold);
  const ids = (items: ReturnType<typeof plan>) =>
    items.map((i) => (i.kind === "fold" ? `fold(${i.parts.map((p) => p.id).join(",")})` : i.part.id));

  it("folds settled successes into one counter", () => {
    expect(ids(plan([tool("a"), tool("b"), tool("c")]))).toEqual(["fold(a,b,c)"]);
  });

  it("folds nothing while any call runs", () => {
    // MUTANT: skip the `isGroupActive` guard -> the finished calls vanish under the reader's eyes.
    expect(ids(plan([tool("a"), tool("b"), running("c")]))).toEqual(["a", "b", "c"]);
  });

  it("keeps a failed or stopped call visible and never folds it", () => {
    expect(ids(plan([tool("a"), failed("e"), tool("b"), stopped("s")]))).toEqual(["fold(a,b)", "e", "s"]);
  });

  it("does not fold a lone success, with or without a failure beside it", () => {
    expect(ids(plan([tool("a")]))).toEqual(["a"]);
    expect(ids(plan([tool("a"), failed("e")]))).toEqual(["a", "e"]);
  });

  it("never folds reasoning, and keeps prose between runs as its own part", () => {
    expect(ids(plan([reasoning("r1"), reasoning("r2")]))).toEqual(["r1", "r2"]);
    expect(ids(plan([tool("a"), tool("b"), text("t"), tool("c"), tool("d")]))).toEqual(["fold(a,b)", "t", "fold(c,d)"]);
  });

  it("keys the counter on its first call, so a growing run does not remount it", () => {
    const [item] = plan([tool("a"), tool("b")]);
    expect(item?.kind === "fold" && item.key).toBe("fold:a");
  });
});
