import type { LayerProps } from 'react-map-gl/maplibre'
import type { PointLayerOptions } from '../types'

export function createPointLayer(
  id: string,
  sourceId: string,
  options: PointLayerOptions = {}
): LayerProps {
  const {
    color = '#3b82f6',
    radius = 6,
    strokeWidth = 2,
    strokeColor = '#fff',
  } = options

  return {
    id,
    type: 'circle',
    source: sourceId,
    paint: {
      'circle-color': color,
      'circle-radius': radius,
      'circle-stroke-width': strokeWidth,
      'circle-stroke-color': strokeColor,
    },
  }
}

export function createHeatmapLayer(
  id: string,
  sourceId: string,
  options: {
    intensity?: number
    radius?: number
    opacity?: number
  } = {}
): LayerProps {
  const { intensity = 1, radius = 20, opacity = 0.8 } = options

  return {
    id,
    type: 'heatmap',
    source: sourceId,
    paint: {
      'heatmap-intensity': intensity,
      'heatmap-radius': radius,
      'heatmap-opacity': opacity,
      'heatmap-color': [
        'interpolate',
        ['linear'],
        ['heatmap-density'],
        0, 'rgba(0, 0, 255, 0)',
        0.2, 'rgb(0, 0, 255)',
        0.4, 'rgb(0, 255, 0)',
        0.6, 'rgb(255, 255, 0)',
        0.8, 'rgb(255, 128, 0)',
        1, 'rgb(255, 0, 0)',
      ],
    },
  }
}
