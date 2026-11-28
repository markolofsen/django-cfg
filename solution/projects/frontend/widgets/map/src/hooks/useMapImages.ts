'use client'

import { useEffect, useState } from 'react'

import { useMapContext } from '../context'

/**
 * A single icon image to register with the map's sprite at runtime.
 */
export interface MapImage {
  /** Image id — reference this from a symbol layer's `icon-image`. */
  id: string
  /** URL to load the image from (PNG/SVG/data-URL). */
  url: string
  /**
   * Treat the image as an SDF (signed-distance field) so `icon-color` can
   * recolor it per-feature. Use for single-color glyph icons.
   */
  sdf?: boolean
  /** Ratio of image pixels to screen pixels (e.g. `2` for @2x assets). */
  pixelRatio?: number
}

export interface UseMapImagesResult {
  /** `true` once every requested image has been registered on the map. */
  ready: boolean
}

/**
 * Register icon images on the map so a `symbol` layer can reference them by
 * id via `icon-image`. Images are loaded with `map.loadImage(url)` (MapLibre
 * 4 returns a Promise resolving to `{ data }`) and added with
 * `map.addImage(id, data, { sdf, pixelRatio })`.
 *
 * - Guards against double-add via `map.hasImage(id)`.
 * - Re-registers on `styledata` — a style swap drops runtime images, so we
 *   re-add them whenever the style reloads.
 * - Removes the images it added on unmount.
 *
 * @example
 * ```tsx
 * useMapImages([{ id: 'pin', url: '/icons/pin.png' }])
 * // then: createSymbolLayer({ id: 'pins', sourceId: 'places', iconImage: 'pin' })
 * ```
 */
export function useMapImages(images: MapImage[]): UseMapImagesResult {
  const { mapRef, isLoaded } = useMapContext()
  const [ready, setReady] = useState(false)

  // Stable key so the effect re-runs only when the image set actually changes.
  const key = images
    .map((img) => `${img.id}|${img.url}|${img.sdf ? 1 : 0}|${img.pixelRatio ?? ''}`)
    .join('::')

  useEffect(() => {
    const map = mapRef.current?.getMap()
    if (!map || !isLoaded) return

    let cancelled = false

    const registerAll = async () => {
      let registered = 0
      await Promise.all(
        images.map(async (img) => {
          try {
            if (map.hasImage(img.id)) {
              registered += 1
              return
            }
            const response = await map.loadImage(img.url)
            if (cancelled || map.hasImage(img.id)) {
              registered += 1
              return
            }
            map.addImage(img.id, response.data, {
              sdf: img.sdf,
              pixelRatio: img.pixelRatio,
            })
            registered += 1
          } catch {
            // Image failed to load — skip it; a symbol layer referencing a
            // missing icon simply renders no icon for that feature.
          }
        }),
      )
      if (!cancelled) setReady(registered === images.length)
    }

    void registerAll()

    // A style reload (`setStyle`) drops runtime-added images — re-add them.
    const onStyleData = () => {
      void registerAll()
    }
    map.on('styledata', onStyleData)

    return () => {
      cancelled = true
      map.off('styledata', onStyleData)
      for (const img of images) {
        try {
          if (map.hasImage(img.id)) map.removeImage(img.id)
        } catch {
          // map may already be torn down
        }
      }
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mapRef, isLoaded, key])

  return { ready }
}
