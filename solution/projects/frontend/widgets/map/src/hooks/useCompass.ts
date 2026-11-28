'use client'

import { useCallback } from 'react'

import { useMapContext } from '../context'

/** What `useCompass` exposes for a compass chip / camera-orientation UI. */
export interface UseCompassResult {
  /** Current camera bearing in degrees (0 = north-up). */
  bearing: number
  /** Current camera pitch in degrees (0 = top-down). */
  pitch: number
  /**
   * Whether the view is rotated or tilted off true north / top-down. Google-
   * style compasses use this to decide whether to show the chip at all and to
   * tint the needle as an "off-north" cue. Threshold is a half-degree so
   * floating-point jitter around 0 doesn't flicker it.
   */
  isOriented: boolean
  /** Ease the camera back to a north-up, top-down view (bearing + pitch → 0). */
  resetNorth: () => void
}

/**
 * Compass state for a map — reads the live `bearing`/`pitch` from the viewport
 * and exposes a one-call reset to north-up + top-down.
 *
 * Pure glue around `useMapContext` (no maplibre runtime import); reusable by
 * any chip inside a `MapProvider`. Mirrors `useTerrain`'s map-access pattern:
 * the camera move goes through the map ref's `easeTo`.
 */
export function useCompass(): UseCompassResult {
  const { mapRef, viewport } = useMapContext()

  const bearing = viewport.bearing ?? 0
  const pitch = viewport.pitch ?? 0
  const isOriented = Math.abs(bearing) > 0.5 || pitch > 0.5

  const resetNorth = useCallback(() => {
    mapRef.current?.getMap().easeTo({ bearing: 0, pitch: 0, duration: 500 })
  }, [mapRef])

  return { bearing, pitch, isOriented, resetNorth }
}
