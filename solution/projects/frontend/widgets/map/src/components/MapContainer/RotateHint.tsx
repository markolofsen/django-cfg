'use client'

import { cn } from '@djangocfg/ui-core/lib'

/**
 * Gesture hint — appears briefly when 3D turns on, since rotate/tilt
 * (right-drag / Ctrl+drag / two fingers) isn't otherwise discoverable. The
 * compass chip then offers a one-click reset back to north.
 */
export function RotateHint({ show }: { show: boolean }) {
  return (
    <div
      aria-hidden={!show}
      className={cn(
        'pointer-events-none absolute bottom-3 left-1/2 z-20 -translate-x-1/2',
        'rounded-full px-3 py-1.5 text-xs font-medium',
        'bg-popover/95 text-popover-foreground border border-border shadow-sm',
        'transition-opacity duration-300',
        show ? 'opacity-100' : 'opacity-0',
      )}
    >
      Right-click or Ctrl+drag to rotate &amp; tilt
    </div>
  )
}
