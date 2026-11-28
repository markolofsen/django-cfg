'use client'

import type { ComponentType, ReactNode } from 'react'
import {
  Dialog,
  DialogContent,
  DialogTitle,
} from '@djangocfg/ui-core/components'

import type { MapViewport, MapStyleKey } from '../../types'
import type { GeocodeResult, ResolveGeocode } from '../../geocode'
import type { MapContainerProps, GeolocateOptions, GeolocatePosition } from './types'

/**
 * Fullscreen dialog — a fresh map seeded with the current viewport.
 *
 * The nested map is the public `MapContainer`, passed in as a prop so this
 * module never imports the folder index (which would form a cycle:
 * index → MapInner → FullscreenDialog → index).
 */
export function FullscreenDialog({
  MapContainer,
  open,
  onOpenChange,
  fullscreenTitle,
  viewport,
  effectiveStyle,
  interactiveLayerIds,
  openInMapsUrl,
  openInMapsLabel,
  googleMapsButton,
  basemapSwitcher,
  basemaps,
  onBasemapChange,
  terrainOn,
  terrainButton,
  terrainLabel,
  onTerrainChange,
  compassButton,
  compassLabel,
  geolocate,
  geolocateLabel,
  geolocateOptions,
  onGeolocate,
  onGeolocateError,
  geocoder,
  geocoderResolve,
  geocoderPlaceholder,
  onGeocoderResult,
  showResetButton,
  ariaLabel,
  onClose,
  children,
}: {
  MapContainer: ComponentType<MapContainerProps>
  open: boolean
  onOpenChange: (open: boolean) => void
  fullscreenTitle: string
  viewport: MapViewport
  effectiveStyle: MapStyleKey | string
  interactiveLayerIds: string[] | undefined
  openInMapsUrl: string | undefined
  openInMapsLabel: string
  googleMapsButton: boolean
  basemapSwitcher: boolean
  basemaps: MapStyleKey[] | undefined
  onBasemapChange: ((key: MapStyleKey) => void) | undefined
  terrainOn: boolean
  terrainButton: boolean
  terrainLabel: string
  onTerrainChange: ((enabled: boolean) => void) | undefined
  compassButton: boolean
  compassLabel: string
  geolocate: boolean
  geolocateLabel: string
  geolocateOptions: GeolocateOptions | undefined
  onGeolocate: ((pos: GeolocatePosition) => void) | undefined
  onGeolocateError: ((err: GeolocationPositionError) => void) | undefined
  geocoder: boolean
  geocoderResolve: ResolveGeocode | undefined
  geocoderPlaceholder: string | undefined
  onGeocoderResult: ((result: GeocodeResult) => void) | undefined
  showResetButton: boolean
  ariaLabel: string
  onClose: () => void
  children?: ReactNode
}) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent
        className="h-[90vh] w-[90vw] max-w-[1400px] overflow-hidden p-0 sm:rounded-xl"
        // The dialog's own X is suppressed — the map renders close as the
        // first chip in its top-right toolbar (via `onClose`), so close /
        // Google / reset share one tidy column like the inline map.
        closeButton={false}
      >
        <DialogTitle className="sr-only">{fullscreenTitle}</DialogTitle>
        {open && (
          <MapContainer
            initialViewport={viewport}
            // Carry the user's current basemap choice into fullscreen.
            mapStyle={effectiveStyle}
            interactiveLayerIds={interactiveLayerIds}
            attributionControl={false}
            reuseMaps={false}
            openInMapsUrl={openInMapsUrl}
            openInMapsLabel={openInMapsLabel}
            googleMapsButton={googleMapsButton}
            basemapSwitcher={basemapSwitcher}
            basemaps={basemaps}
            onBasemapChange={onBasemapChange}
            terrain={terrainOn}
            terrainButton={terrainButton}
            terrainLabel={terrainLabel}
            onTerrainChange={onTerrainChange}
            compassButton={compassButton}
            compassLabel={compassLabel}
            geolocate={geolocate}
            geolocateLabel={geolocateLabel}
            geolocateOptions={geolocateOptions}
            onGeolocate={onGeolocate}
            onGeolocateError={onGeolocateError}
            geocoder={geocoder}
            geocoderResolve={geocoderResolve}
            geocoderPlaceholder={geocoderPlaceholder}
            onGeocoderResult={onGeocoderResult}
            showResetButton={showResetButton}
            ariaLabel={ariaLabel}
            scrollProtection={false}
            fullscreenButton={false}
            onClose={onClose}
            className="h-full w-full"
          >
            {children}
          </MapContainer>
        )}
      </DialogContent>
    </Dialog>
  )
}
