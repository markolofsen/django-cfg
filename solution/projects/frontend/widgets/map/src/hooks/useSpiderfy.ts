'use client'

import { useMemo, useState, useCallback } from 'react'
import type { MarkerData } from '../types'
import {
  offsetOverlappingMarkers,
  getSpiderfyPositions,
  groupOverlappingMarkers,
  type SpiderfyOptions,
} from '../utils/spiderfy'

export interface UseSpiderfyOptions extends SpiderfyOptions {
  /** Enable automatic offset for overlapping markers. Default: true */
  enabled?: boolean
  /** Enable click-to-expand behavior. Default: false */
  expandOnClick?: boolean
}

export interface UseSpiderfyResult {
  /** Processed markers with offset applied */
  markers: MarkerData[]
  /** Currently expanded group (if expandOnClick enabled) */
  expandedGroup: MarkerData[] | null
  /** Center of expanded group */
  expandedCenter: { longitude: number; latitude: number } | null
  /** Expand a group of markers at given location */
  expandGroup: (longitude: number, latitude: number) => void
  /** Collapse expanded group */
  collapseGroup: () => void
  /** Check if a marker is part of the expanded group */
  isExpanded: (markerId: string) => boolean
  /** Get original position for an offset marker */
  getOriginalPosition: (marker: MarkerData) => { longitude: number; latitude: number }
}

/**
 * Hook to handle overlapping markers with automatic offset and optional spiderfy
 *
 * @example Basic usage - automatic offset
 * ```tsx
 * const { markers } = useSpiderfy(rawMarkers)
 *
 * return markers.map(marker => (
 *   <MapMarker key={marker.id} marker={marker} />
 * ))
 * ```
 *
 * @example With click-to-expand
 * ```tsx
 * const { markers, expandGroup, collapseGroup, isExpanded } = useSpiderfy(
 *   rawMarkers,
 *   { expandOnClick: true }
 * )
 *
 * const handleMarkerClick = (marker: MarkerData) => {
 *   if (marker.data?._groupSize > 1) {
 *     expandGroup(marker.longitude, marker.latitude)
 *   }
 * }
 * ```
 */
export function useSpiderfy(
  rawMarkers: MarkerData[],
  options?: UseSpiderfyOptions
): UseSpiderfyResult {
  const {
    enabled = true,
    expandOnClick = false,
    ...spiderfyOptions
  } = options ?? {}

  // Track expanded group state
  const [expandedCenter, setExpandedCenter] = useState<{
    longitude: number
    latitude: number
  } | null>(null)

  // Group overlapping markers
  const groups = useMemo(
    () => groupOverlappingMarkers(rawMarkers, spiderfyOptions.overlapThreshold),
    [rawMarkers, spiderfyOptions.overlapThreshold]
  )

  // Find expanded group if any
  const expandedGroup = useMemo(() => {
    if (!expandedCenter) return null

    const key = `${expandedCenter.longitude.toFixed(6)},${expandedCenter.latitude.toFixed(6)}`

    // Find group near the expanded center
    for (const [groupKey, group] of groups.entries()) {
      if (groupKey === key || group.length > 1) {
        // Check if any marker in group is near expanded center
        const isNear = group.some(m =>
          Math.abs(m.longitude - expandedCenter.longitude) < 0.0001 &&
          Math.abs(m.latitude - expandedCenter.latitude) < 0.0001
        )
        if (isNear) return group
      }
    }

    return null
  }, [groups, expandedCenter])

  // Process markers with offset
  const markers = useMemo(() => {
    if (!enabled) return rawMarkers

    // If we have an expanded group, use spiderfy positions for it
    if (expandOnClick && expandedGroup && expandedCenter) {
      const expandedPositions = getSpiderfyPositions(
        expandedGroup,
        expandedCenter,
        { ...spiderfyOptions, spiralRadius: (spiderfyOptions.spiralRadius ?? 0.0001) * 2 }
      )

      const expandedIds = new Set(expandedGroup.map(m => m.id))

      // Replace expanded markers with their spiderfied positions
      const otherMarkers = rawMarkers.filter(m => !expandedIds.has(m.id))
      const offsetOthers = offsetOverlappingMarkers(otherMarkers, spiderfyOptions)

      const expandedMarkers = expandedPositions.map(({ marker, position }) => ({
        ...marker,
        longitude: position.longitude,
        latitude: position.latitude,
        data: {
          ...marker.data,
          _originalLongitude: marker.longitude,
          _originalLatitude: marker.latitude,
          _isExpanded: true,
        },
      }))

      return [...offsetOthers, ...expandedMarkers]
    }

    return offsetOverlappingMarkers(rawMarkers, spiderfyOptions)
  }, [rawMarkers, enabled, expandOnClick, expandedGroup, expandedCenter, spiderfyOptions])

  // Expand a group at given location
  const expandGroup = useCallback((longitude: number, latitude: number) => {
    setExpandedCenter({ longitude, latitude })
  }, [])

  // Collapse expanded group
  const collapseGroup = useCallback(() => {
    setExpandedCenter(null)
  }, [])

  // Check if marker is expanded
  const isExpanded = useCallback(
    (markerId: string) => {
      if (!expandedGroup) return false
      return expandedGroup.some(m => m.id === markerId)
    },
    [expandedGroup]
  )

  // Get original position for offset marker
  const getOriginalPosition = useCallback(
    (marker: MarkerData): { longitude: number; latitude: number } => {
      if (marker.data?._originalLongitude !== undefined) {
        return {
          longitude: marker.data._originalLongitude as number,
          latitude: marker.data._originalLatitude as number,
        }
      }
      return { longitude: marker.longitude, latitude: marker.latitude }
    },
    []
  )

  return {
    markers,
    expandedGroup,
    expandedCenter,
    expandGroup,
    collapseGroup,
    isExpanded,
    getOriginalPosition,
  }
}
