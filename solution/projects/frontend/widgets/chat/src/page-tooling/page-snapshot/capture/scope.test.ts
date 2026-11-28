// @vitest-environment jsdom
import { afterEach, describe, expect, it } from "vitest";

import { resolveScope } from "./scope";

afterEach(() => {
  document.body.innerHTML = "";
});

/**
 * jsdom does not lay out elements, so geometry-based tiers (3 dialog
 * sizing, heuristic scoring) can only be smoke-tested. These tests
 * cover the structural tier selection — which is the part that matters
 * for ladder ordering.
 */
describe("resolveScope — tier ladder", () => {
  it("honors an explicit target selector first", () => {
    document.body.innerHTML = `<main id="m">content</main><div id="t">x</div>`;
    const scope = resolveScope({ strategy: "container", targetSelector: "#t" });
    expect(scope.tier).toBe("explicit-selector");
    expect(scope.roots[0]?.id).toBe("t");
  });

  it("'full' strategy forces body", () => {
    document.body.innerHTML = `<main>content</main>`;
    const scope = resolveScope({ strategy: "full" });
    expect(scope.tier).toBe("tier4-body");
    expect(scope.roots[0]).toBe(document.body);
  });

  it("Tier 1 — picks [data-ai-context] over <main>", () => {
    document.body.innerHTML = `
      <main>main content</main>
      <div data-ai-context>annotated region</div>
    `;
    const scope = resolveScope({ strategy: "container" });
    expect(scope.tier).toBe("tier1-annotation");
    expect(scope.roots[0]?.dataset.aiContext).toBe("");
  });

  it('Tier 1 — ignores data-ai-context="exclude"', () => {
    document.body.innerHTML = `
      <main>main content</main>
      <div data-ai-context="exclude">excluded</div>
    `;
    const scope = resolveScope({ strategy: "container" });
    // Annotation tier yields nothing usable → falls to <main>.
    expect(scope.tier).toBe("tier2-main");
  });

  it("Tier 2 — picks <main> when no annotation", () => {
    document.body.innerHTML = `
      <nav>navigation</nav>
      <main id="m">main content here</main>
    `;
    const scope = resolveScope({ strategy: "container" });
    expect(scope.tier).toBe("tier2-main");
    expect(scope.roots[0]?.id).toBe("m");
  });

  it('Tier 2 — role="main" also counts', () => {
    document.body.innerHTML = `<div role="main" id="m">content</div>`;
    const scope = resolveScope({ strategy: "container" });
    expect(scope.tier).toBe("tier2-main");
    expect(scope.roots[0]?.id).toBe("m");
  });

  /**
   * jsdom reports zero geometry, so Tier 3 is unreachable without stubbing
   * layout. It is stubbed here rather than skipped, because this is the tier
   * that picks the wrong root in a real browser.
   */
  describe("Tier 3 — heuristic", () => {
    /** Give every element the viewport's size, so area cannot break the tie. */
    function stubFullViewportLayout() {
      const rect = {
        width: 1000,
        height: 800,
        top: 0,
        left: 0,
        right: 1000,
        bottom: 800,
        x: 0,
        y: 0,
        toJSON: () => ({}),
      };
      Object.defineProperty(document.documentElement, "clientWidth", {
        value: 1000,
        configurable: true,
      });
      Object.defineProperty(document.documentElement, "clientHeight", {
        value: 800,
        configurable: true,
      });
      Element.prototype.getBoundingClientRect = function (): DOMRect {
        return rect as DOMRect;
      };
    }

    /**
     * An empty full-viewport overlay must NOT win.
     *
     * A toast layer, a portal root or an injected glow border covers the page
     * and holds nothing. Ranked on area alone it outscores the content it
     * covers, the walk then visits one node, and the snapshot comes back with
     * no children — no error anywhere, the assistant simply told the page is
     * empty.
     */
    it("skips a full-viewport block with no content", () => {
      stubFullViewportLayout();
      document.body.innerHTML = `
        <div id="overlay"></div>
        <div id="content"><button>Save</button><p>hello</p></div>
      `;
      const scope = resolveScope({ strategy: "container" });
      expect(scope.roots[0]?.id).toBe("content");
    });

    it("picks a block that has content over one that has none", () => {
      stubFullViewportLayout();
      document.body.innerHTML = `
        <div id="content"><input /></div>
        <div id="empty"></div>
      `;
      const scope = resolveScope({ strategy: "container" });
      expect(scope.roots[0]?.id).toBe("content");
    });
  });

  it("Tier 4 — falls back to body when nothing else matches", () => {
    // No main, no annotation, no sized blocks (jsdom = zero geometry).
    document.body.innerHTML = `<span>just text</span>`;
    const scope = resolveScope({ strategy: "container" });
    expect(scope.tier).toBe("tier4-body");
  });
});
