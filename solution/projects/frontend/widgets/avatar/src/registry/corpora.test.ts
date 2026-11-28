import { describe, expect, it } from "vitest";

import { hashSeed, pickFromSeed } from "../seed/hash";
import { ARTIFACT_STYLES, PERSON_STYLES, ROOM_STYLES, styleForSeed } from "./corpora";

/**
 * The rule the whole package rests on: one seed, one style, one face, forever.
 *
 * These assert the SEED→STYLE half, which is pure. The seed→drawing half is
 * DiceBear's own contract and is not re-tested here.
 */
describe("style selection", () => {
  it("is stable for a seed", () => {
    for (const seed of ["cid_abc", "room_7", "night-auditor", ""]) {
      expect(styleForSeed("person", seed).id).toBe(styleForSeed("person", seed).id);
    }
  });

  it("spreads across the corpus", () => {
    // THE CONTROL for the line above: returning a constant would satisfy
    // stability and put every agent in one style, which is the exact defect this
    // package was rebuilt to fix.
    const ids = new Set(
      Array.from({ length: 200 }, (_, i) => styleForSeed("person", `cid_${i}`).id),
    );
    expect(ids.size).toBe(PERSON_STYLES.length);
  });

  it("keeps each kind inside its own corpus", () => {
    const personIds = new Set(PERSON_STYLES.map((s) => s.id));
    const roomIds = new Set(ROOM_STYLES.map((s) => s.id));
    const artifactIds = new Set(ARTIFACT_STYLES.map((s) => s.id));
    for (let i = 0; i < 100; i += 1) {
      expect(roomIds.has(styleForSeed("room", `room_${i}`).id)).toBe(true);
      expect(personIds.has(styleForSeed("person", `cid_${i}`).id)).toBe(true);
      expect(artifactIds.has(styleForSeed("artifact", `skill_${i}`).id)).toBe(true);
    }
    // No two corpora may overlap, or the silhouette stops telling a somebody
    // from a place from a tool — which is the whole reason there are three.
    // Pairwise, because a total size check would pass on a three-way tie.
    expect([...personIds].some((id) => roomIds.has(id))).toBe(false);
    expect([...personIds].some((id) => artifactIds.has(id))).toBe(false);
    expect([...roomIds].some((id) => artifactIds.has(id))).toBe(false);
  });

  /**
   * A GOLDEN test, and the reason it exists is worth stating: the corpus is
   * indexed by `hash % length`, so adding, removing or reordering an entry
   * repaints every existing agent. That is an accepted, deliberate cost — but it
   * must never happen by accident, so these pairs fail loudly when the corpus
   * moves. Updating them is the signal that a migration was chosen.
   */
  it("pins the seed to style mapping", () => {
    // LITERALS, computed once by an independent implementation of the hash and
    // pasted here. Deriving them from `styleForSeed` would make this test agree
    // with any corpus whatsoever — including a reordered one — which is the only
    // thing it exists to catch.
    expect(styleForSeed("person", "cid_alpha").id).toBe("lorelei");
    expect(styleForSeed("person", "cid_beta").id).toBe("bottts");
    expect(styleForSeed("person", "cid_gamma").id).toBe("avataaars");
    expect(styleForSeed("person", "night-auditor").id).toBe("lorelei");
    expect(styleForSeed("room", "room_ops").id).toBe("rings");
    expect(styleForSeed("room", "room_release").id).toBe("shapes");
    // Real catalogue slugs, so a corpus change is felt as "these entries
    // repaint" rather than as an abstract index shift.
    expect(styleForSeed("artifact", "filesystem").id).toBe("identicon");
    expect(styleForSeed("artifact", "slack").id).toBe("glass");
  });

  it("carries no style that would oblige an attribution line", () => {
    // Twelve of DiceBear's 31 styles are CC BY 4.0. The core's MIT licence does
    // not cover the artwork, so this is asserted as data rather than trusted to
    // a comment.
    for (const entry of [...PERSON_STYLES, ...ROOM_STYLES, ...ARTIFACT_STYLES]) {
      expect(["CC0-1.0", "MIT", "free-for-commercial"]).toContain(entry.licence);
    }
  });

  it("spreads the artifact corpus too", () => {
    // The control for the golden pair above, and it matters more here than
    // elsewhere: this corpus covers ~1900 catalogue entries, so a constant
    // would read as one texture across a whole catalogue — the exact
    // uniformity the third corpus exists to break.
    const ids = new Set(
      Array.from({ length: 200 }, (_, i) => styleForSeed("artifact", `skill-${i}`).id),
    );
    expect(ids.size).toBe(ARTIFACT_STYLES.length);
  });
});

describe("seed hashing", () => {
  it("mixes low bits, which a corpus index reads", () => {
    // Seeds differing only in a trailing counter are the realistic adversarial
    // case (`system-architect-1`, `-2`, …). A weak hash sends them all to one
    // style.
    const ids = new Set(
      Array.from({ length: 60 }, (_, i) => styleForSeed("person", `system-architect-${i}`).id),
    );
    expect(ids.size).toBe(PERSON_STYLES.length);
  });

  it("refuses an empty corpus rather than returning nothing", () => {
    expect(() => pickFromSeed([], "x")).toThrow();
  });

  it("stays a 32-bit unsigned integer", () => {
    for (const seed of ["", "a", "cid_abc", "широкий", "🙂"]) {
      const hash = hashSeed(seed);
      expect(Number.isInteger(hash)).toBe(true);
      expect(hash).toBeGreaterThanOrEqual(0);
      expect(hash).toBeLessThanOrEqual(0xffffffff);
    }
  });
});
