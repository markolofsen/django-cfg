'use client'

import { useCallback, useEffect, useRef, useState } from 'react'

import { useMapContext } from '../context'
import type { Map as MapLibreMap } from 'maplibre-gl'

export type MapScrollProtectionMode = 'off' | 'desktop' | 'mobile'

export interface UseMapScrollProtectionResult {
  /** Whether the lock overlay should be shown. */
  locked: boolean
  /**
   * Click/tap handler for the overlay. On desktop it unlocks scroll-zoom
   * in place; on mobile it stays locked (the caller opens fullscreen).
   */
  unlock: () => void
  /** True when running in mobile mode — the caller should expand to
   *  fullscreen on tap instead of unlocking in place. */
  isMobileLock: boolean
}

/**
 * Gesture guard for an inline map.
 *
 * - `'desktop'` — Google-Maps-style scroll isolation. Only the wheel/
 *   trackpad **scroll-zoom** is blocked until the user clicks the map;
 *   drag-pan / double-click / pinch stay live. Click inside unlocks,
 *   click outside re-locks. So scrolling a page past the map never
 *   hijacks the zoom, but the map is never fully inert.
 *
 * - `'mobile'` — the map is made **fully static**: scroll-zoom, drag-pan,
 *   touch pinch/rotate, double-click and keyboard are all disabled, so a
 *   finger dragging over the map scrolls the PAGE. There is no in-place
 *   unlock; the caller turns a tap into "open fullscreen", where a fresh
 *   map runs with all gestures enabled. This is the native-app pattern
 *   (static map preview in a feed → tap to open the full map).
 *
 * - `'off'` — every gesture enabled, no overlay.
 */
export function useMapScrollProtection(
  mode: MapScrollProtectionMode,
): UseMapScrollProtectionResult {
  const { mapRef, isLoaded } = useMapContext()
  const [locked, setLocked] = useState(true)

  // Latest `locked` without forcing the document-listener effect to
  // re-subscribe on every toggle.
  const lockedRef = useRef(locked)
  lockedRef.current = locked

  // On mobile the lock is permanent (tap opens fullscreen); only desktop
  // unlocks in place.
  const unlock = useCallback(() => {
    if (mode === 'desktop') setLocked(false)
  }, [mode])

  // All the maplibre gesture handlers we toggle in mobile mode. Listed
  // defensively (some are absent depending on options) — each is guarded.
  const setAllGestures = useCallback(
    (map: MapLibreMap, enable: boolean) => {
      const handlers = [
        map.scrollZoom,
        map.boxZoom,
        map.dragRotate,
        map.dragPan,
        map.keyboard,
        map.doubleClickZoom,
        map.touchZoomRotate,
        (map as unknown as { touchPitch?: { enable(): void; disable(): void } }).touchPitch,
      ]
      for (const h of handlers) {
        if (h && typeof h.enable === 'function') {
          if (enable) h.enable()
          else h.disable()
        }
      }
    },
    [],
  )

  // Apply the lock to maplibre. Re-runs on load and whenever mode/lock change.
  useEffect(() => {
    const map = mapRef.current?.getMap()
    if (!map) return

    if (mode === 'off') {
      // Make sure nothing we may have disabled stays off.
      map.scrollZoom.enable()
      return
    }

    if (mode === 'mobile') {
      // Fully static while locked; fully live once unlocked (never happens
      // on mobile, but keep the branch symmetric).
      setAllGestures(map, !locked)
      return
    }

    // desktop: only the scroll-zoom is gated.
    if (locked) {
      map.scrollZoom.disable()
    } else {
      map.scrollZoom.enable()
    }
  }, [mapRef, isLoaded, mode, locked, setAllGestures])

  // Re-lock (desktop only) when the user clicks anywhere OUTSIDE the map.
  // We do NOT re-lock on mouse-leave: once you've clicked into the map you
  // keep interacting even as the pointer wanders off and back — the Google
  // Maps behavior. Capture phase so we see the click before inner handlers
  // can stop it. Mobile never unlocks in place, so it needs no re-lock.
  useEffect(() => {
    if (mode !== 'desktop') return
    const container = mapRef.current?.getMap()?.getContainer()
    if (!container) return

    const handleDocPointerDown = (e: Event) => {
      const target = e.target as Element | null
      // A toolbar chip (or a menu/tooltip it opens) — never re-locks, and
      // when the map is LOCKED, pressing a control unlocks it: the user is
      // clearly working with the map, so the scroll guard should step aside.
      const onControl = !!target?.closest?.(
        '[data-map-control],[data-radix-popper-content-wrapper],[role="menu"],[role="tooltip"]',
      )

      if (lockedRef.current) {
        // Only desktop unlocks in place; `unlock()` is a no-op on mobile.
        if (onControl) unlock()
        return
      }

      // Unlocked: clicking a control must NOT re-lock (otherwise pressing a
      // toolbar button would immediately re-lock the map).
      if (onControl) return
      if (!container.contains(e.target as Node)) {
        setLocked(true)
      }
    }

    document.addEventListener('pointerdown', handleDocPointerDown, true)
    return () => {
      document.removeEventListener('pointerdown', handleDocPointerDown, true)
    }
  }, [mapRef, isLoaded, mode, unlock])

  // Reset to locked whenever the feature is (re)enabled.
  useEffect(() => {
    if (mode !== 'off') setLocked(true)
  }, [mode])

  return {
    locked: mode !== 'off' && locked,
    unlock,
    isMobileLock: mode === 'mobile' && locked,
  }
}
