'use client'

import { useCallback, useMemo, useState } from 'react'
import type { LngLat } from 'maplibre-gl'

import type { MarkerData } from '../types'

/**
 * A single controlled, draggable position.
 *
 * This is the host-facing shape: `{ id, lng, lat }` plain numbers (plus an
 * optional `label`). It is intentionally *not* `MarkerData` — `MarkerData`
 * uses `longitude`/`latitude` and is the map's internal marker store shape.
 */
export interface DraggablePoint {
  id: string
  lng: number
  lat: number
  label?: string
}

export interface UseDraggableMarkersOptions {
  /** Controlled list of positions. The host owns this array. */
  positions: DraggablePoint[]
  /**
   * Fires with the full, updated array when a marker is dropped (drag-end).
   * The host persists `next` and feeds it back via `positions`.
   */
  onChange: (next: DraggablePoint[]) => void
  /** Optional live callback fired on every drag frame (not committed). */
  onDragMove?: (id: string, lng: number, lat: number) => void
}

/** Drag handlers for one rendered marker, wired to a single position. */
export interface DraggableMarkerHandlers {
  onDragStart: () => void
  onDrag: (marker: MarkerData, lngLat: LngLat) => void
  onDragEnd: (marker: MarkerData, lngLat: LngLat) => void
}

export interface UseDraggableMarkersResult {
  /**
   * The positions to render, as `MarkerData` (the map's marker shape).
   * While a marker is being dragged its entry reflects the live cursor
   * position so the pin follows the pointer smoothly; everything else mirrors
   * `positions` 1:1.
   */
  markers: MarkerData[]
  /** Returns the drag handlers for the marker with the given `id`. */
  getHandlers: (id: string) => DraggableMarkerHandlers
}

/**
 * Controlled convenience layer over `MapMarker`'s native `draggable` /
 * `onDrag*` passthrough.
 *
 * `positions` in, `onChange` out — the host owns persistence. Internally the
 * hook only tracks a *transient* live-drag position so the pin follows the
 * cursor during `onDrag`; the committed source of truth stays in `positions`.
 * On drag-end it normalizes the maplibre `LngLat` object (`.lng`/`.lat`) to
 * plain numbers and emits the full updated array through `onChange`.
 */
export function useDraggableMarkers({
  positions,
  onChange,
  onDragMove,
}: UseDraggableMarkersOptions): UseDraggableMarkersResult {
  // Transient live-drag state: only the marker currently under the pointer.
  const [dragging, setDragging] = useState<{
    id: string
    lng: number
    lat: number
  } | null>(null)

  const markers = useMemo<MarkerData[]>(
    () =>
      positions.map((p) => {
        const live = dragging && dragging.id === p.id ? dragging : null
        return {
          id: p.id,
          longitude: live ? live.lng : p.lng,
          latitude: live ? live.lat : p.lat,
          data: p.label !== undefined ? { label: p.label } : undefined,
        }
      }),
    [positions, dragging]
  )

  const getHandlers = useCallback(
    (id: string): DraggableMarkerHandlers => ({
      onDragStart: () => {
        const p = positions.find((pos) => pos.id === id)
        if (!p) return
        setDragging({ id, lng: p.lng, lat: p.lat })
      },
      onDrag: (_marker, lngLat) => {
        setDragging({ id, lng: lngLat.lng, lat: lngLat.lat })
        onDragMove?.(id, lngLat.lng, lngLat.lat)
      },
      onDragEnd: (_marker, lngLat) => {
        setDragging(null)
        const next = positions.map((pos) =>
          pos.id === id ? { ...pos, lng: lngLat.lng, lat: lngLat.lat } : pos
        )
        onChange(next)
      },
    }),
    [positions, onChange, onDragMove]
  )

  return { markers, getHandlers }
}
