'use client'

/**
 * PMTiles protocol registration for MapLibre.
 *
 * PMTiles is a single-file basemap format (Protomaps, BSD + ODbL) that
 * MapLibre reads DIRECTLY in the browser via HTTP range requests — no tile
 * server, no API key. Host one `.pmtiles` file on any static CDN (S3/R2/
 * GitHub Pages) for a self-hosted / offline basemap.
 *
 * Usage (register ONCE per app lifecycle, e.g. in a top-level effect):
 *
 * ```ts
 * import maplibregl from 'maplibre-gl';
 * import { addPMTilesProtocol } from '@djangocfg/widget-map';
 *
 * useEffect(() => addPMTilesProtocol(maplibregl), []); // returns a cleanup fn
 * ```
 *
 * Then reference the file from a style/source with a `pmtiles://` URL:
 *
 * ```ts
 * // source url:  pmtiles://https://your-cdn.example/basemap.pmtiles
 * ```
 *
 * The `pmtiles` package is dynamically imported so it costs nothing until a
 * consumer actually opts into PMTiles.
 */

/** Minimal shape of the maplibre-gl module we touch (avoids a hard dep). */
interface MapLibreLike {
  addProtocol: (
    name: string,
    handler: (...args: unknown[]) => unknown,
  ) => void
  removeProtocol: (name: string) => void
}

const PROTOCOL = 'pmtiles'

/**
 * Register the `pmtiles://` protocol on the given maplibre-gl module.
 * Returns a cleanup function that removes it — wire it as an effect's
 * teardown. Safe to call once; calling again re-registers (idempotent at
 * the maplibre level, last handler wins).
 */
export function addPMTilesProtocol(maplibregl: MapLibreLike): () => void {
  let cancelled = false

  // Dynamic import keeps `pmtiles` out of the bundle until used.
  void import('pmtiles').then(({ Protocol }) => {
    if (cancelled) return
    const protocol = new Protocol()
    maplibregl.addProtocol(
      PROTOCOL,
      protocol.tile as (...args: unknown[]) => unknown,
    )
  })

  return () => {
    cancelled = true
    try {
      maplibregl.removeProtocol(PROTOCOL)
    } catch {
      // protocol may not have registered yet (import still in flight)
    }
  }
}

/** Build a `pmtiles://` source URL from a plain https URL to a `.pmtiles` file. */
export function pmtilesSourceUrl(fileUrl: string): string {
  return `${PROTOCOL}://${fileUrl}`
}
