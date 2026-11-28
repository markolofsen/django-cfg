'use client'

import {
  createContext,
  useContext,
  useState,
  useRef,
  useMemo,
  useCallback,
  type ReactNode,
} from 'react'
import type { MapRef } from 'react-map-gl/maplibre'
import type { MapContextValue, MapViewport, MarkerData } from '../types'

const MapContext = createContext<MapContextValue | null>(null)

export interface MapProviderProps {
  children: ReactNode
  initialViewport?: Partial<MapViewport>
}

const DEFAULT_VIEWPORT: MapViewport = {
  longitude: 115.1889,
  latitude: -8.4095,
  zoom: 10,
  bearing: 0,
  pitch: 0,
}

export function MapProvider({ children, initialViewport }: MapProviderProps) {
  const mapRef = useRef<MapRef | null>(null)
  const initialViewportRef = useRef<MapViewport>({
    ...DEFAULT_VIEWPORT,
    ...initialViewport,
  })
  const [viewport, setViewportState] = useState<MapViewport>(initialViewportRef.current)
  const [markers, setMarkers] = useState<MarkerData[]>([])
  const [selectedMarker, setSelectedMarker] = useState<MarkerData | null>(null)
  const [hoveredFeature, setHoveredFeature] = useState<GeoJSON.Feature | null>(null)
  const [isLoaded, setIsLoaded] = useState(false)

  const setViewport = useCallback((newViewport: Partial<MapViewport>) => {
    setViewportState((prev) => ({ ...prev, ...newViewport }))
  }, [])

  const resetToInitial = useCallback(() => {
    const map = mapRef.current
    if (map) {
      map.flyTo({
        center: [initialViewportRef.current.longitude, initialViewportRef.current.latitude],
        zoom: initialViewportRef.current.zoom,
        bearing: initialViewportRef.current.bearing ?? 0,
        pitch: initialViewportRef.current.pitch ?? 0,
        duration: 1000,
      })
    }
  }, [])

  const value = useMemo<MapContextValue>(
    () => ({
      mapRef,
      viewport,
      setViewport,
      initialViewport: initialViewportRef.current,
      resetToInitial,
      markers,
      setMarkers,
      selectedMarker,
      setSelectedMarker,
      hoveredFeature,
      setHoveredFeature,
      isLoaded,
      setIsLoaded,
    }),
    [viewport, setViewport, resetToInitial, markers, selectedMarker, hoveredFeature, isLoaded]
  )

  return <MapContext.Provider value={value}>{children}</MapContext.Provider>
}

export function useMapContext(): MapContextValue {
  const context = useContext(MapContext)
  if (!context) {
    throw new Error('useMapContext must be used within a MapProvider')
  }
  return context
}

export { MapContext }
