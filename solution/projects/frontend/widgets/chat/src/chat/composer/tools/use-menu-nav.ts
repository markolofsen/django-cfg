import { useCallback, useEffect, useState, type KeyboardEvent } from "react";

import { NO_ROW, nextRow, stepForKey } from "../../core";

export interface MenuNav {
  /** Index into the flattened rows, or `NO_ROW` before the user navigates. */
  readonly activeIndex: number;
  /** True once a key moved the selection — drives `aria-activedescendant`. */
  readonly navigated: boolean;
  readonly onKeyDown: (event: KeyboardEvent) => void;
  readonly setActiveIndex: (index: number) => void;
}

export interface MenuNavOptions {
  /** How many rows are currently rendered, across all groups. */
  readonly count: number;
  /** Commit the row at this index. */
  readonly onCommit: (index: number) => void;
  readonly onEscape?: () => void;
}

/**
 * React binding over `core/tools/menu/nav`. Where the cursor lands is that module's;
 * this owns only the event and the state holding it.
 *
 * Held keys are the BROWSER's auto-repeat, deliberately: it already fires
 * `keydown` repeatedly at the rate the user set in their OS, so a timer here
 * would ignore that preference and race with it. `event.repeat` is not filtered.
 *
 * The index resets whenever the row count changes — every keystroke in the
 * filter rebuilds the list, and an index held across that points at a different
 * tool than the one the user was looking at.
 */
export function useMenuNav({ count, onCommit, onEscape }: MenuNavOptions): MenuNav {
  const [activeIndex, setActiveIndex] = useState(NO_ROW);

  useEffect(() => setActiveIndex(NO_ROW), [count]);

  const onKeyDown = useCallback(
    (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onEscape?.();
        return;
      }
      if (event.key === "Enter") {
        // Enter before any navigation is not a pick: the user is still typing,
        // and committing row 0 on it commits a row the user never read.
        if (activeIndex < 0) return;
        event.preventDefault();
        onCommit(activeIndex);
        return;
      }

      const step = stepForKey(event.key);
      const next = nextRow(activeIndex, step, count);
      if (next === NO_ROW) return;
      // The filter input owns the caret; without this, ArrowUp jumps it to the
      // start of the query while the selection also moves.
      event.preventDefault();
      setActiveIndex(next);
    },
    [activeIndex, count, onCommit, onEscape],
  );

  return { activeIndex, navigated: activeIndex >= 0, onKeyDown, setActiveIndex };
}
