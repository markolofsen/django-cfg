'use client'

import { useCallback } from 'react';

import { useMapContext } from '../context';

import type { LayerProps } from 'react-map-gl/maplibre'
import type { FilterSpecification } from 'maplibre-gl'
/**
 * Hook for dynamic layer management
 */
export function useMapLayers() {
  const { mapRef, isLoaded } = useMapContext()

  const addLayer = useCallback(
    (layer: LayerProps, beforeId?: string) => {
      const map = mapRef.current?.getMap()
      if (!map || !isLoaded) return

      if (layer.id && map.getLayer(layer.id)) {
        map.removeLayer(layer.id)
      }

      map.addLayer(layer as Parameters<typeof map.addLayer>[0], beforeId)
    },
    [mapRef, isLoaded]
  )

  const removeLayer = useCallback(
    (id: string) => {
      const map = mapRef.current?.getMap()
      if (!map || !isLoaded) return

      if (map.getLayer(id)) {
        map.removeLayer(id)
      }
    },
    [mapRef, isLoaded]
  )

  const setLayerVisibility = useCallback(
    (id: string, visible: boolean) => {
      const map = mapRef.current?.getMap()
      if (!map || !isLoaded) return

      if (map.getLayer(id)) {
        map.setLayoutProperty(id, 'visibility', visible ? 'visible' : 'none')
      }
    },
    [mapRef, isLoaded]
  )

  const setLayerFilter = useCallback(
    (id: string, filter: FilterSpecification | null) => {
      const map = mapRef.current?.getMap()
      if (!map || !isLoaded) return

      if (map.getLayer(id)) {
        map.setFilter(id, filter)
      }
    },
    [mapRef, isLoaded]
  )

  const setLayerPaint = useCallback(
    (id: string, property: string, value: unknown) => {
      const map = mapRef.current?.getMap()
      if (!map || !isLoaded) return

      if (map.getLayer(id)) {
        map.setPaintProperty(
          id,
          property as Parameters<typeof map.setPaintProperty>[1],
          value as never
        )
      }
    },
    [mapRef, isLoaded]
  )

  return {
    addLayer,
    removeLayer,
    setLayerVisibility,
    setLayerFilter,
    setLayerPaint,
  }
}
