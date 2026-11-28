import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";
import { Streamdown } from "streamdown";

/**
 * Why `streamdown` was adopted, asserted rather than assumed.
 *
 * The package is taken for exactly one property — it parses HALF-ARRIVED
 * markdown without splitting the string into blocks — and our own splitter's
 * two measured defects both follow from splitting. A dependency justified by a
 * property nobody checked is a dependency justified by its README, so each
 * claim below is a test that would fail if we swapped it back.
 *
 * These render to STATIC MARKUP, not through a DOM: the questions here are
 * "what did the parser decide" and "did it throw", neither of which needs a
 * renderer, and this keeps the suite in milliseconds.
 */

const render = (markdown: string) => renderToStaticMarkup(<Streamdown>{markdown}</Streamdown>);

describe("the two defects our splitter had", () => {
  it("keeps a loose ordered list in ONE list, so the second item is not '1.'", () => {
    // THE DEFECT: splitBlocks("1. first\n\n2. second") produced two blocks and
    // therefore two independent <ol>, so the second item restarted at 1. Wrong
    // numbers are a lie about the answer, not a cosmetic slip.
    const html = render("1. first\n\n2. second");

    expect(html.match(/<ol/g) ?? []).toHaveLength(1);
    expect(html).toContain("first");
    expect(html).toContain("second");
  });

  it("resolves a reference definition with default splitting and with splitting disabled", () => {
    // streamdown < 2.7 split on blank lines, so its own
    // `parseMarkdownIntoBlocks("see [docs][1]\n\n[1]: …")` returned three pieces
    // and lost the definition exactly the way our splitter did. 2.7 resolves it
    // out of the box; this pins both paths so a regression shows up here.
    // `parseMarkdownIntoBlocksFn: (s) => [s]` (one block, one parse) stays the
    // supported escape if the default ever splits again.
    const SRC = "see [the docs][1]\n\n[1]: https://example.com/x\n";

    const byDefault = render(SRC);
    expect(byDefault).toContain('data-streamdown="link"');
    expect(byDefault).not.toContain("[1]");

    const whole = renderToStaticMarkup(
      <Streamdown parseMarkdownIntoBlocksFn={(source: string) => [source]}>{SRC}</Streamdown>,
    );
    expect(whole).toContain('data-streamdown="link"');
    expect(whole).not.toContain("[1]");
  });

  it("renders links as a safety-gated button rather than a bare href", () => {
    // NOT a defect, and worth pinning because it looks like one: streamdown's
    // linkSafety renders `<button data-streamdown="link">` and confirms the
    // destination on click, instead of emitting `<a href>` straight into a
    // transcript full of model-authored URLs. A test asserting `href="…"` fails
    // here and reads as "links are broken". The control that separates the two
    // is checking whether a plain INLINE link works: if it does not either, the
    // cause is not reference-resolution.
    const html = render("see [docs](https://example.com/x)");

    expect(html).toContain('data-streamdown="link"');
    expect(html).not.toContain("<a href");
  });
});

describe("half-arrived input does not throw", () => {
  // Each of these is a real mid-stream state: the model has emitted a prefix and
  // the next token has not arrived. A renderer that throws here takes the whole
  // transcript row down, which is the failure this dependency exists to prevent.
  const partials = [
    ["an unterminated code fence", "```ts\nconst x = 1;"],
    ["an unterminated inline code span", "call `foo("],
    ["an unterminated bold run", "this is **important"],
    ["a half-written link", "see [the docs]("],
    ["a table with no body yet", "| a | b |\n|---|"],
    ["an unterminated inline formula", "complexity is $O(n \\log"],
    ["an unterminated block formula", "$$\n\\sum_{i=0}^{n}"],
    ["a lone backslash at the end", "a \\"],
    ["a half-written heading", "#"],
  ] as const;

  for (const [name, markdown] of partials) {
    it(`survives ${name}`, () => {
      expect(() => render(markdown)).not.toThrow();
    });
  }

  it("does not leak an unterminated formula's delimiter as typeset math", () => {
    // The honest behaviour while `$…$` is still open is LITERAL TEXT. Typesetting
    // a half-arrived formula would render a different expression than the one the
    // model is writing, and it would change under the user as tokens land.
    const html = render("complexity is $O(n \\log");

    expect(html).not.toContain("katex");
  });
});

describe("the control", () => {
  it("actually renders content, so the assertions above cannot pass on an empty string", () => {
    // Every test here asserts about `html`. If Streamdown returned "" for all
    // input, `not.toThrow()` and `not.toContain()` would all pass while checking
    // nothing — a green suite measuring a renderer that renders nothing.
    const html = render("# Title\n\nA paragraph with **bold** text.\n");

    expect(html).toContain("Title");
    // `data-streamdown`, not a tag name: emphasis renders as
    // `<span class="font-semibold">`, so asserting `<strong>` tests our
    // assumption about someone else's markup rather than testing the parser.
    expect(html).toContain('data-streamdown="strong"');
    expect(html).toContain("<h1");
    expect(html.length).toBeGreaterThan(40);
  });
});
