import type { RefObject } from 'react'
import type {
  MapRef,
  ViewState,
  LayerProps,
  FillLayerSpecification,
  CircleLayerSpecification,
  LineLayerSpecification,
  SymbolLayerSpecification,
  ControlPosition,
  MarkerProps,
} from 'react-map-gl/maplibre'
import type { LngLatBoundsLike, LngLat, FilterSpecification } from 'maplibre-gl'

export type { ControlPosition, MarkerProps }

// ============================================================================
// Marker Types
// ============================================================================

export interface MarkerData {
  id: string
  longitude: number
  latitude: number
  data?: Record<string, unknown>
}

// ============================================================================
// Viewport Types
// ============================================================================

export interface MapViewport extends Partial<ViewState> {
  longitude: number
  latitude: number
  zoom: number
  bearing?: number
  pitch?: number
  transitionDuration?: number
}

// ============================================================================
// Context Types
// ============================================================================

export interface MapContextValue {
  mapRef: RefObject<MapRef | null>
  viewport: MapViewport
  setViewport: (viewport: Partial<MapViewport>) => void
  initialViewport: MapViewport
  resetToInitial: () => void
  markers: MarkerData[]
  setMarkers: React.Dispatch<React.SetStateAction<MarkerData[]>>
  selectedMarker: MarkerData | null
  setSelectedMarker: (marker: MarkerData | null) => void
  hoveredFeature: GeoJSON.Feature | null
  setHoveredFeature: (feature: GeoJSON.Feature | null) => void
  isLoaded: boolean
  setIsLoaded: (loaded: boolean) => void
}

// ============================================================================
// Hook Return Types
// ============================================================================

export interface MapControlActions {
  flyTo: (center: [number, number], zoom?: number, options?: { duration?: number }) => void
  easeTo: (center: [number, number], zoom?: number, options?: { duration?: number }) => void
  fitBounds: (bounds: LngLatBoundsLike, options?: { padding?: number; duration?: number; maxZoom?: number }) => void
  zoomIn: () => void
  zoomOut: () => void
  resetView: (initialViewport: MapViewport) => void
  getCenter: () => [number, number] | null
  getZoom: () => number | null
  getBounds: () => LngLatBoundsLike | null
}

export interface MarkerActions {
  markers: MarkerData[]
  addMarker: (marker: Omit<MarkerData, 'id'>) => string
  removeMarker: (id: string) => void
  updateMarker: (id: string, updates: Partial<Omit<MarkerData, 'id'>>) => void
  clearMarkers: () => void
  fitToMarkers: (paddingOrOpts?: number | { padding?: number; maxZoom?: number }) => void
}

// ============================================================================
// Event Types
// ============================================================================

export interface MapEventHandlers {
  onClick?: (event: MapMouseEvent) => void
  onHover?: (event: MapMouseEvent) => void
  onMoveStart?: () => void
  onMoveEnd?: (viewport: MapViewport) => void
  onZoomStart?: () => void
  onZoomEnd?: (zoom: number) => void
  onLoad?: () => void
}

export interface MapMouseEvent {
  lngLat: LngLat
  point: { x: number; y: number }
  features?: GeoJSON.Feature[]
  originalEvent: MouseEvent
}

// ============================================================================
// Style Types
// ============================================================================

// Single source of truth — derived from `MAP_STYLES` so new basemap keys
// (e.g. OpenFreeMap `liberty`/`bright`/`positron`) flow through automatically.
export type { MapStyleKey } from './styles'

// ============================================================================
// Layer Types (from react-map-gl & maplibre-gl)
// ============================================================================

export type {
  LayerProps,
  FillLayerSpecification,
  CircleLayerSpecification,
  LineLayerSpecification,
  SymbolLayerSpecification,
  FilterSpecification,
}

