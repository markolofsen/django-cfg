'use client'

import { forwardRef } from 'react'
import {
  GeolocateControl,
  type GeolocateControlInstance,
  type GeolocateResultEvent,
  type GeolocateErrorEvent,
} from 'react-map-gl/maplibre'

import type { GeolocateOptions, GeolocatePosition } from './types'

/** The follow-state our chip reflects, derived from the control's events. */
export type GeolocateState = 'idle' | 'active' | 'error'

interface GeolocateHandleProps {
  options: GeolocateOptions
  onGeolocate?: (pos: GeolocatePosition) => void
  onGeolocateError?: (err: GeolocationPositionError) => void
  onStateChange: (state: GeolocateState) => void
}

/**
 * The maplibre `GeolocateControl`, rendered as a child of `<Map>` so its
 * location dot + accuracy circle draw on the map, but with the default
 * control button **hidden** (`display:none`) — our `MapToolbar` chip is the
 * UI and drives it via the forwarded instance ref (`control.trigger()`).
 *
 * `trackUserLocation` gives Google-style follow: first activation centers +
 * follows; panning away drops to passive; re-trigger re-follows. We reflect
 * active/error back to the chip through `onStateChange`.
 *
 * Note: maplibre-gl 4.7.1's `GeolocateControlOptions` has no `showUserHeading`
 * field, so heading is surfaced via `onGeolocate` (and `showHeading` is a
 * forward-compatible no-op on this version).
 */
export const GeolocateHandle = forwardRef<GeolocateControlInstance, GeolocateHandleProps>(
  function GeolocateHandle({ options, onGeolocate, onGeolocateError, onStateChange }, ref) {
    return (
      <GeolocateControl
        ref={ref}
        // Hidden: our chip is the UI. The dot + accuracy circle are map
        // layers (not this button), so they still render.
        style={{ display: 'none' }}
        trackUserLocation
        showUserLocation
        showAccuracyCircle={options.showAccuracyCircle ?? true}
        positionOptions={{ enableHighAccuracy: options.highAccuracy ?? false }}
        fitBoundsOptions={
          options.fitBoundsMaxZoom != null ? { maxZoom: options.fitBoundsMaxZoom } : undefined
        }
        onGeolocate={(e: GeolocateResultEvent) => {
          const c = e.coords
          onGeolocate?.({
            lat: c.latitude,
            lng: c.longitude,
            accuracy: c.accuracy,
            heading: c.heading != null && !Number.isNaN(c.heading) ? c.heading : null,
          })
        }}
        onError={(e: GeolocateErrorEvent) => {
          onStateChange('error')
          onGeolocateError?.(e)
        }}
        onTrackUserLocationStart={() => onStateChange('active')}
        onTrackUserLocationEnd={() => onStateChange('idle')}
      />
    )
  },
)
