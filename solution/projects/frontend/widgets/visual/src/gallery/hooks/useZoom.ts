'use client'

import { useCallback, useRef, useState, useEffect } from 'react';

export interface ZoomState {
  scale: number
  x: number
  y: number
}

export interface UseZoomOptions {
  minScale?: number
  maxScale?: number
  desktopScale?: number
  onZoomChange?: (zoomed: boolean) => void
}

export interface UseZoomReturn {
  state: ZoomState
  isZoomed: boolean
  isDragging: boolean
  handlers: {
    onTouchStart: (e: React.TouchEvent) => void
    onTouchMove: (e: React.TouchEvent) => void
    onTouchEnd: (e: React.TouchEvent) => void
    onClick: (e: React.MouseEvent) => void
    onMouseDown: (e: React.MouseEvent) => void
    onMouseMove: (e: React.MouseEvent) => void
    onMouseUp: () => void
    onMouseLeave: () => void
  }
  reset: () => void
  zoomTo: (scale: number, x?: number, y?: number) => void
  toggleZoom: () => void
}

const INITIAL_STATE: ZoomState = { scale: 1, x: 0, y: 0 }
const ZOOM_THRESHOLD = 1.05

/**
 * Unified zoom hook for both desktop (click/drag) and mobile (pinch/tap)
 */
