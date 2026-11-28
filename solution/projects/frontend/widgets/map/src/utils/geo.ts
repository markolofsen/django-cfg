import type { LngLatBoundsLike } from 'maplibre-gl'

/**
 * Calculate bounding box from an array of coordinates
 */
export function calculateBounds(points: [number, number][]): LngLatBoundsLike {
  if (points.length === 0) {
    throw new Error('Cannot calculate bounds for empty array')
  }

  const lngs = points.map((p) => p[0])
  const lats = points.map((p) => p[1])

  return [
    [Math.min(...lngs), Math.min(...lats)],
    [Math.max(...lngs), Math.max(...lats)],
  ]
}

/**
 * Calculate center point from an array of coordinates
 */
export function calculateCenter(points: [number, number][]): [number, number] {
  if (points.length === 0) {
    throw new Error('Cannot calculate center for empty array')
  }

  const sumLng = points.reduce((acc, p) => acc + p[0], 0)
  const sumLat = points.reduce((acc, p) => acc + p[1], 0)

  return [sumLng / points.length, sumLat / points.length]
}

/**
 * Calculate distance between two points in kilometers (Haversine formula)
 */
export function calculateDistance(
  from: [number, number],
  to: [number, number]
): number {
  const R = 6371 // Earth's radius in km
  const dLat = toRad(to[1] - from[1])
  const dLng = toRad(to[0] - from[0])

  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRad(from[1])) *
      Math.cos(toRad(to[1])) *
      Math.sin(dLng / 2) *
      Math.sin(dLng / 2)

  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

function toRad(deg: number): number {
  return deg * (Math.PI / 180)
}

/**
 * Check if a point is within bounds
 */
export function isPointInBounds(
  point: [number, number],
  bounds: [[number, number], [number, number]]
): boolean {
  const [[minLng, minLat], [maxLng, maxLat]] = bounds
  const [lng, lat] = point

  return lng >= minLng && lng <= maxLng && lat >= minLat && lat <= maxLat
}

/**
 * Expand bounds by a percentage
 */
export function expandBounds(
  bounds: [[number, number], [number, number]],
  percentage: number
): [[number, number], [number, number]] {
  const [[minLng, minLat], [maxLng, maxLat]] = bounds
  const lngDiff = (maxLng - minLng) * (percentage / 100)
  const latDiff = (maxLat - minLat) * (percentage / 100)

  return [
    [minLng - lngDiff, minLat - latDiff],
    [maxLng + lngDiff, maxLat + latDiff],
  ]
}
