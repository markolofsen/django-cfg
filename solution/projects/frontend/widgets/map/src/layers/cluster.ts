import type { ExpressionSpecification, FilterSpecification } from 'maplibre-gl'
import type { LayerProps } from 'react-map-gl/maplibre'

/**
 * `LayerProps` is a union discriminated on `type`, so `filter` and `paint` are
 * not readable from it — only from the member this file actually builds. Both
 * aliases narrow to that member rather than widening the union.
 */
type CircleLayer = Extract<LayerProps, { type: 'circle' }>
type SymbolLayer = Extract<LayerProps, { type: 'symbol' }>
import type { ClusterLayerOptions } from '../types'

/**
 * Cluster fills, low to high density.
 *
 * White, not a colour ramp. A blue/yellow/pink ramp fails twice on a real
 * basemap: yellow disappears against sand and pale landmass, and a saturated
 * blue circle competes with the sea under it. A white disc with a coloured
 * NUMBER and a shadow reads on every basemap because white is the one value the
 * map itself never uses for large filled areas.
 *
 * Density is carried by the label's tint and the disc's size, not by the fill.
 */
const DEFAULT_COLORS: [string, string, string] = ['#ffffff', '#ffffff', '#ffffff']

/**
 * Label colour per density tier.
 *
 * One ink across all three, not a ramp. A number that changes colour with
 * magnitude asks the reader to learn a legend to read a figure that is already
 * written out; size carries the density instead. `#111827` rather than pure
 * black — a true #000 numeral on white is harsher than any type this product
 * sets anywhere else.
 */
const DEFAULT_LABEL_COLORS: [string, string, string] = ['#111827', '#111827', '#111827']

const DEFAULT_RADII: [number, number, number] = [18, 24, 30]
const DEFAULT_THRESHOLDS: [number, number] = [100, 750]
const DEFAULT_HOVER_COLOR = '#0f172a' // slate-900: the disc inverts on hover

/**
 * Last-resort font, used only until `useStyleFont` has read the loaded style.
 *
 * Deliberately NOT a stack: a glyph server serves `fonts/A,B,C/{range}.pbf` as
 * one key, so naming a font the server lacks 404s the whole request and no
 * label renders. There is no safe universal value either — OpenFreeMap holds
 * `Noto Sans Bold` and not `Open Sans Bold`, CARTO the exact reverse — which is
 * why the real value comes from the style, not from here.
 */
const FALLBACK_TEXT_FONT = ['Noto Sans Bold']

export interface ClusterLayers {
  /** Drawn first: the elevation beneath the cluster disc. */
  clusterShadow: CircleLayer
  cluster: CircleLayer
  clusterCount: SymbolLayer
  /** Null unless `weightProperty` is set — see the note where they are built. */
  weightedPointShadow: CircleLayer | null
  weightedPointCircle: CircleLayer | null
  weightedPointCount: SymbolLayer | null
  /** Drawn under a hovered price chip. Null unless `labelProperty` is set. */
  weightedPointHalo: CircleLayer | null
  /** The single-home price label. Null unless `labelProperty` is set. */
  weightedPointLabel: SymbolLayer | null
  /**
   * The same label inverted, for the hovered or selected feature.
   *
   * Its filter matches nothing as built; the component sets it imperatively to
   * the one active key. Null unless `pillImageActive` is supplied.
   */
  weightedPointLabelActive: SymbolLayer | null
  unclusteredPoint: CircleLayer
}

