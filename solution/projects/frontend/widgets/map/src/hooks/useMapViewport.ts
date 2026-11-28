'use client'

import { useCallback, useMemo } from 'react';

import { useMapContext } from '../context';

import type { MapViewport } from '../types'

/**
 * Hook for viewport state and animations
 */
export function useMapViewport() {
  const { mapRef, viewport, setViewport } = useMapContext()

  const animateTo = useCallback(
    (newViewport: Partial<MapViewport>, duration = 1000) => {
      const map = mapRef.current
      if (!map) {
        setViewport(newViewport)
        return
      }

      map.easeTo({
        center: newViewport.longitude !== undefined && newViewport.latitude !== undefined
          ? [newViewport.longitude, newViewport.latitude]
          : undefined,
        zoom: newViewport.zoom,
        bearing: newViewport.bearing,
        pitch: newViewport.pitch,
        duration,
      })
    },
    [mapRef, setViewport]
  )

  const center = useMemo<[number, number]>(
    () => [viewport.longitude, viewport.latitude],
    [viewport.longitude, viewport.latitude]
  )

  const bounds = useMemo(() => {
    const map = mapRef.current
    if (!map) return null

    const b = map.getBounds()
    if (!b) return null

    return {
      north: b.getNorth(),
      south: b.getSouth(),
      east: b.getEast(),
      west: b.getWest(),
    }
    // `viewport` reads as unnecessary because the bounds come from the imperative
    // map instance, not from it. It is the only signal that the view moved: drop
    // it and `bounds` stays frozen at the first camera position for ever.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mapRef, viewport])

  return {
    viewport,
    setViewport,
    animateTo,
    zoom: viewport.zoom,
    center,
    bounds,
  }
}
