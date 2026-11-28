/**
 * Photon geocoder resolver — the data contract + default `fetch` resolver
 * for the address/place autocomplete.
 *
 * Mirrors the link-preview seam (`ResolveLinkPreview`): the UI is purely
 * presentational and resolution is an INJECTABLE async function. The default
 * `photonResolve` hits the public, key-free Photon (Komoot) endpoint — good
 * for dev/internal use. A host can supply its own `resolve` (a Wails/Go
 * method or a Next.js API route proxying Photon / a self-hosted instance) for
 * production, dodging CORS + fair-use throttling.
 *
 * Pure — no React, no map dependency. Safe on the light (maplibre-free)
 * surface.
 */

/** Public Photon search endpoint (OSM data, no API key, fair-use only). */
const PHOTON_ENDPOINT = 'https://photon.komoot.io/api/';

/**
 * One normalized geocoding hit. Plain JSON so it survives transport /
 * persistence. `raw` carries the original GeoJSON feature for hosts that
 * want more than the friendly fields.
 */
export interface GeocodeResult {
  /** `osm_type+osm_id`, else a synthesized stable key. */
  id: string;
  /** Primary line — place `name`, else `street housenumber`. */
  label: string;
  /** Secondary line — `"city, state, country"` (filtered, joined). */
  secondary?: string;
  /** Longitude (GeoJSON x). */
  lng: number;
  /** Latitude (GeoJSON y). */
  lat: number;
  /** `[minLng, minLat, maxLng, maxLat]` when Photon returns an extent. */
  bbox?: [number, number, number, number];
  /**
   * Coarse location kind, normalized across providers. Drives a sensible
   * fallback zoom when there's no `bbox` to fit. `'unknown'` when the
   * provider didn't say.
   */
  kind: GeocodeKind;
  /** The original Photon GeoJSON feature. */
  raw?: unknown;
}

/** Provider-agnostic location granularity (coarse → fine). */
export type GeocodeKind =
  | 'country'
  | 'region' // state / province / county
  | 'city' // city / town / village / locality
  | 'district' // suburb / neighbourhood / borough
  | 'postcode'
  | 'street'
  | 'house' // house / building / address point
  | 'poi' // a named point of interest
  | 'unknown';

/**
 * Fallback zoom per kind — used ONLY when a result has no `bbox` to fit
 * (point results like a house or POI). Bigger area → smaller zoom. These are
 * sensible defaults, not a hardcode of any specific place; the bbox path
 * (below) handles extents universally.
 */
const KIND_ZOOM: Record<GeocodeKind, number> = {
  country: 4,
  region: 7,
  city: 11,
  district: 13,
  postcode: 13,
  street: 15,
  house: 17,
  poi: 16,
  unknown: 14,
};

/**
 * The camera move for a chosen result — the SMART-ZOOM core.
 *
 * Prefer the location's own extent: if `bbox` is present, return a
 * `fitBounds` move so the whole feature frames itself (an island fills the
 * view, a street reads as a street) with no per-place tuning. Otherwise fall
 * back to a `flyTo` at a zoom chosen by the result's `kind`.
 */
export function cameraForResult(
  result: GeocodeResult,
):
  | { type: 'fit'; bbox: [number, number, number, number] }
  | { type: 'fly'; center: [number, number]; zoom: number } {
  if (result.bbox) {
    // Guard against a degenerate (zero-area) bbox — a point disguised as an
    // extent — which would over-zoom; fall through to kind zoom then.
    const [minLng, minLat, maxLng, maxLat] = result.bbox;
    if (maxLng - minLng > 1e-6 && maxLat - minLat > 1e-6) {
      return { type: 'fit', bbox: result.bbox };
    }
  }
  return {
    type: 'fly',
    center: [result.lng, result.lat],
    zoom: KIND_ZOOM[result.kind] ?? KIND_ZOOM.unknown,
  };
}

/**
 * Injectable resolver. Given a query string, returns ranked results. Honors
 * an optional `near` geo-bias (e.g. the current map center), a `limit`, and
 * an `AbortSignal` (rethrows `AbortError` when cancelled; returns `[]` for an
 * empty/blank query).
 */
export type ResolveGeocode = (
  query: string,
  opts?: {
    near?: { lng: number; lat: number };
    limit?: number;
    signal?: AbortSignal;
  },
) => Promise<GeocodeResult[]>;

