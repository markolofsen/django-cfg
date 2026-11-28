"use client"

import { Check, ChevronRight, Circle } from 'lucide-react';
import * as React from 'react';

import { cn } from '../../../lib';
import * as DropdownMenuPrimitive from '@radix-ui/react-dropdown-menu';
import { Link } from '../link';

const DropdownMenu = DropdownMenuPrimitive.Root

const DropdownMenuTrigger = DropdownMenuPrimitive.Trigger

/**
 * Classes for a trigger that stays hidden until the row is hovered or focused
 * — the `…` on a list row, a tab, a tree item.
 *
 * The last clause is the one that is easy to miss and impossible to see in a
 * screenshot of a closed menu: while the menu is OPEN, Radix has moved focus
 * into the portalled panel and the pointer has left the row, so both reveal
 * conditions are false and the trigger fades out under the menu it just
 * opened. `data-state` is set by Radix on any trigger, so this composes with
 * the primitive and with `MenuBuilder` alike.
 *
 * The row must be a `group`. Compose with `cn()` and the row's own sizing.
 */
const revealOnRowInteraction =
  "opacity-0 transition-opacity group-hover:opacity-100 " +
  "group-focus-within:opacity-100 focus-visible:opacity-100 " +
  "data-[state=open]:opacity-100 motion-reduce:transition-none"

const DropdownMenuGroup = DropdownMenuPrimitive.Group

const DropdownMenuPortal = DropdownMenuPrimitive.Portal

const DropdownMenuSub = DropdownMenuPrimitive.Sub

const DropdownMenuRadioGroup = DropdownMenuPrimitive.RadioGroup

const DropdownMenuSubTrigger = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.SubTrigger>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.SubTrigger> & {
    inset?: boolean
  }
>(({ className, inset, children, ...props }, ref) => (
  <DropdownMenuPrimitive.SubTrigger
    ref={ref}
    className={cn(
      "flex cursor-default select-none items-center gap-2 rounded-[var(--radius-sm)] px-(--menu-item-px) py-(--menu-item-py) text-(length:--menu-font-size) outline-none focus:bg-accent data-[state=open]:bg-accent [&_svg]:pointer-events-none [&_svg]:size-4 [&_svg]:shrink-0",
      inset && "pl-8",
      className
    )}
    {...props}
  >
    {children}
    <ChevronRight className="ml-auto" />
  </DropdownMenuPrimitive.SubTrigger>
))
DropdownMenuSubTrigger.displayName =
  DropdownMenuPrimitive.SubTrigger.displayName

const DropdownMenuSubContent = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.SubContent>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.SubContent>
>(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.SubContent
    ref={ref}
    className={cn(
      // Height/scroll mirrors DropdownMenuContent below: a long submenu (e.g. a
      // 40-vendor model list) must cap and scroll INSIDE, not overflow off-screen
      // and clip. `min()` of the space Radix measured to the viewport edge and a
      // comfortable ceiling — a menu that spans the WHOLE screen reads as a page,
      // not a menu, so we stop well short of the viewport even when it would fit.
      "z-[1400] max-h-[min(var(--radix-dropdown-menu-content-available-height),24rem)] min-w-32 overflow-y-auto overflow-x-hidden rounded-[var(--radius-popover)] border bg-popover backdrop-blur-xl p-(--menu-padding) text-popover-foreground shadow-(--popup-shadow) data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
      className
    )}
    {...props}
  />
))
DropdownMenuSubContent.displayName =
  DropdownMenuPrimitive.SubContent.displayName

const DropdownMenuContent = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Content>
>(({ className, sideOffset = 4, collisionPadding = 8, ...props }, ref) => (
  <DropdownMenuPrimitive.Portal>
    <DropdownMenuPrimitive.Content
      ref={ref}
      sideOffset={sideOffset}
      // Keep a gap from the viewport edge instead of sitting flush against it —
      // most visible on phones, where a trigger near the edge would otherwise
      // pin the menu to the very border of the screen.
      collisionPadding={collisionPadding}
      className={cn(
        // See DropdownMenuSubContent: cap at the SMALLER of the space to the
        // viewport edge and a comfortable ceiling, then scroll inside.
        //
        // z-[1400] is the shared popover layer across ui-core (dropdown, select,
        // popover, tooltip, hover-card, context-menu, menubar) — keep them equal.
        // Radix portals this content to <body>, so an open menu is a SIBLING of
        // whatever it was opened from, and z-index is the ONLY arbiter. It must
        // sit ABOVE everything a popover can be opened from: app shells (public
        // drawer z-1000, its navbar z-1001) AND dialogs/alert-dialogs (z-1300) —
        // a Select/language dropdown INSIDE a settings dialog would otherwise
        // render behind it (reported: language list clipped under the dialog).
        // So the layer order is: sheet(200) < shell(1000/1001) < dialog(1300) <
        // popover(1400). A popover always belongs on top of its opener.
        "z-[1400] max-h-[min(var(--radix-dropdown-menu-content-available-height),24rem)] min-w-32 overflow-y-auto overflow-x-hidden rounded-[var(--radius-popover)] border bg-popover backdrop-blur-xl p-(--menu-padding) text-popover-foreground shadow-(--popup-shadow)",
        "data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
        className
      )}
      {...props}
    />
  </DropdownMenuPrimitive.Portal>
))
DropdownMenuContent.displayName = DropdownMenuPrimitive.Content.displayName

