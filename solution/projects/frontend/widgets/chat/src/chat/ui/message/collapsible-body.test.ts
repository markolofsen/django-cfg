import { describe, expect, it } from "vitest";
import { readFile } from "node:fs/promises";

import { carriesWidget, collapseState } from "./collapsible-body";

/**
 * The clamp/trigger policy.
 *
 * The DOM half — whether an element actually overflows — is a browser check:
 * this package's tests run without a DOM, and jsdom would report `scrollHeight`
 * as zero for every element, which is a green that measures nothing. What is
 * covered here is every way the DECISION can be silently wrong once that
 * boolean is known.
 */
describe("collapseState", () => {
  it("clamps a long turn and offers the control", () => {
    expect(collapseState(false, false, true)).toEqual({ clamped: true, showTrigger: true });
  });

  it("offers no control when the turn fits", () => {
    // The deception this prevents: a "show more" under a short message promises
    // a disclosure that would reveal nothing.
    expect(collapseState(false, false, false).showTrigger).toBe(false);
  });

  it("lifts the clamp once the reader opens it, and keeps the way back", () => {
    expect(collapseState(false, true, true)).toEqual({ clamped: false, showTrigger: true });
  });

  it("never clamps a turn that is still arriving", () => {
    // Both halves matter: a streaming reply must not fold, AND it must not show
    // a control that appears and disappears as the answer grows.
    expect(collapseState(true, false, true)).toEqual({ clamped: false, showTrigger: false });
  });

  it("does not re-clamp an expanded turn when it starts streaming again", () => {
    expect(collapseState(true, true, true).clamped).toBe(false);
  });

  /**
   * Position now reaches this decision, and the earlier claim that it never
   * could was wrong about the transcript rather than about the risk.
   *
   * A row IS handed only its id — but it can ask the store which id is last, so
   * the rule needed no new plumbing. What the original note got right is the
   * hazard: a live positional read folds the answer someone is mid-way through.
   * That is answered by freezing the flag at mount (`useCollapse`), not by
   * keeping the parameter out.
   *
   * The three REQUIRED parameters still describe the message alone, so the
   * arity check keeps its original meaning: eligibility is opt-out, and a
   * caller that knows nothing about position gets the message-only rule.
   */
  it("takes only message facts as required arguments", () => {
    expect(collapseState.length).toBe(3);
  });
});

// The newest turn is left open, and the rule is POSITIONAL — which is exactly
// the shape this feature's plan warned about. What makes it safe is that
// `useCollapse` reads `collapsible` through `useState`'s initialiser, so the
// answer is frozen at mount.
//
// This asserts the SOURCE, because the property is about a hook's call shape
// and this package renders with no DOM: a behavioural test would need to mount,
// push a message, and re-render, which is a browser check. Naming the mechanism
// here is what stops a later edit from "simplifying" the freeze away.
describe("the newest-turn rule cannot fold a turn retroactively", () => {
  it("reads `collapsible` through a state initialiser, never live", async () => {
    const src = await readFile(
      new URL("./collapsible-body.tsx", import.meta.url),
      "utf8",
    );
    // Control: the hook is still here, so a miss below is a real change rather
    // than a renamed file this test silently stopped covering.
    expect(src).toContain("export function useCollapse");
    expect(src).toContain("const [mayCollapse] = useState(collapsible)");
  });

  it("decides eligibility by last id, in the row that owns the state", async () => {
    const src = await readFile(new URL("./collapsible-row.tsx", import.meta.url), "utf8");
    expect(src).toContain("function useMayCollapse");
    expect(src).toContain("ids[ids.length - 1] !== id");
  });
});

// An ineligible turn is shown WHOLE and offers nothing, however tall.
//
// The parameter is fourth and defaulted, so every existing caller keeps its
// meaning; this pins the one case that default hides.
describe("collapseState, when the turn may not collapse", () => {
  it("neither clamps nor offers a control, even when it overflows", () => {
    expect(collapseState(false, false, true, false)).toEqual({
      clamped: false,
      showTrigger: false,
    });
  });

  it("outranks the expanded flag too, so nothing can re-enable it", () => {
    expect(collapseState(false, true, true, false).showTrigger).toBe(false);
  });

  // Control: the SAME inputs with the turn eligible do produce a clamp, so the
  // assertions above are about the flag rather than about the other arguments.
  it("is the flag that decides — the same inputs collapse when eligible", () => {
    expect(collapseState(false, false, true, true)).toEqual({
      clamped: true,
      showTrigger: true,
    });
  });
});

describe("carriesWidget: media is never folded under 'Show more'", () => {
  const attachment = (kind: string) => ({ type: "attachment", attachment: { id: "a", name: "x", kind, mime: "x/y", size: 1, url: "/x" } });
  const message = (...parts: unknown[]) => ({ id: "m", parts }) as never;

  it("a picture or a video keeps the turn open", () => {
    expect(carriesWidget(message({ type: "text", text: "what is this?" }, attachment("image")))).toBe(true);
    expect(carriesWidget(message(attachment("video")))).toBe(true);
  });

  it("a plain file or text alone may still fold", () => {
    expect(carriesWidget(message({ type: "text", text: "long" }, attachment("document")))).toBe(false);
  });
});
