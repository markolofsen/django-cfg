"use client"

import * as React from 'react'

import { cn } from '../../../lib/utils'

export interface FilterButtonProps
  extends Omit<React.ButtonHTMLAttributes<HTMLButtonElement>, 'type' | 'value'> {
  /** Leading icon. Rendered decoratively — the name comes from the label. */
  icon?: React.ComponentType<{ className?: string }>
  /** Trailing icon, typically a chevron for a control that opens a menu. */
  trailingIcon?: React.ComponentType<{ className?: string }>
  /**
   * The chosen option, shown in place of the label.
   *
   * A pill showing an answer keeps it visible when the row is tight, while the
   * ones still asking a question collapse to their icon: "SUV" is worth the
   * space, "Body type" is what the icon already says.
   */
  value?: React.ReactNode
  /** Marks a filter that is applied. Tints the control. */
  active?: boolean
  /**
   * A number worth showing on the control — active filters, or available
   * options. Zero and `undefined` both render nothing, so a caller can pass a
   * count straight through without guarding it.
   */
  count?: number
  /** Filled rather than outlined. For the one control that opens the panel. */
  variant?: 'outline' | 'solid'
}

/**
 * A filter control in a toolbar: a pill with an icon, a label, and optionally a
 * count.
 *
 * Its one piece of behaviour is that the label collapses when the row runs out
 * of room — see `filter-bar.css`, which owns the query. The button keeps its
 * accessible name through that collapse via `aria-label`, which is the part
 * both product frontends lost: they hid the text with `clip-path: inset(50%)`,
 * which removes it from sight while leaving it in the accessibility tree, so
 * the icon-only state reads correctly to a screen reader by accident and only
 * for as long as the text stays in the DOM.
 *
 * Must be rendered inside a `FilterBar`: the height and the container query
 * both come from the row.
 */
export const FilterButton = React.forwardRef<HTMLButtonElement, FilterButtonProps>(
  (
    {
      className,
      icon: Icon,
      trailingIcon: TrailingIcon,
      children,
      value,
      active = false,
      count,
      variant = 'outline',
      'aria-label': ariaLabel,
      ...props
    },
    ref
  ) => {
    const answered = value != null && value !== ''
    const label = answered ? value : children
    const showCount = typeof count === 'number' && count > 0

    // The name has to survive the label collapsing to nothing, and it has to
    // read as the question plus its answer ("Body type: SUV") rather than the
    // answer alone, which says nothing about what was chosen. The count joins
    // it because the badge itself is decorative — a bare "3" announced after a
    // label is a number without a noun.
    const base =
      answered && typeof children === 'string' && typeof value === 'string'
        ? `${children}: ${value}`
        : typeof children === 'string'
          ? children
          : undefined
    const name = ariaLabel ?? (base && showCount ? `${base} (${count})` : base)

    return (
      <button
        ref={ref}
        type="button"
        data-slot="filter-pill"
        data-active={active || undefined}
        data-answered={answered || undefined}
        aria-label={name}
        className={cn(
          'filter-pill inline-flex shrink-0 items-center gap-2 rounded-full',
          'h-[var(--filter-control-h,2.375rem)] px-3.5',
          'text-sm font-medium whitespace-nowrap',
          'transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring',
          'disabled:pointer-events-none disabled:opacity-50',
          '[&_svg]:size-4 [&_svg]:shrink-0',
          variant === 'solid'
            ? 'bg-primary text-primary-foreground hover:bg-primary/90'
            : cn(
                'border bg-background hover:bg-accent hover:text-accent-foreground',
                // An applied filter reads as chosen without shouting: the edge
                // carries it, not a fill that would compete with the solid
                // control beside it.
                //
                // Both states keep `text-foreground`. `text-muted-foreground`
                // was the obvious choice for "not applied" and measured 4.21:1
                // on the light theme — under AA for a control label. An unset
                // filter is a normal control, not a de-emphasised one; what
                // marks the applied one is the border.
                'text-foreground',
                // Weight as well as colour: a border tint alone would make
                // "applied" a colour-only signal, which the accessibility rules
                // rule out. Usually the label also changes — an applied filter
                // shows its `value` — but `active` can be set without one.
                active
                  ? 'border-primary/60 font-semibold'
                  : 'border-border'
              ),
          className
        )}
        {...props}
      >
        {Icon && <Icon aria-hidden className="opacity-70" />}
        {label != null && <span className="filter-pill-label">{label}</span>}
        {showCount && (
          <span
            aria-hidden
            className={cn(
              'inline-flex min-w-5 items-center justify-center rounded-full px-1.5',
              'text-xs font-semibold tabular-nums',
              // On the filled control the badge has to invert, or it disappears
              // into its own background. Both frontends wrote this pair by hand.
              variant === 'solid'
                ? 'bg-primary-foreground text-primary'
                : 'bg-muted text-foreground'
            )}
          >
            {count}
          </span>
        )}
        {TrailingIcon && <TrailingIcon aria-hidden className="opacity-50" />}
      </button>
    )
  }
)
FilterButton.displayName = 'FilterButton'
