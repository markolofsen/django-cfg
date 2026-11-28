'use client'

/**
 * Free DEM (digital-elevation-model) source for 3D terrain + hillshade.
 *
 * Uses **AWS Terrain Tiles** — Terrarium-encoded elevation PNGs served as
 * free, open data from the public `elevation-tiles-prod` S3 bucket. No API
 * key, no account, no usage limit. MapLibre renders 3D terrain and hillshade
 * natively from a `raster-dem` source — no external tile service needed.
 *
 * See `packages/@dev/active/ui-tools-plan14-map-capabilities/reports/research.md` §2.
 */
import type { RasterDEMSourceSpecification } from 'maplibre-gl'

/** Terrarium-encoded DEM tile URL template (AWS open data, key-free). */
export const TERRAIN_DEM_URL =
  'https://elevation-tiles-prod.s3.amazonaws.com/terrarium/{z}/{x}/{y}.png'

/**
 * Ready-to-use `raster-dem` source spec for the free AWS Terrarium DEM.
 * Pass straight to `map.addSource(id, TERRAIN_DEM)`.
 */
export const TERRAIN_DEM: RasterDEMSourceSpecification = {
  type: 'raster-dem',
  tiles: [TERRAIN_DEM_URL],
  encoding: 'terrarium',
  tileSize: 256,
  maxzoom: 15,
}
