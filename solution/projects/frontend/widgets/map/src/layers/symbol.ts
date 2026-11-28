import type { LayerProps, SymbolLayerSpecification } from 'react-map-gl/maplibre'
import type { SymbolLayerOptions } from '../types'

/**
 * `layout` / `paint` on `SymbolLayerSpecification` are declared optional
 * (`layout?: {…}`), so `SymbolLayerSpecification['layout']` widens to
 * `{…} | undefined`. Indexing that union per-key (e.g.
 * `SymbolLayerSpecification['layout']['icon-image']`) is what leaks
 * TS2339 into stricter consumer typechecks (cmdop's `tsc --noEmit`).
 * Strip the `| undefined` once here so the rest of the file builds a
 * single, fully-typed object literal instead of per-key indexed casts.
 */
type SymbolLayout = NonNullable<SymbolLayerSpecification['layout']>
type SymbolPaint = NonNullable<SymbolLayerSpecification['paint']>

/**
 * Create a `symbol` layer that draws a registered icon (and optional text
 * label) per feature — the data-driven path for many icons at scale.
 *
 * Register the icon image first with the `useMapImages` hook, then pass its
 * id (or a data-driven expression like `['get', 'icon']`) as `iconImage`.
 *
 * Two ways to do custom markers:
 * - **For a few rich markers**, use a DOM `MapMarker` with `children` (or its
 *   `color`/`size` props) — full React content per marker.
 * - **For many data-driven icons at scale**, use this symbol layer over a
 *   GeoJSON source: MapLibre renders the icons on the GPU from the sprite.
 *
 * @example
 * ```tsx
 * useMapImages([{ id: 'pin', url: '/icons/pin.png' }])
 * const layer = createSymbolLayer({
 *   id: 'places',
 *   sourceId: 'places-src',
 *   iconImage: 'pin',
 *   iconSize: 0.5,
 *   textField: ['get', 'name'],
 * })
 * ```
 */
export function createSymbolLayer({
  id,
  sourceId,
  iconImage,
  iconSize,
  iconAllowOverlap = true,
  textField,
  textSize = 12,
  textColor = '#1f2937',
  textOffset = [0, 1.2],
  minZoom,
  maxZoom,
}: SymbolLayerOptions): LayerProps {
  // Build one fully-typed `layout` literal up front (all keys present-or-
  // omitted), so TS checks it as a unit against `SymbolLayout` rather than
  // assigning per-key into a `… | undefined` indexed type. The option
  // values are the author's loosened `DataDrivenValue<…>` (static value OR
  // expression array); each is asserted to its concrete layout-property
  // type via the non-nullable `SymbolLayout[…]` indexed access.
  const labelKeys: Partial<SymbolLayout> =
    textField !== undefined
      ? {
          'text-field': textField as SymbolLayout['text-field'],
          'text-size': textSize as SymbolLayout['text-size'],
          'text-offset': textOffset,
          'text-anchor': 'top',
        }
      : {}

  const layout: SymbolLayout = {
    'icon-image': iconImage as SymbolLayout['icon-image'],
    'icon-allow-overlap': iconAllowOverlap,
    ...(iconSize !== undefined
      ? { 'icon-size': iconSize as SymbolLayout['icon-size'] }
      : {}),
    ...labelKeys,
  }

  const paint: SymbolPaint = textField !== undefined ? { 'text-color': textColor } : {}

  const layer: LayerProps = {
    id,
    type: 'symbol',
    source: sourceId,
    layout,
    paint,
  }

  if (minZoom !== undefined) layer.minzoom = minZoom
  if (maxZoom !== undefined) layer.maxzoom = maxZoom

  return layer
}