/** Photon feature `properties` (the subset we read). */
interface PhotonProperties {
  osm_type?: string;
  osm_id?: number | string;
  name?: string;
  street?: string;
  housenumber?: string;
  city?: string;
  state?: string;
  country?: string;
  postcode?: string;
  /** Photon's coarse type, e.g. `city` / `street` / `house` / `country`. */
  type?: string;
  /** OSM tag key/value, e.g. `place`/`city`, `highway`/`residential`. */
  osm_key?: string;
  osm_value?: string;
  /** `[minLng, maxLat, maxLng, minLat]` per Photon's extent ordering. */
  extent?: [number, number, number, number];
}

interface PhotonFeature {
  geometry?: { coordinates?: [number, number] };
  properties?: PhotonProperties;
}

interface PhotonResponse {
  features?: PhotonFeature[];
}

/** Build a `[minLng, minLat, maxLng, maxLat]` bbox from Photon's extent. */
function normalizeExtent(
  extent: PhotonProperties['extent'],
): GeocodeResult['bbox'] {
  if (!extent || extent.length !== 4) return undefined;
  const [minLng, maxLat, maxLng, minLat] = extent;
  return [minLng, minLat, maxLng, maxLat];
}

/**
 * Map Photon's `type` (plus OSM `osm_key`/`osm_value` as a fallback) onto our
 * coarse, provider-agnostic `GeocodeKind`. Pure lookup — no magic numbers.
 */
function normalizeKind(p: PhotonProperties): GeocodeKind {
  switch ((p.type ?? '').toLowerCase()) {
    case 'country':
      return 'country';
    case 'state':
    case 'region':
    case 'province':
    case 'county':
      return 'region';
    case 'city':
    case 'town':
    case 'village':
    case 'locality':
      return 'city';
    case 'district':
    case 'suburb':
    case 'neighbourhood':
      return 'district';
    case 'postcode':
      return 'postcode';
    case 'street':
      return 'street';
    case 'house':
    case 'building':
      return 'house';
  }
  // Fallbacks from the OSM tag when `type` is missing/unknown.
  const key = (p.osm_key ?? '').toLowerCase();
  if (key === 'highway') return 'street';
  if (key === 'place') return 'city';
  if (key === 'boundary') return 'region';
  if (key === 'building') return 'house';
  if (key === 'amenity' || key === 'shop' || key === 'tourism' || key === 'leisure') {
    return 'poi';
  }
  return 'unknown';
}

/** Normalize one Photon GeoJSON feature → `GeocodeResult` (or `null`). */
function toResult(feature: PhotonFeature, index: number): GeocodeResult | null {
  const coords = feature.geometry?.coordinates;
  if (!coords || coords.length !== 2) return null;
  const [lng, lat] = coords;
  if (typeof lng !== 'number' || typeof lat !== 'number') return null;

  const p = feature.properties ?? {};

  const label =
    p.name ||
    [p.street, p.housenumber].filter(Boolean).join(' ') ||
    [p.city, p.state, p.country].filter(Boolean).join(', ') ||
    'Unknown location';

  const secondary = [p.city, p.state, p.country].filter(Boolean).join(', ');

  const id =
    p.osm_type && p.osm_id != null
      ? `${p.osm_type}${p.osm_id}`
      : `${lng.toFixed(6)},${lat.toFixed(6)}#${index}`;

  return {
    id,
    label,
    secondary: secondary || undefined,
    lng,
    lat,
    bbox: normalizeExtent(p.extent),
    kind: normalizeKind(p),
    raw: feature,
  };
}

/**
 * Default resolver: a built-in `fetch` to the public, key-free Photon
 * endpoint. Honors `near` (geo-bias), `limit`, and `signal`. Returns `[]`
 * for a blank query; rethrows `AbortError` when the request is cancelled.
 */
export const photonResolve: ResolveGeocode = async (query, opts) => {
  const q = query.trim();
  if (!q) return [];

  const limit = opts?.limit ?? 5;
  const params = new URLSearchParams({ q, limit: String(limit) });
  if (opts?.near) {
    params.set('lat', String(opts.near.lat));
    params.set('lon', String(opts.near.lng));
  }

  const response = await fetch(`${PHOTON_ENDPOINT}?${params.toString()}`, {
    signal: opts?.signal,
    headers: { Accept: 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Photon request failed: ${response.status}`);
  }

  const json = (await response.json()) as PhotonResponse;
  const features = json.features ?? [];

  return features
    .map((feature, index) => toResult(feature, index))
    .filter((r): r is GeocodeResult => r !== null);
};
