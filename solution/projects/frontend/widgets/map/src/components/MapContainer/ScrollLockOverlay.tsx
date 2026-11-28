'use client'

import { useState } from 'react'
import { cn } from '@djangocfg/ui-core/lib'

/**
 * Gesture overlay. Desktop: tap unlocks scroll-zoom in place. Mobile: the map
 * is fully static, tap expands to fullscreen. `touch-action: pan-y` lets a
 * vertical swipe scroll the PAGE straight through the overlay so the static
 * map never traps the scroll.
 */
export function ScrollLockOverlay({
  isMobileLock,
  resolvedHint,
  onActivate,
}: {
  isMobileLock: boolean
  resolvedHint: string
  onActivate: () => void
}) {
  const [overlayHovered, setOverlayHovered] = useState(false)

  return (
    <button
      type="button"
      onClick={onActivate}
      onMouseEnter={() => setOverlayHovered(true)}
      onMouseLeave={() => setOverlayHovered(false)}
      aria-label={`${resolvedHint} (map interaction is locked)`}
      style={{ touchAction: 'pan-y' }}
      className={cn(
        'absolute inset-0 z-10 flex items-center justify-center',
        'cursor-pointer border-0 bg-transparent p-0 transition-colors',
        'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-ring',
        overlayHovered && 'bg-foreground/5'
      )}
    >
      <span
        className={cn(
          // Same popover surface as the control chips — floating hint.
          // Mobile has no hover, so the "Tap to expand" hint is shown
          // persistently; desktop reveals it on hover.
          'pointer-events-none select-none rounded-full px-3 py-1.5 text-xs font-medium',
          'bg-popover/95 text-popover-foreground border border-border shadow-sm transition-opacity',
          isMobileLock || overlayHovered ? 'opacity-100' : 'opacity-0'
        )}
      >
        {resolvedHint}
      </span>
    </button>
  )
}
