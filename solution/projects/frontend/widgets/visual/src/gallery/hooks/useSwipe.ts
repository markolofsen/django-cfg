'use client'

import { useCallback, useState } from 'react';

import type { TouchEvent } from 'react'

export interface UseSwipeOptions {
  /** Minimum swipe distance in pixels */
  minDistance?: number
  /** Callback when swiped left */
  onSwipeLeft?: () => void
  /** Callback when swiped right */
  onSwipeRight?: () => void
  /** Callback when swiped up */
  onSwipeUp?: () => void
  /** Callback when swiped down */
  onSwipeDown?: () => void
}

interface TouchPosition {
  x: number
  y: number
}

/**
 * Hook for handling swipe gestures
 */
export function useSwipe({
  minDistance = 50,
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
}: UseSwipeOptions = {}) {
  const [touchStart, setTouchStart] = useState<TouchPosition | null>(null)
  const [touchEnd, setTouchEnd] = useState<TouchPosition | null>(null)

  const handleTouchStart = useCallback((e: TouchEvent) => {
    setTouchEnd(null)
    const touch = e.targetTouches[0]
    if (touch) {
      setTouchStart({ x: touch.clientX, y: touch.clientY })
    }
  }, [])

  const handleTouchMove = useCallback((e: TouchEvent) => {
    const touch = e.targetTouches[0]
    if (touch) {
      setTouchEnd({ x: touch.clientX, y: touch.clientY })
    }
  }, [])

  const handleTouchEnd = useCallback(() => {
    if (!touchStart || !touchEnd) return

    const deltaX = touchStart.x - touchEnd.x
    const deltaY = touchStart.y - touchEnd.y
    const absX = Math.abs(deltaX)
    const absY = Math.abs(deltaY)

    // Determine if horizontal or vertical swipe
    if (absX > absY && absX > minDistance) {
      // Horizontal swipe
      if (deltaX > 0) {
        onSwipeLeft?.()
      } else {
        onSwipeRight?.()
      }
    } else if (absY > absX && absY > minDistance) {
      // Vertical swipe
      if (deltaY > 0) {
        onSwipeUp?.()
      } else {
        onSwipeDown?.()
      }
    }

    setTouchStart(null)
    setTouchEnd(null)
  }, [touchStart, touchEnd, minDistance, onSwipeLeft, onSwipeRight, onSwipeUp, onSwipeDown])

  return {
    onTouchStart: handleTouchStart,
    onTouchMove: handleTouchMove,
    onTouchEnd: handleTouchEnd,
  }
}
