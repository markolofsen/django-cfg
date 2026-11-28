"use client"

import * as React from 'react'

import { cn } from '../../../lib/utils'

export interface FilterBarProps extends React.HTMLAttributes<HTMLDivElement> {
  /**
   * What a row that does not fit does.
   *
   * `wrap` (default) drops controls onto a second line — right for a filter row
   * above a result list, where every control should stay reachable.
   * `scroll` keeps one line and scrolls it — right under a header, where a
   * second line would push the content down.
   */
  overflow?: 'wrap' | 'scroll'
  /**
   * Row height, any CSS length. Every control inside reads it, so a toolbar
   * lines up without anyone restyling a neighbour's component.
   * @default '2.375rem'
   */
  height?: string
}

/**
 * The row a set of filter controls sits in.
 *
 * It owns two things the controls cannot own individually: the shared height,
 * and the container the pills measure themselves against so their labels
 * collapse when THIS ROW is tight rather than when the window is.
 *
 * Both product frontends were missing exactly this piece, and paid for it by
 * restyling whatever component happened to be next in the row — `SelectTrigger`
 * in one, `Button size="sm"` in the other — to make the heights agree.
 */
export const FilterBar = React.forwardRef<HTMLDivElement, FilterBarProps>(
  ({ className, overflow = 'wrap', height, style, ...props }, ref) => (
    <div
      ref={ref}
      data-slot="filter-bar"
      data-overflow={overflow}
      className={cn('filter-bar', className)}
      style={height ? ({ '--filter-control-h': height, ...style } as React.CSSProperties) : style}
      {...props}
    />
  )
)
FilterBar.displayName = 'FilterBar'
