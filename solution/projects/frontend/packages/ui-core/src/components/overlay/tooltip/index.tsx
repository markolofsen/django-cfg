"use client"

import * as React from 'react';

import * as TooltipPrimitive from '@radix-ui/react-tooltip';

import { formatHotkey } from '../../../hooks/hotkey/formatHotkey';
import { useCanHover } from '../../../hooks/media/useCanHover';
import { cn } from '../../../lib/utils';

const TooltipProvider = TooltipPrimitive.Provider

/** A tooltip names a control; it is not a surface to reach into, so it closes the moment the pointer leaves the trigger (no hoverable content, as in Notion). Pass `disableHoverableContent={false}` for one with a link inside. */
const Tooltip = ({ disableHoverableContent = true, ...props }: React.ComponentProps<typeof TooltipPrimitive.Root>) => (
  <TooltipPrimitive.Root disableHoverableContent={disableHoverableContent} {...props} />
)

const TooltipTrigger = TooltipPrimitive.Trigger

const TooltipContent = React.forwardRef<
  React.ElementRef<typeof TooltipPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof TooltipPrimitive.Content>
>(({ className, sideOffset = 4, ...props }, ref) => (
  <TooltipPrimitive.Portal>
    <TooltipPrimitive.Content
      ref={ref}
      aria-describedby={undefined}
      sideOffset={sideOffset}
      className={cn(
        // Surface from tokens: by default INVERSE (foreground bg + background text, high contrast on any panel);
        // a preset (Notion) points --tooltip-bg/-fg/-border at the popover surface instead.
        "pointer-events-none z-[1400] overflow-hidden rounded-[var(--radius-tooltip)] border border-[var(--tooltip-border,transparent)] bg-[var(--tooltip-bg,var(--foreground))] px-3 py-1.5 text-xs font-medium text-[var(--tooltip-fg,var(--background))] shadow-md animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
        className
      )}
      {...props}
    />
  </TooltipPrimitive.Portal>
))
TooltipContent.displayName = TooltipPrimitive.Content.displayName

/** What a control says about itself on hover: a text (or node), or this config. One shape for every control that takes a `tooltip` prop. */
export interface TooltipConfig {
  /** The name of the action. Pass `null` for a hotkey-only hint (an icon that already says what it does). */
  content: React.ReactNode
  /** A `useHotkey` string (`mod+j`), shown after the content in a muted tone, written for the viewer's system (⌘J on a Mac, Ctrl+J elsewhere). */
  hotkey?: string
  side?: 'top' | 'right' | 'bottom' | 'left'
  align?: 'start' | 'center' | 'end'
  sideOffset?: number
  /** Hover delay in ms. Default 400. */
  delay?: number
  /** Keep it open while the pointer is over it (a tooltip with a link). Default false. */
  hoverable?: boolean
}

export type TooltipProp = React.ReactNode | TooltipConfig

function isConfig(value: TooltipProp): value is TooltipConfig {
  return typeof value === 'object' && value !== null && !React.isValidElement(value) && 'content' in value
}

/**
 * Wraps one trigger element in the standard tooltip. This is what a `tooltip` prop on `Button` / `ButtonLink` calls; reach for it directly only around something that is not a button.
 * It does not mount a `TooltipProvider` (the host's `UiProviders` does, once). Nothing is drawn (and no wrapper is added) when `tooltip` is empty or the device cannot hover (`useCanHover`: a phone or tablet). A disabled button gets no pointer events, so its trigger is a `span`.
 */
function TooltipHint({ tooltip, children, disabled = false }: { tooltip: TooltipProp; children: React.ReactElement; disabled?: boolean }) {
  const canHover = useCanHover()
  if (tooltip === undefined || tooltip === null || tooltip === false || tooltip === '' || !canHover) return children
  const config: TooltipConfig = isConfig(tooltip) ? tooltip : { content: tooltip }
  const trigger = disabled ? <span className="inline-flex cursor-not-allowed">{children}</span> : children
  return (
    <TooltipPrimitive.Root delayDuration={config.delay ?? 400} disableHoverableContent={!config.hoverable}>
      <TooltipTrigger asChild>{trigger}</TooltipTrigger>
      <TooltipContent
        side={config.side}
        align={config.align}
        sideOffset={config.sideOffset}
        className={cn('flex items-center gap-3', config.hotkey ? 'whitespace-nowrap' : undefined, config.hoverable && 'pointer-events-auto')}
      >
        {config.content != null && config.content !== '' ? <span>{config.content}</span> : null}
        {config.hotkey ? <span className="opacity-60">{formatHotkey(config.hotkey)}</span> : null}
      </TooltipContent>
    </TooltipPrimitive.Root>
  )
}

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider, TooltipHint }
