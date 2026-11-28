import { featureFilter, validateStyleMin } from '@maplibre/maplibre-gl-style-spec'
import type { FilterSpecification, LayerSpecification, StyleSpecification } from 'maplibre-gl'
import { describe, expect, it } from 'vitest'

import { createClusterLayers } from './cluster'

/**
 * The MLS search map's own configuration. Kept here rather than inlined per
 * test: the defect these guard against only appears when `labelProperty`,
 * `pillImage` and `labelMinZoom` are ALL set, which is exactly the production
 * combination and no default.
 */
const OPTIONS = {
  sourceId: 'markets',
  weightProperty: 'count',
  labelProperty: 'price',
  labelMinZoom: 13,
  identityProperty: 'id',
  pillImage: 'pill',
  pillImageActive: 'pill-active',
} as const

/**
 * The layers as a STYLE, ready for the validator MapLibre itself runs.
 *
 * A minimal source is supplied because every layer names one; the validator
 * refuses a layer whose source is absent, which would mask the paint errors
 * this exists to find.
 */
function asStyle(layers: Record<string, unknown>): StyleSpecification {
  const mounted = Object.values(layers).filter(
    (layer): layer is LayerSpecification =>
      Boolean(layer) && typeof layer === 'object' && 'id' in (layer as object),
  )
  return {
    version: 8,
    // Every real basemap declares one, and `text-field` is invalid without it.
    // Its absence is a property of this fixture, not of the layers.
    glyphs: 'https://example.invalid/fonts/{fontstack}/{range}.pbf',
    sources: {
      [OPTIONS.sourceId]: { type: 'geojson', data: { type: 'FeatureCollection', features: [] } },
    },
    layers: mounted,
  } as StyleSpecification
}

describe('createClusterLayers', () => {
  /**
   * MapLibre rejects `['zoom']` anywhere but the top of a paint expression and
   * DROPS THE WHOLE LAYER when it does — one console line, no render, no
   * throw. That silence is why this is a test rather than a review note: it
   * shipped to production and took `-weighted-point` off the style, so above
   * `clusterMaxZoom` — where the cluster is gone and that circle is the only
   * marker left — the map went blank on zoom-in.
   */
  it('builds layers MapLibre accepts', () => {
    const errors = validateStyleMin(asStyle(createClusterLayers(OPTIONS)))
    expect(errors.map((error) => error.message)).toEqual([])
  })

  /**
   * A listing with no published price gets no chip, so the circle IS its
   * marker. Measured on Bali, 13% of points carry none.
   */
  it('draws the lone circle for a feature that has no label', () => {
    const { weightedPointCircle } = createClusterLayers(OPTIONS)
    expect(weightedPointCircle).not.toBeNull()
    // The chipless branch must survive into the built expression, or a priced
    // map hides every unpriced home behind a 0.01-alpha hit target.
    expect(JSON.stringify(weightedPointCircle?.paint)).toContain(OPTIONS.labelProperty)
  })
})

/**
 * M4 — the render invariant: a feature in frame that no layer draws is a bug.
 *
 * The dropped `-weighted-point` layer was invisible to every other check. The
 * style validated once it was gone, the suite stayed green, and the map went
 * blank only above `clusterMaxZoom`, where that circle is the last layer left.
 * What would have caught it is asking, per feature and per zoom, whether
 * ANYTHING still draws this.
 *
 * MapLibre's own `featureFilter` answers it, so this asserts the real filter
 * semantics rather than a reading of them. Zoom is honoured as the renderer
 * does: a layer draws at `z` only within [`minzoom`, `maxzoom`).
 */
function drawnBy(
  layers: Record<string, unknown>,
  feature: GeoJSON.Feature,
  zoom: number,
): string[] {
  return mounted(layers)
    .filter((layer) => {
      const { minzoom = 0, maxzoom = 24 } = layer as { minzoom?: number; maxzoom?: number }
      if (zoom < minzoom || zoom >= maxzoom) return false
      const filter = (layer as { filter?: unknown }).filter
      if (filter === undefined) return true
      return featureFilter(filter as FilterSpecification, "layers[0].filter").filter(
        { zoom } as never,
        feature as never,
        {} as never,
      )
    })
    .map((layer) => layer.id)
}

/**
 * The layers `MapCluster` actually mounts — not everything `createClusterLayers`
 * returns.
 *
 * `unclusteredPoint` and `weightedPointCircle` are MUTUALLY EXCLUSIVE:
 * `MapCluster` renders `{weightedPointCircle ? null : <Layer {...unclusteredPoint} />}`.
 * Treating both as present makes the plain dot a fallback that catches every
 * lone feature at every zoom, and the invariant below can then never fail — it
 * passed against a build with `weighted-point` deliberately dropped, which is
 * the exact production defect it exists to catch.
 */
function mounted(layers: Record<string, unknown>): LayerSpecification[] {
  const all = Object.values(layers).filter(
    (layer): layer is LayerSpecification =>
      Boolean(layer) && typeof layer === 'object' && 'id' in (layer as object),
  )
  // The plain dot is mounted only by a caller with NO weight. Deciding that
  // from whether `-weighted-point` survived would re-add the dot the moment
  // that layer went missing — restoring the fallback that hid the defect.
  // `OPTIONS` is weighted, so here the dot is never mounted.
  return all.filter((layer) => !layer.id.endsWith('-unclustered-point'))
}

const point = (properties: Record<string, unknown>): GeoJSON.Feature => ({
  type: 'Feature',
  properties,
  geometry: { type: 'Point', coordinates: [115.21, -8.65] },
})

describe('every feature in frame is drawn by something', () => {
  const layers = createClusterLayers(OPTIONS)

  /**
   * The three kinds the MLS source actually emits, named as the map sees them.
   * `count` is the weight; a cluster carries `point_count` instead.
   */
  const kinds = {
    'a cluster': point({ point_count: 42, count: 42 }),
    'a group of several at one spot': point({ count: 7, price: '$500k' }),
    'a single priced home': point({ count: 1, price: '$500k' }),
    // 13% of Bali points carry no price. This is the feature whose ONLY marker
    // is the circle, so it is the one the dropped layer made invisible.
    'a single home with no price': point({ count: 1 }),
  }

  // z14 is below `labelMinZoom` (13) only on the way in; the walk covers the
  // handover to the chip and everything above `clusterMaxZoom`, which is where
  // the production blank appeared.
  const zooms = [14, 15, 16, 17, 18, 19, 20]

  for (const [name, feature] of Object.entries(kinds)) {
    it(`draws ${name} at every zoom from 14 to 20`, () => {
      for (const zoom of zooms) {
        expect(drawnBy(layers, feature, zoom), `${name} at z${zoom}`).not.toEqual([])
      }
    })
  }

  /**
   * Stronger than "something draws it", and the specific regression:
   * `queryRenderedFeatures` hit-tests the CIRCLE, never a symbol. A chip alone
   * is a marker nobody can click, so the circle must survive at every zoom —
   * including above `clusterMaxZoom`, where it is also the only thing visible.
   */
  it('keeps the hit-target circle under every single home, at every zoom', () => {
    for (const zoom of zooms) {
      for (const feature of [kinds['a single priced home'], kinds['a single home with no price']]) {
        expect(
          drawnBy(layers, feature, zoom),
          `hit target at z${zoom}`,
        ).toContain(`${OPTIONS.sourceId}-weighted-point`)
      }
    }
  })
})
