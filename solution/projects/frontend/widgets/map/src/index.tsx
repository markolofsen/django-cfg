'use client';

/**
 * The default entry, and the LAZY one.
 *
 * MapLibre GL is ~800 KB gzipped and only `MapContainer` imports it at
 * runtime, so the container arrives through a dynamic import and everything
 * else — markers, popups, layer factories, hooks, geometry — is re-exported
 * synchronously. Those are thin wrappers over `react-map-gl/maplibre` whose
 * `maplibre-gl` imports are TYPE-only and erase, so they cost tens of KB, not
 * the library.
 *
 * `@djangocfg/widget-map/eager` is the same surface with the container
 * imported statically. Reach for it only where the map is the page and the
 * placeholder is a flash — importing BOTH entries in one app defeats the
 * split, because the eager one is a static edge into the same chunk.
 *
 * All components are `'use client'`; never render them on the Next.js server.
 */

import * as React from 'react';
import { createLazyComponent, MapLoadingFallback } from './lazy';
import type { MapContainerProps } from './components/light';

// ============================================================================
// Lazy Components
// ============================================================================

/**
 * LazyMapContainer - Lazy-loaded map container
 *
 * Automatically shows loading state while MapLibre GL loads (~800KB)
 */
export const LazyMapContainer = createLazyComponent<MapContainerProps>(
  () =>
    import('./components/MapContainer').then((mod) => ({
      default: mod.MapContainer,
    })),
  {
    displayName: 'LazyMapContainer',
    fallback: <MapLoadingFallback minHeight={400} />,
  }
);

/**
 * LazyMapView - Lazy-loaded map view (alias for MapContainer)
 */
export const LazyMapView = createLazyComponent<Omit<MapContainerProps, 'initialViewport'>>(
  () =>
    import('./components/MapContainer').then((mod) => ({
      default: mod.MapView,
    })),
  {
    displayName: 'LazyMapView',
    fallback: <MapLoadingFallback minHeight={400} />,
  }
);

// ============================================================================
// Light primitives — direct re-exports
//
// MapMarker / MapPopup / MapCluster / MapSource / MapLayer / MapControls
// etc. are thin wrappers around `react-map-gl/maplibre`. They don't import
// `maplibre-gl` at module scope (only types, which are erased), so exporting
// them synchronously here costs ~tens of KB at most — not the ~800KB of
// MapLibre GL itself.
//
// The heavy library only loads when `LazyMapContainer` actually mounts,
// because `MapContainer.tsx` (the only module that imports `maplibre-gl`
// at runtime) is reached exclusively via the dynamic import above.
//
// This means consumers can write:
//
//   import { LazyMapContainer, MapMarker, MapPopup } from '@djangocfg/widget-map'
//
// …and still get correct code-splitting.
// ============================================================================

export {
  MapMarker,
  MapPopup,
  MapCluster,
  MapSource,
  MapLayer,
  MapControls,
  CustomOverlay,
  MapLegend,
  LayerSwitcher,
  MeasureControl,
  DraggableMarkers,
  GeocoderInput,
  GeocoderControl,
  CompassChip,
  MarkerCard,
  MapMarkers,
} from './components/light';

export type { DraggableMarkersProps, DraggablePoint } from './components/light';
export type { GeocoderInputProps, GeocoderControlProps } from './components/light';
export type { CompassChipProps } from './components/light';
// Marker info-cards — light wrappers (no maplibre at module scope), safe on
// the synchronous surface. `MarkerCard` data type lives in `./cards`.
export type {
  MarkerCardProps,
  MapMarkersProps,
  MarkerWithCard,
  MarkerCardAction,
  MarkerCardData,
  MarkerCardActionData,
} from './components/light';
// Card-data shape under `MarkerCardInfo` (the `MarkerCard` value is the
// component re-exported above).
export type { MarkerCard as MarkerCardInfo } from './cards';

// Geocoder resolver — pure, key-free Photon (light; no maplibre runtime).
export { photonResolve, cameraForResult } from './geocode';
export type { GeocodeResult, GeocodeKind, ResolveGeocode } from './geocode';

