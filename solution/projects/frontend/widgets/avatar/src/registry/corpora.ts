import type { Style } from "@dicebear/core";

import { pickFromSeed } from "../seed/hash";

/**
 * Which drawings exist, and which seed gets which.
 *
 * Three corpora, because a person, a place and a tool are different kinds of
 * thing. Drawing a room with a face would say it were one; drawing a Skill with
 * a face would say the same of a tool. The difference is legible as a
 * SILHOUETTE — a mixed list separates by shape before the eye reaches any glyph,
 * which is what a mixed `All` listing needs, since it interleaves skills, tool
 * servers and roles in one column.
 *
 * Every entry is attribution-free (CC0, MIT, or free-for-commercial). Twelve of
 * DiceBear's styles are CC BY 4.0 and would oblige a consumer to carry a credit
 * line; the core's MIT licence does not cover the artwork. `licence` is recorded
 * as DATA rather than as a comment so the constraint is assertable — a comment
 * cannot fail a test.
 */

export type AvatarKind = "person" | "room" | "artifact";

export interface StyleEntry {
  /** Stable identity, independent of list position. Golden tests name these, so
   *  a reordered corpus fails loudly instead of silently repainting everyone. */
  readonly id: string;
  readonly licence: "CC0-1.0" | "MIT" | "free-for-commercial";
  /**
   * Loaded on demand, and ALWAYS from the style's own package.
   *
   * Never from `@dicebear/collection`: a barrel re-export is a static import to
   * the bundler, so one lazy import of the barrel pulls all 31 styles into a
   * single 2 MB chunk. Per-package imports split — a character style lands in
   * its own ~115 KB chunk, and a session downloads only the styles its own
   * roster seeds.
   */
  readonly load: () => Promise<Style<Record<string, unknown>>>;
}

/**
 * A style package's whole namespace IS its `Style` — `{create, meta, schema}`.
 *
 * Only `@dicebear/collection` exposes the named binding (`m.shapes`), and that
 * barrel is exactly what must not be imported. Naming this conversion once keeps
 * the six lazy imports below from repeating a cast each.
 */
type StyleModule = Style<Record<string, unknown>>;
const asStyle = (module: unknown) => module as StyleModule;

/**
 * Characters, for agents and machines.
 *
 * Picked for distance from EACH OTHER rather than for individual quality: the
 * corpus exists to break a uniform column, so a second style resembling the
 * first would add weight and no variety. Line-drawn, hand-drawn, illustrated,
 * flat-vector, robot and 8-bit are six recognisably different hands.
 *
 * Costly — 8 KB to 118 KB gzipped each — which is why they are lazy. Loading all
 * six eagerly would be a 29x regression against the library this replaced.
 */
export const PERSON_STYLES: readonly StyleEntry[] = [
  { id: "notionists", licence: "CC0-1.0", load: () => import("@dicebear/notionists").then(asStyle) },
  { id: "openPeeps", licence: "CC0-1.0", load: () => import("@dicebear/open-peeps").then(asStyle) },
  { id: "lorelei", licence: "CC0-1.0", load: () => import("@dicebear/lorelei").then(asStyle) },
  { id: "avataaars", licence: "free-for-commercial", load: () => import("@dicebear/avataaars").then(asStyle) },
  { id: "bottts", licence: "free-for-commercial", load: () => import("@dicebear/bottts").then(asStyle) },
  { id: "pixelArt", licence: "CC0-1.0", load: () => import("@dicebear/pixel-art").then(asStyle) },
];

/**
 * Abstract marks, for rooms.
 *
 * A composite of the members' faces was considered and rejected before this
 * plan: unreadable at roster size, and it repaints when membership changes — an
 * identity that moves is not one. A seeded abstract mark answers both, and is
 * cheap enough (4 KB each) to load eagerly, so a room never flashes a
 * placeholder.
 */
export const ROOM_STYLES: readonly StyleEntry[] = [
  { id: "shapes", licence: "CC0-1.0", load: () => import("@dicebear/shapes").then(asStyle) },
  { id: "rings", licence: "CC0-1.0", load: () => import("@dicebear/rings").then(asStyle) },
];

/**
 * Abstract marks, for capabilities — a Skill or an MCP server.
 *
 * A tool is neither a somebody nor a place, and both alternatives were wrong in
 * a way a reader would notice: a face claims agency the thing does not have, and
 * the room corpus argues from MEMBERSHIP, which a capability has none of.
 *
 * Deliberately NOT `@dicebear/icons`. Its Bootstrap glyphs draw a recognisable
 * object — a wrench, a gear, a plug — so a seed would assert something about
 * what the capability DOES, chosen by a hash. A mark that means nothing is
 * honest; a pictogram picked at random is a claim, and it would be wrong more
 * often than right across a large catalogue.
 *
 * Two styles rather than one: this corpus covers skills and tool servers, an
 * order of magnitude more entries than either other corpus, and a single
 * generator across that many rows reads as one texture instead of as identity.
 * Both are geometric and cheap, so — like rooms, and unlike the character styles
 * — nothing here justifies a placeholder frame.
 */
export const ARTIFACT_STYLES: readonly StyleEntry[] = [
  { id: "identicon", licence: "CC0-1.0", load: () => import("@dicebear/identicon").then(asStyle) },
  { id: "glass", licence: "CC0-1.0", load: () => import("@dicebear/glass").then(asStyle) },
];

/**
 * A TOTAL map, not a chain of ternaries.
 *
 * A `KIND_ICON` record in a catalogue row is written this way
 * after a real defect — it was binary, so a role silently wore the MCP server's
 * icon. The same reasoning applies one layer down: a fourth `AvatarKind` must be
 * a compile error here, never a silent fall to `PERSON_STYLES`, which would put
 * a face on whatever the new kind turned out to be.
 */
const CORPORA: Record<AvatarKind, readonly StyleEntry[]> = {
  person: PERSON_STYLES,
  room: ROOM_STYLES,
  artifact: ARTIFACT_STYLES,
};

export function corpusFor(kind: AvatarKind): readonly StyleEntry[] {
  return CORPORA[kind];
}

/**
 * The style a seed draws in — the rule the whole design rests on.
 *
 * Chosen BY THE SEED, never randomly and never from a list position, so one seed
 * yields one style yields one face, on every device and every reload, with
 * nothing persisted. That is what lets a host offer many art styles without
 * giving any single agent two faces.
 */
export function styleForSeed(kind: AvatarKind, seed: string): StyleEntry {
  return pickFromSeed(corpusFor(kind), seed);
}
