import type { ReactNode } from "react";

import { useChatCopy } from "../../../i18n";
import { Suggestions } from "../../primitives/suggestions";

export interface ChatSuggestionsProps {
  /**
   * Icon KEY → glyph. Absent, or an unmapped key, draws no glyph — a row still
   * works without its picture.
   *
   * A function rather than a map so the host owns the lookup: the catalogue
   * names glyphs as data, and this package ships no icon library. That is the
   * same contract the composer's slash menu takes.
   */
  readonly icon?: (key: string) => ReactNode;
}

/*
  Full width with the text left-aligned: the titles differ in length, and
  centred rows of different widths give the eye no shared edge to scan down.

  `text-left` is not redundant with the flex alignment — a button centres its
  text by default, and that survives `items-center`.
*/
const ROW =
  "group flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-left " +
  "text-[length:var(--chat-text)] transition-colors hover:bg-foreground/5 " +
  "focus-visible:bg-foreground/5 focus-visible:outline-none";

const TITLE = "min-w-0 truncate text-muted-foreground group-hover:text-foreground";

/*
  No gap between rows: they are one column of targets, and a pointer moving down
  it must not cross dead space between them. The rows' own padding is the
  spacing.

  `pb-3` is the air between the last row and the field, so the group reads as an
  offer above the input rather than part of it.

  `-ms-3` cancels the row's `px-3` so the glyphs line up with the field's text.
  The LOGICAL property, not `-ml-3`: the row mirrors under `dir="rtl"` on its
  own, and a physical margin would pull it the wrong way.
*/
const LIST = "-ms-3 flex flex-col pb-3";

/**
 * The starter rows, styled.
 *
 * ONE assembly, for the reason `ChatTranscript` is one: a host composing the
 * primitive by hand ships whichever part it forgot, and nothing fails — the
 * feature is simply absent.
 *
 * Mounted in the composer's `above` slot rather than in the transcript. Both
 * are defensible; the composer wins because that is where the user already
 * looks when deciding what to type, and because these rows are an INPUT
 * affordance — sitting where the answer appears made them read as content the
 * room already had.
 *
 * WHEN they show is the primitive's decision, not this slot's: `<Suggestions>`
 * renders nothing unless the room is genuinely empty, so a host passes it
 * unconditionally the way it passes `<AskSurface>`.
 *
 * A vertical list, not the horizontal pills the vendored Vercel primitive uses.
 * The chat pane is often narrow on a wide screen, and pills either wrap into a
 * ragged block or scroll sideways, which hides rows behind a gesture nobody
 * makes on a first visit. Vercel's own docs widget — the shape this was modelled
 * on — is vertical for the same reason.
 */
export function ChatSuggestions({ icon }: ChatSuggestionsProps) {
  const copy = useChatCopy().transcript;

  return (
    <Suggestions className={LIST} label={copy.suggestionsLabel}>
      {({ suggestion, onSelect }) => {
        // An absent glyph collapses rather than reserving a gap: a list where
        // only some rows have icons should not indent the rest to match.
        const glyph = icon?.(suggestion.icon ?? "");
        return (
          <button type="button" onClick={onSelect} className={ROW}>
            {glyph}
            <span className={TITLE}>{suggestion.title}</span>
          </button>
        );
      }}
    </Suggestions>
  );
}
