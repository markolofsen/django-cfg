'use client'

import { useCallback, useState, useEffect, useMemo, useRef, memo, type ReactNode } from 'react'
import { Source, Layer, useMap, Popup } from 'react-map-gl/maplibre'
import type { GeoJSONSource, MapMouseEvent } from 'maplibre-gl'
import type { MapRef } from 'react-map-gl/maplibre'
import { createClusterLayers } from '../layers'
import { useStyleFont } from '../hooks/useStyleFont'
import { usePillImage, PILL_IMAGE_ID, PILL_IMAGE_ACTIVE_ID } from '../hooks/usePillImage'
import type { ClusterLayerOptions } from '../types'

// Inject popup styles once
const POPUP_STYLE_ID = 'map-cluster-popup-styles'
function injectPopupStyles() {
  if (typeof document === 'undefined') return
  if (document.getElementById(POPUP_STYLE_ID)) return

  const style = document.createElement('style')
  style.id = POPUP_STYLE_ID
  style.textContent = `
    .maplibregl-popup.map-popup-clean .maplibregl-popup-content {
      padding: 0 !important;
      background: transparent !important;
      box-shadow: none !important;
      border-radius: 0 !important;
    }
    .maplibregl-popup.map-popup-clean .maplibregl-popup-tip {
      display: none !important;
    }
  `
  document.head.appendChild(style)
}

/**
 * Only the ids the style actually holds.
 *
 * `queryRenderedFeatures` THROWS on a layer that is not in the style — it does
 * not skip it — and the selection's layer comes and goes with the selection, so
 * an unfiltered list is a handler that dies whenever nothing is selected.
 */
function presentLayers(map: MapRef, ids: string[]): string[] {
  return ids.filter((id) => map.getLayer(id))
}

export interface MapClusterProps {
  sourceId: string
  data: GeoJSON.FeatureCollection
  clusterRadius?: number
  clusterMaxZoom?: number
  onClusterClick?: (clusterId: number, coordinates: [number, number]) => void
  onPointClick?: (feature: GeoJSON.Feature) => void
  /** Render prop for popup content - handles popup state automatically */
  renderPopup?: (feature: GeoJSON.Feature, onClose: () => void) => ReactNode
  /** Popup anchor position */
  popupAnchor?: 'top' | 'bottom' | 'left' | 'right'
  /** Popup offset */
  popupOffset?: number | [number, number]
  /** Pan offset X when clicking point (pixels). Positive = point shifts right. */
  panOffsetX?: number
  /** Pan offset Y when clicking point (pixels). Positive = point shifts down. */
  panOffsetY?: number
  colors?: [string, string, string]
  /** Label tint per density tier. See `ClusterLayerOptions.labelColors`. */
  labelColors?: [string, string, string]
  radii?: [number, number, number]
  thresholds?: [number, number]
  /** Color when marker/cluster is hovered */
  hoverColor?: string
  /**
   * Feature property drawn beside a single feature — its price, typically.
   * See `ClusterLayerOptions.labelProperty`.
   */
  labelProperty?: string
  /**
   * Feature property naming ONE feature, used to pick the active chip.
   * Defaults to `labelProperty`. See `ClusterLayerOptions.identityProperty`.
   */
  identityProperty?: string
  /**
   * The ONE feature that stays inverted while nothing is hovered, by identity.
   *
   * Hover wins while the pointer is over a chip, and the selection returns when
   * it leaves: a card open on the right must keep its pin marked, or the
   * visitor loses which one they are reading.
   *
   * One feature, never a group: a ~110 m cell here draws all 84 of Bali's
   * densest chips on one coordinate as a black blob.
   */
  activeKey?: string | null
  /**
   * The visitor clicked the map itself, hitting nothing.
   *
   * Used to clear a selection. Distinct from `onPointClick(null)`, which does
   * not exist: a point click always names a point.
   */
  onEmptyClick?: () => void
  /**
   * Zoom below which a lone feature's price label is not drawn.
   *
   * The feature still draws — as a dot — and stays clickable. See
   * `ClusterLayerOptions.labelMinZoom` for the measurement behind it.
   */
  labelMinZoom?: number
  /**
   * The pointer entered or left a lone feature, named by `identityProperty`.
   *
   * Null on leaving, and null over a CLUSTER — a cluster is many features and
   * names none of them. The chip inversion happens here either way, so a
   * caller that ignores this loses nothing.
   */
  onPointHover?: (key: string | null) => void
  /**
   * A feature to mark as though the pointer were over it, by identity.
   *
   * The other half of brushing: hovering a row in a list beside the map marks
   * its pin — the one pin, so the row and the pin agree. A real pointer hover
   * takes precedence while it lasts.
   */
  hoveredKey?: string | null
  /**
   * Feature property to SUM into each cluster, instead of counting features.
   *
   * Use when one feature already stands for many — an aggregate point carrying
   * its own `count`, a store with a stock level. Without it, three points
   * carrying 949, 2083 and 372 cluster into a circle labelled "3".
   *
   * Wires both ends: the source gets a `clusterProperties` sum under this name,
   * and the layers read it for colour, radius and label.
   */
  weightProperty?: string
  /**
   * Cluster label font stack. Defaults to one read from the ACTIVE style.
   *
   * Pass a value only to override that; a constant here is what breaks when
   * the visitor switches basemap. See `useStyleFont`.
   */
  textFont?: string[]
}

