import { describe, expect, it } from "vitest";

import { failureFromElement, failureFromPlayRejection } from "./media-failure";

/** A `MediaError` stand-in: the browser type is not constructible in a test. */
function mediaError(code: number): MediaError {
  return { code, message: "" } as MediaError;
}

describe("failureFromElement", () => {
  /**
   * The decisive case. Code 1 is `MEDIA_ERR_ABORTED`, which fires on every
   * `src` change — and this player changes `src` on every track switch. If it
   * produced a failure, picking a new track would show an error every time.
   */
  it("says nothing about an abort", () => {
    expect(failureFromElement(mediaError(1))).toBeNull();
  });

  /**
   * The spec allows an `error` event whose `media.error` is null. Reading a
   * code off it would throw inside an event listener.
   */
  it("says nothing when the element reports no error object", () => {
    expect(failureFromElement(null)).toBeNull();
  });

  it("reads a network failure as the machine going away, and names it", () => {
    expect(failureFromElement(mediaError(2), "mac-studio")).toEqual({
      reason: "machine-unreachable",
      machineId: "mac-studio",
    });
  });

  /**
   * Without a machine the cause is still the same cause — the field is optional
   * precisely so an unnamed one does not become a different, vaguer reason.
   */
  it("omits the machine rather than inventing one", () => {
    expect(failureFromElement(mediaError(2))).toEqual({ reason: "machine-unreachable" });
  });

  it("reads a decode failure as a refusal", () => {
    expect(failureFromElement(mediaError(3))).toEqual({ reason: "refused" });
  });

  it("reads an unsupported source as a refusal", () => {
    expect(failureFromElement(mediaError(4))).toEqual({ reason: "refused" });
  });

  /**
   * Codes beyond the spec's 1-4 exist in the wild. An unknown one must still
   * name a cause; falling through to null would be silence with no explanation,
   * which is the failure this vocabulary exists to remove.
   */
  it("still names a cause for a code outside the spec", () => {
    expect(failureFromElement(mediaError(5))).toEqual({ reason: "unknown" });
  });
});

describe("failureFromPlayRejection", () => {
  /**
   * An autoplay refusal is not a fault: the file is fine and one click fixes
   * it. It gets its own member so the surface can ask rather than apologise.
   */
  it("reads an autoplay refusal as blocked", () => {
    const refusal = new Error("gesture required");
    refusal.name = "NotAllowedError";
    expect(failureFromPlayRejection(refusal)).toEqual({ reason: "blocked" });
  });

  it("reads any other rejection as unknown", () => {
    const other = new Error("boom");
    other.name = "NotSupportedError";
    expect(failureFromPlayRejection(other)).toEqual({ reason: "unknown" });
  });

  it("survives a rejection that is not an Error at all", () => {
    expect(failureFromPlayRejection("nope")).toEqual({ reason: "unknown" });
  });
});
