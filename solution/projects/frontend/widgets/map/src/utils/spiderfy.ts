/**
 * Spiderfy Utilities
 *
 * Handle overlapping markers by spreading them out in a spiral/circle pattern.
 * Provides both static offset for initial display and animated spiderfy on click.
 */

import type { MarkerData } from '../types'

/** Configuration for spiderfy behavior */
export interface SpiderfyOptions {
  /** Minimum distance (in degrees) to consider points as overlapping. Default: 0.00001 (~1m) */
  overlapThreshold?: number
  /** Base radius for spiral in degrees. Default: 0.0001 (~10m) */
  spiralRadius?: number
  /** Whether to apply random jitter (vs deterministic spiral). Default: false */
  useJitter?: boolean
  /** Jitter amount in degrees when useJitter=true. Default: 0.00005 */
  jitterAmount?: number
}

const DEFAULT_OPTIONS: Required<SpiderfyOptions> = {
  overlapThreshold: 0.00001,
  spiralRadius: 0.0001,
  useJitter: false,
  jitterAmount: 0.00005,
}

/**
 * Group markers by their location (within threshold)
 * Returns map of "location key" -> markers at that location
 */
export function groupOverlappingMarkers(
  markers: MarkerData[],
  threshold: number = DEFAULT_OPTIONS.overlapThreshold
): Map<string, MarkerData[]> {
  const groups = new Map<string, MarkerData[]>()
  const assigned = new Set<string>()

  for (const marker of markers) {
    if (assigned.has(marker.id)) continue

    // Find all markers within threshold of this one
    const group: MarkerData[] = [marker]
    assigned.add(marker.id)

    for (const other of markers) {
      if (assigned.has(other.id)) continue

      const distance = Math.sqrt(
        Math.pow(marker.longitude - other.longitude, 2) +
        Math.pow(marker.latitude - other.latitude, 2)
      )

      if (distance <= threshold) {
        group.push(other)
        assigned.add(other.id)
      }
    }

    // Use first marker's coords as key
    const key = `${marker.longitude.toFixed(6)},${marker.latitude.toFixed(6)}`
    groups.set(key, group)
  }

  return groups
}

/**
 * Calculate spiral position for a point in a group
 * Uses Fermat's spiral for even distribution
 */
function getSpiralOffset(
  index: number,
  total: number,
  options: Required<SpiderfyOptions>
): { dLng: number; dLat: number } {
  if (total === 1 || index === 0) {
    return { dLng: 0, dLat: 0 }
  }

  const { spiralRadius } = options

  // Fermat spiral: r = a * sqrt(n), theta = n * golden_angle. The angular step
  // IS the golden angle, so points-per-rotation is not a free parameter here.
  const goldenAngle = Math.PI * (3 - Math.sqrt(5)) // ~137.5 degrees
  const angle = index * goldenAngle
  const radius = spiralRadius * Math.sqrt(index)

  return {
    dLng: radius * Math.cos(angle),
    dLat: radius * Math.sin(angle),
  }
}

/**
 * Calculate jitter offset (random but deterministic based on id)
 */
function getJitterOffset(
  markerId: string,
  options: Required<SpiderfyOptions>
): { dLng: number; dLat: number } {
  // Simple hash from id for deterministic "randomness"
  let hash = 0
  for (let i = 0; i < markerId.length; i++) {
    hash = ((hash << 5) - hash) + markerId.charCodeAt(i)
    hash = hash & hash
  }

  const { jitterAmount } = options
  const angle = (hash % 360) * (Math.PI / 180)
  const distance = (Math.abs(hash % 1000) / 1000) * jitterAmount

  return {
    dLng: distance * Math.cos(angle),
    dLat: distance * Math.sin(angle),
  }
}

/**
 * Apply offset to overlapping markers
 *
 * Returns new array with adjusted coordinates.
 * Original markers are not modified.
 *
 * @example
 * ```tsx
 * const adjustedMarkers = offsetOverlappingMarkers(markers, {
 *   spiralRadius: 0.0002,  // Larger spread
 * })
 * ```
 */
export function offsetOverlappingMarkers(
  markers: MarkerData[],
  options?: SpiderfyOptions
): MarkerData[] {
  const opts = { ...DEFAULT_OPTIONS, ...options }
  const groups = groupOverlappingMarkers(markers, opts.overlapThreshold)

  const result: MarkerData[] = []

  for (const group of groups.values()) {
    const only = group.length === 1 ? group[0] : undefined
    if (only !== undefined) {
      // Single marker, no offset needed
      result.push(only)
      continue
    }

    // Multiple markers at same location - apply offset
    group.forEach((marker, index) => {
      const offset = opts.useJitter
        ? getJitterOffset(marker.id, opts)
        : getSpiralOffset(index, group.length, opts)

      result.push({
        ...marker,
        longitude: marker.longitude + offset.dLng,
        latitude: marker.latitude + offset.dLat,
        data: {
          ...marker.data,
          _originalLongitude: marker.longitude,
          _originalLatitude: marker.latitude,
          _isOffset: true,
          _groupSize: group.length,
        },
      })
    })
  }

  return result
}

/**
 * Get spiderfy positions for animation
 *
 * Returns positions for markers to animate TO when expanding.
 * Use for click-to-expand behavior.
 *
 * @example
 * ```tsx
 * const expanded = getSpiderfyPositions(overlappingMarkers, center)
 * // Animate markers to their expanded positions
 * ```
 */
export function getSpiderfyPositions(
  markers: MarkerData[],
  center: { longitude: number; latitude: number },
  options?: SpiderfyOptions
): Array<{ marker: MarkerData; position: { longitude: number; latitude: number } }> {
  const opts = { ...DEFAULT_OPTIONS, ...options }

  return markers.map((marker, index) => {
    const offset = getSpiralOffset(index, markers.length, opts)

    return {
      marker,
      position: {
        longitude: center.longitude + offset.dLng,
        latitude: center.latitude + offset.dLat,
      },
    }
  })
}

/**
 * Check if markers have overlapping points
 */
export function hasOverlappingMarkers(
  markers: MarkerData[],
  threshold: number = DEFAULT_OPTIONS.overlapThreshold
): boolean {
  const groups = groupOverlappingMarkers(markers, threshold)
  return Array.from(groups.values()).some(group => group.length > 1)
}

/**
 * Get statistics about overlapping markers
 */
export function getOverlapStats(
  markers: MarkerData[],
  threshold: number = DEFAULT_OPTIONS.overlapThreshold
): {
  totalMarkers: number
  uniqueLocations: number
  maxOverlap: number
  overlappingGroups: number
} {
  const groups = groupOverlappingMarkers(markers, threshold)
  const groupSizes = Array.from(groups.values()).map(g => g.length)

  return {
    totalMarkers: markers.length,
    uniqueLocations: groups.size,
    maxOverlap: Math.max(...groupSizes, 0),
    overlappingGroups: groupSizes.filter(s => s > 1).length,
  }
}
