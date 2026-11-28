'use client'

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

export interface VirtualListOptions {
  /** Total number of items */
  itemCount: number
  /** Width of each item in pixels */
  itemWidth: number
  /** Gap between items in pixels */
  gap?: number
  /** Number of items to render outside visible area */
  overscan?: number
}

export interface VirtualListReturn {
  /** Container ref to attach to scrollable element */
  containerRef: React.RefObject<HTMLDivElement | null>
  /** Total width of all items (for spacer) */
  totalWidth: number
  /** Visible items with their positions */
  virtualItems: VirtualItem[]
  /** Scroll to specific index */
  scrollToIndex: (index: number, behavior?: ScrollBehavior) => void
}

export interface VirtualItem {
  index: number
  start: number
  size: number
}

/**
 * Hook for virtualizing horizontal list items
 * Only renders items that are visible + overscan buffer
 */
export function useVirtualList({
  itemCount,
  itemWidth,
  gap = 8,
  overscan = 3,
}: VirtualListOptions): VirtualListReturn {
  const containerRef = useRef<HTMLDivElement>(null)
  const [scrollLeft, setScrollLeft] = useState(0)
  const [containerWidth, setContainerWidth] = useState(0)

  // Calculate total width
  const totalWidth = useMemo(() => {
    if (itemCount === 0) return 0
    return itemCount * itemWidth + (itemCount - 1) * gap
  }, [itemCount, itemWidth, gap])

  // Handle scroll
  useEffect(() => {
    const container = containerRef.current
    if (!container) return

    const handleScroll = () => {
      setScrollLeft(container.scrollLeft)
    }

    const handleResize = () => {
      setContainerWidth(container.clientWidth)
    }

    // Initial measurements
    handleResize()
    handleScroll()

    container.addEventListener('scroll', handleScroll, { passive: true })

    const resizeObserver = new ResizeObserver(handleResize)
    resizeObserver.observe(container)

    return () => {
      container.removeEventListener('scroll', handleScroll)
      resizeObserver.disconnect()
    }
  }, [])

  // Calculate visible items
  const virtualItems = useMemo((): VirtualItem[] => {
    if (itemCount === 0 || containerWidth === 0) return []

    const itemWithGap = itemWidth + gap

    // Find start and end indices
    const startIndex = Math.max(0, Math.floor(scrollLeft / itemWithGap) - overscan)
    const endIndex = Math.min(
      itemCount - 1,
      Math.ceil((scrollLeft + containerWidth) / itemWithGap) + overscan
    )

    const items: VirtualItem[] = []
    for (let i = startIndex; i <= endIndex; i++) {
      items.push({
        index: i,
        start: i * itemWithGap,
        size: itemWidth,
      })
    }

    return items
  }, [itemCount, itemWidth, gap, scrollLeft, containerWidth, overscan])

  // Scroll to index
  const scrollToIndex = useCallback(
    (index: number, behavior: ScrollBehavior = 'smooth') => {
      const container = containerRef.current
      if (!container) return

      const itemWithGap = itemWidth + gap
      const targetScroll = index * itemWithGap - containerWidth / 2 + itemWidth / 2

      container.scrollTo({
        left: Math.max(0, targetScroll),
        behavior,
      })
    },
    [itemWidth, gap, containerWidth]
  )

  return {
    containerRef,
    totalWidth,
    virtualItems,
    scrollToIndex,
  }
}
