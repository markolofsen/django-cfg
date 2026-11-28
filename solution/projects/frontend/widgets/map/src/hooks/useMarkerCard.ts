'use client'

import { useCallback, useMemo, useState } from 'react'

export interface UseMarkerCardResult {
  /** The currently open marker id, or `null` when none is open. */
  openId: string | null
  /** Open the card for `id` (closes any other open card). */
  open: (id: string) => void
  /** Close the open card. */
  close: () => void
  /** Toggle `id` — closes it if it's already the open one. */
  toggle: (id: string) => void
  /** Whether `id` is the currently open card. */
  isOpen: (id: string) => boolean
}

/**
 * useMarkerCard — selection state for marker info-cards. Holds a single
 * `openId` so only ONE card is open at a time; opening a new id closes the
 * previous, and `toggle` closes the same id. Pure React glue — no UI, no map
 * dependency. Drives `MapMarkers`, or use it standalone for manual control.
 */
export function useMarkerCard(): UseMarkerCardResult {
  const [openId, setOpenId] = useState<string | null>(null)

  const open = useCallback((id: string) => setOpenId(id), [])
  const close = useCallback(() => setOpenId(null), [])
  const toggle = useCallback(
    (id: string) => setOpenId((prev) => (prev === id ? null : id)),
    []
  )
  const isOpen = useCallback((id: string) => openId === id, [openId])

  return useMemo(
    () => ({ openId, open, close, toggle, isOpen }),
    [openId, open, close, toggle, isOpen]
  )
}
