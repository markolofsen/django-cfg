import type { KeyboardEvent } from "react";
import { describe, expect, it, vi } from "vitest";

import { composerKeyDown, type ComposerKeysOptions } from "./keys";

/**
 * The resolver is a pure function over a key event, so it is testable directly
 * — no DOM, no source ratchet. What it decides is one piece of ordering, and it
 * fails silently.
 */

/** A key event with only the fields the resolver reads. */
function keyEvent(key: string, shiftKey = false): KeyboardEvent<HTMLTextAreaElement> {
  return { key, shiftKey, preventDefault: vi.fn() } as unknown as KeyboardEvent<HTMLTextAreaElement>;
}

function options(overrides: Partial<ComposerKeysOptions> = {}): ComposerKeysOptions {
  return {
    recall: { reset: vi.fn(), onKeyDown: vi.fn() },
    draftText: "deploy the thing",
    ...overrides,
  };
}

describe("Enter announces the send", () => {
  it("announces before resetting recall", () => {
    // The ORDER is the assertion. `recall.reset()` drops the ladder walk, and a
    // listener that grows the ladder must have been told first — reversed, an
    // immediate ArrowUp misses the prompt that just went out.
    const order: string[] = [];
    const opts = options({
      onSending: () => order.push("sending"),
      recall: { reset: () => order.push("reset"), onKeyDown: vi.fn() },
    });

    composerKeyDown(keyEvent("Enter"), opts);

    expect(order).toEqual(["sending", "reset"]);
  });

  it("says nothing for Shift+Enter, which inserts a newline", () => {
    const onSending = vi.fn();
    composerKeyDown(keyEvent("Enter", true), options({ onSending }));
    expect(onSending).not.toHaveBeenCalled();
  });

  it("says nothing for a blank draft, which does not send", () => {
    const onSending = vi.fn();
    composerKeyDown(keyEvent("Enter"), options({ draftText: "   ", onSending }));
    expect(onSending).not.toHaveBeenCalled();
  });

  it("still sends when nobody is listening", () => {
    // `onSending` is optional: the package must work with no host subscribed.
    const opts = options({ onSending: undefined });
    expect(() => composerKeyDown(keyEvent("Enter"), opts)).not.toThrow();
    expect(opts.recall.reset).toHaveBeenCalledOnce();
  });
});
