"use client"

import * as React from 'react';

import * as PopoverPrimitive from '@radix-ui/react-popover';

import { cn } from '../../../lib/utils';

const Popover = PopoverPrimitive.Root

const PopoverTrigger = PopoverPrimitive.Trigger

const PopoverAnchor = PopoverPrimitive.Anchor

const PopoverContent = React.forwardRef<
  React.ElementRef<typeof PopoverPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Content>
>(({ className, align = "center", sideOffset = 4, collisionPadding = 8, forceMount, onWheel, onTouchMove, ...props }, ref) => (
  // `forceMount` must reach BOTH halves, and that is the whole reason it is
  // destructured rather than swept up by `...props` (live 2026-08-15).
  //
  // Radix declares it on `Portal` AND on `Content`, and the Portal is the outer
  // one: with it only on Content, the Portal still unmounts on close and takes
  // the subtree — including any <audio>/<video> element — with it. A cmdop
  // status-bar player mounted in a popover therefore went SILENT the moment the
  // panel closed, and no amount of `forceMount` on the content could stop it,
  // because that content no longer had a portal to live in.
  //
  // Passing it to both keeps the DOM alive while closed; Radix then leaves the
  // `data-state="closed"` attribute for the caller to style (the built-in
  // fade/zoom classes below already key off it), so nothing changes visually for
  // the callers that do not opt in.
  <PopoverPrimitive.Portal forceMount={forceMount}>
    <PopoverPrimitive.Content
      forceMount={forceMount}
      ref={ref}
      // `data-slot` lets descendants detect they're inside a popover surface.
      // The Calendar keys its `bg-transparent` override off
      // `[[data-slot=popover-content]_&]` so a calendar rendered in a popover
      // drops its own `bg-background` panel and inherits the popover surface —
      // without this attribute that rule never matches and the calendar shows a
      // mismatched darker rectangle inside the popover.
      data-slot="popover-content"
      aria-describedby={undefined}
      // A popover is portaled to <body>, outside an open Dialog's content, so the
      // Dialog's scroll lock (react-remove-scroll) swallows wheel/touch scrolling
      // inside it — a long list inside a settings dialog would not scroll at all.
      // Stopping propagation here keeps those events from reaching the lock.
      onWheel={(e) => { onWheel?.(e); e.stopPropagation(); }}
      onTouchMove={(e) => { onTouchMove?.(e); e.stopPropagation(); }}
      align={align}
      sideOffset={sideOffset}
      // Radix defaults this to 0, which lets a popover that does not fit below
      // its trigger flip above it and sit flush against the top edge of the
      // window, first rows clipped by the viewport. The padding also feeds
      // `--radix-popover-content-available-height`, which `.popover-panel`
      // (in the class list below) caps the whole panel to.
      collisionPadding={collisionPadding}
      className={cn(
        "popover-panel z-[1400] w-72 rounded-[var(--radius-popover)] border bg-popover backdrop-blur-xl p-4 text-popover-foreground shadow-(--popup-shadow) outline-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
        className
      )}
      {...props}
    />
  </PopoverPrimitive.Portal>
))
PopoverContent.displayName = PopoverPrimitive.Content.displayName

const PopoverArrow = React.forwardRef<
  React.ElementRef<typeof PopoverPrimitive.Arrow>,
  React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Arrow>
>(({ className, ...props }, ref) => (
  <PopoverPrimitive.Arrow
    ref={ref}
    className={cn('fill-popover', className)}
    {...props}
  />
))
PopoverArrow.displayName = PopoverPrimitive.Arrow.displayName

export { Popover, PopoverTrigger, PopoverContent, PopoverAnchor, PopoverArrow }
