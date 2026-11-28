import type { LayerProps, LineLayerSpecification } from 'react-map-gl/maplibre'
import type { LineLayerOptions, RouteLayerOptions } from '../types'

export function createLineLayer({
  id,
  sourceId,
  color = '#3b82f6',
  width = 3,
  opacity = 1,
  dashArray,
  lineCap = 'round',
  lineJoin = 'round',
  blur = 0,
  minZoom,
  maxZoom,
}: LineLayerOptions): LayerProps {
  const paint: LineLayerSpecification['paint'] = {
    'line-color': color,
    'line-width': width,
    'line-opacity': opacity,
  }

  if (dashArray) {
    paint['line-dasharray'] = dashArray
  }

  if (blur > 0) {
    paint['line-blur'] = blur
  }

  const layer: LayerProps = {
    id,
    type: 'line',
    source: sourceId,
    layout: {
      'line-cap': lineCap,
      'line-join': lineJoin,
    },
    paint,
  }

  if (minZoom !== undefined) layer.minzoom = minZoom
  if (maxZoom !== undefined) layer.maxzoom = maxZoom

  return layer
}

export function createRouteLayers({
  sourceId,
  color = '#3b82f6',
  width = 4,
  ...rest
}: RouteLayerOptions): {
  outline: LayerProps
  route: LayerProps
} {
  return {
    outline: createLineLayer({
      id: `${sourceId}-outline`,
      sourceId,
      color: '#ffffff',
      width: width + 2,
      lineCap: 'round',
      lineJoin: 'round',
      ...rest,
    }),
    route: createLineLayer({
      id: `${sourceId}-route`,
      sourceId,
      color,
      width,
      lineCap: 'round',
      lineJoin: 'round',
      ...rest,
    }),
  }
}

export function createDashedLineLayer(
  options: Omit<LineLayerOptions, 'dashArray'>
): LayerProps {
  return createLineLayer({
    ...options,
    dashArray: [2, 2],
  })
}

export function createAnimatedLineLayer(options: LineLayerOptions): LayerProps {
  return createLineLayer({
    ...options,
    dashArray: [0, 4, 3],
  })
}
