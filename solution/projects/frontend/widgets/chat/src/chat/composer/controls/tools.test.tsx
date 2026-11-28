import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import type { ChatCapabilities } from "../../core";
import { ChatProvider } from "../../store";
import { mockAdapter, MOCK_TOOL_CATALOGUE } from "../../testing";
import { ComposerTools } from "./tools";

/**
 * The claims the `+` control is load-bearing for: an absent capability draws
 * nothing, and a pick never sends.
 */

const render = (capabilities?: ChatCapabilities) =>
  renderToStaticMarkup(
    <ChatProvider adapter={mockAdapter({ script: [] })} capabilities={capabilities}>
      <ComposerTools>+</ComposerTools>
    </ChatProvider>,
  );

describe("the + control", () => {
  /** Absent-not-stubbed: a disabled `+` is a promise the product cannot keep.
   *  MUTANT: render the button unconditionally → this dies. */
  it("draws nothing without a tools capability", () => {
    expect(render()).toBe("");
  });

  it("draws a collapsed trigger once the capability arrives", () => {
    const html = render({ tools: { entries: MOCK_TOOL_CATALOGUE } });

    expect(html).toContain("<button");
    // A trigger with no `aria-expanded` gives a screen reader no way to know
    // it opens a dialog.
    expect(html).toContain('aria-expanded="false"');
    expect(html).toContain('aria-haspopup="dialog"');
  });

  /** An empty catalogue still gets a trigger — the sheet says it is empty. */
  it("draws the trigger for a capability with no entries", () => {
    const html = render({ tools: { entries: [] } });
    expect(html).toContain("<button");
  });

  /**
   * Three states, not two.
   *
   * "No capability" and "the server has not answered yet" used to render the
   * same: the trigger vanished until the reply landed, so the same room showed
   * it or not depending on whether a 60s cache was warm. Disabling here is not
   * the promise the absent case refuses to make — the tools are coming.
   *
   * MUTANT: drop `loading` from the pending test → the trigger renders enabled
   * and this dies.
   */
  it("holds the trigger's place, disabled, while the server is still answering", () => {
    const html = render({ tools: { entries: [], loading: true } });

    expect(html).toContain("<button");
    // The rendered ATTRIBUTE, not the word: `disabled:opacity-40` sits in the
    // class list either way, so a bare substring passes on an enabled button.
    expect(html).toContain('disabled=""');
    expect(html).toContain('aria-busy="true"');
  });

  /** Once the answer lands the control is live, not merely present. */
  it("enables the trigger as soon as entries arrive", () => {
    const html = render({ tools: { entries: MOCK_TOOL_CATALOGUE, loading: true } });

    expect(html).not.toContain('disabled=""');
    expect(html).not.toContain("aria-busy");
  });

  /** Loading is a state of the CAPABILITY, never a way to conjure one. */
  it("still draws nothing when there is no capability at all", () => {
    expect(render()).toBe("");
  });
});

/**
 * A pick STAGES the tool and stops. It must reach no send door: sending
 * immediately would leave no room to add a file or edit the wording.
 *
 * The control stages through `useComposer`, whose api also carries `send` and
 * `canSend` — so the gate names the send members rather than the hook, which is
 * what it can honestly assert without a DOM to click in.
 */
describe("picking", () => {
  it("never sends: the control touches no send member", async () => {
    const source = await import("node:fs").then((fs) =>
      fs.readFileSync(new URL("./tools.tsx", import.meta.url), "utf8"),
    );

    // The control: a moved file reads empty and every assertion below would
    // then pass while measuring nothing.
    expect(source).toContain("ComposerTools");
    // It must still STAGE, or a pick lands in silence.
    expect(source).toContain("toggleTool");
    // MUTANT: destructure `send` from useComposer and call it → these die.
    expect(source).not.toMatch(/\bsend\(/);
    expect(source).not.toMatch(/\bcanSend\b/);
    expect(source).not.toContain("useChatStore");
  });
});