export const MapCluster = memo(function MapCluster({
  sourceId,
  data,
  clusterRadius = 50,
  clusterMaxZoom = 14,
  onClusterClick,
  onPointClick,
  renderPopup,
  popupAnchor = 'bottom',
  popupOffset = 15,
  panOffsetX = 0,
  panOffsetY = 150,
  colors,
  labelColors,
  radii,
  thresholds,
  hoverColor,
  weightProperty,
  labelProperty,
  identityProperty,
  labelMinZoom,
  activeKey = null,
  onEmptyClick,
  onPointHover,
  hoveredKey = null,
  textFont,
}: MapClusterProps) {
  const { current: map } = useMap()
  // The active style's own font, so a basemap switch cannot 404 the labels.
  const styleFont = useStyleFont()
  const resolvedFont = textFont ?? styleFont
  // The pill behind a single feature's label. Registered rather than taken from
  // the style's sprite, which differs per basemap; false until it is on the map,
  // so the layer is not built naming an image that does not exist yet.
  const pillReady = usePillImage()
  // Held in a ref, not a dependency: the hover subscription's deps are
  // deliberately narrow, and a caller's inline arrow would re-subscribe every
  // render, rebinding mousemove on every hit layer mid-gesture.
  const onPointHoverRef = useRef(onPointHover)
  onPointHoverRef.current = onPointHover
  // Read inside the pointer handlers, which must not re-subscribe when a row is
  // hovered — that would rebind mousemove on every hit layer mid-gesture.
  const hoveredKeyRef = useRef(hoveredKey)
  hoveredKeyRef.current = hoveredKey

  const [selectedFeature, setSelectedFeature] = useState<GeoJSON.Feature | null>(null)
  const [popupCoords, setPopupCoords] = useState<[number, number] | null>(null)

  // Inject popup styles on mount
  useEffect(() => {
    injectPopupStyles()
  }, [])

  // Memoize layers so layer ids stay referentially stable across renders.
  // Without this, the click/hover effect below re-subscribes on every render.
  const {
    clusterShadow,
    cluster,
    clusterCount,
    weightedPointShadow,
    weightedPointCircle,
    weightedPointCount,
    weightedPointHalo,
    weightedPointLabel,
    weightedPointLabelActive,
    unclusteredPoint,
  } = useMemo(() => {
    const layerOptions: ClusterLayerOptions = {
      sourceId,
      colors,
      labelColors,
      radii,
      thresholds,
      hoverColor,
      weightProperty,
      labelProperty,
      identityProperty,
      labelMinZoom,
      pillImage: pillReady ? PILL_IMAGE_ID : undefined,
      pillImageActive: pillReady ? PILL_IMAGE_ACTIVE_ID : undefined,
      textFont: resolvedFont,
    }
      return createClusterLayers(layerOptions)
    }, [sourceId, colors, labelColors, radii, thresholds, hoverColor, weightProperty, labelProperty, identityProperty, labelMinZoom, pillReady, resolvedFont])


  const clusterLayerId = cluster.id as string
  // The point layer that is actually MOUNTED, which is not always the plain
  // dot: a weighted caller mounts `weighted-point` instead. Naming the wrong one
  // is not a silent miss — `queryRenderedFeatures` THROWS on a layer the style
  // does not hold, aborting the whole handler and the cluster click with it.
  const pointLayerId = (weightedPointCircle ?? unclusteredPoint).id as string

  /**
   * Which feature the POINTER is over, as state rather than a layer filter.
   *
   * A `setFilter` on the clustered chip layer matches every feature sharing the
   * key, so a cell holding 30 listings inverts all 30 at once. Feeding the
   * unclustered source instead makes "exactly one" structural — `find` returns
   * one feature or none.
   *
   * A symbol cannot restyle itself on feature state, so the second source is
   * the mechanism; this only selects which feature goes into it.
   */
  const [pointerKey, setPointerKey] = useState<string | null>(null)

  // An external hover (a row in a list beside the map) and the pointer drive
  // the same single chip. The pointer wins while it is over a feature.
  useEffect(() => {
    if (hoveredKey === null) return
    setPointerKey(null)
  }, [hoveredKey])

  /**
   * The selected feature, lifted OUT of the clustered source.
   *
  /**
   * The selection's own layer: the active chip, unfiltered.
   *
   * Drawn from its own UNCLUSTERED source, so it is visible at every zoom over
   * the cluster that would otherwise fold it into a counted circle. The
   * alternative — zooming until it separates — moves the camera four or five
   * levels on every selection.
   *
   * Built by DELETING `filter` rather than setting it to `undefined` —
   * `react-map-gl` forwards the key either way, and MapLibre rejects the layer
   * with "filter: array expected, undefined found". Everything in this source is
   * the selection, so there is nothing to filter; an inherited filter would also
   * name the clustered source's properties.
   */
  const selectedLayer = useMemo(() => {
    if (!weightedPointLabelActive) return null
    const { filter: _ignored, ...rest } = weightedPointLabelActive
    return {
      ...rest,
      id: `${sourceId}-selected-label`,
      source: `${sourceId}-selected`,
    }
  }, [weightedPointLabelActive, sourceId])

  /**
   * The ONE feature to draw inverted: what the pointer is over, else what is
   * marked from outside.
   *
   * One feature, always — a `find`, never a `filter`. Resolving the key through
   * a property naming a GROUP marks a home's whole ~110 m cell: Bali's densest
   * holds 84 chips, all drawn on one coordinate with `icon-allow-overlap`, a
   * black blob the size of a district — and it brushes two rows from one pin
   * and two pins from one row.
   *
   * Hover takes precedence over the selection while it lasts, which is the
   * behaviour a pointer implies — and the selection returns when it leaves.
   */
  const selectedData = useMemo<GeoJSON.FeatureCollection>(() => {
    const identity = identityProperty ?? labelProperty
    const empty: GeoJSON.FeatureCollection = { type: 'FeatureCollection', features: [] }

    const wanted = pointerKey ?? hoveredKey ?? activeKey
    if (!wanted || !identity) return empty

    // The active chip is a chip: it can only draw a feature that HAS a label.
    // The resting layer says the same in a filter (`['has', labelProperty]`),
    // which this one cannot inherit — the copy onto the unclustered source
    // drops `filter` — so the guard lives here, on what the source holds.
    // Without it a listing with no published price inverts into a black
    // rectangle with no text.
    const match = data.features.find(
      (feature) =>
        feature.properties?.[identity] === wanted
        && (!labelProperty || feature.properties?.[labelProperty] !== undefined),
    )
    return match ? { type: 'FeatureCollection', features: [match] } : empty
  }, [activeKey, hoveredKey, pointerKey, data, identityProperty, labelProperty])

  // Every layer the pointer may be over, built once so the handlers below share
  // one identity. The price pill is included: it is the visible marker for a
  // single home, and a pointer on the chip but not on the small circle beneath
  // it must still select that home.
  const hitLayerIds = useMemo(() => {
    const ids = [clusterLayerId, pointLayerId]
    if (weightedPointLabel) ids.push(weightedPointLabel.id as string)
    // The selection's own layer, or clicking the SELECTED chip would read as a
    // click on empty map and clear itself — and inside a cluster that chip is
    // the only thing there to click.
    if (selectedLayer) ids.push(selectedLayer.id)
    return ids
  }, [clusterLayerId, pointLayerId, weightedPointLabel, selectedLayer])

  const handleClosePopup = useCallback(() => {
    setSelectedFeature(null)
    setPopupCoords(null)
  }, [])

  const handleClick = useCallback(
    async (event: MapMouseEvent) => {
      if (!map) return

      const features = map.queryRenderedFeatures(event.point, {
        layers: presentLayers(map, hitLayerIds),
      })

      // Read the element, then guard it: a `length` check narrows nothing.
      const feature = features?.[0]
      if (feature === undefined) return

      const geometry = feature.geometry

      if (geometry.type !== 'Point') return

      const coordinates = geometry.coordinates as [number, number]
      const clusterId = feature.properties?.cluster_id

      if (clusterId) {
        const source = map.getSource(sourceId) as GeoJSONSource
        if (!source) return

        try {
          const zoom = await source.getClusterExpansionZoom(clusterId)
          map.easeTo({
            center: coordinates,
            zoom,
            duration: 500,
          })
          onClusterClick?.(clusterId, coordinates)
        } catch (error) {
          console.error('Error expanding cluster:', error)
        }
      } else {
        // Handle point click
        onPointClick?.(feature)

        // If renderPopup is provided, show popup and pan to point
        if (renderPopup) {
          // Pan map to center on point with offset for popup visibility
          map.easeTo({
            center: coordinates,
            duration: 300,
            offset: [panOffsetX, panOffsetY],
          })
          setSelectedFeature(feature)
          setPopupCoords(coordinates)
        }
      }
    },
    [map, sourceId, hitLayerIds, onClusterClick, onPointClick, renderPopup, panOffsetX, panOffsetY]
  )

  // Close popup when clicking empty area
  const handleMapClick = useCallback(
    (event: MapMouseEvent) => {
      if (!map) return

      const features = map.queryRenderedFeatures(event.point, {
        layers: presentLayers(map, hitLayerIds),
      })

      // Empty map: the third way out, beside the card's own close and zooming
      // away. Without it a selection can only be replaced, never cleared, and a
      // visitor who is done reading has nowhere to click.
      if (!features || features.length === 0) {
        handleClosePopup()
        onEmptyClick?.()
      }
    },
    [map, hitLayerIds, handleClosePopup, onEmptyClick]
  )

  // Register click and hover handlers with proper cleanup
  useEffect(() => {
    if (!map) return

    let currentHoveredId: number | string | null = null

    // Helper to clear hover state.
    // Guarded: on unmount the source may already be gone, which would throw.
    const clearHoverState = () => {
      if (currentHoveredId !== null) {
        if (map.getSource(sourceId)) {
          map.setFeatureState(
            { source: sourceId, id: currentHoveredId },
            { hover: false }
          )
        }
        currentHoveredId = null
      }
    }

    // Only on a CHANGE. `mousemove` fires per pointer sample, and a setState in
    // the parent on every one of them re-renders the list beside the map at
    // pointer frequency.
    let reported: string | null = null
    const reportHover = (value: string | null) => {
      if (value === reported) return
      reported = value
      onPointHoverRef.current?.(value)
    }

    // Hover handler for both clusters and points
    const handleMouseMove = (e: MapMouseEvent) => {
      const features = map.queryRenderedFeatures(e.point, {
        layers: presentLayers(map, hitLayerIds),
      })

      const feature = features[0]
      if (feature !== undefined) {
        map.getCanvas().style.cursor = 'pointer'
        const featureId = feature.id

        if (featureId !== undefined && featureId !== currentHoveredId) {
          clearHoverState()
          currentHoveredId = featureId
          map.setFeatureState(
            { source: sourceId, id: featureId },
            { hover: true }
          )
        }
        // One read: the pin under the pointer. Only a lone feature carries an
        // identity; a cluster carries a count, and names no one pin.
        const identity = feature.properties?.[identityProperty ?? labelProperty ?? '']
        const key = typeof identity === 'string' ? identity : null
        setPointerKey(key)
        // The same pin outward, so a row beside the map marks the pin the
        // visitor is actually over — not its neighbours within ~110 m.
        reportHover(key)
      } else {
        map.getCanvas().style.cursor = ''
        clearHoverState()
        // Back to whatever the list beside the map says is hovered, not blank:
        // the pointer leaving a pin does not un-hover a row.
        setPointerKey(null)
        reportHover(null)
      }
    }

    const handleMouseLeave = () => {
      map.getCanvas().style.cursor = ''
      clearHoverState()
      setPointerKey(null)
      reportHover(null)
    }

    // Bound to EVERY hit layer, the price pill included: binding one set here
    // and querying a different set inside the handlers leaves the pill visible
    // but inert. `map.on(type, layerId, …)` tolerates a layer that does not
    // exist yet — unlike `queryRenderedFeatures` — and the effect re-runs when
    // the id list changes, so the selection's layer binds as soon as it appears.
    for (const id of hitLayerIds) {
      map.on('click', id, handleClick)
      map.on('mousemove', id, handleMouseMove)
      map.on('mouseleave', id, handleMouseLeave)
    }
    map.on('click', handleMapClick)

    // Cleanup on unmount
    return () => {
      clearHoverState()
      for (const id of hitLayerIds) {
        map.off('click', id, handleClick)
        map.off('mousemove', id, handleMouseMove)
        map.off('mouseleave', id, handleMouseLeave)
      }
      map.off('click', handleMapClick)
    }
  }, [map, sourceId, hitLayerIds, handleClick, handleMapClick])

  return (
    <>
      <Source
        id={sourceId}
        type="geojson"
        data={data}
        cluster={true}
        clusterMaxZoom={clusterMaxZoom}
        clusterRadius={clusterRadius}
        // The summed property a weighted cluster reads. Supercluster evaluates
        // this bottom-up as it builds each zoom level, so the total is exact
        // rather than recomputed per frame.
        clusterProperties={
          weightProperty
            ? { [weightProperty]: ['+', ['get', weightProperty]] }
            : undefined
        }
        generateId={true}
      >
        {/* Order is paint order: shadow, disc, number. */}
        {weightedPointShadow ? <Layer {...weightedPointShadow} /> : null}
        <Layer {...clusterShadow} />
        <Layer {...cluster} />
        <Layer {...clusterCount} />
        {/* A weighted lone point renders as its own circle+label; the plain dot
            is the fallback for callers with no weight. Exactly one of the two
            matches any given feature, because both filter on `!point_count` and
            only one is mounted.

            Flat, never wrapped in a fragment: `Source` clones its children to
            inject the source id, so a fragment between them receives `source`
            as a prop and React warns that Fragment takes only `key`/`children`. */}
        {weightedPointCircle ? <Layer {...weightedPointCircle} /> : null}
        {weightedPointCount ? <Layer {...weightedPointCount} /> : null}
        {/* Before the label, so the ring sits UNDER the chip it highlights. */}
        {weightedPointHalo ? <Layer {...weightedPointHalo} /> : null}
        {weightedPointLabel ? <Layer {...weightedPointLabel} /> : null}
        {weightedPointCircle ? null : <Layer {...unclusteredPoint} />}
      </Source>

      {/* The selection, outside the clustering.
          
          A second `Source` rather than a layer on the first: `cluster: true` is
          a property of the SOURCE, so the only way a feature can escape being
          folded into a circle is to come from somewhere that does not cluster.
          Empty when nothing is selected, so it costs nothing. */}
      {selectedLayer ? (
        <Source id={`${sourceId}-selected`} type="geojson" data={selectedData}>
          <Layer {...selectedLayer} />
        </Source>
      ) : null}

      {/* Popup rendered via render prop */}
      {renderPopup && selectedFeature && popupCoords && (
        <Popup
          longitude={popupCoords[0]}
          latitude={popupCoords[1]}
          anchor={popupAnchor}
          onClose={handleClosePopup}
          closeOnClick={false}
          closeButton={false}
          offset={popupOffset}
          maxWidth="none"
          className="map-popup-clean"
        >
          {renderPopup(selectedFeature, handleClosePopup)}
        </Popup>
      )}
    </>
  )
})