export function createClusterLayers(options: ClusterLayerOptions): ClusterLayers {
  const {
    sourceId,
    colors = DEFAULT_COLORS,
    labelColors = DEFAULT_LABEL_COLORS,
    radii = DEFAULT_RADII,
    thresholds = DEFAULT_THRESHOLDS,
    hoverColor = DEFAULT_HOVER_COLOR,
    weightProperty,
    labelProperty,
    pillImage,
    pillImageActive,
    identityProperty,
    labelMinZoom,
    textFont = FALLBACK_TEXT_FONT,
  } = options

  // What decides a cluster's colour, size and label: the summed weight where
  // one was named, the feature count otherwise. `point_count` stays the
  // fallback so every existing caller is unaffected.
  const magnitude: ExpressionSpecification = weightProperty
    ? ['get', weightProperty]
    : ['get', 'point_count']

  /**
   * `magnitude` coerced to a number, for COMPARISONS only.
   *
   * `['get', …]` yields null when the property is absent, and comparing null
   * with a number throws inside the tile worker — "Expected value to be of type
   * number, but found null instead" — which aborts that tile's layout. A
   * missing weight is treated as 1: one feature, standing for itself.
   *
   * Paint and label expressions keep the raw `magnitude`; only `<=` and `>`
   * need this.
   */
  const magnitudeNumber: ExpressionSpecification = ['to-number', magnitude, 1]

  const step = <T,>(low: T, mid: T, high: T): ExpressionSpecification =>
    ['step', magnitude, low, thresholds[0], mid, thresholds[1], high] as ExpressionSpecification

  const onHover = (hovered: unknown, resting: unknown): ExpressionSpecification =>
    ['case', ['boolean', ['feature-state', 'hover'], false], hovered, resting] as ExpressionSpecification

  /**
   * The shadow, drawn as a second circle beneath the disc.
   *
   * MapLibre's circle layer has no box-shadow, so elevation is a blurred
   * sibling: a slightly larger, dark, very transparent circle offset downward.
   * Without it a white disc on a pale basemap has no edge at all.
   */
  const shadow = (id: string, filter: FilterSpecification): CircleLayer => ({
    id,
    type: 'circle',
    source: sourceId,
    filter,
    paint: {
      'circle-color': 'rgba(15,23,42,0.22)',
      'circle-radius': step(radii[0] + 3, radii[1] + 3, radii[2] + 3),
      'circle-blur': 0.7,
      'circle-translate': [0, 2],
    },
  })

  /**
   * The disc: white fill, dark ring, shadow beneath, inverting on hover.
   *
   * Ring AND shadow, because they do different jobs. The ring is the edge —
   * it makes the numeral's container definite at any size. The shadow is the
   * lift — it separates the disc from the basemap under it, which a ring alone
   * cannot do when the basemap is pale. Drop either and the marker either
   * merges into sand or reads as a flat sticker.
   */
  const disc = (id: string, filter: FilterSpecification): CircleLayer => ({
    id,
    type: 'circle',
    source: sourceId,
    filter,
    paint: {
      'circle-color': onHover(hoverColor, step(colors[0], colors[1], colors[2])),
      'circle-radius': onHover(
        step(radii[0] + 2, radii[1] + 2, radii[2] + 2),
        step(radii[0], radii[1], radii[2]),
      ),
      // A dark ring, scaling with the disc: 2 px on a small cluster, 3 px on a
      // large one, so weight reads at a glance without the fill changing colour.
      // Dark rather than white — a white ring on a white disc is a thicker blob,
      // not an edge, and the marker merges into the basemap.
      'circle-stroke-width': step(2, 2, 3),
      'circle-stroke-color': '#111827',
    },
  })

  /** The number: one dark ink, inverted to white when the disc inverts. */
  const label = (
    id: string,
    filter: FilterSpecification,
    field: ExpressionSpecification,
  ): SymbolLayer => ({
    id,
    type: 'symbol',
    source: sourceId,
    filter,
    layout: {
      'text-field': field,
      'text-size': step(13, 14, 15),
      'text-font': textFont,
      // A cluster label never yields: it is drawn on a disc this file placed,
      // so hiding the number would leave an unlabelled circle.
      'text-allow-overlap': true,
      // It DOES take part in collision, though — `ignore-placement` lets a lone
      // price chip settle on top of it, hiding the marker standing for a hundred
      // homes behind the one standing for a single home. The chip yields
      // instead; it is the cheaper loss.
      'text-ignore-placement': false,
    },
    paint: {
      'text-color': onHover('#ffffff', step(labelColors[0], labelColors[1], labelColors[2])),
      // No halo. It exists to rescue a label on an unpredictable basemap; here
      // the label sits on a disc this file drew, so it only muddies the
      // numeral's edges.
    },
  })

  // `point_count_abbreviated` is supercluster's own shortened count and has no
  // equivalent for a summed property, so a weighted cluster formats its own.
  const countField: ExpressionSpecification = weightProperty
    ? ['number-format', magnitude, { 'max-fraction-digits': 0 }]
    : ['get', 'point_count_abbreviated']

  const isCluster: FilterSpecification = ['has', 'point_count']
  const isLone: FilterSpecification = ['!', ['has', 'point_count']]

  /**
   * The ring under a hovered price chip — and the ONLY hover the chip gets.
   *
   * A circle, deliberately: MapLibre refuses every way of making the symbol
   * itself respond (the list is on the label layer's paint block), while a
   * circle has none of those restrictions. So the feedback is drawn beneath
   * rather than on the thing being pointed at.
   *
   * Invisible at rest (`opacity: 0`, `radius: 0`), so it costs nothing until
   * the pointer arrives.
   */
  const hoverHalo = (id: string, filter: FilterSpecification): CircleLayer => ({
    id,
    type: 'circle',
    source: sourceId,
    filter,
    paint: {
      'circle-color': hoverColor,
      // A soft shadow, not a disc.
      //
      // A circle cannot take a pill's shape, so a large opaque one reads as a
      // grey blob escaping the chip's corners. Just under the chip's height with
      // a blurred edge reads as a cast shadow instead.
      'circle-radius': onHover(15, 0),
      'circle-opacity': onHover(0.3, 0),
      'circle-blur': 0.5,
      'circle-translate': [0, 1],
    },
  })

  /** A lone feature that still stands for more than one home. */
  const groupOfOneOrMore: FilterSpecification = ['all', isLone, ['>', magnitudeNumber, 1]]

  const cluster = disc(`${sourceId}-clusters`, isCluster)
  const clusterCount = label(`${sourceId}-cluster-count`, isCluster, countField)

  /**
   * The lone-point paint, as one expression per zoom band.
   *
   * Three facts have to hold at once and they fight each other:
   *
   * - A point weighing more than 1 is a GROUP and keeps the cluster look.
   * - A lone home yields its circle to the price chip that replaces it.
   * - It may only yield where a chip is actually drawn: the chip layer filters
   *   on `['has', labelProperty]`, so a listing with no published price would
   *   otherwise fade into a hit target with no marker — clickable and
   *   invisible. On Bali 13% of points carry no price.
   *
   * **`interpolate` must be the OUTERMOST node.** MapLibre rejects `['zoom']`
   * anywhere but the top of a paint expression — "may only be used as input to
   * a top-level step or interpolate" — and a rejected expression drops the WHOLE
   * layer with no render and no warning beyond one console line. Nesting the
   * zoom fade inside the `case` chain drops `-weighted-point`, and above
   * `clusterMaxZoom` that is the only layer left: the map goes blank on zoom-in.
   *
   * So the branching is duplicated into each stop instead. One level over one
   * zoom, so the dot fades out as the chip takes over rather than blinking.
   */
  const lonePaint = <T,>(opts: { group: T; chipless: T; behindChip: T }): T | ExpressionSpecification => {
    // Which look a feature gets at a given zoom, chip or no chip.
    const at = (lone: T): ExpressionSpecification =>
      [
        'case',
        ['>', magnitudeNumber, 1],
        opts.group,
        labelProperty === undefined ? lone : ['case', ['has', labelProperty], lone, opts.chipless],
      ] as ExpressionSpecification

    if (labelMinZoom === undefined) return at(opts.behindChip)

    return [
      'interpolate',
      ['linear'],
      ['zoom'],
      labelMinZoom - 1,
      at(opts.chipless),
      labelMinZoom,
      at(opts.behindChip),
    ] as ExpressionSpecification
  }

  // A lone point is drawn as the same object as a cluster when a weight is in
  // play, because it IS one: every feature carries a count, and a point holding
  // 2,083 listings must not look like one holding 5.
  //
  // The exception is a weight of exactly 1 — one home, which is not a group and
  // must not read as one: a split cluster whose survivor still wears a cluster's
  // clothes is a disc labelled "1". It draws as a small solid pin instead.
  const weightedPointCircle: CircleLayer | null = weightProperty
    ? ((base) => {
        // Whether a chip ever replaces this circle. Without both, the circle IS
        // the marker at every zoom and keeps its resting look.
        const chipped = Boolean(pillImage && labelProperty)
        return {
          ...base,
          paint: {
            ...base.paint,
            'circle-radius': lonePaint({
              group: onHover(
                step(radii[0] + 2, radii[1] + 2, radii[2] + 2),
                step(radii[0], radii[1], radii[2]),
              ),
              // Full size under a chip as well as without one: this circle is
              // the layer `queryRenderedFeatures` hit-tests, and a symbol is
              // not, so shrinking it would make a priced listing unclickable.
              chipless: onHover(9, 7),
              behindChip: onHover(9, 7),
            }),
            'circle-color': lonePaint({
              group: onHover(hoverColor, step(colors[0], colors[1], colors[2])),
              // WHITE, like every other marker on this map.
              //
              // A listing with no published price gets no chip, so this circle
              // is its marker. A solid dark disc reads as a foreign object
              // beside the white pills and white cluster discs; this is the same
              // white body with the same dark ring, one size down.
              chipless: onHover(hoverColor, colors[0]),
              // Under a chip the circle is the HIT TARGET, not the marker, and
              // it is NOT `rgba(0,0,0,0)`: MapLibre excludes a fully
              // transparent circle from `queryRenderedFeatures`, which kills
              // hover and clicks on every priced pin. `circle-opacity` carries
              // the invisibility instead — the hit test does not consult it.
              behindChip: onHover(hoverColor, labelColors[0]),
            }),
            // 0.01, not 0: see the colour note. Zero is also excluded from the
            // hit test on some versions; a hundredth of an alpha is invisible
            // on any display and still a real, queryable feature.
            'circle-opacity': lonePaint({
              group: 1,
              chipless: 1,
              behindChip: chipped ? 0.01 : 1,
            }),
            'circle-stroke-width': lonePaint<number | ExpressionSpecification>({
              group: step(2, 2, 3),
              // The ring is what makes a white dot legible on pale ground; it
              // is the only edge a chipless pin has.
              chipless: 2,
              behindChip: chipped ? 0 : 2,
            }),
            'circle-stroke-opacity': lonePaint({
              group: 1,
              chipless: 1,
              behindChip: chipped ? 0 : 1,
            }),
            'circle-stroke-color': '#111827',
          },
        }
      })(disc(`${sourceId}-weighted-point`, isLone))
    : null

  const weightedPointCount: SymbolLayer | null = weightProperty
    ? {
        ...label(`${sourceId}-weighted-point-count`, isLone, countField),
        // A single home carries no number — the pin IS the statement.
        filter: groupOfOneOrMore,
      }
    : null

  /**
   * What a single home shows instead of a dot: its own headline figure.
   *
   * A dot says "something is here", which the visitor already knew — the map is
   * a map of listings. A price says which listing, and lets a buyer compare a
   * whole neighbourhood without opening anything.
   *
   * Two placement facts decide whether these appear at all:
   *
   * - **Overlap is refused**, unlike the cluster counts. Two prices stacked are
   *   unreadable and neither can be trusted, so MapLibre drops the lower-
   *   priority one. Dense areas therefore show a subset — which is correct, and
   *   is why a cluster still carries the count.
   * - **`sort-key` makes that subset meaningful.** Without one the survivor is
   *   whichever feature the source happened to order first; with it the dearest
   *   home wins its neighbourhood, so what stays on screen is the market's
   *   upper edge rather than an arbitrary pick.
   */
  const weightedPointLabel: SymbolLayer | null =
    weightProperty && labelProperty && pillImage
      ? {
          id: `${sourceId}-weighted-point-label`,
          type: 'symbol',
          source: sourceId,
          // `minzoom` on the LAYER, not a filter: it stops the chip being drawn
          // without touching the source, so the circle beneath it — what
          // `queryRenderedFeatures` hit-tests — keeps its full radius and the
          // listing stays clickable at every zoom.
          ...(labelMinZoom === undefined ? {} : { minzoom: labelMinZoom }),
          // Only a single home, and only one that HAS a figure. An empty pill
          // floating on the sea is worse than the dot it replaced.
          filter: ['all', isLone, ['<=', magnitudeNumber, 1], ['has', labelProperty]],
          layout: {
            'text-field': ['get', labelProperty],
            // A constant, and it MUST be one. `feature-state` is unavailable in
            // any layout property: symbol layout is computed during layout,
            // before feature state exists, and MapLibre responds by silently
            // dropping the ENTIRE layer — no console error, no partial render,
            // and every symptom points at the image or the font instead.
            //
            // Hover therefore lands in `paint` below, which is evaluated per
            // frame and does see feature state.
            'text-size': 12,
            'text-font': textFont,
            // The pill: one stretchable image sized to its own label, so the
            // price sits INSIDE a chip rather than beside a dot. `icon-text-fit`
            // is what does the stretching, and it needs a nine-patch image —
            // see `usePillImage`, which draws one instead of trusting whichever
            // sprite the visitor's basemap happens to ship.
            'icon-image': pillImage,
            // `width` only. `both` stretches the chip vertically to the text's
            // own line box too, which on a one-line label is a near-circular
            // blob; the height stays the image's own.
            'icon-text-fit': 'width',
            'icon-text-fit-padding': [0, 8, 0, 8],
            'icon-allow-overlap': false,
            'icon-ignore-placement': false,
            // The chip and its price are ONE symbol: without this MapLibre may
            // place the icon and drop the text, leaving empty pills. The cost
            // is that a failure to place the icon takes the price with it,
            // which is why the nine-patch arithmetic in `usePillImage` is
            // load-bearing rather than cosmetic.
            'icon-optional': false,
            // Room to breathe between neighbours, in pixels. Without it two
            // chips touch and read as one wide control.
            'icon-padding': 2,
            // Overlap is NOT allowed here, unlike the counts. Two prices on top
            // of each other are unreadable and neither can be trusted; MapLibre
            // drops the lower-priority one instead, which is what every
            // price-pin map does.
            'text-allow-overlap': false,
            'text-ignore-placement': false,
            // Lower sorts first and wins placement, so this is negated: the
            // dearest home survives its neighbourhood rather than whichever one
            // the source listed first.
            'symbol-sort-key': ['-', 0, ['to-number', ['get', 'sortWeight'], 0]],
          },
          paint: {
            // NOTHING here reads feature state, and that is a hard limit rather
            // than a choice. On MapLibre 4.7.1:
            //
            // - `text-size` in layout → rejected outright ("feature-state data
            //   expressions are not supported with layout properties").
            // - `icon-image` swapped on state → ACCEPTED by the validator, then
            //   renders nothing. Worse than a rejection: no error at all.
            // - `icon-color` → needs an SDF icon, and an SDF cannot be
            //   nine-patch stretched (it renders the pill as a circle).
            // - `icon-translate` → "data expressions not supported". It is a
            //   paint property but not a data-driven one.
            //
            // So the chip itself cannot respond to the pointer. The hover is
            // carried entirely by `weightedPointHalo` beneath it — a circle,
            // which has none of these restrictions.
            'text-color': labelColors[0],
          },
        }
      : null

  /**
   * The active chip: the same label, inverted, over the one feature that is
   * hovered or selected.
   *
   * A SECOND LAYER is the only route. A symbol cannot restyle itself on feature
   * state — `text-size` in layout is rejected, `icon-image` swapped on state is
   * accepted and then draws nothing, `icon-color` needs an SDF (which cannot be
   * nine-patch stretched), and `icon-translate` refuses data expressions. A
   * `filter` on feature state is likewise accepted and inert, because filters
   * are evaluated when a tile is parsed and state is not available there.
   *
   * **This is a TEMPLATE, not a mounted layer.** `MapCluster` copies it onto a
   * second, UNCLUSTERED source holding exactly one feature — the pin under the
   * pointer, or the one marked from outside — and drops the `filter` on the way.
   * See `selectedData`. Mounted over the clustered source instead, a filter
   * matches every feature in a TILE, including the ones supercluster folded into
   * a circle, so a selection inside a cluster could not be drawn at all.
   *
   * Selection is matched on `identityProperty`, never on the label: two homes at
   * the same price share a label and both would invert.
   */
  const weightedPointLabelActive: SymbolLayer | null =
    weightedPointLabel && pillImageActive && labelProperty
      ? {
          ...weightedPointLabel,
          id: `${sourceId}-weighted-point-label-active`,
          // `minzoom` is INHERITED from the resting chip and must not be.
          //
          // `labelMinZoom` is a rule about a CROWD — a hundred resting prices
          // competing for one screen. This layer draws one chip by construction,
          // so that crowd cannot form here, and inheriting the threshold leaves
          // a dot that highlights nothing below it: dead to hover at the zoom
          // where a visitor most needs to know which pin they are on.
          minzoom: 0,
          filter: ['==', ['get', identityProperty ?? labelProperty], '\u0000none'],
          layout: {
            ...weightedPointLabel.layout,
            'icon-image': pillImageActive,
            // It must never lose placement to the RESTING chip it is replacing,
            // which is what `allow-overlap` buys: this source is drawn above
            // and its feature is already on the map below.
            'icon-allow-overlap': true,
            'text-allow-overlap': true,
            // But it still takes part in placement, so it cannot suppress the
            // neighbours it is drawn over, nor answer
            // `queryRenderedFeatures` in their place.
            //
            // It has no siblings to defend against, and must not: if the source
            // ever held a whole ~110 m cell, `allow-overlap` above would draw
            // Bali's densest 84 chips on one coordinate as a black blob —
            // `ignore-placement: false` does not prevent it. The guarantee is
            // upstream, in the one-feature source.
            'icon-ignore-placement': false,
            'text-ignore-placement': false,
          },
          paint: {
            ...weightedPointLabel.paint,
            'text-color': '#ffffff',
          },
        }
      : null

  // The plain dot, for callers with no weight — one feature, one thing.
  const unclusteredPoint: CircleLayer = {
    id: `${sourceId}-unclustered-point`,
    type: 'circle',
    source: sourceId,
    filter: isLone,
    paint: {
      'circle-color': onHover(hoverColor, labelColors[0]),
      'circle-radius': onHover(9, 7),
      'circle-stroke-width': 2,
      'circle-stroke-color': '#ffffff',
      // The one place a white ring is right: a dark pin needs the light edge,
      // which is the exact inverse of the disc above.
    },
  }

  return {
    clusterShadow: shadow(`${sourceId}-cluster-shadow`, isCluster),
    cluster,
    clusterCount,
    // Only a GROUP is elevated. A single home is a small solid pin with a white
    // ring; a shadow under it would make one listing shout louder than the
    // cluster of forty beside it.
    weightedPointShadow: weightProperty
      ? shadow(`${sourceId}-weighted-point-shadow`, groupOfOneOrMore)
      : null,
    weightedPointCircle,
    weightedPointCount,
    weightedPointHalo:
      weightProperty && labelProperty && pillImage
        ? hoverHalo(`${sourceId}-weighted-point-halo`, [
            'all',
            isLone,
            ['<=', magnitudeNumber, 1],
            ['has', labelProperty],
          ])
        : null,
    weightedPointLabel,
    weightedPointLabelActive,
    unclusteredPoint,
  }
}
