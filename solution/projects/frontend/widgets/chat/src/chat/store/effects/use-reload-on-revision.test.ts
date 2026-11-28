import { readFileSync } from "node:fs";
import { join } from "node:path";
import { describe, expect, it } from "vitest";

import { reloadDecision } from "../../core/room/reload-decision";

/**
 * The room-change re-seed inside `useReloadOnRevision`.
 *
 * The rule itself (`reload-decision.ts`) is pure and tested next to itself. What
 * cannot be tested there is the hook's REFS, and one of them decides whether the
 * rule is asked a meaningful question at all: `seen` holds a revision, revisions
 * are per-room counters, and comparing one room's against another's is not a
 * comparison.
 *
 * Source and not behaviour for the reason `provider.test.ts` states — no jsdom
 * resolves in this package. The first assertion below is real behaviour though:
 * it drives the actual rule with the values a room switch produces, so the cost
 * of getting this wrong is demonstrated rather than described.
 */

const SOURCE = readFileSync(join(__dirname, "use-reload-on-revision.ts"), "utf8");

describe("why the re-seed exists", () => {
  it("would fire a redundant reload on a switch out of a busy room", () => {
    // Left a room that had received hints (revision 3); the new room has no
    // entry in the store, so it reads 0. Without the re-seed these are compared
    // and the difference reads as "the room moved".
    expect(
      reloadDecision({ revision: 0, seen: 3, streaming: false, deferred: false }),
    ).toBe("reload");
    // The re-seed makes the comparison meaningful: `seen` becomes the new room's
    // own opening revision, which is not a change.
    expect(
      reloadDecision({ revision: 0, seen: 0, streaming: false, deferred: false }),
    ).toBe("ignore");
  });
});

describe("the hook re-seeds on a room change", () => {
  it("tracks which room `seen` describes", () => {
    // MUTANT: delete the `seenRoom` block → this dies, and every switch out of a
    // room that received a WS hint re-fetches the history the new room just read.
    expect(
      SOURCE,
      "no room guard: revisions from two different rooms get compared",
    ).toContain("seenRoom.current !== room");
    const guard = SOURCE.slice(
      SOURCE.indexOf("seenRoom.current !== room"),
      SOURCE.indexOf("useEffect(("),
    );
    expect(guard.length).toBeGreaterThan(0);
    // Re-seeding `seen` is the point; without it the guard is bookkeeping only.
    expect(guard).toContain("seen.current = revision");
  });

  it("also clears a deferred change, which belonged to the room being left", () => {
    // A change deferred mid-stream in room A must not be served by room B: the
    // rule's `deferred` branch reloads unconditionally, so a stale flag turns
    // into a reload of the wrong room's history.
    //
    // MUTANT: drop `deferred.current = false` from the guard → this dies.
    const guard = SOURCE.slice(
      SOURCE.indexOf("seenRoom.current !== room"),
      SOURCE.indexOf("useEffect(("),
    );
    expect(guard).toContain("deferred.current = false");
  });

  it("re-seeds during render, not in an effect", () => {
    // An effect runs after the effect below it in declaration order would have
    // already asked the rule — with the previous room's `seen`. The reload it
    // fires cannot be taken back.
    //
    // MUTANT: wrap the guard in `useEffect(..., [room])` → this dies.
    const beforeEffect = SOURCE.slice(0, SOURCE.indexOf("useEffect(("));
    expect(beforeEffect).toContain("seenRoom.current !== room");
  });
});
