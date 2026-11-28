import { cn } from '@djangocfg/ui-core/lib'

/**
 * Controls overlaid on the map. The map tiles are always a light basemap,
 * but per ui-core's style guide we use semantic tokens (never raw color
 * scales). `popover` is the floating-chrome surface — the same token
 * tooltips/menus use — so these chips read like maplibre's own controls
 * and stay legible over the map in both light and dark themes.
 */
export const MAP_CONTROL_CLASS = cn(
  'inline-flex items-center justify-center rounded-lg',
  'bg-popover/95 text-popover-foreground backdrop-blur-sm shadow-sm border border-border',
  'hover:bg-popover transition-colors',
  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring'
)
