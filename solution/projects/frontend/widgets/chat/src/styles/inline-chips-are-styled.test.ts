import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

/**
 * The inline chips take their appearance from a class the stylesheet owns, and
 * nothing else can see that the two agree.
 *
 * A component naming a class no rule defines type-checks, lints and tests
 * clean — it renders unstyled. The link chip takes `.chat-chip` for the shared
 * rules (em sizing, inherited colour, the baseline donor) and adds
 * `.chat-link-chip` for its own, so a rename that touches one side is exactly
 * the failure this catches.
 */

// Paths inside the entry are relative to IT, not to this test.
const STYLES = import.meta.dirname;
const ENTRY = readFileSync(join(STYLES, "index.css"), "utf8");
const CSS = [...ENTRY.matchAll(/@import "\.\/([^"]+)"/g)]
  .map(([, path]) => readFileSync(join(STYLES, path ?? ""), "utf8"))
  .join("\n");

/** A chip component's source. `readFileSync` throws if the file moved. */
function sourceOf(file: string): string {
  return readFileSync(join(import.meta.dirname, "..", "chat", "ui", "chips", file), "utf8");
}

/**
 * Every rule body this selector owns, joined.
 *
 * All of them, not the first: a chip class is declared in more than one place
 * on purpose — a shape rule where the ceiling lives, and a colour rule further
 * down where `data-role` decides the side. Taking `indexOf` alone reads
 * whichever comes first and reports the other as missing.
 *
 * Scoped to the selector at all because searching the whole sheet for
 * `max-width` cannot tell the file chip's ceiling from the link chip's, and
 * would pass on a sheet where one of them lost its rule entirely.
 */
function ruleFor(selector: string): string {
  const bodies: string[] = [];
  for (let at = CSS.indexOf(`${selector} {`); at >= 0; at = CSS.indexOf(`${selector} {`, at + 1)) {
    bodies.push(CSS.slice(at, CSS.indexOf("}", at)));
  }
  expect(bodies, selector).not.toHaveLength(0);
  return bodies.join("\n");
}

describe("inline chips", () => {
  it("reads a stylesheet that is actually there", () => {
    // Every substring assertion below passes over an empty string, so an import
    // list that resolved to nothing would turn the rest of this file green.
    expect(CSS.length).toBeGreaterThan(2000);
  });

  it("defines the shared chip rule", () => {
    expect(CSS).toContain(".chat-surface .chat-chip {");
    expect(CSS).toContain(".chat-surface .chat-chip > svg {");
    expect(CSS).toContain(".chat-surface .chat-chip:where(:hover) {");
  });

  it("gives the chip the shared class plus its own", () => {
    expect(sourceOf("link-chip.tsx")).toContain("chat-chip chat-link-chip");
  });

  it("defines a rule for every chip class the components name", () => {
    expect(CSS).toContain(".chat-surface .chat-link-chip {");
  });

  it("styles the anchor a host's link override would otherwise leave bare", () => {
    // `.chat-link` is applied by the host, which opts out of the renderer's
    // default anchor the moment it overrides `components.a`.
    const rule = CSS.slice(CSS.indexOf(".chat-surface .chat-link {"));
    expect(rule.slice(0, rule.indexOf("}"))).toContain("text-decoration: underline");
  });

  it("reads the bubble side from the DOM, not from a prop", () => {
    // `components` is memoized once per screen, so no per-message value can
    // reach these chips. The stylesheet keys off the wrapper's `data-role`
    // instead; a chip carrying `text-primary` again would silently win over it
    // inside a user bubble.
    expect(CSS).toContain('[data-role="user"]');
    expect(sourceOf("link-chip.tsx")).not.toContain("text-primary");
    expect(sourceOf("link-chip.tsx")).not.toContain("isUser");
  });

  it("sizes a host-supplied glyph, which arrives as a span not an svg", () => {
    // The `> svg` rule cannot reach it: the typed icon set wraps its SVG in a
    // span carrying an INLINE pixel size, so without this rule the glyph keeps
    // a fixed 16px while the surface's type moves, and donates the baseline the
    // label owns. `!important` is what beats the inline style.
    const selector = '.chat-surface .chat-chip > span:where([aria-hidden="true"], [role="img"])';
    expect(CSS).toContain(`${selector} {`);
    const rule = CSS.slice(CSS.indexOf(`${selector} {`));
    const body = rule.slice(0, rule.indexOf("}"));
    expect(body).toContain("align-self: center");
    expect(body).toContain("width: 1em !important");
  });


  it("keeps the width ceiling in the sheet, not in a class list", () => {
    // One owner per element: a `max-w-[…]` utility beside a `max-width` rule is
    // two places to look and two places to forget. The VALUE is the sheet's to
    // tune; what this asserts is that the chip has exactly one ceiling and that
    // it lives here.
    expect(sourceOf("link-chip.tsx")).not.toContain("max-w-[");
    expect(ruleFor(".chat-surface .chat-link-chip")).toMatch(/max-width:\s*\d+(\.\d+)?rem/);
  });
});
