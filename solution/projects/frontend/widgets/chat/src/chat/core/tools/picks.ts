/**
 * A tool the user picked from the menu, and the marker that carries it.
 *
 * The marker reaches the MODEL, not the transcript. It says "the user chose
 * this from the menu" in a form that survives a sentence around it, which a
 * bare name cannot: `upload_file` in prose is indistinguishable from a word
 * that was typed, and that ambiguity is the whole reason the menu exists.
 */

import { toolURL } from "../links";

/** A picked tool: the registry's id, and the label the user actually saw. */
export interface ToolPick {
  readonly id: string;
  /** What the menu row said. Shown on the chip; never sent. */
  readonly label: string;
  /**
   * The entry's icon KEY, carried so the chip can draw the same glyph the menu
   * row did. Absent ⇒ no glyph; the id is not a fallback, because a host maps
   * these keys and an id it never mapped would resolve to nothing anyway.
   */
  readonly icon?: string;
  /**
   * Carried from the catalogue row so the composer can say what is still
   * missing without holding the catalogue itself — the draft is what the
   * placeholder reads, and a pick is the only thing on it that knows.
   */
  readonly needs?: "file" | "skill";
}

/**
 * The marker a picked tool becomes in the outbound text: a markdown link
 * `[<label>](app://tool/<id>)`.
 *
 * A link rather than a bare token because the same string has two readers. The
 * MODEL reads the label, which is the human name of the tool and says more than
 * an id does; the RENDERER reads the href, which is the exact registry id and
 * is what a chip must resolve. A bare `[tool:<id>]` served only the second, and
 * printed as noise to the first.
 *
 * An empty label falls back to the id — a link with no text renders as nothing
 * at all, which would hide the pick from the model entirely.
 */
export function toolMarker(id: string, label: string): string {
  return `[${escapeLinkText(label || id)}](${toolURL(id)})`;
}

/**
 * Escape the characters that would end a markdown link's text early.
 *
 * Only `[` and `]` matter: either one unbalances the bracket pair, so the
 * parser stops reading the label there and the href becomes visible prose.
 * Labels rarely contain them, and a label that does must still round-trip.
 */
function escapeLinkText(label: string): string {
  return label.replace(/([[\]])/g, "\\$1");
}

/**
 * Ids named by markers in a text, in the order they appear.
 *
 * For a host that must reconcile what a user typed against what they picked.
 * Matched on the HREF, not the label: the id is the half that identifies the
 * tool, and a label may be renamed, translated, or typed by the user.
 *
 * The label is skipped with an escape-aware scan so a `\]` inside it cannot end
 * the pair early — the other half of what `escapeLinkText` writes.
 */
export function readToolMarkers(text: string): readonly string[] {
  const found: string[] = [];
  for (const match of text.matchAll(/\[(?:\\.|[^\\[\]])*\]\(app:\/\/tool\/([^)\s]+)\)/g)) {
    // The group is guaranteed by the pattern, but not by the type: an indexed
    // read is `string | undefined` under the compiler's checked-access rule.
    const raw = match[1];
    if (raw === undefined) continue;
    // The writer percent-encodes the id, so the reader must decode it or an id
    // with a reserved character never matches the pick it came from.
    try {
      found.push(decodeURIComponent(raw));
    } catch {
      found.push(raw);
    }
  }
  return found;
}

/**
 * Append each pick's marker to the text the model receives.
 *
 * Appended at the END, never at the caret: the markers describe the whole turn,
 * and splicing one into the middle of a sentence would change what the prose
 * around it means.
 *
 * A pick already named in the text is not repeated — a user who typed the
 * marker themselves, or a draft restored from storage, would otherwise send it
 * twice and read as two requests.
 */
export function appendToolMarkers(text: string, picks: readonly ToolPick[] | undefined): string {
  // Tolerates a draft built before this field existed. `Draft` crosses the
  // package boundary, so a host or a stored draft can still carry the old
  // shape, and a missing list means "picked nothing" rather than a crash on
  // the send path.
  if (picks === undefined || picks.length === 0) return text;

  const already = new Set(readToolMarkers(text));
  const markers = picks
    .filter((pick) => !already.has(pick.id))
    .map((pick) => toolMarker(pick.id, pick.label));
  if (markers.length === 0) return text;

  const body = text.trim();
  return body === "" ? markers.join(" ") : `${body} ${markers.join(" ")}`;
}

/** A text with its tool markers removed, and the ids they named. */
export interface StrippedToolMarkers {
  readonly text: string;
  readonly ids: readonly string[];
}

/**
 * Split pasted text into prose and the tools it names.
 *
 * The marker is what `buildOutbound` WRITES, so copying a sent turn and pasting
 * it back returns raw markdown to the box. The user sees a URL they did not
 * type and a tool nothing staged — the round trip loses exactly the fact the
 * marker exists to carry.
 *
 * Ids only. Whether a tool is offered here is the catalogue's answer, and a
 * label lifted from the text would name a tool this host may not register.
 */
export function stripToolMarkers(text: string): StrippedToolMarkers {
  const ids = readToolMarkers(text);
  if (ids.length === 0) return { text, ids };

  // Collapse the space the marker was joined with, so removing a trailing one
  // does not leave the prose ending in a blank.
  const stripped = text
    .replace(/\s*\[(?:\\.|[^\\[\]])*\]\(app:\/\/tool\/[^)\s]+\)/g, "")
    .trim();
  return { text: stripped, ids };
}
