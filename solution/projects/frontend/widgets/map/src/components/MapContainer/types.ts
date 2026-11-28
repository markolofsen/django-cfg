import type { ReactNode } from 'react'

import type { MapViewport, MapStyleKey } from '../../types'
import type { GeocodeResult, ResolveGeocode } from '../../geocode'

/**
 * Tunables forwarded to the maplibre `GeolocateControl` that backs the
 * locate-me chip. All optional; sensible privacy-friendly defaults.
 */
export interface GeolocateOptions {
  /**
   * Use the device's high-accuracy provider (GPS). More precise but slower
   * and battery-hungry — off by default.
   * @default false
   */
  highAccuracy?: boolean
  /**
   * Show a heading arrow on the location dot when a compass heading is
   * available. (No-op on maplibre versions without heading support.)
   * @default true
   */
  showHeading?: boolean
  /**
   * Draw the translucent accuracy circle (95% confidence) around the dot.
   * @default true
   */
  showAccuracyCircle?: boolean
  /**
   * Cap how far the camera zooms in when easing to the user (very accurate
   * fixes can otherwise zoom street-level).
   */
  fitBoundsMaxZoom?: number
}

/** A single successful position fix surfaced to `onGeolocate`. */
export interface GeolocatePosition {
  lat: number
  lng: number
  /** Accuracy radius in meters. */
  accuracy: number
  /** Compass heading in degrees (0 = north), or null when unknown. */
  heading: number | null
}

