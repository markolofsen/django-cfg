'use client'

import { useCallback, memo, type ReactNode, type KeyboardEvent } from 'react'
import { Marker, type MarkerEvent, type MarkerDragEvent } from 'react-map-gl/maplibre'
import type { LngLat } from 'maplibre-gl'
import type { MarkerData } from '../types'

export interface MapMarkerProps {
  marker: MarkerData
  onClick?: (marker: MarkerData) => void
  children?: ReactNode
  anchor?: 'center' | 'top' | 'bottom' | 'left' | 'right' | 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'
  draggable?: boolean
  onDragStart?: (marker: MarkerData) => void
  onDrag?: (marker: MarkerData, lngLat: LngLat) => void
  onDragEnd?: (marker: MarkerData, lngLat: LngLat) => void
  color?: string
  size?: number
  /** Accessible label for the marker (used when onClick is set) */
  ariaLabel?: string
}

const DefaultPin = memo(function DefaultPin({
  size = 24,
  color = '#ef4444'
}: {
  size?: number
  color?: string
}) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden="true"
      style={{ cursor: 'pointer' }}
    >
      <path
        d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"
        fill={color}
        stroke="#fff"
        strokeWidth="1.5"
      />
      <circle cx="12" cy="9" r="2.5" fill="#fff" />
    </svg>
  )
})

export const MapMarker = memo(function MapMarker({
  marker,
  onClick,
  children,
  anchor = 'bottom',
  draggable = false,
  onDragStart,
  onDrag,
  onDragEnd,
  color,
  size,
  ariaLabel,
}: MapMarkerProps) {
  const handleClick = useCallback(
    (e: MarkerEvent<MouseEvent>) => {
      e.originalEvent.stopPropagation()
      onClick?.(marker)
    },
    [onClick, marker]
  )

  const handleDragStart = useCallback(
    (_e: MarkerDragEvent) => {
      onDragStart?.(marker)
    },
    [onDragStart, marker]
  )

  const handleDrag = useCallback(
    (e: MarkerDragEvent) => {
      onDrag?.(marker, e.lngLat)
    },
    [onDrag, marker]
  )

  const handleDragEnd = useCallback(
    (e: MarkerDragEvent) => {
      onDragEnd?.(marker, e.lngLat)
    },
    [onDragEnd, marker]
  )

  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!onClick) return
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault()
        onClick(marker)
      }
    },
    [onClick, marker]
  )

  const content = children ?? <DefaultPin color={color} size={size} />

  return (
    <Marker
      longitude={marker.longitude}
      latitude={marker.latitude}
      anchor={anchor}
      draggable={draggable}
      onClick={handleClick}
      onDragStart={handleDragStart}
      onDrag={handleDrag}
      onDragEnd={handleDragEnd}
    >
      {onClick ? (
        <div
          role="button"
          tabIndex={0}
          aria-label={ariaLabel ?? `Map marker ${marker.id}`}
          onKeyDown={handleKeyDown}
          style={{ cursor: 'pointer', display: 'inline-flex', outline: 'none' }}
        >
          {content}
        </div>
      ) : (
        content
      )}
    </Marker>
  )
})