export function useZoom(options: UseZoomOptions = {}): UseZoomReturn {
  const { minScale = 1, maxScale = 3, desktopScale = 2, onZoomChange } = options

  const [state, setState] = useState<ZoomState>(INITIAL_STATE)
  const [isDragging, setIsDragging] = useState(false)

  const touchRef = useRef<{
    // Touch tracking
    initialDistance: number
    initialScale: number
    initialX: number
    initialY: number
    centerX: number
    centerY: number
    isPinching: boolean
    lastTap: number
    // Container dimensions
    containerWidth: number
    containerHeight: number
    // Mouse drag tracking
    dragStartX: number
    dragStartY: number
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
    dragStartX: 0,
    dragStartY: 0,
  })

  const isZoomed = state.scale > ZOOM_THRESHOLD

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
    return {
      x: (containerWidth * (scale - 1)) / 2,
      y: (containerHeight * (scale - 1)) / 2,
    }
  }, [])

  // Clamp pan position within bounds
  const clampPan = useCallback((x: number, y: number, scale: number) => {
    const maxPan = getMaxPan(scale)
    return {
      x: Math.max(-maxPan.x, Math.min(maxPan.x, x)),
      y: Math.max(-maxPan.y, Math.min(maxPan.y, y)),
    }
  }, [getMaxPan])

  // ========== TOUCH HANDLERS (MOBILE) ==========

  const handleTouchStart = useCallback((e: React.TouchEvent) => {
    const touches = e.touches
    const rect = e.currentTarget.getBoundingClientRect()
    touchRef.current.containerWidth = rect.width
    touchRef.current.containerHeight = rect.height

    // Double tap to zoom
    const touch0 = touches[0]
    if (touches.length === 1 && touch0) {
      const now = Date.now()
      const timeSinceLastTap = now - touchRef.current.lastTap

      if (timeSinceLastTap < 300) {
        e.preventDefault()
        if (isZoomed) {
          setState(INITIAL_STATE)
          onZoomChange?.(false)
        } else {
          const x = touch0.clientX - rect.left - rect.width / 2
          const y = touch0.clientY - rect.top - rect.height / 2
          setState({ scale: desktopScale, x: -x * 0.5, y: -y * 0.5 })
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
  }, [isZoomed, state, getDistance, getCenter, desktopScale, onZoomChange])

  const handleTouchMove = useCallback((e: React.TouchEvent) => {
    const touches = e.touches

    // Pinch zoom
    if (touches.length === 2 && touchRef.current.isPinching) {
      e.preventDefault()

      const currentDistance = getDistance(touches)
      const scaleDelta = currentDistance / touchRef.current.initialDistance
      let newScale = touchRef.current.initialScale * scaleDelta
      newScale = Math.max(minScale, Math.min(maxScale, newScale))

      const center = getCenter(touches)
      const dx = center.x - touchRef.current.centerX
      const dy = center.y - touchRef.current.centerY

      const { x: clampedX, y: clampedY } = clampPan(
        touchRef.current.initialX + dx,
        touchRef.current.initialY + dy,
        newScale
      )

      setState({ scale: newScale, x: clampedX, y: clampedY })

      if (newScale > ZOOM_THRESHOLD !== isZoomed) {
        onZoomChange?.(newScale > ZOOM_THRESHOLD)
      }
    }

    // Pan when zoomed (single finger)
    const panTouch = touches[0]
    if (touches.length === 1 && panTouch && isZoomed && !touchRef.current.isPinching) {
      e.preventDefault()

      const newX = panTouch.clientX - touchRef.current.initialX
      const newY = panTouch.clientY - touchRef.current.initialY
      const { x: clampedX, y: clampedY } = clampPan(newX, newY, state.scale)

      setState((prev) => ({ ...prev, x: clampedX, y: clampedY }))
    }
  }, [isZoomed, state.scale, minScale, maxScale, getDistance, getCenter, clampPan, onZoomChange])

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

  // ========== MOUSE HANDLERS (DESKTOP) ==========

  const handleClick = useCallback((e: React.MouseEvent) => {
    // Skip if we were dragging
    if (isDragging) return

    const rect = e.currentTarget.getBoundingClientRect()
    touchRef.current.containerWidth = rect.width
    touchRef.current.containerHeight = rect.height

    if (isZoomed) {
      setState(INITIAL_STATE)
      onZoomChange?.(false)
    } else {
      // Zoom to click position
      const x = ((e.clientX - rect.left) / rect.width - 0.5) * -100
      const y = ((e.clientY - rect.top) / rect.height - 0.5) * -100
      setState({ scale: desktopScale, x, y })
      onZoomChange?.(true)
    }
  }, [isZoomed, isDragging, desktopScale, onZoomChange])

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (!isZoomed) return
    e.preventDefault()
    setIsDragging(true)
    touchRef.current.dragStartX = e.clientX - state.x
    touchRef.current.dragStartY = e.clientY - state.y

    const rect = e.currentTarget.getBoundingClientRect()
    touchRef.current.containerWidth = rect.width
    touchRef.current.containerHeight = rect.height
  }, [isZoomed, state.x, state.y])

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isDragging) return

    const newX = e.clientX - touchRef.current.dragStartX
    const newY = e.clientY - touchRef.current.dragStartY
    const { x: clampedX, y: clampedY } = clampPan(newX, newY, state.scale)

    setState((prev) => ({ ...prev, x: clampedX, y: clampedY }))
  }, [isDragging, state.scale, clampPan])

  // Tracked so unmounting mid-drag does not leave the timer scheduled.
  const dragEndTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null)

  useEffect(
    () => () => {
      if (dragEndTimerRef.current) clearTimeout(dragEndTimerRef.current)
    },
    []
  )

  const handleMouseUp = useCallback(() => {
    // Small delay to prevent click from triggering after drag
    if (dragEndTimerRef.current) clearTimeout(dragEndTimerRef.current)
    dragEndTimerRef.current = setTimeout(() => {
      dragEndTimerRef.current = null
      setIsDragging(false)
    }, 10)
  }, [])

  // ========== COMMON ACTIONS ==========

  const reset = useCallback(() => {
    setState(INITIAL_STATE)
    setIsDragging(false)
    onZoomChange?.(false)
  }, [onZoomChange])

  const zoomTo = useCallback((scale: number, x = 0, y = 0) => {
    const clampedScale = Math.max(minScale, Math.min(maxScale, scale))
    const { x: clampedX, y: clampedY } = clampPan(x, y, clampedScale)
    setState({ scale: clampedScale, x: clampedX, y: clampedY })
    onZoomChange?.(clampedScale > ZOOM_THRESHOLD)
  }, [minScale, maxScale, clampPan, onZoomChange])

  const toggleZoom = useCallback(() => {
    if (isZoomed) {
      setState(INITIAL_STATE)
      onZoomChange?.(false)
    } else {
      setState({ scale: desktopScale, x: 0, y: 0 })
      onZoomChange?.(true)
    }
  }, [isZoomed, desktopScale, onZoomChange])

  return {
    state,
    isZoomed,
    isDragging,
    handlers: {
      onTouchStart: handleTouchStart,
      onTouchMove: handleTouchMove,
      onTouchEnd: handleTouchEnd,
      onClick: handleClick,
      onMouseDown: handleMouseDown,
      onMouseMove: handleMouseMove,
      onMouseUp: handleMouseUp,
      onMouseLeave: handleMouseUp,
    },
    reset,
    zoomTo,
    toggleZoom,
  }
}