export interface MapContainerProps {
  children?: ReactNode
  initialViewport?: Partial<MapViewport>
  mapStyle?: MapStyleKey | string
  interactiveLayerIds?: string[]
  className?: string
  style?: React.CSSProperties
  cursor?: string
  /**
   * Show the CARTO / OpenStreetMap attribution pill. Off by default for a
   * clean embedded look. Note: CARTO & OSM licenses require attribution to
   * appear somewhere — if you hide it here, surface it elsewhere in your UI.
   * @default false
   */
  attributionControl?: boolean
  /**
   * Pool and reuse maplibre instances across mounts. Off by default — a
   * reused instance can come back style-less (blank map) under Storybook
   * HMR / story switches / chat lists. Enable only for a single, stable,
   * long-lived full-page map.
   * @default false
   */
  reuseMaps?: boolean
  /**
   * URL to open in an external maps app. When omitted, a Google Maps URL
   * is generated from the current center (see `googleMapsButton`). Pass
   * this to point at Apple Maps / a custom deep link instead.
   */
  openInMapsUrl?: string
  /** Label for the open in maps button */
  openInMapsLabel?: string
  /**
   * Show an "Open in Google Maps" button that deep-links to the current
   * center. Suppressed when `openInMapsUrl` is provided (the host link
   * takes over). Set `false` to hide it.
   * @default true
   */
  googleMapsButton?: boolean
  /** Auto-reset to initial viewport after N ms of inactivity (0 = disabled) */
  autoResetDelay?: number
  /** Show reset button */
  showResetButton?: boolean
  /**
   * Block wheel/trackpad zoom until the user clicks the map (Google Maps
   * style). Stops an inline map from hijacking the page scroll. Drag-pan,
   * touch and double-click zoom stay live. Click outside or move the
   * pointer off the map to re-lock.
   * @default true
   */
  scrollProtection?: boolean
  /** Hint shown on the lock overlay while scroll-zoom is blocked. */
  scrollProtectionHint?: string
  /**
   * Width (px) at/under which the map collapses to the touch/"mobile"
   * preview (gestures off, tap-to-expand) even with a fine pointer. Passed
   * to `useMapTouchMode`. Default 768 (Tailwind `md`).
   *
   * Set `0` to OPT OUT of width-based collapse — the map then only goes
   * mobile on a real coarse pointer (touchscreen), not because its column
   * is narrow. Use this for a map embedded in a narrow column (e.g. a chat
   * transcript < 768px) that should keep the desktop scroll-lock + controls.
   * @default 768
   */
  mobileBreakpoint?: number
  /**
   * Show a button that opens the map full-screen in a large dialog
   * (Google-Maps-style "expand"). Scroll protection is off inside the
   * dialog since the map already fills the screen.
   * @default true
   */
  fullscreenButton?: boolean
  /** Accessible / tooltip label for the fullscreen button. */
  fullscreenLabel?: string
  /** Title for the fullscreen dialog (screen readers). */
  fullscreenTitle?: string
  /**
   * Show a basemap switcher (a Layers button → dropdown) in the toolbar,
   * Google-Maps style. Lets the user pick the map style at runtime.
   * @default true
   */
  basemapSwitcher?: boolean
  /**
   * Explicit list of basemap keys to offer in the switcher. When omitted,
   * the switcher shows all key-free built-ins (CARTO + OpenFreeMap) plus
   * `satellite` only if it's actually usable (host-keyed). See
   * `resolveBasemapOptions`.
   */
  basemaps?: MapStyleKey[]
  /** Accessible / tooltip label for the basemap switcher button. */
  basemapLabel?: string
  /** Notified when the user picks a basemap from the switcher. */
  onBasemapChange?: (key: MapStyleKey) => void
  /**
   * Render 3D terrain + hillshade from the free AWS Terrarium DEM (no API
   * key). Eases the camera pitch in so it reads as 3D; toggles off cleanly.
   * @default false
   */
  terrain?: boolean
  /**
   * Show a toolbar chip (a Mountain icon) that toggles 3D terrain at
   * runtime, in the same top-right control column as the other chips.
   * @default true
   */
  terrainButton?: boolean
  /** Accessible / tooltip label for the terrain toggle button. */
  terrainLabel?: string
  /** Notified when the user toggles terrain from the chip. */
  onTerrainChange?: (enabled: boolean) => void
  /**
   * Show a compass chip that appears only when the map is rotated or
   * tilted (Google-style); its needle reflects the current bearing and a
   * click eases the camera back to a north-up, top-down view. Rotate/tilt
   * the map with right-drag, Ctrl+drag, or two fingers.
   * @default true
   */
  compassButton?: boolean
  /** Accessible / tooltip label for the compass (reset-north) button. */
  compassLabel?: string
  /**
   * Show a Google-style "locate me" chip that drives maplibre's built-in
   * `GeolocateControl` — centers + follows the user (track mode), with a
   * location dot + accuracy circle. Privacy: **off by default**; nothing
   * requests the OS permission prompt unless this is `true` AND the user
   * presses the chip. Requires a secure context (HTTPS / localhost).
   * @default false
   */
  geolocate?: boolean
  /** Accessible / tooltip label for the locate-me chip. */
  geolocateLabel?: string
  /** Tunables forwarded to the underlying `GeolocateControl`. */
  geolocateOptions?: GeolocateOptions
  /** Notified on each successful position fix while geolocation is active. */
  onGeolocate?: (pos: GeolocatePosition) => void
  /** Notified when geolocation fails (permission denied / unavailable / timeout). */
  onGeolocateError?: (err: GeolocationPositionError) => void
  /**
   * Show a Google-Maps-style search chip (a magnifier) in the toolbar that
   * toggles an on-map address/place autocomplete. Collapsed by default:
   * clicking the chip reveals an autofocused input (top-left), and clicking
   * it again / pressing Esc / picking a result hides it. Picking a result
   * flies the camera there and drops a pin. **Off by default** (opt-in).
   * @default false
   */
  geocoder?: boolean
  /**
   * Injectable geocode resolver for the search chip. Defaults to the
   * free, key-free public Photon endpoint. Pass a backend/route proxy in
   * production to dodge CORS + throttling.
   */
  geocoderResolve?: ResolveGeocode
  /** Placeholder for the search input. */
  geocoderPlaceholder?: string
  /** Notified with the chosen result after the camera flies to it. */
  onGeocoderResult?: (result: GeocodeResult) => void
  /**
   * When set, a close button is rendered as the FIRST chip in the
   * top-right control toolbar (used by the fullscreen dialog so the
   * close / Google / reset controls share one tidy column instead of
   * scattering the dialog's own X into a different corner).
   */
  onClose?: () => void
  /** Accessible label for the map region (screen readers) */
  ariaLabel?: string
}

export type MapInnerProps = Omit<MapContainerProps, 'initialViewport'>;
