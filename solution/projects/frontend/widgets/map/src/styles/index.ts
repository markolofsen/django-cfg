/**
 * Built-in basemap styles.
 *
 * `light` / `dark` / `streets` — CARTO, free, no API key.
 * `satellite` — MapTiler, **needs an API key** in the URL (not injected
 *   here; pass your own keyed style URL to `mapStyle` to use it).
 * `liberty` / `bright` / `positron` — **OpenFreeMap** public instance:
 *   genuinely free, no key, no limits, commercial use allowed (donation-
 *   funded, no SLA). See `packages/@dev/active/ui-tools-plan14-map-capabilities`.
 *
 * For a self-hosted / offline single-file basemap, use the PMTiles helper
 * (`addPMTilesProtocol`) and pass a `pmtiles://…`-backed style instead.
 */
// Free DEM source for 3D terrain + hillshade (AWS Terrarium, key-free).
export { TERRAIN_DEM, TERRAIN_DEM_URL } from './terrain'

export const MAP_STYLES = {
  light: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
  dark: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
  streets: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
  satellite: 'https://api.maptiler.com/maps/satellite/style.json',
  // OpenFreeMap — key-free, no limits, commercial OK.
  liberty: 'https://tiles.openfreemap.org/styles/liberty',
  bright: 'https://tiles.openfreemap.org/styles/bright',
  positron: 'https://tiles.openfreemap.org/styles/positron',
} as const

export type MapStyleKey = keyof typeof MAP_STYLES

export function getMapStyle(key: MapStyleKey | string): string {
  if (key in MAP_STYLES) {
    return MAP_STYLES[key as MapStyleKey]
  }
  return key
}

/** Human label for the basemap switcher menu. */
export const MAP_STYLE_LABELS: Record<MapStyleKey, string> = {
  light: 'Light',
  dark: 'Dark',
  streets: 'Streets',
  satellite: 'Satellite',
  liberty: 'Liberty',
  bright: 'Bright',
  positron: 'Positron',
}

/** Basemap keys that work with NO API key (safe to always offer). */
export const KEY_FREE_STYLES: readonly MapStyleKey[] = [
  'light',
  'dark',
  'streets',
  'liberty',
  'bright',
  'positron',
]

/**
 * Pick the basemap options to show in the switcher, smartly:
 * - all key-free built-ins, PLUS
 * - `satellite` ONLY when usable — i.e. the host passed its own keyed
 *   satellite style (a full URL via `mapStyle`/`current`), since the
 *   built-in MapTiler satellite needs a key we don't ship.
 *
 * A host can override entirely by passing an explicit `requested` list.
 */
export function resolveBasemapOptions(
  requested: readonly MapStyleKey[] | undefined,
  current: MapStyleKey | string | undefined,
): MapStyleKey[] {
  if (requested && requested.length) return [...requested]
  const opts: MapStyleKey[] = [...KEY_FREE_STYLES]
  // Offer satellite only if the active style is a host-supplied URL (keyed)
  // OR the current key is already 'satellite' (host wired a key elsewhere).
  if (current === 'satellite') opts.push('satellite')
  return opts
}
