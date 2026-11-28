'use client'

import { useCallback } from 'react';

import { useMapContext } from '../context';
import { useMapControl } from './useMapControl';

import type { MarkerActions, MarkerData } from '../types'

let markerId = 0
const generateMarkerId = () => `marker-${++markerId}`

/**
 * Hook for marker management
 * Provides methods to add, remove, update markers
 */
export function useMarkers(): MarkerActions {
  const { markers, setMarkers } = useMapContext()
  const { fitBounds } = useMapControl()

  const addMarker = useCallback(
    (marker: Omit<MarkerData, 'id'>): string => {
      const id = generateMarkerId()
      setMarkers((prev) => [...prev, { ...marker, id }])
      return id
    },
    [setMarkers]
  )

  const removeMarker = useCallback(
    (id: string) => {
      setMarkers((prev) => prev.filter((m) => m.id !== id))
    },
    [setMarkers]
  )

  const updateMarker = useCallback(
    (id: string, updates: Partial<Omit<MarkerData, 'id'>>) => {
      setMarkers((prev) =>
        prev.map((m) => (m.id === id ? { ...m, ...updates } : m))
      )
    },
    [setMarkers]
  )

  const clearMarkers = useCallback(() => {
    setMarkers([])
  }, [setMarkers])

  const fitToMarkers = useCallback(
    // Accepts a plain `padding` number (back-compat) or an options object.
    // `maxZoom` (default 16) stops a single / tightly-clustered set from
    // zooming all the way in and losing surrounding context.
    (paddingOrOpts: number | { padding?: number; maxZoom?: number } = 50) => {
      if (markers.length === 0) return

      const { padding = 50, maxZoom = 16 } =
        typeof paddingOrOpts === 'number' ? { padding: paddingOrOpts } : paddingOrOpts

      const single = markers.length === 1 ? markers[0] : undefined
      if (single !== undefined) {
        const marker = single
        fitBounds(
          [
            [marker.longitude - 0.01, marker.latitude - 0.01],
            [marker.longitude + 0.01, marker.latitude + 0.01],
          ],
          { padding, maxZoom }
        )
        return
      }

      const lngs = markers.map((m) => m.longitude)
      const lats = markers.map((m) => m.latitude)

      const bounds: [[number, number], [number, number]] = [
        [Math.min(...lngs), Math.min(...lats)],
        [Math.max(...lngs), Math.max(...lats)],
      ]

      fitBounds(bounds, { padding, maxZoom })
    },
    [markers, fitBounds]
  )

  return {
    markers,
    addMarker,
    removeMarker,
    updateMarker,
    clearMarkers,
    fitToMarkers,
  }
}
