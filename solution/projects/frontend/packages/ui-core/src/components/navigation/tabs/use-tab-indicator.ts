"use client"

import * as React from 'react'

/**
 * Keeps the sliding indicator under the active tab.
 *
 * Measurement rather than arithmetic: tabs here carry real words ("All",
 * "Deals", "Body type"), so they are never equal width and the CSS-only trick
 * of a fixed `--step` per index drifts as soon as a label changes or a
 * translation lands. The numbers go out as custom properties and `tabs.css`
 * does the animating, so React never runs a frame of it.
 *
 * It re-measures on the three things that actually move a tab: the selection
 * changing, the list resizing (a breakpoint, a sidebar opening), and a font
 * finishing loading — that last one is the subtle one, since a fallback face
 * lays out at a different width and the pill would otherwise keep a stale one.
 *
 * The selection is read from the DOM (`data-state`) rather than taken as an
 * argument, because that is the one source both controlled and uncontrolled
 * Tabs agree on — a `value` prop is absent in the uncontrolled case, and
 * `defaultValue` goes stale the moment the reader clicks.
 */
export function useTabIndicator<T extends HTMLElement>() {
  const ref = React.useRef<T | null>(null)
  const [ready, setReady] = React.useState(false)

  React.useLayoutEffect(() => {
    const list = ref.current
    if (!list) return

    const measure = () => {
      const tab = list.querySelector<HTMLElement>('[role="tab"][data-state="active"]')
      if (!tab) return
      list.style.setProperty('--tab-indicator-x', `${tab.offsetLeft}px`)
      list.style.setProperty('--tab-indicator-w', `${tab.offsetWidth}px`)
      setReady(true)
    }

    measure()

    const resize = new ResizeObserver(measure)
    resize.observe(list)
    for (const tab of list.querySelectorAll('[role="tab"]')) resize.observe(tab)

    // Radix flips `data-state` on the triggers; watching the attribute covers
    // selection by click, by keyboard and by the parent changing `value`,
    // without this hook needing to know which of the three happened.
    const mutation = new MutationObserver(measure)
    mutation.observe(list, {
      subtree: true,
      attributes: true,
      attributeFilter: ['data-state'],
      childList: true,
    })

    // `document.fonts` is absent in older WebViews; the indicator is simply
    // measured once there instead of re-measured after the swap.
    document.fonts?.ready.then(measure).catch(() => {})

    return () => {
      resize.disconnect()
      mutation.disconnect()
    }
  }, [])

  return { ref, ready }
}
