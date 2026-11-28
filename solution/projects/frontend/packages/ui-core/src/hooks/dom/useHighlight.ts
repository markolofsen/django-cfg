"use client"

import * as React from 'react'

/**
 * The active-row state for a cmdk list inside a popover, and the scroll that
 * has to accompany it.
 *
 * Two things are going on, and neither works alone:
 *
 * 1. **The highlight is controlled.** cmdk otherwise activates the FIRST row,
 *    so a picker with a selection opens showing the top of the list rather than
 *    the value it holds. `onValueChange` is mandatory with a controlled value —
 *    cmdk then stores nothing itself and delegates every move to the caller, so
 *    omitting it freezes the arrow keys.
 *
 * 2. **Opening has to scroll.** cmdk schedules its own `scrollIntoView` when
 *    the value changes, but the popover keeps its list MOUNTED between opens
 *    (`sameNodeAcrossOpens: true`), so on the second open nothing re-mounts and
 *    nothing re-scrolls; on the first, the value is set before 252 rows have
 *    finished registering and there is nothing to scroll to yet. Measured both
 *    ways: selection at index 84, `scrollTop` 0. So the scroll is driven from
 *    the OPEN transition, after a paint, rather than left to the library.
 *
 * Ongoing arrow-key movement stays cmdk's own job; this only handles the jump
 * that opening owes the user.
 *
 * ```tsx
 * const highlight = useHighlight(open, value)
 * <Command value={highlight.value} onValueChange={highlight.setValue}>
 *   <CommandList ref={highlight.listRef}>…</CommandList>
 * </Command>
 * ```
 */
export function useHighlight(open: boolean, selected: string | null | undefined) {
  const [value, setValue] = React.useState("")
  const listRef = React.useRef<HTMLDivElement | null>(null)

  // `selected` is read through a ref so that changing the selection does not
  // re-run the open effect — only the open transition itself should scroll.
  const selectedRef = React.useRef(selected)
  selectedRef.current = selected

  React.useEffect(() => {
    if (!open) return
    setValue(selectedRef.current ?? "")
  }, [open])

  // Deliberately NOT `requestAnimationFrame`: a background tab never runs one,
  // so a popover opened in an inactive window would stay parked at the top
  // (this is how the bug first showed up — `document.hidden` and no scroll).
  // A layout effect keyed on the resolved highlight runs as soon as React has
  // committed the rows, in any tab, and before the browser paints.
  React.useLayoutEffect(() => {
    if (!open || !value) return
    const list = listRef.current
    if (!list) return

    // The row is found by VALUE rather than by `aria-selected`, which cmdk sets
    // in its own scheduled pass — by then this effect has already run.
    const row = list.querySelector(
      `[cmdk-item][data-value="${CSS.escape(value)}"]`
    )
    row?.scrollIntoView({ block: 'nearest' })
  }, [open, value])

  return { value, setValue, listRef }
}