export interface ClusterLayerOptions {
  sourceId: string
  colors?: [string, string, string]
  radii?: [number, number, number]
  thresholds?: [number, number]
  hoverColor?: string
  /**
   * Feature property to SUM into a cluster's size and label, instead of
   * counting features.
   *
   * Supercluster counts features, which is right when one feature is one thing.
   * It is wrong when a feature already stands for many — an aggregate point
   * carrying `count: 949`, a store with a stock level, a sensor with a reading.
   * Three such points then render a cluster reading "3".
   *
   * Naming a property here makes the cluster read the total. The source must
   * declare the matching `clusterProperties` sum for it to exist — see
   * `weightProperty` on `MapCluster`, which wires both ends.
   */
  /**
   * Label tint per density tier, low to high.
   *
   * This is where the density ramp lives: the disc stays white on every tier so
   * it reads on any basemap, and the NUMBER carries the magnitude.
   */
  labelColors?: [string, string, string]
  /**
   * Feature property drawn beside a SINGLE feature — typically its price.
   *
   * Only applies where `weightProperty` resolves to 1, i.e. one real thing
   * rather than a group. Without it a lone feature is an anonymous dot.
   */
  labelProperty?: string
  /**
   * Id of a registered nine-patch image to draw `labelProperty` inside.
   *
   * Turns the label into a PILL: `icon-text-fit` stretches this image to its
   * own text. Omit and the label is drawn bare. See `usePillImage`, which
   * registers one rather than relying on the active style's sprite.
   */
  pillImage?: string
  /**
   * Nine-patch image for the ACTIVE (hovered or selected) chip.
   *
   * A second image, because a plain icon cannot be tinted and a symbol cannot
   * restyle itself on feature state. See `weightedPointLabelActive`.
   */
  pillImageActive?: string
  /**
   * Feature property that identifies ONE feature, for the active chip.
   *
   * Defaults to `labelProperty`, which is wrong wherever two features can
   * share a label — two homes at the same price would both invert.
   *
   * **It must be unique per feature.** A shared value resolves to whichever
   * feature comes first, so the chip is drawn on a listing the visitor is not
   * pointing at, carrying that listing's price — or no text at all where it
   * has none.
   *
   * **There is no second, coarser identity.** There was one — a property
   * naming the ~110 m cell, so a selection could mark a whole group — and
   * every defect it caused was the same defect: marking a group draws every
   * chip in it on one coordinate (84 of them on Bali, as one black blob), and
   * brushes every row sharing the cell. A pin is a pin.
   */
  identityProperty?: string
  /**
   * Zoom below which `labelProperty` is not drawn. Omit to always draw it.
   *
   * A price answers "how much here", which is a question about a
   * NEIGHBOURHOOD. Zoomed out the map answers "where is the supply", and a
   * single home's price is not an answer to it — while the pill, which
   * stretches to its text, physically outweighs the cluster of a hundred
   * beside it.
   *
   * Measured on the MLS Bali catalogue (3,360 points, 753 cells): at z10–11
   * between 500 and 600 lone chips compete for one screen and roughly ten
   * survive placement, so what is shown is whichever won the pixels rather
   * than anything the visitor chose. Below the threshold those features still
   * draw — as the small dot a lone feature gets — so nothing disappears from
   * the map; only its price does.
   */
  labelMinZoom?: number
  weightProperty?: string
  /**
   * Font stack for cluster labels. Defaults to `['Noto Sans Bold']`.
   *
   * A glyph server serves a stack as ONE key — `fonts/A,B,C/0-255.pbf` — so a
   * fallback the server does not hold 404s the whole request and no label
   * renders. Name only fonts the active style's glyph endpoint actually has.
   */
  textFont?: string[]
}

export interface PointLayerOptions {
  color?: string
  radius?: number
  strokeWidth?: number
  strokeColor?: string
}

export interface PolygonLayerOptions {
  fillColor?: string
  fillOpacity?: number
  /** Drawn as `fill-outline-color`, which is always hairline-thin. */
  strokeColor?: string
}

// ============================================================================
// Line Layer Types
// ============================================================================

export interface LineLayerOptions {
  id: string
  sourceId: string
  color?: string
  width?: number
  opacity?: number
  dashArray?: number[]
  lineCap?: 'butt' | 'round' | 'square'
  lineJoin?: 'bevel' | 'round' | 'miter'
  blur?: number
  minZoom?: number
  maxZoom?: number
}

export interface RouteLayerOptions extends Omit<LineLayerOptions, 'id'> {
  sourceId: string
}

// ============================================================================
// Symbol Layer Types
// ============================================================================

/** A data-driven expression (e.g. `['get', 'icon']`) or a static value. */
export type DataDrivenValue<T> = T | unknown[]

export interface SymbolLayerOptions {
  id: string
  sourceId: string
  /**
   * Registered image id (see `useMapImages`) OR a data-driven expression
   * selecting one per feature, e.g. `['get', 'icon']`.
   */
  iconImage: DataDrivenValue<string>
  iconSize?: DataDrivenValue<number>
  iconAllowOverlap?: boolean
  /** Property name or expression for an optional text label. */
  textField?: DataDrivenValue<string>
  textSize?: DataDrivenValue<number>
  textColor?: string
  textOffset?: [number, number]
  minZoom?: number
  maxZoom?: number
}

// ============================================================================
// Control Types
// ============================================================================

export interface DrawControlProps {
  position?: ControlPosition
  displayControlsDefault?: boolean
  controls?: {
    point?: boolean
    line_string?: boolean
    polygon?: boolean
    trash?: boolean
    combine_features?: boolean
    uncombine_features?: boolean
  }
  defaultMode?: string
  onCreate?: (evt: { features: object[] }) => void
  onUpdate?: (evt: { features: object[]; action: string }) => void
  onDelete?: (evt: { features: object[] }) => void
}

export interface GeocoderControlProps {
  position: ControlPosition
  marker?: boolean | Omit<MarkerProps, 'longitude' | 'latitude'>
  placeholder?: string
  collapsed?: boolean
  clearOnBlur?: boolean
  showResultsWhileTyping?: boolean
  minLength?: number
  limit?: number
  language?: string
  countries?: string
  zoom?: number
  flyTo?: boolean | object
  onLoading?: (e: object) => void
  onResults?: (e: object) => void
  onResult?: (e: object) => void
  onError?: (e: object) => void
}

export interface CustomOverlayProps {
  children: React.ReactNode
}

// ============================================================================
// Legend Types
// ============================================================================

export interface LegendItem {
  id: string
  label: string
  color?: string
  icon?: React.ReactNode
  type?: 'circle' | 'line' | 'fill' | 'symbol'
  visible?: boolean
}

export interface MapLegendProps {
  items: LegendItem[]
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'
  title?: string
  collapsible?: boolean
  defaultCollapsed?: boolean
  className?: string
  style?: React.CSSProperties
  onItemClick?: (item: LegendItem) => void
}

// ============================================================================
// Layer Switcher Types
// ============================================================================

export interface LayerConfig {
  id: string
  label: string
  defaultVisible?: boolean
  group?: string
}

export interface LayerSwitcherProps {
  layers: LayerConfig[]
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right'
  title?: string
  collapsible?: boolean
  defaultCollapsed?: boolean
  showToggleAll?: boolean
  className?: string
  style?: React.CSSProperties
  onChange?: (layerId: string, visible: boolean) => void
}
