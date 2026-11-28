'use client'

import { useCallback, useRef, useState } from 'react';

export interface PinchZoomState {
  scale: number
  x: number
  y: number
}

export interface UsePinchZoomOptions {
  minScale?: number
  maxScale?: number
  onZoomChange?: (zoomed: boolean) => void
}

export interface UsePinchZoomReturn {
  state: PinchZoomState
  isZoomed: boolean
  handlers: {
    onTouchStart: (e: React.TouchEvent) => void
    onTouchMove: (e: React.TouchEvent) => void
    onTouchEnd: (e: React.TouchEvent) => void
  }
  reset: () => void
  zoomTo: (scale: number, x?: number, y?: number) => void
}

const INITIAL_STATE: PinchZoomState = { scale: 1, x: 0, y: 0 }

/**
 * Hook for pinch-to-zoom functionality on touch devices
 */
export function usePinchZoom(options: UsePinchZoomOptions = {}): UsePinchZoomReturn {
  const { minScale = 1, maxScale = 3, onZoomChange } = options

  const [state, setState] = useState<PinchZoomState>(INITIAL_STATE)

  // Track touch state and container size
  const touchRef = useRef<{
    initialDistance: number
    initialScale: number
    initialX: number
    initialY: number
    centerX: number
    centerY: number
    isPinching: boolean
    lastTap: number
    containerWidth: number
    containerHeight: number
  }>({
    initialDistance: 0,
    initialScale: 1,
    initialX: 0,
    initialY: 0,
    centerX: 0,
    centerY: 0,
    isPinching: false,
    lastTap: 0,
    containerWidth: 0,
    containerHeight: 0,
  })

  const isZoomed = state.scale > 1.05

  // Calculate distance between two touch points
  const getDistance = useCallback((touches: React.TouchList): number => {
    const a = touches[0]
    const b = touches[1]
    if (!a || !b) return 0
    const dx = a.clientX - b.clientX
    const dy = a.clientY - b.clientY
    return Math.sqrt(dx * dx + dy * dy)
  }, [])

  // Get center point between two touches
  const getCenter = useCallback((touches: React.TouchList): { x: number; y: number } => {
    const a = touches[0]
    const b = touches[1]
    if (!a) return { x: 0, y: 0 }
    if (!b) return { x: a.clientX, y: a.clientY }
    return {
      x: (a.clientX + b.clientX) / 2,
      y: (a.clientY + b.clientY) / 2,
    }
  }, [])

  // Calculate max pan based on container size and scale
  const getMaxPan = useCallback((scale: number) => {
    const { containerWidth, containerHeight } = touchRef.current
    // When zoomed, allow panning up to half the "extra" size
    // At 2x zoom on 400px container: can pan 200px in each direction
    return {
      x: (containerWidth * (scale - 1)) / 2,
      y: (containerHeight * (scale - 1)) / 2,
    }
  }, [])

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    const touches = e.touches

    // Store container dimensions from the element
    const rect = e.currentTarget.getBoundingClientRect()
    touchRef.current.containerWidth = rect.width
    touchRef.current.containerHeight = rect.height

    // Double tap to zoom
    const touch0 = touches[0]
    if (touches.length === 1 && touch0) {
      const now = Date.now()
      const timeSinceLastTap = now - touchRef.current.lastTap

      if (timeSinceLastTap < 300) {
        // Double tap detected
        e.preventDefault()
        if (isZoomed) {
          setState(INITIAL_STATE)
          onZoomChange?.(false)
        } else {
          const x = touch0.clientX - rect.left - rect.width / 2
          const y = touch0.clientY - rect.top - rect.height / 2
          setState({ scale: 2, x: -x * 0.5, y: -y * 0.5 })
          onZoomChange?.(true)
        }
        touchRef.current.lastTap = 0
        return
      }

      touchRef.current.lastTap = now

      // Single finger - start pan (if zoomed)
      if (isZoomed) {
        touchRef.current.initialX = touch0.clientX - state.x
        touchRef.current.initialY = touch0.clientY - state.y
      }
    }

    // Two finger pinch
    if (touches.length === 2) {
      e.preventDefault()
      touchRef.current.isPinching = true
      touchRef.current.initialDistance = getDistance(touches)
      touchRef.current.initialScale = state.scale

      const center = getCenter(touches)
      touchRef.current.centerX = center.x
      touchRef.current.centerY = center.y
      touchRef.current.initialX = state.x
      touchRef.current.initialY = state.y
    }
  }, [isZoomed, state, getDistance, getCenter, onZoomChange])

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    const touches = e.touches

    // Pinch zoom
    if (touches.length === 2 && touchRef.current.isPinching) {
      e.preventDefault()

      const currentDistance = getDistance(touches)
      const scaleDelta = currentDistance / touchRef.current.initialDistance
      let newScale = touchRef.current.initialScale * scaleDelta

      // Clamp scale
      newScale = Math.max(minScale, Math.min(maxScale, newScale))

      // Calculate new position to zoom toward center
      const center = getCenter(touches)
      const dx = center.x - touchRef.current.centerX
      const dy = center.y - touchRef.current.centerY

      // Apply pan limits
      const maxPan = getMaxPan(newScale)
      const newX = Math.max(-maxPan.x, Math.min(maxPan.x, touchRef.current.initialX + dx))
      const newY = Math.max(-maxPan.y, Math.min(maxPan.y, touchRef.current.initialY + dy))

      setState({
        scale: newScale,
        x: newX,
        y: newY,
      })

      if (newScale > 1.05 !== isZoomed) {
        onZoomChange?.(newScale > 1.05)
      }
    }

    // Pan when zoomed (single finger)
    const panTouch = touches[0]
    if (touches.length === 1 && panTouch && isZoomed && !touchRef.current.isPinching) {
      e.preventDefault()

      const maxPan = getMaxPan(state.scale)
      const newX = panTouch.clientX - touchRef.current.initialX
      const newY = panTouch.clientY - touchRef.current.initialY

      setState((prev) => ({
        ...prev,
        x: Math.max(-maxPan.x, Math.min(maxPan.x, newX)),
        y: Math.max(-maxPan.y, Math.min(maxPan.y, newY)),
      }))
    }
  }, [isZoomed, state.scale, minScale, maxScale, getDistance, getCenter, getMaxPan, onZoomChange])

  const handleTouchEnd = useCallback((e: React.TouchEvent) => {
    if (e.touches.length < 2) {
      touchRef.current.isPinching = false
    }

    // Snap to 1 if close
    if (state.scale < 1.1 && state.scale > 0.9) {
      setState(INITIAL_STATE)
      onZoomChange?.(false)
    }
  }, [state.scale, onZoomChange])

  const reset = useCallback(() => {
    setState(INITIAL_STATE)
    onZoomChange?.(false)
  }, [onZoomChange])

  const zoomTo = useCallback((scale: number, x = 0, y = 0) => {
    const clampedScale = Math.max(minScale, Math.min(maxScale, scale))
    setState({ scale: clampedScale, x, y })
    onZoomChange?.(clampedScale > 1.05)
  }, [minScale, maxScale, onZoomChange])

  return {
    state,
    isZoomed,
    handlers: {
      onTouchStart: handleTouchStart,
      onTouchMove: handleTouchMove,
      onTouchEnd: handleTouchEnd,
    },
    reset,
    zoomTo,
  }
}
