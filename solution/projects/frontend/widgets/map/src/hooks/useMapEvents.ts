'use client'

import { useEffect, useRef } from 'react';

import { useMapContext } from '../context';

import type { MapEventHandlers, MapMouseEvent, MapViewport } from '../types'
import type { MapMouseEvent as MapLibreMouseEvent } from 'maplibre-gl'

/**
 * Hook for subscribing to map events
 * Automatically cleans up event listeners on unmount
 *
 * Handlers are stored in a ref so callers don't need to memoize the
 * `handlers` object — the underlying map listeners are attached once
 * (per `isLoaded`) and always call the latest handler implementations.
 */
export function useMapEvents(handlers: MapEventHandlers) {
  const { mapRef, setViewport, setHoveredFeature, isLoaded } = useMapContext()

  // Keep latest handlers without forcing re-subscription.
  const handlersRef = useRef(handlers)
  useEffect(() => {
    handlersRef.current = handlers
  }, [handlers])

  useEffect(() => {
    const map = mapRef.current?.getMap()
    if (!map || !isLoaded) return

    const handleClick = (
      event: MapLibreMouseEvent & { features?: GeoJSON.Feature[] }
    ) => {
      const onClick = handlersRef.current.onClick
      if (!onClick) return
      const mapEvent: MapMouseEvent = {
        lngLat: event.lngLat,
        point: event.point,
        features: event.features,
        originalEvent: event.originalEvent,
      }
      onClick(mapEvent)
    }

    const handleMouseMove = (
      event: MapLibreMouseEvent & { features?: GeoJSON.Feature[] }
    ) => {
      const onHover = handlersRef.current.onHover
      if (!onHover) return
      const feature = event.features?.[0] ?? null
      setHoveredFeature(feature)
      const mapEvent: MapMouseEvent = {
        lngLat: event.lngLat,
        point: event.point,
        features: event.features,
        originalEvent: event.originalEvent,
      }
      onHover(mapEvent)
    }

    const handleMoveStart = () => {
      handlersRef.current.onMoveStart?.()
    }

    const handleMoveEnd = () => {
      const center = map.getCenter()
      const newViewport: MapViewport = {
        longitude: center.lng,
        latitude: center.lat,
        zoom: map.getZoom(),
        bearing: map.getBearing(),
        pitch: map.getPitch(),
      }
      setViewport(newViewport)
      handlersRef.current.onMoveEnd?.(newViewport)
    }

    const handleZoomStart = () => {
      handlersRef.current.onZoomStart?.()
    }

    const handleZoomEnd = () => {
      handlersRef.current.onZoomEnd?.(map.getZoom())
    }

    map.on('click', handleClick)
    map.on('mousemove', handleMouseMove)
    map.on('movestart', handleMoveStart)
    map.on('moveend', handleMoveEnd)
    map.on('zoomstart', handleZoomStart)
    map.on('zoomend', handleZoomEnd)

    return () => {
      map.off('click', handleClick)
      map.off('mousemove', handleMouseMove)
      map.off('movestart', handleMoveStart)
      map.off('moveend', handleMoveEnd)
      map.off('zoomstart', handleZoomStart)
      map.off('zoomend', handleZoomEnd)
    }
  }, [mapRef, isLoaded, setViewport, setHoveredFeature])

  // Fire onLoad once the map reports loaded.
  useEffect(() => {
    if (isLoaded) {
      handlersRef.current.onLoad?.()
    }
  }, [isLoaded])
}
