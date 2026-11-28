import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

/**
 * The key-handling protocol, ratcheted in the source.
 *
 * This package has no jsdom, so the alternative to reading the source is not a
 * better test — it is no test. What is guarded is one ORDER and one EARLY
 * RETURN, and both are invisible to types and to static markup:
 *
 *   the host's handler runs FIRST, and a `preventDefault()` from it stops
 *   Enter-to-send.
 *
 * Getting either wrong is silent. Call the host second and Enter sends the turn
 * before the claimant can act on it; drop the `defaultPrevented` check and it
 * sends the turn as WELL. Both look like a working composer until a key the
 * host wanted goes to the wrong place.
 *
 * Comments are stripped first, because every phrase below also appears in the
 * prose above the code — a ratchet satisfied by its own documentation would
 * pass on a file with the implementation deleted. The stripper has a control
 * test, since a broken stripper fails open.
 */

const SOURCE = readFileSync(new URL("./input.tsx", import.meta.url), "utf8");
const CODE = SOURCE.replace(/\/\*[\s\S]*?\*\//g, "").replace(/\/\/.*$/gm, "");

describe("comment stripper (control)", () => {
  it("removes comments but keeps code", () => {
    const stripped = "/* a */ const x = 1; // b\nconst y = 2;"
      .replace(/\/\*[\s\S]*?\*\//g, "")
      .replace(/\/\/.*$/gm, "");
    expect(stripped).toContain("const x = 1;");
    expect(stripped).toContain("const y = 2;");
    expect(stripped).not.toContain("a");
    expect(stripped).not.toContain("b");
  });

  it("leaves real code in input.tsx after stripping", () => {
    expect(CODE).toContain("hostKeyDown");
  });
});

describe("the host owns a key before this component does", () => {
  it("accepts a host handler", () => {
    expect(CODE).toContain("onKeyDown: hostKeyDown");
  });

  it("calls the host BEFORE its own Enter handling", () => {
    const handler = CODE.slice(CODE.indexOf("const onKeyDown"));
    const host = handler.indexOf("hostKeyDown?.(event)");
    const enter = handler.indexOf('event.key !== "Enter"');
    expect(host).toBeGreaterThan(-1);
    expect(enter).toBeGreaterThan(-1);
    expect(host).toBeLessThan(enter);
  });

  it("abandons its own handling once the host prevented default", () => {
    const handler = CODE.slice(CODE.indexOf("const onKeyDown"));
    const veto = handler.indexOf("if (event.defaultPrevented) return;");
    const enter = handler.indexOf('event.key !== "Enter"');
    expect(veto).toBeGreaterThan(-1);
    expect(veto).toBeLessThan(enter);
  });

  it("re-runs the handler when the host's changes", () => {
    // A stale closure would call the FIRST render's handler forever, so a menu
    // that opened later could never claim Enter.
    //
    // Asserted as MEMBERSHIP, not as the exact literal: the array may
    // legitimately grow, and pinning the whole string makes every such addition
    // look like a regression while catching nothing a membership check misses.
    expect(CODE).toMatch(/\[canSend, send, hostKeyDown[,\]]/);
  });
});

describe("the seam stays narrow", () => {
  /**
   * `onKeyDown` is a named prop, and the only escape hatch. A spread would let a
   * host re-bind `onChange`, `value` or `onPaste` and take over state this
   * component owns — the door the 83-prop predecessor left open.
   */
  it("never spreads arbitrary props onto the textarea", () => {
    const element = CODE.slice(CODE.indexOf("<textarea"));
    expect(element).not.toContain("{...props}");
    expect(element).not.toContain("{...rest}");
  });

  it("keeps the composition guard, which Enter-to-send depends on", () => {
    // An IME confirms a candidate with Enter and that Enter reaches keydown.
    expect(CODE).toContain("composing.current || event.nativeEvent.isComposing");
  });
});
