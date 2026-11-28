import { describe, expect, it } from "vitest";

import { expireAll, isPending, propose, settle } from "./proposal";

const fill = { kind: "fill", ref: "@e4", value: "a@b.c" } as const;

describe("proposal", () => {
  it("starts pending", () => {
    expect(isPending(propose("p1", fill, "the Email field"))).toBe(true);
  });

  it("records the outcome it settled with", () => {
    const settled = settle(propose("p1", fill, "Email"), "rejected");
    expect(settled.state).toEqual({ status: "settled", outcome: "rejected" });
    expect(isPending(settled)).toBe(false);
  });

  /**
   * A double click on Approve must not run the action twice, and a sweep that
   * expires open proposals must not overwrite an answer the user just gave.
   */
  it("ignores a second answer", () => {
    const once = settle(propose("p1", fill, "Email"), "approved");
    expect(settle(once, "rejected")).toBe(once);
    expect(settle(once, "expired").state).toEqual({
      status: "settled",
      outcome: "approved",
    });
  });

  it("expires everything still open, and leaves settled ones alone", () => {
    const open = propose("p1", fill, "Email");
    const answered = settle(propose("p2", fill, "Name"), "rejected");

    const [first, second] = expireAll([open, answered]);

    expect(first?.state).toEqual({ status: "settled", outcome: "expired" });
    expect(second).toBe(answered);
  });
});
