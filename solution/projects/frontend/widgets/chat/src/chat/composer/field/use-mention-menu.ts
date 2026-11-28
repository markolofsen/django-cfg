import { useCallback, useState, type KeyboardEvent } from "react";

import { filterMentionItems, mentionToken, type MentionItem } from "../../core/room/recipient";
import { applyTrigger, detectTrigger } from "../../core/room/mentions";

/**
 * Names contain spaces ("Mark Olofsen"), so the query may too; three words is
 * the bound that keeps a stray `@` from matching the rest of the message.
 */
const MATCH = { allowSpaces: true, maxWords: 3 } as const;

export interface MentionMenuState {
  readonly open: boolean;
  readonly candidates: readonly MentionItem[];
  readonly activeIndex: number;
  /** True once the keyboard has moved the highlight; gates `aria-activedescendant`. */
  readonly navigated: boolean;
  /** Feed every text change and caret move. */
  readonly onCaret: (text: string, caret: number) => void;
  /** Offer to the textarea's keydown first; true means the menu took the key. */
  readonly onKeyDown: (event: KeyboardEvent<HTMLTextAreaElement>) => boolean;
  readonly commit: (item: MentionItem) => void;
}

interface Nav {
  readonly query: string;
  readonly index: number;
  readonly navigated: boolean;
}

/**
 * The `@` menu over a textarea, synchronous and fed by the host's item list.
 *
 * Detection is `detectTrigger(text, caret)` and nothing else: the menu is open
 * exactly while that returns a match that selects at least one item, so there is
 * no open flag to fall out of step with the text. The only state is what the
 * text cannot say: where the caret is, which row the keyboard is on, and the
 * `@` the sender dismissed with Escape.
 *
 * Restored from django-cfg `981754ced^` (`use-mentions` + `MentionsSession`),
 * minus the async search, the abort bookkeeping and the `/` command twin: a
 * room's list is a few names the host already holds.
 */
export function useMentionMenu(
  items: readonly MentionItem[] | undefined,
  text: string,
  setText: (text: string) => void,
  placeCaret: (caret: number) => void,
): MentionMenuState {
  const [caret, setCaret] = useState(0);
  const [dismissed, setDismissed] = useState<number | null>(null);
  const [nav, setNav] = useState<Nav>({ query: "", index: 0, navigated: false });

  const match = items === undefined ? null : detectTrigger(text, "@", caret, MATCH);
  const candidates =
    items === undefined || match === null || dismissed === match.offset
      ? []
      : filterMentionItems(items, match.query);
  const query = match?.query ?? "";
  // A new query starts the highlight over: the row it was on may be gone.
  const current: Nav = nav.query === query ? nav : { query, index: 0, navigated: false };
  const activeIndex = Math.min(current.index, Math.max(0, candidates.length - 1));
  const open = candidates.length > 0;

  const onCaret = useCallback(
    (nextText: string, nextCaret: number) => {
      setCaret(nextCaret);
      // The dismissed `@` is forgotten the moment the caret leaves it.
      if (detectTrigger(nextText, "@", nextCaret, MATCH) === null) setDismissed(null);
    },
    [],
  );

  const commit = useCallback(
    (item: MentionItem) => {
      if (match === null) return;
      const next = applyTrigger(text, match, caret, mentionToken(item));
      setText(next.text);
      setCaret(next.caret);
      placeCaret(next.caret);
    },
    [match, text, caret, setText, placeCaret],
  );

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>): boolean => {
    // A candidate window confirms with Enter; that keystroke is not ours.
    if (!open || event.nativeEvent.isComposing) return false;
    const move = (delta: number) => {
      event.preventDefault();
      setNav({
        query,
        index: (activeIndex + delta + candidates.length) % candidates.length,
        navigated: true,
      });
    };
    switch (event.key) {
      case "ArrowDown":
        move(1);
        return true;
      case "ArrowUp":
        move(-1);
        return true;
      case "Enter":
      case "Tab": {
        if (event.shiftKey || event.altKey || event.ctrlKey || event.metaKey) return false;
        const chosen = candidates[activeIndex];
        if (chosen === undefined) return false;
        event.preventDefault();
        commit(chosen);
        return true;
      }
      case "Escape":
        event.preventDefault();
        setDismissed(match?.offset ?? null);
        return true;
      default:
        return false;
    }
  };

  return { open, candidates, activeIndex, navigated: current.navigated, onCaret, onKeyDown, commit };
}
