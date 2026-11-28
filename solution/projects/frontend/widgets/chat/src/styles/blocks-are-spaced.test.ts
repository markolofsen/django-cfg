import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * Block-level parts take their spacing from a class the stylesheet owns, and
 * nothing else can see that the two agree.
 *
 * The defect this guards: cards and pictures rendered flush against each other
 * and against the prose, because the transcript stacks every part at one flat
 * gap and only `.chat-tool` had a rhythm of its own. A renderer that names
 * `chat-block` while no rule defines it type-checks, lints and tests clean —
 * and reproduces the defect exactly.
 */

// Paths inside the entry are relative to IT, not to this test.
const STYLES = import.meta.dirname;
const ENTRY = readFileSync(join(STYLES, "index.css"), "utf8");
const CSS = [...ENTRY.matchAll(/@import "\.\/([^"]+)"/g)]
  .map(([, path]) => readFileSync(join(STYLES, path ?? ""), "utf8"))
  .join("\n");

function sourceOf(...segments: readonly string[]): string {
  return readFileSync(join(import.meta.dirname, "..", ...segments), "utf8");
}

describe("the class the renderers name", () => {
  it("is worn by every media kind, from one wrapper", () => {
    // At the widget's entry rather than on each renderer: eleven kinds behind
    // one event, and a per-renderer class is a rule the twelfth joins by
    // remembering to.
    expect(sourceOf("chat", "media", "media.tsx")).toContain('className="chat-block"');
  });
});

describe("the rules that class resolves to", () => {
  it("separates a box from the text above it", () => {
    expect(CSS).toMatch(/\.chat-tool,\s*\.chat-block\s*\{[^}]*margin-block-start:\s*0\.875rem/);
  });

  it("draws two adjacent boxes closer than a box and prose", () => {
    // The pairing is what the flat transcript gap cannot express, and all four
    // orders matter: a tool call followed by a card is as common as two cards.
    for (const pair of [
      ".chat-tool + .chat-tool",
      ".chat-block + .chat-block",
      ".chat-tool + .chat-block",
      ".chat-block + .chat-tool",
    ]) {
      expect(CSS, pair).toContain(pair);
    }
    expect(CSS).toMatch(/\.chat-block \+ \.chat-tool\s*\{[^}]*margin-block-start:\s*0\.5rem/);
  });

  it("gives the first part of a turn no leading margin", () => {
    // A reply that opens with a picture would otherwise start indented from its
    // own row by a margin meant to separate it from a sibling it does not have.
    expect(CSS).toMatch(
      /\.chat-tool:first-child,\s*\.chat-block:first-child\s*\{[^}]*margin-block-start:\s*0\b/,
    );
  });

  it("keeps the rhythm in ONE file, so the two selectors cannot disagree", () => {
    // `tool.css` owned the tool half before block-level parts existed. Two
    // files agreeing today is two files to edit tomorrow, and the failure is
    // silent — which is why `block.css` is the only place the rhythm lives,
    // whatever set of block renderers the package happens to ship.
    const tool = readFileSync(join(STYLES, "tool.css"), "utf8");
    expect(tool).not.toMatch(/\.chat-tool[^{]*\{[^}]*margin-block-start/);
    const block = readFileSync(join(STYLES, "block.css"), "utf8");
    expect(block).toMatch(/\.chat-tool,\s*\.chat-block\s*\{[^}]*margin-block-start/);
  });
});
