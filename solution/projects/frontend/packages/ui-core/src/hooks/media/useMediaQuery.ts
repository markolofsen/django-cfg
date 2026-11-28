'use client';

import { useCallback, useSyncExternalStore } from 'react';

/**
 * Tailwind v4 default breakpoints (rem → px at 16px base).
 * In v4 these are CSS variables: var(--breakpoint-sm), var(--breakpoint-md), etc.
 *
 * Usage with useMediaQuery:
 *   useMediaQuery(`(max-width: ${BREAKPOINTS.md - 1}px)`) // < 768px
 *   useMediaQuery(`(min-width: ${BREAKPOINTS.lg}px)`)     // >= 1024px
 */
export const BREAKPOINTS = {
  sm: 640,    // 40rem — phones landscape
  md: 768,    // 48rem — tablets portrait
  lg: 1024,   // 64rem — tablets landscape / small laptops
  xl: 1280,   // 80rem — desktops
  '2xl': 1536, // 96rem
} as const

export type Breakpoint = keyof typeof BREAKPOINTS

/**
 * Reactive media query hook.
 *
 * WHY useSyncExternalStore:
 *   A media query has no server value, so the hydration render MUST return the
 *   same `false` the server rendered — reading `matchMedia` there makes React
 *   throw "server rendered HTML didn't match the client" for any component that
 *   branches on the result (a narrow-viewport `<Sidebar>` renders its drawer
 *   branch against the server's desktop markup). `getServerSnapshot` is the
 *   only reliable way to pin that first render: React calls it during hydration
 *   as well as on the server, then re-renders with the real match after mount.
 *   A lazy `useState` initializer cannot express that distinction.
 *
 *   Consequence to design around: the first painted frame is always the
 *   `false` branch. Components that must not flash should let CSS decide
 *   (Tailwind `md:` variants) rather than branch in JS.
 *
 * @example
 * const isPhone   = useMediaQuery('(max-width: 639px)')
 * const isDark    = useMediaQuery('(prefers-color-scheme: dark)')
 * const isLandscape = useMediaQuery('(orientation: landscape)')
 */
export function useMediaQuery(query: string): boolean {
  const subscribe = useCallback(
    (onChange: () => void) => {
      if (typeof window === 'undefined' || !window.matchMedia) return () => {}
      const mediaQuery = window.matchMedia(query)
      mediaQuery.addEventListener('change', onChange)
      return () => mediaQuery.removeEventListener('change', onChange)
    },
    [query]
  )

  const getSnapshot = useCallback(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return false
    return window.matchMedia(query).matches
  }, [query])

  return useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)
}

function getServerSnapshot(): boolean {
  return false
}
