'use client'

import {
  NavigationControl,
  FullscreenControl,
  GeolocateControl,
  ScaleControl,
} from 'react-map-gl/maplibre'

import type { FitBoundsOptions } from 'maplibre-gl'

type ControlPosition = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'

export interface MapControlsProps {
  position?: ControlPosition
  showNavigation?: boolean
  showFullscreen?: boolean
  /** Show maplibre's raw `GeolocateControl` (track mode). @default false */
  showGeolocate?: boolean
  /**
   * Draw a heading arrow on the location dot. Forwarded to the control; a
   * no-op on maplibre versions without heading support.
   */
  showUserHeading?: boolean
  /**
   * Draw the translucent accuracy circle around the dot.
   * @default true (maplibre default)
   */
  showAccuracyCircle?: boolean
  /** Browser Geolocation API `PositionOptions` (enableHighAccuracy, timeout…). */
  positionOptions?: PositionOptions
  /** Options used when the control eases the camera to the user's location. */
  fitBoundsOptions?: FitBoundsOptions
  showScale?: boolean
  scaleUnit?: 'imperial' | 'metric' | 'nautical'
}

export function MapControls({
  position = 'top-right',
  showNavigation = true,
  showFullscreen = false,
  showGeolocate = false,
  showUserHeading,
  showAccuracyCircle,
  positionOptions,
  fitBoundsOptions,
  showScale = false,
  scaleUnit = 'metric',
}: MapControlsProps) {
  return (
    <>
      {showNavigation && (
        <NavigationControl position={position} showCompass showZoom />
      )}
      {showFullscreen && <FullscreenControl position={position} />}
      {showGeolocate && (
        <GeolocateControl
          position={position}
          trackUserLocation
          // All optional — undefined falls back to maplibre's own defaults,
          // so existing `showGeolocate` callers are unaffected.
          {...(showUserHeading !== undefined ? { showUserHeading } : {})}
          {...(showAccuracyCircle !== undefined ? { showAccuracyCircle } : {})}
          {...(positionOptions !== undefined ? { positionOptions } : {})}
          {...(fitBoundsOptions !== undefined ? { fitBoundsOptions } : {})}
        />
      )}
      {showScale && <ScaleControl unit={scaleUnit} />}
    </>
  )
}
