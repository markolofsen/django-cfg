'use client'

/**
 * GeocoderControl — the thin map-bound wrapper around `GeocoderInput`.
 *
 * Renders the autocomplete as an on-map control (a positioned overlay, top-
 * left by default). On select it flies the camera to the picked coordinate
 * via `useMapControl().flyTo`, optionally drops a marker, and calls an
 * optional `onResult`. Biases search to the current map center (`near`).
 *
 * Must live inside a `<MapProvider>` (i.e. rendered as a child of
 * `MapContainer`). The `data-map-control` attribute is load-bearing: the
 * scroll-protection re-lock skips clicks inside it so the input stays usable.
 */

import { useCallback, useState } from 'react'

import { cn } from '@djangocfg/ui-core/lib'

import { useMapControl } from '../hooks/useMapControl'
import { useMapViewport } from '../hooks/useMapViewport'
import { GeocoderInput } from './GeocoderInput'
import { MapMarker } from './MapMarker'
import { cameraForResult } from '../geocode'
import type { GeocodeResult, ResolveGeocode } from '../geocode'
import type { MarkerData } from '../types'

type ControlCorner = 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'

const cornerClass: Record<ControlCorner, string> = {
  'top-left': 'top-3 left-3',
  'top-right': 'top-3 right-3',
  'bottom-left': 'bottom-3 left-3',
  'bottom-right': 'bottom-3 right-3',
}

export interface GeocoderControlProps {
  /** Injectable resolver. Defaults to public Photon (`photonResolve`). */
  resolve?: ResolveGeocode
  /** On-map corner for the search box. Default `top-left`. */
  position?: ControlCorner
  /** Input placeholder. */
  placeholder?: string
  /**
   * Override the smart zoom. By default the camera fits the result's extent
   * (`bbox`) when available, else flies to a zoom chosen by the result kind
   * (country/city/street/house…). Set this to force a fixed fly-to zoom for
   * every pick instead.
   */
  zoom?: number
  /** Padding (px) around a fitted bounding box. Default 48. */
  fitPadding?: number
  /** Cap the zoom when fitting tiny extents (avoid over-zoom). Default 16. */
  fitMaxZoom?: number
  /** Drop a pin at the picked location. Default `true`. */
  marker?: boolean
  /** Called with the chosen result after the camera flies. */
  onResult?: (result: GeocodeResult) => void
  /** Max results. Default 5. */
  limit?: number
  /**
   * Controlled visibility of the search input. When omitted the control is
   * uncontrolled and the input is always visible (the standalone, always-on
   * usage). Pass `open` (with `onClose`) to drive it from a toolbar toggle.
   */
  open?: boolean
  /** Called when the input requests to close (Esc / select). Controlled mode. */
  onClose?: () => void
  /** Focus the input when it appears. Default `false`. */
  autoFocus?: boolean
  className?: string
}

export function GeocoderControl({
  resolve,
  position = 'top-left',
  placeholder,
  zoom,
  fitPadding = 48,
  fitMaxZoom = 16,
  marker = true,
  onResult,
  limit,
  open,
  onClose,
  autoFocus = false,
  className,
}: GeocoderControlProps) {
  const { flyTo, fitBounds } = useMapControl()
  const { center } = useMapViewport()
  const [pin, setPin] = useState<MarkerData | null>(null)

  // Uncontrolled (no `open` prop) → always visible, like the original
  // always-on control. Controlled → the host (toolbar chip) owns visibility.
  const isControlled = open !== undefined
  const inputVisible = isControlled ? open : true

  const handleSelect = useCallback(
    (result: GeocodeResult) => {
      // Smart zoom: a fixed `zoom` override wins; otherwise fit the result's
      // extent (island, street, district frame themselves) and fall back to a
      // kind-based zoom for point results with no bbox.
      const cam = cameraForResult(result)
      if (zoom !== undefined) {
        flyTo([result.lng, result.lat], zoom)
      } else if (cam.type === 'fit') {
        fitBounds(cam.bbox, { padding: fitPadding, maxZoom: fitMaxZoom })
      } else {
        flyTo(cam.center, cam.zoom)
      }
      if (marker) {
        setPin({
          id: `geocoder-${result.id}`,
          longitude: result.lng,
          latitude: result.lat,
          data: { label: result.label },
        })
      }
      onResult?.(result)
      // Picking a result dismisses the input in controlled (toolbar) mode.
      onClose?.()
    },
    [flyTo, fitBounds, zoom, fitPadding, fitMaxZoom, marker, onResult, onClose],
  )

  return (
    <>
      {inputVisible ? (
        <div
          data-map-control
          className={cn('absolute z-20 w-72 max-w-[calc(100%-1.5rem)]', cornerClass[position], className)}
          // Esc closes in controlled mode (the input also stops propagation
          // of its own Escape, but the wrapper catch covers the case where
          // focus has left the cmdk input).
          onKeyDown={(e) => {
            if (e.key === 'Escape' && isControlled) {
              e.stopPropagation()
              onClose?.()
            }
          }}
        >
          <GeocoderInput
            resolve={resolve}
            onSelect={handleSelect}
            placeholder={placeholder}
            near={{ lng: center[0], lat: center[1] }}
            limit={limit}
            autoFocus={autoFocus}
          />
        </div>
      ) : null}
      {pin ? <MapMarker marker={pin} ariaLabel={String(pin.data?.label ?? 'Result')} /> : null}
    </>
  )
}
