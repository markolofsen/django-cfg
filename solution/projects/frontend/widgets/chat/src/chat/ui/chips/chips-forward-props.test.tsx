import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { LinkChip } from "./link-chip";

/**
 * An inline chip must forward unknown props to its element.
 *
 * A hover card, a tooltip and a context menu all attach themselves by CLONING
 * their child with extra props (`asChild` in Radix terms). A chip that
 * destructures only the props it knows drops those silently: the chip renders
 * perfectly, the wrapper mounts, and the card simply never opens — with
 * nothing in the DOM to show why. That is exactly how the link chip shipped,
 * and it cost a browser session to find.
 *
 * Asserted on the MARKUP rather than through a real trigger: the failure is
 * "the attribute never reached the element", which is visible without a DOM
 * and without pulling Radix into this package's tests.
 */
describe("inline chips forward props", () => {
  it("puts a wrapper's data attributes on the link chip's anchor", () => {
    const html = renderToStaticMarkup(
      <LinkChip href="https://example.com/x" data-state="closed" aria-expanded={false} />,
    );
    expect(html).toContain('data-state="closed"');
    expect(html).toContain('aria-expanded="false"');
  });

  it("does not let a caller override the link chip's hardened target and rel", () => {
    // The spread is FIRST for this reason: `rel` is what stops the opened page
    // reaching back through `window.opener`, and a caller must not be able to
    // drop it by passing one of its own.
    const html = renderToStaticMarkup(
      <LinkChip href="https://example.com/x" target="_self" rel="opener" />,
    );
    expect(html).toContain('target="_blank"');
    expect(html).toContain('rel="noreferrer noopener"');
  });
});
