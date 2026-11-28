'use client'

import { useCallback, useEffect, useRef, useState, type ComponentType } from 'react'
import Map, {
  type ViewStateChangeEvent,
  type GeolocateControlInstance,
} from 'react-map-gl/maplibre'
import 'maplibre-gl/dist/maplibre-gl.css'

import { useMapContext } from '../../context'
import { useCompass, useMapScrollProtection, useMapTouchMode, useTerrain } from '../../hooks'
import { MapToolbar } from './MapToolbar'
import { ScrollLockOverlay } from './ScrollLockOverlay'
import { RotateHint } from './RotateHint'
import { FullscreenDialog } from './FullscreenDialog'
import { GeolocateHandle, type GeolocateState } from './GeolocateHandle'
import { GeocoderControl } from '../GeocoderControl'
import { useBasemapState } from './hooks/useBasemapState'
import { useExternalMapsUrl } from './hooks/useExternalMapsUrl'
import { useAutoReset } from './hooks/useAutoReset'
import type { MapContainerProps, MapInnerProps } from './types'

export function MapInner({
  children,
  mapStyle = 'light',
  interactiveLayerIds,
  style,
  cursor,
  attributionControl = false,
  // `reuseMaps` pools maplibre instances across mounts. It saves init cost
  // but in practice (Storybook HMR, switching stories, chat lists mounting/
  // unmounting map blocks) a reused instance comes back with no style —
  // a blank white map that never requests its style.json. Default OFF for
  // correctness; opt back in for a single long-lived full-page map.
  reuseMaps = false,
  openInMapsUrl,
  openInMapsLabel = 'Open in Maps',
  googleMapsButton = true,
  autoResetDelay = 0,
  showResetButton = false,
  scrollProtection = true,
  scrollProtectionHint = 'Click to interact',
  mobileBreakpoint,
  fullscreenButton = true,
  fullscreenLabel = 'Expand map',
  fullscreenTitle = 'Map',
  basemapSwitcher = true,
  basemaps,
  basemapLabel = 'Map style',
  onBasemapChange,
  terrain = false,
  terrainButton = true,
  terrainLabel = '3D terrain',
  onTerrainChange,
  compassButton = true,
  compassLabel = 'Reset bearing to north',
  geolocate = false,
  geolocateLabel = 'Show your location',
  geolocateOptions,
  onGeolocate,
  onGeolocateError,
  geocoder = false,
  geocoderResolve,
  geocoderPlaceholder,
  onGeocoderResult,
  onClose,
  ariaLabel = 'Interactive map',
  MapContainerComponent,
}: MapInnerProps & { MapContainerComponent: ComponentType<MapContainerProps> }) {
  const { mapRef, viewport, setViewport, setIsLoaded, resetToInitial, initialViewport } = useMapContext()

  // Active basemap — seeded from `mapStyle`, then driven by the switcher.
  const { activeKey, effectiveStyle, resolvedStyle, basemapOptions, handleBasemapPick } =
    useBasemapState({ mapStyle, basemaps, onBasemapChange })

  // 3D terrain — seeded from the `terrain` prop, then driven by the chip.
  const [terrainOn, setTerrainOn] = useState(terrain)
  useEffect(() => setTerrainOn(terrain), [terrain])
  useTerrain({ enabled: terrainOn })

  // Brief gesture hint when 3D turns on — rotation/tilt isn't discoverable
  // (it's right-drag / Ctrl+drag), so surface it, then auto-hide.
  const [showRotateHint, setShowRotateHint] = useState(false)
  useEffect(() => {
    if (!terrainOn) {
      setShowRotateHint(false)
      return
    }
    setShowRotateHint(true)
    const t = setTimeout(() => setShowRotateHint(false), 4500)
    return () => clearTimeout(t)
  }, [terrainOn])
  const handleTerrainToggle = useCallback(() => {
    setTerrainOn((prev) => {
      const next = !prev
      onTerrainChange?.(next)
      return next
    })
  }, [onTerrainChange])

  // Compass — reset the camera to a north-up, top-down view. Google-style:
  // the chip only shows when the view is rotated or tilted, and its needle
  // rotates to reflect the current bearing. One click eases back to north.
  // Math/reset live in `useCompass`; the toolbar gates the chip on it.
  const { bearing, isOriented, resetNorth } = useCompass()

  // Locate-me (GPS). Drives maplibre's built-in GeolocateControl via its
  // instance ref; the chip calls `trigger()` and reflects active/error from
  // the control's events. Privacy: the control is only mounted when
  // `geolocate` is true, and nothing prompts permission until the chip is
  // pressed (`trigger()`) — never on mount.
  const geolocateRef = useRef<GeolocateControlInstance | null>(null)
  const [geolocateState, setGeolocateState] = useState<GeolocateState>('idle')
  const handleGeolocateTrigger = useCallback(() => {
    // A new trigger after an error is a retry — clear the disabled look so
    // the events can re-drive state.
    setGeolocateState((s) => (s === 'error' ? 'idle' : s))
    geolocateRef.current?.trigger()
  }, [])

  // Geocoder search — a toolbar magnifier chip toggles an on-map autocomplete
  // (Google-Maps style). Collapsed by default; the chip flips `geocoderOpen`,
  // which mounts the controlled `GeocoderControl` (autofocused). Picking a
  // result / Esc / re-clicking the chip closes it.
  const [geocoderOpen, setGeocoderOpen] = useState(false)
  const handleGeocoderToggle = useCallback(() => setGeocoderOpen((o) => !o), [])
  const closeGeocoder = useCallback(() => setGeocoderOpen(false), [])

  // External-maps link (host URL wins, else Google Maps at current center).
  const { externalMapsUrl, externalMapsLabel } = useExternalMapsUrl({
    openInMapsUrl,
    openInMapsLabel,
    googleMapsButton,
    viewport,
  })

  // Fullscreen — opens a fresh map in a large dialog, seeded with the
  // viewport the user is currently looking at.
  const [fullscreenOpen, setFullscreenOpen] = useState(false)

  // `onClose` is only ever passed to the dialog's own (fullscreen) map, so
  // it doubles as "this instance is the expanded one" — there gestures are
  // always live.
  const isFullscreenInstance = !!onClose

  // Gesture mode. Touch / narrow inline maps are made fully static (a
  // finger drags the PAGE, never the map); the user taps to expand into
  // the fullscreen dialog where the map is fully interactive. Desktop
  // keeps the Google-Maps scroll-isolation. The expanded map is always
  // live. Detection is `matchMedia`-based so it reacts to DevTools device
  // emulation, real touchscreens and window resizes (see useMapTouchMode).
  // `mobileBreakpoint` lets a narrow-column embed (chat transcript < md) opt
  // out of width-based mobile collapse: pass 0 → only a real coarse pointer
  // (touchscreen) triggers the mobile preview, not the column's width. When
  // undefined, useMapTouchMode keeps its 768px default.
  const isTouch = useMapTouchMode(mobileBreakpoint)
  const protectionMode = !scrollProtection || isFullscreenInstance
    ? 'off'
    : isTouch
      ? 'mobile'
      : 'desktop'

  const { locked, unlock, isMobileLock } = useMapScrollProtection(protectionMode)

  // Overlay tap: desktop unlocks in place; mobile opens fullscreen.
  const handleOverlayActivate = useCallback(() => {
    if (isMobileLock) {
      setFullscreenOpen(true)
    } else {
      unlock()
    }
  }, [isMobileLock, unlock])

  // Hint adapts to the gesture model.
  const resolvedHint = isMobileLock ? 'Tap to expand' : scrollProtectionHint

  // Check if viewport has changed from initial
  const hasViewportChanged =
    Math.abs(viewport.longitude - initialViewport.longitude) > 0.0001 ||
    Math.abs(viewport.latitude - initialViewport.latitude) > 0.0001 ||
    Math.abs(viewport.zoom - initialViewport.zoom) > 0.1

  const handleMove = useCallback(
    (evt: ViewStateChangeEvent) => {
      setViewport({
        longitude: evt.viewState.longitude,
        latitude: evt.viewState.latitude,
        zoom: evt.viewState.zoom,
        bearing: evt.viewState.bearing,
        pitch: evt.viewState.pitch,
      })
    },
    [setViewport]
  )

  const { handleMoveStart, handleMoveEnd } = useAutoReset({ autoResetDelay, resetToInitial })

  const handleLoad = useCallback(() => {
    setIsLoaded(true)
  }, [setIsLoaded])

  return (
    <>
      <Map
        ref={mapRef}
        {...viewport}
        onMove={handleMove}
        onMoveStart={handleMoveStart}
        onMoveEnd={handleMoveEnd}
        onLoad={handleLoad}
        mapStyle={resolvedStyle}
        interactiveLayerIds={interactiveLayerIds}
        // `compact` collapses the credit line into a single "ⓘ" that expands on
        // click. CARTO and OSM require the attribution to be present, so it is
        // not removed — it stops occupying the bottom edge of the canvas, which
        // is what Google and Airbnb do with theirs.
        attributionControl={attributionControl ? { compact: true } : false}
        reuseMaps={reuseMaps}
        style={{
          width: '100%',
          height: '100%',
          ...style,
        }}
        cursor={cursor}
        aria-label={ariaLabel}
      >
        {geolocate && (
          <GeolocateHandle
            ref={geolocateRef}
            options={geolocateOptions ?? {}}
            onGeolocate={onGeolocate}
            onGeolocateError={onGeolocateError}
            onStateChange={setGeolocateState}
          />
        )}
        {/* Toolbar-toggled geocoder. Controlled (open driven by the chip),
            autofocused on reveal. Rendered inside <Map> so its dropped pin
            (a react-map-gl Marker) has the map context; the input overlay is
            absolute-positioned top-left, clear of the top-right chip column. */}
        {geocoder && (
          <GeocoderControl
            open={geocoderOpen}
            onClose={closeGeocoder}
            autoFocus
            resolve={geocoderResolve}
            placeholder={geocoderPlaceholder}
            onResult={onGeocoderResult}
          />
        )}
        {children}
      </Map>

      {locked && (
        <ScrollLockOverlay
          isMobileLock={isMobileLock}
          resolvedHint={resolvedHint}
          onActivate={handleOverlayActivate}
        />
      )}

      <MapToolbar
        onClose={onClose}
        fullscreenButton={fullscreenButton}
        fullscreenLabel={fullscreenLabel}
        onFullscreenOpen={() => setFullscreenOpen(true)}
        basemapSwitcher={basemapSwitcher}
        basemapOptions={basemapOptions}
        basemapLabel={basemapLabel}
        activeKey={activeKey}
        onBasemapPick={handleBasemapPick}
        terrainButton={terrainButton}
        terrainLabel={terrainLabel}
        terrainOn={terrainOn}
        onTerrainToggle={handleTerrainToggle}
        compassButton={compassButton}
        isOriented={isOriented}
        compassLabel={compassLabel}
        bearing={bearing}
        onResetNorth={resetNorth}
        geolocate={geolocate}
        geolocateLabel={geolocateLabel}
        geolocateState={geolocateState}
        onGeolocateTrigger={handleGeolocateTrigger}
        geocoder={geocoder}
        geocoderOpen={geocoderOpen}
        onGeocoderToggle={handleGeocoderToggle}
        externalMapsUrl={externalMapsUrl}
        externalMapsLabel={externalMapsLabel}
        showResetButton={showResetButton}
        hasViewportChanged={hasViewportChanged}
        onResetToInitial={resetToInitial}
      />

      <RotateHint show={showRotateHint} />

      {fullscreenButton && (
        <FullscreenDialog
          MapContainer={MapContainerComponent}
          open={fullscreenOpen}
          onOpenChange={setFullscreenOpen}
          fullscreenTitle={fullscreenTitle}
          viewport={viewport}
          effectiveStyle={effectiveStyle}
          interactiveLayerIds={interactiveLayerIds}
          openInMapsUrl={openInMapsUrl}
          openInMapsLabel={openInMapsLabel}
          googleMapsButton={googleMapsButton}
          basemapSwitcher={basemapSwitcher}
          basemaps={basemaps}
          onBasemapChange={onBasemapChange}
          terrainOn={terrainOn}
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
          onClose={() => setFullscreenOpen(false)}
        >
          {children}
        </FullscreenDialog>
      )}
    </>
  )
}
