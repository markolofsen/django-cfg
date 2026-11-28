'use client'

import { MapProvider } from '../../context'
import { MapInner } from './MapInner'
import type { MapContainerProps } from './types'

export type { MapContainerProps, GeolocateOptions, GeolocatePosition } from './types'

export function MapContainer({
  children,
  initialViewport,
  className,
  ...props
}: MapContainerProps) {
  return (
    <div className={className} style={{ width: '100%', height: '100%', position: 'relative' }}>
      <MapProvider initialViewport={initialViewport}>
        <MapInner {...props} MapContainerComponent={MapContainer}>{children}</MapInner>
      </MapProvider>
    </div>
  )
}

/**
 * Use this when you need the map inside an existing MapProvider
 */
export function MapView(props: Omit<MapContainerProps, 'initialViewport'>) {
  return <MapInner {...props} MapContainerComponent={MapContainer} />
}
