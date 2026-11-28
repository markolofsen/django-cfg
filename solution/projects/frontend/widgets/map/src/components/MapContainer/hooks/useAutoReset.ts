'use client'

import { useCallback, useEffect, useRef } from 'react'

/**
 * Auto-reset timer. After `autoResetDelay` ms of inactivity the map eases back
 * to its initial viewport. Interaction (move-start) cancels any pending reset;
 * move-end (re)arms the timer when the feature is enabled.
 */
export function useAutoReset({
  autoResetDelay,
  resetToInitial,
}: {
  autoResetDelay: number
  resetToInitial: () => void
}) {
  const resetTimerRef = useRef<NodeJS.Timeout | null>(null)
  const isInteractingRef = useRef(false)

  const handleMoveStart = useCallback(() => {
    isInteractingRef.current = true
    // Clear any pending reset timer
    if (resetTimerRef.current) {
      clearTimeout(resetTimerRef.current)
      resetTimerRef.current = null
    }
  }, [])

  const handleMoveEnd = useCallback(() => {
    isInteractingRef.current = false
    // Start auto-reset timer if enabled
    if (autoResetDelay > 0) {
      resetTimerRef.current = setTimeout(() => {
        if (!isInteractingRef.current) {
          resetToInitial()
        }
      }, autoResetDelay)
    }
  }, [autoResetDelay, resetToInitial])

  // Cleanup timer on unmount
  useEffect(() => {
    return () => {
      if (resetTimerRef.current) {
        clearTimeout(resetTimerRef.current)
      }
    }
  }, [])

  return { handleMoveStart, handleMoveEnd }
}
