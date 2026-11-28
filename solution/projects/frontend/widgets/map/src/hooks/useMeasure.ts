'use client'

import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { length as turfLength, area as turfArea } from '@turf/turf'

import { useMapContext } from '../context'
import { createLineString, createPolygon, createFeatureCollection } from '../utils'
import type { MapMouseEvent as MapLibreMouseEvent } from 'maplibre-gl'

/** Measure interaction mode. */
export type MeasureMode = 'distance' | 'area'

export interface UseMeasureResult {
  /** Current measure mode (`'distance'` = path length, `'area'` = polygon area). */
  mode: MeasureMode
  /** Switch the measure mode. Clears the in-progress vertices. */
  setMode: (mode: MeasureMode) => void
  /** Vertices collected so far, as `[lng, lat]` pairs in click order. */
  points: [number, number][]
  /**
   * The collected geometry as a FeatureCollection ready for `MapSource`.
   * A LineString in `'distance'` mode, a Polygon in `'area'` mode (empty
   * until enough vertices exist to form the geometry).
   */
  geojson: GeoJSON.FeatureCollection
  /**
   * The running total — kilometres in `'distance'` mode, square metres in
   * `'area'` mode. `0` until at least two (distance) / three (area) points.
   */
  total: number
  /** Human-readable total, e.g. `"1.24 km"`, `"3,420 m²"`, `"0.34 km²"`. */
  totalLabel: string
  /** Remove all collected vertices. */
  clear: () => void
  /** Whether the measure interaction is listening for map clicks. */
  active: boolean
  /** Start / stop listening for map clicks. Stopping clears the vertices. */
  setActive: (active: boolean) => void
}

const numberFormat = new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 })

/** Format a distance in kilometres into a compact `m`/`km` label. */
function formatDistance(km: number): string {
  if (km <= 0) return '0 m'
  if (km < 1) return `${numberFormat.format(km * 1000)} m`
  return `${km.toFixed(2)} km`
}

/** Format an area in square metres into a compact `m²`/`km²` label. */
function formatArea(m2: number): string {
  if (m2 <= 0) return '0 m²'
  if (m2 < 1_000_000) return `${numberFormat.format(m2)} m²`
  return `${(m2 / 1_000_000).toFixed(2)} km²`
}

/**
 * Click-to-measure interaction for the Map tool.
 *
 * Subscribes to map clicks while `active` and appends each `[lng, lat]` to
 * the vertex list, recomputing a running total with turf:
 * - `'distance'` → a LineString, total via `turf.length` (km).
 * - `'area'` → a Polygon, total via `turf.area` (m²).
 *
 * Geometry is built with the tool's own `createLineString` / `createPolygon`
 * helpers so it matches house style and renders through the existing
 * `createLineLayer` / `createPolygonLayer` factories.
 *
 * Must be used inside a `MapProvider` (it reads `useMapContext`).
 */
export function useMeasure(initialMode: MeasureMode = 'distance'): UseMeasureResult {
  const { mapRef, isLoaded } = useMapContext()

  const [mode, setModeState] = useState<MeasureMode>(initialMode)
  const [active, setActiveState] = useState(false)
  const [points, setPoints] = useState<[number, number][]>([])

  // Latest mode/active read inside the (re-subscribed only on isLoaded) click
  // handler, so changing mode/active never re-binds the underlying listener.
  const modeRef = useRef(mode)
  const activeRef = useRef(active)
  useEffect(() => {
    modeRef.current = mode
  }, [mode])
  useEffect(() => {
    activeRef.current = active
  }, [active])

  const clear = useCallback(() => {
    setPoints([])
  }, [])

  const setMode = useCallback((next: MeasureMode) => {
    setModeState(next)
    setPoints([])
  }, [])

  const setActive = useCallback((next: boolean) => {
    setActiveState(next)
    // Stopping the interaction discards the in-progress measurement.
    if (!next) setPoints([])
  }, [])

  // Subscribe to map clicks. Listener is attached once per `isLoaded`; the
  // handler reads the latest mode/active via refs (same pattern as
  // `useMapEvents`).
  useEffect(() => {
    const map = mapRef.current?.getMap()
    if (!map || !isLoaded) return

    const handleClick = (event: MapLibreMouseEvent) => {
      if (!activeRef.current) return
      const { lng, lat } = event.lngLat
      setPoints((prev) => [...prev, [lng, lat]])
    }

    map.on('click', handleClick)
    return () => {
      map.off('click', handleClick)
    }
  }, [mapRef, isLoaded])

  // Reflect the active state as a crosshair cursor on the map canvas.
  useEffect(() => {
    const map = mapRef.current?.getMap()
    if (!map || !isLoaded) return
    const canvas = map.getCanvas()
    if (!canvas) return
    const previous = canvas.style.cursor
    if (active) canvas.style.cursor = 'crosshair'
    return () => {
      canvas.style.cursor = previous
    }
  }, [mapRef, isLoaded, active])

  const geojson = useMemo<GeoJSON.FeatureCollection>(() => {
    if (mode === 'distance') {
      if (points.length < 2) return createFeatureCollection()
      return createFeatureCollection([createLineString(points)])
    }
    if (points.length < 3) return createFeatureCollection()
    return createFeatureCollection([createPolygon(points)])
  }, [mode, points])

  const total = useMemo<number>(() => {
    if (mode === 'distance') {
      if (points.length < 2) return 0
      return turfLength(createLineString(points), { units: 'kilometers' })
    }
    if (points.length < 3) return 0
    return turfArea(createPolygon(points))
  }, [mode, points])

  const totalLabel = useMemo<string>(
    () => (mode === 'distance' ? formatDistance(total) : formatArea(total)),
    [mode, total]
  )

  return {
    mode,
    setMode,
    points,
    geojson,
    total,
    totalLabel,
    clear,
    active,
    setActive,
  }
}
