/**
 * Every component EXCEPT the container.
 *
 * The split the package's two entries rest on. These are thin wrappers over
 * `react-map-gl/maplibre`'s named exports and hold no static edge to MapLibre
 * GL; `MapContainer` does, through `MapInner`'s `<Map>` and its stylesheet.
 *
 * The lazy entry imports THIS barrel, never `./index`. Re-exporting the
 * container from a barrel the lazy entry reads puts the ~800 KB back into the
 * entry chunk with nothing failing — which is exactly what had happened, and
 * what `src/entries.test.ts` now catches.
 */

export { MapControls } from './MapControls'
export { MapMarker } from './MapMarker'
export { MapPopup } from './MapPopup'
export { MapCluster } from './MapCluster'
export { MapSource, MapLayer } from './MapSource'
export { CustomOverlay } from './CustomOverlay'
export { MapLegend } from './MapLegend'
export { LayerSwitcher } from './LayerSwitcher'
export { MeasureControl } from './MeasureControl'

// DrawControl and GeocoderControl require optional dependencies
// See DrawControl.tsx and GeocoderControl.tsx for implementation examples

// Types are exported from ../types.ts
// The container's PROPS are here — types erase, so naming them costs nothing.
export type { MapContainerProps, GeolocateOptions, GeolocatePosition } from './MapContainer'
export type { MapControlsProps } from './MapControls'
export type { MapMarkerProps } from './MapMarker'
export type { MapPopupProps } from './MapPopup'
export type { MapClusterProps } from './MapCluster'
export type { MapSourceProps, MapLayerProps } from './MapSource'
export type { MeasureControlProps } from './MeasureControl'

export { DraggableMarkers } from './DraggableMarkers'
export type { DraggableMarkersProps, DraggablePoint } from './DraggableMarkers'

// Geocoder — free, key-free Photon autocomplete (presentational input +
// thin map-bound control). Injectable `resolve`; no optional deps.
export { GeocoderInput } from './GeocoderInput'
export { GeocoderControl } from './GeocoderControl'
export type { GeocoderInputProps } from './GeocoderInput'
export type { GeocoderControlProps } from './GeocoderControl'

// Compass chip — presentational reset-to-north control with a Google-style
// color cue (accent needle when the view is rotated/tilted). Use inside a
// MapProvider, fed by `useCompass`.
export { CompassChip } from './CompassChip'
export type { CompassChipProps } from './CompassChip'

// Marker info-cards — a Google-Maps-style card popup above a pin. `MarkerCard`
// is the default presentational card (data-driven, standalone); `MapMarkers`
// wires click → card-above-pin (one open at a time). Both inside a MapProvider.
export { MarkerCard } from './MarkerCard'
export type { MarkerCardProps } from './MarkerCard'
export { MapMarkers } from './MapMarkers'
export type { MapMarkersProps, MarkerWithCard } from './MapMarkers'
// Card data types. NOTE: the `MarkerCard` *type* (card data shape) is exported
// from the top-level Map barrel / `cards` — here the `MarkerCard` name is the
// component value, so we only surface the non-colliding card types.
export type {
  MarkerCardAction,
  MarkerCardData,
  MarkerCardActionData,
} from '../cards/types'
