import { readFileSync } from "node:fs";
import { join } from "node:path";

import { describe, expect, it } from "vitest";

const CSS = readFileSync(join(import.meta.dirname, "run.css"), "utf8");
const rule = (selector: string): string => CSS.match(new RegExp(`(?:^|\\n)${selector.replace(/[.[\]]/g, "\\$&")}\\s*\\{([^}]*)\\}`))?.[1] ?? "";

/**
 * The list's rhythm is a layout property no jsdom test measures, so the source is
 * pinned (the browser measurement, 28 px rows 2 px apart with and without a
 * disclosure, is in the plan's evidence). A host's touch-target rule on buttons once
 * made rows with a chevron 30 px taller than plain ones.
 */
describe("the Run list's rhythm", () => {
  it("a button in the block never brings its own minimum height", () => {
    expect(CSS).toContain(".chat-run button { min-block-size: 0; min-inline-size: 0; }");
  });

  it("a step's line is one height whether it is a button or a div", () => {
    expect(rule(".chat-run-step-head")).toContain("line-height: 1.5");
    expect(rule(".chat-run-step-head")).toContain("font: inherit");
  });

  it("the touch target is an invisible overflow, not padding", () => {
    expect(CSS).toContain("button.chat-run-step-head::after");
    expect(CSS).toMatch(/::after\s*\{[^}]*position: absolute;[^}]*inset-block: -0\.25rem/);
  });

  it("the copy button adds no height: absolute, 16 px", () => {
    const copy = rule(".chat-run-copy");
    expect(copy).toContain("position: absolute");
    expect(copy).toContain("inline-size: 1rem");
    expect(copy).toContain("block-size: 1rem");
  });
});
