import { describe, expect, it } from "vitest";

import { scenario } from "./builder";
import { tokens } from "./model";

const meta = { id: "t", title: "T", note: "n", group: "tools", prompt: "go" } as const;

describe("the scenario builder", () => {
  it("is deterministic: the same seed gives the same times", () => {
    const make = (seed: number) => scenario({ ...meta, seed }).say("one two three four five six ").tool("kb", {}).build();
    expect(make(3)).toEqual(make(3));
    expect(make(3)).not.toEqual(make(4));
  });

  it("keeps tool latency in its band and token cadence in its band", () => {
    const built = scenario(meta).tool("a", {}).tool("b", {}).tool("c", {}).say("a b c d e f g h ").build();
    const steps = built.beats.filter((beat) => beat.kind === "step");
    for (let i = 0; i < steps.length; i += 2) {
      const span = (steps[i + 1]?.at ?? 0) - (steps[i]?.at ?? 0);
      expect(span).toBeGreaterThanOrEqual(80);
      expect(span).toBeLessThanOrEqual(2500);
    }
    const say = built.beats.find((beat) => beat.kind === "say");
    expect(say && say.kind === "say" ? say.ms / tokens(say.text).length : 0).toBeGreaterThanOrEqual(20);
    expect(say && say.kind === "say" ? say.ms / tokens(say.text).length : 99).toBeLessThanOrEqual(60);
  });

  it("starts a call and settles it under the same step id", () => {
    const built = scenario(meta).tool("kb", { ms: 500, label: "Searching" }).build();
    const [running, settled] = built.beats;
    expect(running).toMatchObject({ kind: "step", step: { step_id: "s1", status: "running" } });
    expect(settled).toMatchObject({ kind: "step", step: { step_id: "s1", status: "ok", duration_ms: 500 } });
    expect((settled?.at ?? 0) - (running?.at ?? 0)).toBe(500);
  });

  it("interleaves parallel calls by time and numbers the frames in the order they are sent", () => {
    const built = scenario(meta)
      .parallel([
        ["a", { ms: 900 }],
        ["b", { ms: 200 }],
      ])
      .build();
    const order = built.beats.flatMap((beat) => (beat.kind === "step" ? [`${String(beat.step.step_id)}:${String(beat.step.status)}`] : []));
    expect(order).toEqual(["s1:running", "s2:running", "s2:ok", "s1:ok"]);
    const sequence = built.beats.flatMap((beat) => (beat.kind === "step" ? [beat.eventSeq] : []));
    expect(sequence).toEqual([1, 2, 3, 4]);
  });

  it("joins tokens back into the text", () => {
    expect(tokens("Hello big world\n").join("")).toBe("Hello big world\n");
  });
});
