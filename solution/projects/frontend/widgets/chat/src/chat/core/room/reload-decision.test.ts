import { describe, expect, it } from "vitest";

import { reloadDecision } from "./reload-decision";

const at = (over: Partial<Parameters<typeof reloadDecision>[0]> = {}) =>
  reloadDecision({ revision: 1, seen: 1, streaming: false, deferred: false, ...over });

describe("reloadDecision", () => {
  it("does nothing while the room has not moved", () => {
    // The mount case. A room that just read its history must not read it again
    // because its opening revision is non-zero.
    expect(at()).toBe("ignore");
    expect(at({ revision: 7, seen: 7 })).toBe("ignore");
  });

  it("reloads once the room moved and nothing is streaming", () => {
    expect(at({ revision: 2, seen: 1 })).toBe("reload");
  });

  it("never reloads over a live stream", () => {
    // MUTANT: drop the streaming branch → this dies. Seeding replaces the
    // transcript wholesale and clears the streaming id, so a reload here
    // deletes the reply while it is being written.
    expect(at({ revision: 2, seen: 1, streaming: true })).toBe("defer");
  });

  it("serves the deferred change when the stream ends", () => {
    // MUTANT: return "ignore" for a settled deferral → this dies. A message
    // that arrived mid-turn would stay invisible until the room is reopened —
    // the original defect through a narrower window.
    expect(at({ deferred: true })).toBe("reload");
  });

  it("keeps deferring while the stream continues", () => {
    // The deferral must survive renders that do not change the revision, or a
    // re-render mid-stream would forget the owed reload.
    expect(at({ streaming: true, deferred: true })).toBe("defer");
  });

  it("stays quiet mid-stream when there is nothing owed", () => {
    // Streaming is not itself a reason to reload later; only a change is.
    expect(at({ streaming: true })).toBe("ignore");
  });
});
