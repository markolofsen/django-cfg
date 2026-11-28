'use client'

import { memo, type ReactNode } from 'react'
import { Popup } from 'react-map-gl/maplibre'

export interface MapPopupProps {
  longitude: number
  latitude: number
  onClose: () => void
  children: ReactNode
  anchor?: 'top' | 'bottom' | 'left' | 'right' | 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'
  closeOnClick?: boolean
  closeButton?: boolean
  className?: string
  maxWidth?: string
  offset?: number | [number, number]
}

export const MapPopup = memo(function MapPopup({
  longitude,
  latitude,
  onClose,
  children,
  anchor = 'bottom',
  closeOnClick = true,
  closeButton = true,
  className,
  maxWidth = '300px',
  offset = 15,
}: MapPopupProps) {
  return (
    <Popup
      longitude={longitude}
      latitude={latitude}
      anchor={anchor}
      onClose={onClose}
      closeOnClick={closeOnClick}
      closeButton={closeButton}
      className={className}
      maxWidth={maxWidth}
      offset={offset}
    >
      {children}
    </Popup>
  )
})
