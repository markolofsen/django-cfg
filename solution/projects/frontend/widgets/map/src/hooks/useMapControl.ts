'use client'

import { useCallback } from 'react';

import { useMapContext } from '../context';

import type { LngLatBoundsLike } from 'maplibre-gl'
import type { MapControlActions, MapViewport } from '../types'

/**
 * Hook for imperative map control
 * Provides methods for programmatic map navigation
 */
export function useMapControl(): MapControlActions {
  const { mapRef } = useMapContext()

  const flyTo = useCallback(
    (center: [number, number], zoom?: number, options?: { duration?: number }) => {
      mapRef.current?.flyTo({
        center,
        zoom,
        duration: options?.duration ?? 2000,
      })
    },
    [mapRef]
  )

  const easeTo = useCallback(
    (center: [number, number], zoom?: number, options?: { duration?: number }) => {
      mapRef.current?.easeTo({
        center,
        zoom,
        duration: options?.duration ?? 500,
      })
    },
    [mapRef]
  )

  const fitBounds = useCallback(
    (
      bounds: LngLatBoundsLike,
      options?: { padding?: number; duration?: number; maxZoom?: number },
    ) => {
      mapRef.current?.fitBounds(bounds, {
        padding: options?.padding ?? 50,
        duration: options?.duration ?? 1000,
        ...(options?.maxZoom !== undefined ? { maxZoom: options.maxZoom } : {}),
      })
    },
    [mapRef]
  )

  const zoomIn = useCallback(() => {
    const currentZoom = mapRef.current?.getZoom() ?? 10
    mapRef.current?.easeTo({ zoom: currentZoom + 1, duration: 300 })
  }, [mapRef])

  const zoomOut = useCallback(() => {
    const currentZoom = mapRef.current?.getZoom() ?? 10
    mapRef.current?.easeTo({ zoom: Math.max(0, currentZoom - 1), duration: 300 })
  }, [mapRef])

  const resetView = useCallback(
    (initialViewport: MapViewport) => {
      mapRef.current?.flyTo({
        center: [initialViewport.longitude, initialViewport.latitude],
        zoom: initialViewport.zoom,
        bearing: initialViewport.bearing ?? 0,
        pitch: initialViewport.pitch ?? 0,
        duration: 1000,
      })
    },
    [mapRef]
  )

  const getCenter = useCallback((): [number, number] | null => {
    const center = mapRef.current?.getCenter()
    return center ? [center.lng, center.lat] : null
  }, [mapRef])

  const getZoom = useCallback((): number | null => {
    return mapRef.current?.getZoom() ?? null
  }, [mapRef])

  const getBounds = useCallback((): LngLatBoundsLike | null => {
    const bounds = mapRef.current?.getBounds()
    if (!bounds) return null
    return [
      [bounds.getWest(), bounds.getSouth()],
      [bounds.getEast(), bounds.getNorth()],
    ]
  }, [mapRef])

  return {
    flyTo,
    easeTo,
    fitBounds,
    zoomIn,
    zoomOut,
    resetView,
    getCenter,
    getZoom,
    getBounds,
  }
}
