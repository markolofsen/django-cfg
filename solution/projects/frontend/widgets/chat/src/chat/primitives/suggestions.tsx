import type { ReactNode } from "react";

import type { ChatSuggestion } from "../core/capabilities";
import { emptyDraft } from "../core/compose/outbound";
import { useCapabilities, useChatStore, useHistoryLoaded, useMessageIds } from "../store";
import { useTurnActivity } from "./transcript/use-turn-activity";

export interface SuggestionsProps {
  /**
   * Render one row. Called with the suggestion and the handler that sends it.
   *
   * A render prop rather than a built-in button, for the reason `jumpToLatest`
   * is one: the chrome and the icon are the host's, and this package ships no
   * icon library. A primitive that decides its own chrome is how a primitive
   * turns back into 83 props.
   */
  readonly children: (props: SuggestionRenderProps) => ReactNode;
  /**
   * Wrapped around the rows. Absent ⇒ they render as siblings, which is what a
   * host supplying its own container wants.
   */
  readonly className?: string;
  /**
   * The list's accessible name. Copy is the host's — no locales here.
   *
   * Without it the group is an unnamed landmark and a screen reader announces
   * only "list", with nothing to say what these rows start.
   */
  readonly label?: string;
}

export interface SuggestionRenderProps {
  readonly suggestion: ChatSuggestion;
  /** Send this suggestion's prompt. Already bound; the row only calls it. */
  readonly onSelect: () => void;
}

/**
 * The starter rows for an empty room.
 *
 * Renders NOTHING when the capability is absent, the list is empty, or the room
 * is not empty — never an empty container, which would still spend the parent's
 * `gap` and push the composer down.
 *
 * It owns the emptiness test itself, so every mount point agrees on it.
 */
/**
 * Whether starter rows will render right now.
 *
 * Exported because the transcript's "no messages yet" line is a FALLBACK for
 * exactly this: when rows are offered they already say the room is empty and
 * name what to do, so the line becomes a caption for the obvious. One predicate,
 * two readers, so the two can never both appear or both vanish.
 */
export function useHasSuggestions(): boolean {
  const { suggestions } = useCapabilities();
  const ids = useMessageIds();
  const historyLoaded = useHistoryLoaded();
  const activity = useTurnActivity();

  // The two suppressions `<Transcript>` applies to its own empty state, both
  // bought with incidents: a first turn sent into a fresh room is not an empty
  // room, and an unanswered fetch is not either — a 90-message room would
  // otherwise open on starter prompts while history loads.
  const roomIsEmpty = ids.length === 0 && historyLoaded && activity === null;

  return roomIsEmpty && (suggestions?.items.length ?? 0) > 0;
}

export function Suggestions({ children, className, label }: SuggestionsProps) {
  const { suggestions } = useCapabilities();
  const store = useChatStore();
  const show = useHasSuggestions();
  const items = suggestions?.items ?? [];

  if (!show || suggestions === undefined) return null;

  const { onPick, replyLanguage } = suggestions;
  // `store.send`, not the adapter: it queues behind a running turn and mints the
  // optimistic row, so a picked row and a typed message are one event
  // downstream. `prompt`, never `title` — the title is an abbreviation.
  //
  // The language sentence is appended, not hidden: whatever is sent is what the
  // transcript stores forever, and a hidden marker would need every surface
  // (web, messengers, search, export) to strip it and keep stripping it.
  const pick = (suggestion: ChatSuggestion) => {
    const text = replyLanguage
      ? `${suggestion.prompt} Reply in ${replyLanguage}.`
      : suggestion.prompt;
    void store.send({ ...emptyDraft, text });
    onPick?.(suggestion);
  };

  // Built here so the JSX below only lays out values that exist: an inline
  // `() => pick(s)` is a new function per row per render.
  const rows = items.map((suggestion) => ({
    id: suggestion.id,
    node: children({ suggestion, onSelect: () => pick(suggestion) }),
  }));

  // `listitem` on a wrapper, not on the host's row: a button carrying both roles
  // loses one of them depending on the reader.
  return (
    <div className={className} role="list" aria-label={label}>
      {rows.map((row) => (
        <div key={row.id} role="listitem" className="contents">
          {row.node}
        </div>
      ))}
    </div>
  );
}
