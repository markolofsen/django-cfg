import { describe, expect, it } from "vitest";

import { step } from "../../ui/run/stories/steps";
import { PAGE_SIZE, STEP_CAP, windowSteps } from "./paging";
import { selectRun } from "./view";

const many = (n: number, over: (i: number) => Record<string, unknown> = () => ({})) => selectRun(Array.from({ length: n }, (_, i) => step(`s${i + 1}`, over(i)))).steps;
const title = (s: { name?: string }) => s.name ?? "?";

describe("windowSteps", () => {
  it("shows a page and counts what is behind it", () => {
    const w = windowSteps(many(60), PAGE_SIZE, title);
    expect(w.shown).toHaveLength(PAGE_SIZE);
    expect(w.hidden).toBe(35);
    expect(w.earlier).toBeNull();
  });

  // MUTANT: page without the pin -> a failure past page one is hidden behind "Show more".
  it("never hides a failed or running step behind the page", () => {
    const steps = many(60, (i) => (i === 50 ? { status: "error" } : i === 59 ? { status: "running" } : {}));
    const ids = windowSteps(steps, PAGE_SIZE, title).shown.map((s) => s.id);
    expect(ids).toContain("m:s51");
    expect(ids).toContain("m:s60");
  });

  it("folds the oldest settled steps past the cap into one counted line, in arrival order for the rest", () => {
    const steps = many(STEP_CAP + 30, (i) => ({ name: i % 3 === 0 ? "a" : "b" }));
    const w = windowSteps(steps, 1000, title);
    expect(w.earlier?.count).toBe(30);
    expect(w.earlier?.top[0]).toMatchObject({ name: "b" });
    expect(w.shown).toHaveLength(STEP_CAP);
    expect(w.shown[0]?.id).toBe("m:s31");
  });

  it("keeps a failed step that is older than the cap", () => {
    const steps = many(STEP_CAP + 30, (i) => (i === 2 ? { status: "error" } : {}));
    const w = windowSteps(steps, 1000, title);
    expect(w.shown[0]?.id).toBe("m:s3");
    expect(w.earlier?.count).toBe(29);
  });
});
