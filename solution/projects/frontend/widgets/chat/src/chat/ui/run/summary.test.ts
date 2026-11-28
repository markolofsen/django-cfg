import { describe, expect, it } from "vitest";

import { CHAT_DICTIONARIES } from "../../../i18n";
import { selectRun, stepTitle } from "../../core/run/view";
import { runSummary } from "./summary";
import { step } from "./stories/steps";

const title = (s: Parameters<typeof stepTitle>[0]) => stepTitle(s, undefined, (k) => k);
const spoken = (ms: number) => say([step("s1", { started_ms: 0, duration_ms: ms })]).text;
const say = (parts: Parameters<typeof selectRun>[0], language: keyof typeof CHAT_DICTIONARIES = "en") => runSummary(selectRun(parts), CHAT_DICTIONARIES[language], language, title);

describe("the collapsed line", () => {
  it("names the live step and counts the tools while it works", () => {
    expect(say([step("s1"), step("s2", { status: "running", label: "Reading 3 emails" })])).toEqual({ text: "Reading 3 emails… · 2 tools", tone: "live" });
  });

  it("does not double an ellipsis the server already wrote", () => {
    expect(say([step("s1", { status: "running", label: "Reading…" })]).text).toBe("Reading… · 1 tool");
  });

  it("settled: only how long it worked, never a tool count", () => {
    expect(say([step("s1", { started_ms: 0, duration_ms: 4000 }), step("s2", { started_ms: 4000, duration_ms: 6000 })])).toEqual({ text: "Worked for 10s", tone: "ok" });
  });

  it("rounds to whole seconds (never 0s), and switches to minutes", () => {
    expect(spoken(400)).toBe("Worked for 1s");
    expect(spoken(12_400)).toBe("Worked for 12s");
    expect(spoken(65_000)).toBe("Worked for 1m 5s");
  });

  it("says just Worked when the server sent no timing", () => {
    expect(say([step("s1")]).text).toBe("Worked");
  });

  it("a failed call is counted after the time, in warning tone", () => {
    expect(say([step("s1", { started_ms: 0, duration_ms: 10_000 }), step("s2", { status: "error" })])).toEqual({ text: "Worked for 10s · 1 failed", tone: "warn" });
  });

  it("a stopped turn says Stopped and keeps the count", () => {
    expect(say([step("s1"), step("s2", { status: "cancelled" })])).toEqual({ text: "Stopped · 2 tools", tone: "muted" });
  });

  it("uses the language's plural (Russian: one, few, many)", () => {
    const tools = (n: number) => say(Array.from({ length: n }, (_, i) => step(`s${i + 1}`, { status: "running" })), "ru").text;
    expect(tools(1)).toContain("1 инструмент");
    expect(tools(2)).toContain("2 инструмента");
    expect(tools(5)).toContain("5 инструментов");
  });
});
