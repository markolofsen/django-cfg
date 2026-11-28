'use client'

import { memo } from 'react'
import { Button, ButtonLink } from '@djangocfg/ui-core/components'
import { cn } from '@djangocfg/ui-core/lib'
import type { MarkerCard as MarkerCardData, MarkerCardAction } from '../cards/types'

export interface MarkerCardProps extends MarkerCardData {
  /** Extra classes on the card root. */
  className?: string
}

const VARIANT_MAP = {
  default: 'default',
  outline: 'outline',
  ghost: 'ghost',
} as const

function CardAction({ action }: { action: MarkerCardAction }) {
  const variant = VARIANT_MAP[action.variant ?? 'outline']

  if (action.href) {
    return (
      <ButtonLink
        href={action.href}
        size="sm"
        variant={variant}
        elevated={false}
        target="_blank"
        rel="noopener noreferrer"
      >
        {action.icon}
        {action.label}
      </ButtonLink>
    )
  }

  return (
    <Button size="sm" variant={variant} elevated={false} onClick={action.onClick}>
      {action.icon}
      {action.label}
    </Button>
  )
}

/**
 * MarkerCard — the DEFAULT presentational info-card for a map marker
 * (Google-Maps-desktop style). Renders from plain data: an optional image
 * header, a badge pill, a title, a clamped description, and an action row of
 * links/buttons. Standalone-usable (no map dependency) and built on semantic
 * tokens only. `MapMarkers` renders this inside a `MapPopup` above the pin.
 */
export const MarkerCard = memo(function MarkerCard({
  title,
  description,
  image,
  badge,
  actions,
  className,
}: MarkerCardProps) {
  return (
    <div
      className={cn(
        'flex max-w-[260px] flex-col overflow-hidden rounded-lg border border-border bg-card text-card-foreground shadow-md',
        className
      )}
    >
      {image && (
        <img
          src={image}
          alt={title}
          className="h-28 w-full object-cover"
          loading="lazy"
        />
      )}

      <div className="flex flex-col gap-1.5 p-3">
        {badge && (
          <span className="inline-flex w-fit items-center rounded-full bg-muted px-2 py-0.5 text-[11px] font-medium text-muted-foreground">
            {badge}
          </span>
        )}

        <h3 className="text-sm font-medium leading-snug text-foreground">{title}</h3>

        {description && (
          <p className="line-clamp-3 text-xs leading-relaxed text-muted-foreground">
            {description}
          </p>
        )}

        {actions && actions.length > 0 && (
          <div className="mt-1.5 flex flex-wrap gap-1.5">
            {actions.map((action, i) => (
              <CardAction key={`${action.label}-${i}`} action={action} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
})
