'use client'

import { useEffect, useRef } from 'react'

import { useMapContext } from '../context'
import { TERRAIN_DEM } from '../styles'

import type { RasterDEMSourceSpecification } from 'maplibre-gl'

/** Stable source / layer ids the hook owns. */
const DEM_SOURCE_ID = 'terrain-dem'
const HILLSHADE_LAYER_ID = 'terrain-hillshade'

/** Default vertical exaggeration — subtle, reads as 3D without caricature. */
const DEFAULT_EXAGGERATION = 1.2
/** Pitch eased in when terrain is enabled so it actually reads as 3D. */
const TERRAIN_PITCH = 60

export interface UseTerrainOptions {
  /** Turn 3D terrain on/off. */
  enabled?: boolean
  /**
   * `raster-dem` source spec to use. Defaults to the free AWS Terrarium DEM
   * (`TERRAIN_DEM`) — no API key required.
   */
  source?: RasterDEMSourceSpecification
  /** Vertical exaggeration passed to `setTerrain`. @default 1.2 */
  exaggeration?: number
  /** Also add a `hillshade` layer from the same DEM. @default true */
  hillshade?: boolean
  /**
   * Ease the camera pitch in (to ~60°) when enabling and back to 0 when
   * disabling, so a flat map visibly becomes 3D. Opt out for hosts that
   * drive pitch themselves. @default true
   */
  autoPitch?: boolean
}

/**
 * 3D terrain + hillshade from a free `raster-dem` source.
 *
 * When `enabled`, adds the DEM source (if absent), calls `setTerrain`, and
 * optionally a `hillshade` layer. On disable/unmount it clears terrain and
 * removes the source + layer cleanly. Re-applies on `styledata` because a
 * style reload drops terrain. Terrain only reads as 3D with `pitch > 0`, so
 * `autoPitch` eases the camera in/out (default on).
 *
 * Mirrors the map-access + add/remove + cleanup pattern of `useMapLayers`.
 */
export function useTerrain({
  enabled = false,
  source = TERRAIN_DEM,
  exaggeration = DEFAULT_EXAGGERATION,
  hillshade = true,
  autoPitch = true,
}: UseTerrainOptions) {
  const { mapRef, isLoaded } = useMapContext()

  // Keep latest opts in refs so the styledata listener always reads current
  // values without re-subscribing.
  const optsRef = useRef({ source, exaggeration, hillshade })
  optsRef.current = { source, exaggeration, hillshade }

  useEffect(() => {
    const map = mapRef.current?.getMap()
    if (!map || !isLoaded) return

    const apply = () => {
      const m = mapRef.current?.getMap()
      if (!m || !m.isStyleLoaded()) return
      const { source: src, exaggeration: ex, hillshade: shade } = optsRef.current

      if (!m.getSource(DEM_SOURCE_ID)) {
        m.addSource(DEM_SOURCE_ID, src)
      }
      m.setTerrain({ source: DEM_SOURCE_ID, exaggeration: ex })

      if (shade) {
        if (!m.getLayer(HILLSHADE_LAYER_ID)) {
          m.addLayer({
            id: HILLSHADE_LAYER_ID,
            type: 'hillshade',
            source: DEM_SOURCE_ID,
          })
        }
      } else if (m.getLayer(HILLSHADE_LAYER_ID)) {
        m.removeLayer(HILLSHADE_LAYER_ID)
      }
    }

    const teardown = () => {
      const m = mapRef.current?.getMap()
      if (!m) return
      try {
        if (m.getTerrain()) m.setTerrain(null)
        if (m.getLayer(HILLSHADE_LAYER_ID)) m.removeLayer(HILLSHADE_LAYER_ID)
        if (m.getSource(DEM_SOURCE_ID)) m.removeSource(DEM_SOURCE_ID)
      } catch {
        // style may have been swapped out mid-teardown — ignore.
      }
    }

    if (!enabled) {
      teardown()
      if (autoPitch && map.getPitch() > 0) {
        map.easeTo({ pitch: 0, duration: 600 })
      }
      return
    }

    apply()
    if (autoPitch && map.getPitch() === 0) {
      map.easeTo({ pitch: TERRAIN_PITCH, duration: 800 })
    }

    // A style reload drops terrain/sources — re-apply when the style settles.
    map.on('styledata', apply)
    return () => {
      map.off('styledata', apply)
      teardown()
    }
  }, [mapRef, isLoaded, enabled, autoPitch])
}
