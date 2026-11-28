/**
 * The DOM half of roving tabindex. The index arithmetic lives in
 * `core/screen/roving.ts`, where it is tested.
 *
 * Deliberately DOM-driven rather than list-driven: rows are rendered by the
 * HOST, so this hook cannot know their shape. It reads the elements marked with
 * `data-chat-item` at the moment a key is pressed, which also keeps it correct
 * while the transcript streams.
 */

import { useCallback, useState, type KeyboardEvent } from "react";

import { CHAT_ITEM_ATTR, clampIndex, isRovingKey, nextIndex } from "../../core/screen";

export interface RovingFocus {
  readonly onKeyDown: (event: KeyboardEvent<HTMLElement>) => void;
  /** Spread onto each row. Only the active row is tabbable. */
  readonly itemProps: (index: number) => {
    readonly tabIndex: number;
    readonly [CHAT_ITEM_ATTR]: string;
  };
}

/**
 * @param count how many rows there are. Needed because messages arrive while
 *   the user reads: an active index that outlives its row would leave EVERY row
 *   at `tabIndex={-1}`, so the transcript stops being reachable by Tab and
 *   nothing about it looks broken.
 */
export function useRovingFocus(count: number): RovingFocus {
  // State, not a ref: `tabIndex` is rendered output, so moving the active row
  // has to re-render the rows. A ref would move focus once and leave every
  // row's tabIndex frozen at its initial value.
  const [active, setActive] = useState(0);
  const current = clampIndex(active, count);

  const onKeyDown = useCallback(
    (event: KeyboardEvent<HTMLElement>) => {
      if (!isRovingKey(event.key)) return;

      const items = Array.from(
        event.currentTarget.querySelectorAll<HTMLElement>(`[${CHAT_ITEM_ATTR}]`),
      );
      const next = nextIndex(event.key, clampIndex(active, items.length), items.length);
      // `null` means the key moves nowhere — at the last row, ArrowDown must
      // still scroll the PAGE, so it is left to the browser rather than
      // swallowed by a preventDefault that changes nothing.
      if (next === null) return;

      const target = items[next];
      if (target === undefined) return;

      event.preventDefault();
      setActive(next);
      target.focus();
    },
    [active],
  );

  const itemProps = useCallback(
    (index: number) => ({
      tabIndex: index === current ? 0 : -1,
      [CHAT_ITEM_ATTR]: "",
    }),
    [current],
  );

  return { onKeyDown, itemProps };
}
