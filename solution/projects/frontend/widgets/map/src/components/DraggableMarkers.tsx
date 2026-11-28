'use client'

import { memo, type ReactNode } from 'react'

import { MapMarker } from './MapMarker'
import {
  useDraggableMarkers,
  type DraggablePoint,
} from '../hooks/useDraggableMarkers'
import type { MarkerData } from '../types'

export type { DraggablePoint }

export interface DraggableMarkersProps {
  /** Controlled list of draggable positions. */
  positions: DraggablePoint[]
  /**
   * Fires with the full, updated array when a marker is dropped (drag-end).
   * The host persists `next` and feeds it back via `positions`.
   */
  onChange: (next: DraggablePoint[]) => void
  /** Optional live callback fired on every drag frame (not committed). */
  onDragMove?: (id: string, lng: number, lat: number) => void
  /** Pin color (passed through to `MapMarker`). */
  color?: string
  /** Pin size in px (passed through to `MapMarker`). */
  size?: number
  /** Custom marker renderer; replaces the default pin. */
  renderMarker?: (marker: MarkerData) => ReactNode
}

/**
 * Thin controlled component that renders one draggable `MapMarker` per
 * position. Must be mounted inside `<MapProvider>` (i.e. as a child of
 * `MapContainer` / `MapView`), like `MapLegend`.
 *
 * Dragging a pin commits its new `{ lng, lat }` through `onChange`. The
 * maplibre `LngLat` object delivered by the drag callbacks is normalized to
 * plain numbers inside `useDraggableMarkers`.
 */
function DraggableMarkersComponent({
  positions,
  onChange,
  onDragMove,
  color,
  size,
  renderMarker,
}: DraggableMarkersProps) {
  const { markers, getHandlers } = useDraggableMarkers({
    positions,
    onChange,
    onDragMove,
  })

  return (
    <>
      {markers.map((marker) => {
        const handlers = getHandlers(marker.id)
        return (
          <MapMarker
            key={marker.id}
            marker={marker}
            draggable
            color={color}
            size={size}
            ariaLabel={`Draggable marker ${marker.id}`}
            onDragStart={handlers.onDragStart}
            onDrag={handlers.onDrag}
            onDragEnd={handlers.onDragEnd}
          >
            {renderMarker ? renderMarker(marker) : undefined}
          </MapMarker>
        )
      })}
    </>
  )
}

export const DraggableMarkers = memo(DraggableMarkersComponent)
