import { describe, expect, it } from "vitest";

import { step } from "../../ui/run/stories/steps";
import { detailOf, hasDetail, resolvePrivacy, thoughtText } from "./privacy";
import { selectRun, type RunStep } from "./view";

const open = (over: Record<string, unknown> = {}): RunStep =>
  selectRun([step("s1", { args: { q: "john@example.com", n: 3 }, args_size: 20, result: { preview: "found john@example.com in 3 mails", size: 33 }, purpose: "to find mail", refs: [{ kind: "email", id: "1", title: "Hello" }], ...over })]).steps[0]!;

describe("the defaults", () => {
  it("show argument names and a result preview, nothing more", () => {
    const detail = detailOf(open(), resolvePrivacy());
    expect(detail.args).toEqual([{ key: "q" }, { key: "n" }]);
    expect(detail.result).toContain("found");
  });
});

describe("argsMode and resultMode", () => {
  it("hidden shows nothing; masked and full show values", () => {
    expect(detailOf(open(), resolvePrivacy({ argsMode: "hidden", resultMode: "hidden" }))).toMatchObject({ notShared: false });
    expect(detailOf(open(), resolvePrivacy({ argsMode: "hidden", resultMode: "hidden" })).args).toBeUndefined();
    expect(detailOf(open(), resolvePrivacy({ argsMode: "hidden", resultMode: "hidden" })).result).toBeUndefined();
    expect(detailOf(open(), resolvePrivacy({ argsMode: "full" })).args).toEqual([{ key: "q", value: "john@example.com" }, { key: "n", value: "3" }]);
  });

  it("a preview is clipped to maxPreviewChars; full is not", () => {
    const long = open({ result: { preview: "x".repeat(500), size: 500 } });
    expect(detailOf(long, resolvePrivacy({ maxPreviewChars: 40 })).result).toHaveLength(41);
    expect(detailOf(long, resolvePrivacy({ resultMode: "full" })).result).toHaveLength(500);
  });

  it("an unknown mode falls back to the narrow default", () => {
    expect(detailOf(open(), resolvePrivacy({ argsMode: "everything" as never })).args).toEqual([{ key: "q" }, { key: "n" }]);
  });
});

describe("maskPatterns", () => {
  const privacy = resolvePrivacy({ argsMode: "full", maskPatterns: ["[\\w.]+@[\\w.]+"] });

  it("replace a match in the arguments and in the result", () => {
    const detail = detailOf(open(), privacy);
    expect(detail.args?.[0]?.value).toBe("•••");
    expect(detail.result).not.toContain("john@example.com");
  });

  // MUTANT: skip a pattern that throws -> the value is shown unmasked.
  it("a pattern that does not compile closes the detail instead of opening it", () => {
    const broken = resolvePrivacy({ argsMode: "full", resultMode: "full", maskPatterns: ["(unclosed"] });
    const detail = detailOf(open(), broken);
    expect(detail.args).toBeUndefined();
    expect(detail.result).toBeUndefined();
  });
});

describe("fail closed", () => {
  // MUTANT: treat a missing redaction mark as "none" -> a step nobody vetted leaks its detail.
  it("shows no detail for a step the server did not mark", () => {
    const plain = selectRun([{ type: "tool", id: "c", toolName: "read", toolState: { state: "output-available", input: { secret: 1 }, output: "x" } }]).steps[0]!;
    expect(detailOf(plain, resolvePrivacy({ argsMode: "full", resultMode: "full" }))).toMatchObject({ notShared: false });
    expect(hasDetail(detailOf(plain, resolvePrivacy({ argsMode: "full", resultMode: "full" })))).toBe(false);
  });

  it("says so when the server omitted a step's detail", () => {
    const detail = detailOf(open({ redaction: "omitted" }), resolvePrivacy({ argsMode: "full", resultMode: "full" }));
    expect(detail).toMatchObject({ notShared: true });
    expect(detail.args).toBeUndefined();
    expect(hasDetail(detail)).toBe(true);
  });

  it("labelsOnly shows no detail at all, whatever the modes say", () => {
    const detail = detailOf(open({ tokens: { input: 5, output: 6 } }), resolvePrivacy({ labelsOnly: true, argsMode: "full", resultMode: "full", showReasoningText: true }));
    expect(hasDetail(detail)).toBe(false);
  });

  it("a thought's words need the host's say-so, and labelsOnly overrides it", () => {
    const thought = selectRun([{ type: "reasoning", id: "r", text: "my private plan", streaming: false }]).steps[0]!;
    expect(thoughtText(thought, resolvePrivacy())).toBeUndefined();
    expect(thoughtText(thought, resolvePrivacy({ showReasoningText: true }))).toBe("my private plan");
    expect(thoughtText(thought, resolvePrivacy({ showReasoningText: true, labelsOnly: true }))).toBeUndefined();
    expect(thoughtText(thought, resolvePrivacy({ showReasoningText: true }), 5)).toBe("… plan");
  });
});
