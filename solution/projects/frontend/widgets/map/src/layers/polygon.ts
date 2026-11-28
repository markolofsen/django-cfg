import type { LayerProps } from 'react-map-gl/maplibre'
import type { PolygonLayerOptions } from '../types'

export function createPolygonLayer(
  id: string,
  sourceId: string,
  options: PolygonLayerOptions = {}
): LayerProps {
  // A MapLibre `fill` layer has no line width — `fill-outline-color` is always
  // one pixel. A polygon that needs a thicker border pairs this with
  // `createPolygonOutlineLayer`, which is a `line` layer and can express one.
  const {
    fillColor = '#3b82f6',
    fillOpacity = 0.3,
    strokeColor = '#1d4ed8',
  } = options

  return {
    id,
    type: 'fill',
    source: sourceId,
    paint: {
      'fill-color': fillColor,
      'fill-opacity': fillOpacity,
      'fill-outline-color': strokeColor,
    },
  }
}

export function createPolygonOutlineLayer(
  id: string,
  sourceId: string,
  options: {
    color?: string
    width?: number
  } = {}
): LayerProps {
  const { color = '#1d4ed8', width = 2 } = options

  return {
    id,
    type: 'line',
    source: sourceId,
    paint: {
      'line-color': color,
      'line-width': width,
    },
  }
}

export function createHighlightLayer(
  id: string,
  sourceId: string,
  options: {
    fillColor?: string
    fillOpacity?: number
  } = {}
): LayerProps {
  const {
    fillColor = '#fbbf24',
    fillOpacity = 0.5,
  } = options

  return {
    id,
    type: 'fill',
    source: sourceId,
    paint: {
      'fill-color': fillColor,
      'fill-opacity': fillOpacity,
    },
  }
}