export { MapProvider, useMapContext, MapContext } from './context';
export type { MapProviderProps } from './context';

export type {
  MapContainerProps,
  GeolocateOptions,
  GeolocatePosition,
  MapMarkerProps,
  MapPopupProps,
  MapClusterProps,
  MapSourceProps,
  MapLayerProps,
  MapControlsProps,
  MeasureControlProps,
} from './components/light';

// Basemap styles (incl. free OpenFreeMap keys) + PMTiles protocol helper —
// light, safe to load synchronously alongside the lazy container.
export {
  MAP_STYLES,
  getMapStyle,
  MAP_STYLE_LABELS,
  KEY_FREE_STYLES,
  resolveBasemapOptions,
  TERRAIN_DEM,
  TERRAIN_DEM_URL,
} from './styles';
export { addPMTilesProtocol, pmtilesSourceUrl } from './protocols/pmtiles';

// Hooks — pure React glue (maplibre is a TYPE-only import here, so these
// add no runtime weight and are safe on the synchronous lazy surface).
export {
  useMap,
  useMapControl,
  useMarkers,
  useMapEvents,
  useMapViewport,
  useMapLayers,
  useSpiderfy,
  useMapTouchMode,
  useMapScrollProtection,
  useMapImages,
  useMeasure,
  useTerrain,
  useCompass,
  useGeolocation,
  useControl,
  useDraggableMarkers,
  useGeocoder,
  useMarkerCard,
  type UseMarkerCardResult,
  type UseCompassResult,
  type UseGeocoderOptions,
  type UseGeocoderResult,
  type UseSpiderfyOptions,
  type UseSpiderfyResult,
  type MapImage,
  type UseMapImagesResult,
  type UseMeasureResult,
  type MeasureMode,
  type UseTerrainOptions,
  type GeolocationFix,
  type GeolocationStatus,
  type UseGeolocationOptions,
  type UseGeolocationResult,
  type UseDraggableMarkersOptions,
  type UseDraggableMarkersResult,
  type DraggableMarkerHandlers,
} from './hooks';

// Layer factories — pure functions returning `LayerProps` (type-only deps).
export {
  createClusterLayers,
  createPointLayer,
  createHeatmapLayer,
  createPolygonLayer,
  createPolygonOutlineLayer,
  createHighlightLayer,
  createLineLayer,
  createRouteLayers,
  createDashedLineLayer,
  createAnimatedLineLayer,
  createSymbolLayer,
} from './layers';

// Geometry + spiderfy utils — pure, dependency-free helpers.
export {
  calculateBounds,
  calculateCenter,
  calculateDistance,
  isPointInBounds,
  expandBounds,
  toGeoJSON,
  fromGeoJSON,
  createPoint,
  createPolygon,
  createLineString,
  createFeatureCollection,
  offsetOverlappingMarkers,
  getSpiderfyPositions,
  groupOverlappingMarkers,
  hasOverlappingMarkers,
  getOverlapStats,
} from './utils';

// The full type surface. `./types` is the single source of truth for the
// shapes; the barrels above export the values.
export type {
  MarkerData,
  MapViewport,
  MapStyleKey,
  MapContextValue,
  MapControlActions,
  MarkerActions,
  MapEventHandlers,
  MapMouseEvent,
  LayerProps,
  FillLayerSpecification,
  CircleLayerSpecification,
  LineLayerSpecification,
  SymbolLayerSpecification,
  FilterSpecification,
  ControlPosition,
  MarkerProps,
  ClusterLayerOptions,
  PointLayerOptions,
  PolygonLayerOptions,
  LineLayerOptions,
  RouteLayerOptions,
  SymbolLayerOptions,
  DrawControlProps,
  CustomOverlayProps,
  LegendItem,
  MapLegendProps,
  LayerConfig,
  LayerSwitcherProps,
} from './types';

// `react-map-gl/maplibre` primitives, so a consumer composing its own layers
// need not add the dependency itself. Light: their `maplibre-gl` imports are
// type-only.
export type { ViewState, MapRef } from 'react-map-gl/maplibre';
export { Source, Layer, Marker, Popup } from 'react-map-gl/maplibre';
