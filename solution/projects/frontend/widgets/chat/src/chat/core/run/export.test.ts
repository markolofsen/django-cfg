import { describe, expect, it } from "vitest";

import { step } from "../../ui/run/stories/steps";
import { runToMarkdown, type ExportWords } from "./export";
import { resolvePrivacy } from "./privacy";
import { selectRun, stepTitle } from "./view";

const words: ExportWords = { title: (s) => stepTitle(s, undefined, (k) => k), status: (s) => s, arguments: "Arguments", result: "Result" };
const view = selectRun([step("s1", { label: "Searching", summary: "3 hits", duration_ms: 1200, args: { q: "refunds" }, result: { preview: "a\nb", size: 3 } }), step("s2", { status: "error", label: "Lookup", redaction: "omitted", args: { q: "secret" } })]);

describe("export", () => {
  it("writes the steps in order, with what the screen shows", () => {
    const md = runToMarkdown(view, resolvePrivacy({ argsMode: "full" }), words);
    expect(md.split("\n")[0]).toBe("1. Searching (ok, 1.2 s) - 3 hits");
    expect(md).toContain("Arguments: q=refunds");
    expect(md).toContain("Result: a b");
    expect(md).toContain("2. Lookup (error)");
  });

  // MUTANT: build the export from the raw parts -> it carries what privacy hid.
  it("carries nothing the privacy hid", () => {
    const hidden = resolvePrivacy({ argsMode: "hidden", resultMode: "hidden" });
    expect(runToMarkdown(view, hidden, words)).not.toContain("refunds");
    expect(runToMarkdown(view, resolvePrivacy({ argsMode: "full" }), words)).not.toContain("secret");
  });
});
