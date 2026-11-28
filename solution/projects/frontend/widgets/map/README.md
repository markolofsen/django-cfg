# Map

Interactive maps for `@djangocfg/widget-map`, built on [MapLibre GL](https://maplibre.org/) via `react-map-gl` — markers, clustered GeoJSON, popups, layer factories, free OpenFreeMap / PMTiles basemaps, a runtime basemap switcher, 3D terrain, address/place autocomplete (geocoder), a compass, click-to-measure, draggable markers, custom marker icons, and an opt-in locate-me (GPS) chip, all behind a small Provider/Context surface.

> **Bundle warning.** MapLibre GL is heavy (~800 KB gzipped). The `@djangocfg/widget-map` entry is already the **lazy** one — `LazyMapContainer` defers the MapLibre chunk until it mounts. All components are `'use client'`; never render them on the Next.js server.

## Install

```bash
pnpm add @djangocfg/widget-map @djangocfg/ui-core
```

## Quick start

```tsx
import { LazyMapContainer, MapMarker } from '@djangocfg/widget-map';

<div className="h-96 rounded-xl overflow-hidden">
  <LazyMapContainer
    initialViewport={{ latitude: 25.08, longitude: 55.14, zoom: 13 }}
    mapStyle="light"
  >
    <MapMarker
      marker={{ id: 'home', latitude: 25.08, longitude: 55.14 }}
      color="#10b981"
      size={32}
    />
  </LazyMapContainer>
</div>
```

The container provides its own `MapProvider`. To use the map context from a sibling (e.g. a button calling `flyTo`), wrap your tree in `<MapProvider>` and render `<MapView>` inside it. See [container](./@docs/container.md).

## Public exports — `@djangocfg/widget-map`

The package subpath resolves to the lazy entry. It surfaces:

**Components** — `LazyMapContainer`, `LazyMapView` (code-split), `MapView`-via-`MapContainer` types, plus the light primitives: `MapMarker`, `MapPopup`, `MapCluster`, `MapSource`, `MapLayer`, `MapControls`, `CustomOverlay`, `MapLegend`, `LayerSwitcher`, `MeasureControl`, `DraggableMarkers`, `GeocoderInput`, `GeocoderControl`, `CompassChip`, `MarkerCard`, `MapMarkers`.

**Context** — `MapProvider`, `useMapContext`, `MapContext`.

**Styles** — `MAP_STYLES`, `getMapStyle`, `MAP_STYLE_LABELS`, `KEY_FREE_STYLES`, `resolveBasemapOptions`, and the free terrain DEM source `TERRAIN_DEM` / `TERRAIN_DEM_URL`.

**PMTiles** — `addPMTilesProtocol`, `pmtilesSourceUrl` (self-hosted / offline basemaps).

**Geocoder** — `photonResolve` (default key-free Photon resolver), `cameraForResult` (smart-zoom helper), and types `GeocodeResult`, `GeocodeKind`, `ResolveGeocode`. See [geocoder](./@docs/geocoder.md).

**Types** — `MapContainerProps`, `GeolocateOptions`, `GeolocatePosition`, `MapMarkerProps`, `MapPopupProps`, `MapClusterProps`, `MapSourceProps`, `MapLayerProps`, `MapControlsProps`, `MeasureControlProps`, `DraggableMarkersProps`, `DraggablePoint`, `GeocoderInputProps`, `GeocoderControlProps`, `CompassChipProps`, `MapProviderProps`, `MapViewport`, `MapStyleKey`, `MarkerData`, plus hook types `GeolocationFix`, `GeolocationStatus`, `UseGeolocationOptions`, `UseGeolocationResult`, `UseGeocoderOptions`, `UseGeocoderResult`, `UseCompassResult`, `UseTerrainOptions`, `UseMeasureResult`, `MeasureMode`, `MapImage`, `UseMapImagesResult`, `UseDraggableMarkersOptions`, `UseDraggableMarkersResult`, `DraggableMarkerHandlers`, plus the marker-card types `MarkerCardProps`, `MapMarkersProps`, `MarkerWithCard`, `MarkerCardInfo` (the card data shape), `MarkerCardAction`, `MarkerCardData`, `MarkerCardActionData`, `UseMarkerCardResult`.

**Hooks** — `useMap`, `useMapControl`, `useMarkers`, `useMapEvents`, `useMapViewport`, `useMapLayers`, `useControl`, `useSpiderfy` (+ `UseSpiderfyOptions` / `UseSpiderfyResult` types), `useMarkerCard` (single-open marker-card selection state), the feature hooks `useCompass`, `useTerrain`, `useMeasure`, `useMapImages`, `useDraggableMarkers`, `useGeocoder`, and the map-independent `useGeolocation` (live browser position for custom "where am I" UI; see [hooks](./@docs/hooks.md#usegeolocationoptions)). `useMapScrollProtection` / `useMapTouchMode` are also exported — they power `scrollProtection`, which wires them for you.

**Layer factories** — `createClusterLayers`, `createPointLayer`, `createHeatmapLayer`, `createPolygonLayer`, `createPolygonOutlineLayer`, `createHighlightLayer`, `createLineLayer`, `createRouteLayers`, `createDashedLineLayer`, `createAnimatedLineLayer`, `createSymbolLayer`.

**Geometry utils** — `calculateBounds`, `calculateCenter`, `calculateDistance`, `isPointInBounds`, `expandBounds`, `toGeoJSON`, `fromGeoJSON`, `createPoint`, `createPolygon`, `createLineString`, `createFeatureCollection`.

**Spiderfy utils** — `offsetOverlappingMarkers`, `getSpiderfyPositions`, `groupOverlappingMarkers`, `hasOverlappingMarkers`, `getOverlapStats`.

## Docs

| Doc | Covers |
|---|---|
| [container.md](./@docs/container.md) | `MapContainer` / `MapView` — full props, control toolbar (search · terrain · compass · locate-me / GPS chips), scroll protection & mobile, fullscreen dialog. |
| [basemaps.md](./@docs/basemaps.md) | Map styles, the runtime basemap switcher, OpenFreeMap, satellite/keys, PMTiles, 3D terrain (free DEM). |
| [markers-popups.md](./@docs/markers-popups.md) | `MapMarker`, `MapPopup`, `MapCluster`, marker info-cards (`MarkerCard` / `MapMarkers` / `useMarkerCard`), draggable markers, overlapping points / spiderfy. |
| [layers.md](./@docs/layers.md) | `MapSource` / `MapLayer`, the layer factories, custom marker icons (symbol layer), geometry utilities. |
| [geocoder.md](./@docs/geocoder.md) | Address/place autocomplete — `GeocoderInput` / `GeocoderControl`, the toolbar search chip, `photonResolve`, smart zoom (`cameraForResult`), `useGeocoder`. |
| [hooks.md](./@docs/hooks.md) | Every hook, with an example. |
| [advanced.md](./@docs/advanced.md) | `CustomOverlay`, `MapLegend`, `LayerSwitcher`, `MeasureControl`, the DrawControl recipe, lazy loading, SSR. |
| [stories.md](./@docs/stories.md) | The Storybook stories list. |

## The two entries

| Import | Container | For |
|---|---|---|
| `@djangocfg/widget-map` | behind `React.lazy` | everything — this is the default for a reason |
| `@djangocfg/widget-map/eager` | a static edge | the map IS the page and a placeholder reads as a flash |

`eager` is derived from the root (`export * from './index'` plus the static
container), so the two surfaces cannot drift; `src/entries.test.ts` walks the
static import graph and holds the split itself.

**Importing both in one app defeats the split** — the static edge pulls
MapLibre into the entry chunk whatever the other half does.

## Verify

```bash
pnpm --filter @djangocfg/widget-map check-types test
```

## Related

- Underlying lib: [`react-map-gl` (MapLibre adapter)](https://visgl.github.io/react-map-gl/) on top of [MapLibre GL JS](https://maplibre.org/maplibre-gl-js/docs/)
