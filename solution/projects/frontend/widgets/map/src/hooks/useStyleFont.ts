'use client'

import { useEffect, useRef, useState } from 'react'
import { useMap } from 'react-map-gl/maplibre'

/**
 * The font stack the ACTIVE basemap can actually render.
 *
 * A glyph server serves a stack as one key — `fonts/A,B,C/{range}.pbf` — so a
 * name the server does not hold 404s the whole request and no label renders.
 * There is no safe constant: measured 2026-09-12, OpenFreeMap serves
 * `Noto Sans Bold` and 404s `Open Sans Bold`, CARTO does the exact opposite,
 * and they share no font at all. A hardcoded stack therefore breaks half the
 * switcher's options — which is what made the pins vanish on Light and Dark.
 *
 * So it is read from the style rather than declared: the style's own symbol
 * layers name fonts its glyph endpoint is guaranteed to hold. Bold is
 * preferred where the style offers one, since these are numerals on a filled
 * circle.
 *
 * Re-reads on `styledata`, which is what fires when the visitor switches
 * basemap.
 */
export function useStyleFont(): string[] | undefined {
  const { current: map } = useMap()
  const [font, setFont] = useState<string[] | undefined>(undefined)
  // Cleared on every style change, so a basemap switch re-reads.
  const resolved = useRef(false)

  useEffect(() => {
    if (!map) return

    const invalidate = () => {
      resolved.current = false
    }
    map.on('styledataloading', invalidate)

    const read = () => {
      // `idle` fires continuously, so this returns early once a font is known:
      // walking every layer of a large style on each frame would be real work
      // for an answer that cannot change without a style change.
      if (resolved.current) return
      const layers = map.getStyle()?.layers
      if (!layers) return

      const stacks: string[][] = []
      for (const layer of layers) {
        if (layer.type !== 'symbol') continue
        const value = layer.layout?.['text-font']
        // Only a literal array is usable. A `text-font` given as an expression
        // resolves per feature and cannot be reused as a constant here.
        if (Array.isArray(value) && value.every((name) => typeof name === 'string')) {
          stacks.push(value as string[])
        }
      }

      if (stacks.length === 0) return
      const bold = stacks.find((stack) => stack.some((name) => /bold/i.test(name)))
      resolved.current = true
      setFont(bold ?? stacks[0])
    }

    read()
    // `load` and `idle` alongside `styledata`, for the race described in
    // `usePillImage`: `styledata` may already have fired before this effect
    // ran, and on its own it would then never resolve a font.
    map.on('styledata', read)
    map.on('load', read)
    map.on('idle', read)
    return () => {
      map.off('styledataloading', invalidate)
      map.off('styledata', read)
      map.off('load', read)
      map.off('idle', read)
    }
  }, [map])

  return font
}
