'use client'

import { useMapContext } from '../context';

/**
 * Hook to access the map context
 * Must be used within a MapProvider
 */
export function useMap() {
  return useMapContext()
}
