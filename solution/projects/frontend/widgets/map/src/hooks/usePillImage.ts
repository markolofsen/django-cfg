'use client'

import { useEffect, useState } from 'react'
import { useMap } from 'react-map-gl/maplibre'

/** Image id registered on the map. Stable, so layers can name it statically. */
export const PILL_IMAGE_ID = 'mls-pill'
/** The same chip inverted, drawn for the hovered or selected feature. */
export const PILL_IMAGE_ACTIVE_ID = 'mls-pill-active'

/**
 * Registers a rounded-rectangle image for `icon-text-fit` price pills.
 *
 * A pill is an icon that STRETCHES to its label, which MapLibre does through
 * `icon-text-fit` against a nine-patch `stretchX`/`stretchY`/`content` image.
 * The built-in styles each ship their own sprite under their own names and a
 * caller cannot rely on any of them — the same per-style problem the glyph
 * stack had — so the image is drawn here and added to whichever style loaded.
 *
 * **Not SDF, deliberately.** An SDF icon encodes shape as a distance field, and
 * stretching a distance field rescales the distances with it: the 10px corner
 * radius grew with the label until the pill rendered as a giant circle. A plain
 * RGBA bitmap stretches only the bands the nine-patch marks, which is what
 * keeps the corners the size they were drawn. The cost is that `icon-color`
 * no longer tints it, so hover inverts the TEXT rather than the chip.
 *
 * Re-added on `styledata`, because switching basemap replaces the style and
 * every image registered against it.
 */
export function usePillImage(): boolean {
  const { current: map } = useMap()
  const [ready, setReady] = useState(false)

  useEffect(() => {
    if (!map) return

    const add = () => {
      // `idle` fires continuously, so this must be cheap and idempotent:
      // `setReady(true)` on an already-true state is a no-op in React, and
      // `hasImage` short-circuits before any drawing happens.
      if (map.hasImage(PILL_IMAGE_ID) && map.hasImage(PILL_IMAGE_ACTIVE_ID)) {
        setReady(true)
        return
      }

      // Drawn at 2x and declared `pixelRatio: 2`, so the corners stay smooth
      // on a retina display instead of showing the stair-step a 1x bitmap has.
      const scale = 2
      // A 28px-tall chip whose caps are semicircles — a pill. `height` is the
      // chip's real height; `cap` is how much of each end cannot stretch.
      //
      // The arithmetic here is load-bearing, and getting it wrong does not
      // degrade the pill, it DELETES it: MapLibre drops a symbol whose fitted
      // content box is narrower than its own non-stretchable ends, and with
      // `icon-optional: false` the label goes with it. A 32px image with a 15px
      // radius made the two caps 60 of its 64 pixels — wider than any content
      // box — which is exactly how the price pins vanished.
      //
      // So the caps stay at half the height (a semicircle, the minimum that
      // still reads as a pill) and the image is deliberately WIDER than tall,
      // leaving a real middle band to stretch.
      // Even, so `height / 2` is a whole pixel: the nine-patch bands are image
      // pixels and MapLibre wants integers.
      const height = 28
      const cap = height / 2
      const width = height + 8
      const radius = cap
      const canvas = document.createElement('canvas')
      canvas.width = width * scale
      canvas.height = height * scale
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      // `roundRect` is the one API here that is not universally old. Bail
      // rather than throwing: `ready` stays false, the layer is never built,
      // and a single home falls back to its dot — a worse pin, not a blank map.
      if (typeof ctx.roundRect !== 'function') return
      ctx.scale(scale, scale)

      ctx.fillStyle = '#ffffff'
      ctx.strokeStyle = '#111827'
      ctx.lineWidth = 2
      ctx.beginPath()
      // Inset by half the stroke, or the ring is clipped by the canvas edge.
      ctx.roundRect(1, 1, width - 2, height - 2, radius - 1)
      ctx.fill()
      ctx.stroke()

      const nine = {
        pixelRatio: scale,
        // In IMAGE pixels, which is why every value is scaled.
        //
        // `stretchX` is the band BETWEEN the caps — the only part that may
        // grow. `stretchY` is a sliver at the vertical centre, present so the
        // chip is a legal nine-patch; nothing stretches it, because
        // `icon-text-fit` is `width`.
        //
        // `content` must sit INSIDE the caps, or the fitted box is narrower
        // than the ends and MapLibre drops the symbol. It is the middle band
        // inset by the ring.
        stretchX: [[cap * scale, (width - cap) * scale]] as [number, number][],
        stretchY: [[(cap - 1) * scale, (cap + 1) * scale]] as [number, number][],
        content: [cap * scale, 3 * scale, (width - cap) * scale, (height - 3) * scale] as
          [number, number, number, number],
      }

      const pixels = () =>
        new Uint8ClampedArray(ctx.getImageData(0, 0, width * scale, height * scale).data)

      map.addImage(
        PILL_IMAGE_ID,
        { width: width * scale, height: height * scale, data: pixels() },
        nine,
      )

      // TWO images, because a plain (non-SDF) icon cannot be tinted at all and
      // every way of restyling one symbol on hover is closed on MapLibre 4.7.1
      // (the measured list is on the label layer). The active state is drawn by
      // a SECOND layer naming this second image, whose filter is set
      // imperatively to the one key that is hovered or selected — a filter over
      // a real property works where feature state does not.
      ctx.clearRect(0, 0, width, height)
      ctx.fillStyle = '#111827'
      ctx.strokeStyle = '#111827'
      ctx.beginPath()
      ctx.roundRect(1, 1, width - 2, height - 2, radius - 1)
      ctx.fill()
      ctx.stroke()
      map.addImage(
        PILL_IMAGE_ACTIVE_ID,
        { width: width * scale, height: height * scale, data: pixels() },
        nine,
      )

      setReady(true)
    }

    add()
    // THREE events, not one, and the reason is a race that leaves the pill
    // silently unregistered.
    //
    // `styledata` fires while the style loads — which may be BEFORE this effect
    // runs, on a map the container already mounted. Subscribing to it alone
    // therefore waits for an event that has already happened and will not
    // repeat until the visitor switches basemap, so `ready` stays false and the
    // layer naming the image is never built. `load` and `idle` close that
    // window: `load` for the first style, `idle` as the backstop for a style
    // that finished between render and effect.
    map.on('styledata', add)
    map.on('load', add)
    map.on('idle', add)
    return () => {
      map.off('styledata', add)
      map.off('load', add)
      map.off('idle', add)
    }
  }, [map])

  return ready
}
