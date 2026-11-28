'use client'

import { Compass } from 'lucide-react'
import { cn } from '@djangocfg/ui-core/lib'
import { TooltipHint } from '@djangocfg/ui-core/components'

import { MAP_CONTROL_CLASS } from './MapContainer/constants'

export interface CompassChipProps {
  /** Current camera bearing in degrees; the needle counter-rotates by this. */
  bearing: number
  /**
   * Whether the view is rotated/tilted off true north. Drives the color cue:
   * an accent needle (Google's gray→red "you're off-north") when oriented,
   * the neutral chip foreground otherwise. The chip is typically only rendered
   * while oriented (the caller gates it), so the visible needle reads accent.
   */
  oriented: boolean
  /** Click handler — ease the camera back to a north-up, top-down view. */
  onReset: () => void
  /** Accessible / tooltip label. @default 'Reset bearing to north' */
  label?: string
  /** Extra classes merged onto the chip button. */
  className?: string
}

/**
 * Compass chip — a Google-Maps-style reset-to-north control.
 *
 * Presentational: the needle counter-rotates by `bearing` so it keeps
 * pointing at true north as the map turns underneath it, and it tints to an
 * ACCENT (`text-primary`) when `oriented` to signal "you're off true north"
 * (our semantic stand-in for Google's red needle). Click eases the camera
 * back to north-up + top-down via `onReset`. Keyboard-reachable; the chip
 * lives inside the toolbar's `data-map-control` region so it never re-locks
 * scroll. Mirrors the terrain/geolocate chip pattern (`MAP_CONTROL_CLASS`,
 * `Tooltip`, semantic tokens only).
 */
export function CompassChip({
  bearing,
  oriented,
  onReset,
  label = 'Reset bearing to north',
  className,
}: CompassChipProps) {
  return (
    <TooltipHint tooltip={{ content: label, side: 'left' }}>
      <button
        type="button"
        onClick={onReset}
        aria-label={label}
        className={cn(MAP_CONTROL_CLASS, 'w-9 h-9', oriented && 'text-primary', className)}
      >
        <Compass
          className="w-4 h-4"
          aria-hidden="true"
          // Counter-rotate the needle so it points to true north as the
          // map rotates underneath it.
          style={{ transform: `rotate(${-bearing}deg)` }}
        />
      </button>
    </TooltipHint>
  )
}