const DropdownMenuItem = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Item>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Item> & {
    inset?: boolean
    href?: string
    /** Visual style. `destructive` paints the row red on focus. */
    variant?: "default" | "destructive"
    key?: React.Key
  }
>(({ className, inset, href, variant = "default", children, ...props }, ref) => {
  const classes = cn(
    "relative flex cursor-default select-none items-center gap-2 rounded-[var(--radius-sm)] px-(--menu-item-px) py-(--menu-item-py) text-(length:--menu-font-size) outline-none transition-colors focus:bg-foreground/[0.07] data-[disabled]:pointer-events-none data-[disabled]:opacity-50 [&>svg]:size-4 [&>svg]:shrink-0",
    "data-[variant=destructive]:text-destructive data-[variant=destructive]:focus:bg-destructive/10 data-[variant=destructive]:focus:text-destructive",
    inset && "pl-8",
    className
  )

  if (href) {
    return (
      <DropdownMenuPrimitive.Item asChild ref={ref} data-variant={variant} {...props}>
        <Link href={href} className={classes}>
          {children}
        </Link>
      </DropdownMenuPrimitive.Item>
    )
  }

  return (
    <DropdownMenuPrimitive.Item
      ref={ref}
      data-variant={variant}
      className={classes}
      {...props}
    >
      {children}
    </DropdownMenuPrimitive.Item>
  )
})
DropdownMenuItem.displayName = DropdownMenuPrimitive.Item.displayName

const DropdownMenuCheckboxItem = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.CheckboxItem>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.CheckboxItem> & { key?: React.Key }
>(({ className, children, checked, ...props }, ref) => (
  <DropdownMenuPrimitive.CheckboxItem
    ref={ref}
    className={cn(
      "relative flex cursor-default select-none items-center rounded-[var(--radius-sm)] py-(--menu-item-py) pl-8 pr-2 text-(length:--menu-font-size) outline-none transition-colors focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
      className
    )}
    checked={checked}
    {...props}
  >
    <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
      <DropdownMenuPrimitive.ItemIndicator>
        <Check className="h-4 w-4" />
      </DropdownMenuPrimitive.ItemIndicator>
    </span>
    {children}
  </DropdownMenuPrimitive.CheckboxItem>
))
DropdownMenuCheckboxItem.displayName =
  DropdownMenuPrimitive.CheckboxItem.displayName

const DropdownMenuRadioItem = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.RadioItem>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.RadioItem> & { key?: React.Key }
>(({ className, children, ...props }, ref) => (
  <DropdownMenuPrimitive.RadioItem
    ref={ref}
    className={cn(
      "relative flex cursor-default select-none items-center rounded-[var(--radius-sm)] py-(--menu-item-py) pl-8 pr-2 text-(length:--menu-font-size) outline-none transition-colors focus:bg-accent focus:text-accent-foreground data-[disabled]:pointer-events-none data-[disabled]:opacity-50",
      className
    )}
    {...props}
  >
    <span className="absolute left-2 flex h-3.5 w-3.5 items-center justify-center">
      <DropdownMenuPrimitive.ItemIndicator>
        <Circle className="h-2 w-2 fill-current" />
      </DropdownMenuPrimitive.ItemIndicator>
    </span>
    {children}
  </DropdownMenuPrimitive.RadioItem>
))
DropdownMenuRadioItem.displayName = DropdownMenuPrimitive.RadioItem.displayName

const DropdownMenuLabel = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Label>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Label> & {
    inset?: boolean
  }
>(({ className, inset, ...props }, ref) => (
  <DropdownMenuPrimitive.Label
    ref={ref}
    className={cn(
      "px-(--menu-item-px) py-(--menu-item-py) text-(length:--menu-label-font-size) font-(weight:--menu-label-weight) text-(color:--menu-label-color)",
      inset && "pl-8",
      className
    )}
    {...props}
  />
))
DropdownMenuLabel.displayName = DropdownMenuPrimitive.Label.displayName

const DropdownMenuSeparator = React.forwardRef<
  React.ElementRef<typeof DropdownMenuPrimitive.Separator>,
  React.ComponentPropsWithoutRef<typeof DropdownMenuPrimitive.Separator>
>(({ className, ...props }, ref) => (
  <DropdownMenuPrimitive.Separator
    ref={ref}
    // Soft hairline via the --divider token (was bg-muted, which is darker than
    // the popover surface and read as a hard dark groove).
    className={cn("mx-1.5 my-1 h-px bg-divider", className)}
    {...props}
  />
))
DropdownMenuSeparator.displayName = DropdownMenuPrimitive.Separator.displayName

const DropdownMenuShortcut = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLSpanElement>) => {
  return (
    <span
      className={cn("ml-auto text-xs tracking-widest opacity-60", className)}
      {...props}
    />
  )
}
DropdownMenuShortcut.displayName = "DropdownMenuShortcut"

export {
  DropdownMenu,
  DropdownMenuTrigger,
  revealOnRowInteraction,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuCheckboxItem,
  DropdownMenuRadioItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuShortcut,
  DropdownMenuGroup,
  DropdownMenuPortal,
  DropdownMenuSub,
  DropdownMenuSubContent,
  DropdownMenuSubTrigger,
  DropdownMenuRadioGroup,
}
