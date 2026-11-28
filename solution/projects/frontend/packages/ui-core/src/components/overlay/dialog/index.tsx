"use client"

import * as React from 'react';

import * as DialogPrimitive from '@radix-ui/react-dialog';
import { Cross2Icon } from '@radix-ui/react-icons';

import { cn } from '../../../lib/utils';

const Dialog = DialogPrimitive.Root

const DialogTrigger = DialogPrimitive.Trigger

const DialogPortal = DialogPrimitive.Portal

const DialogClose = DialogPrimitive.Close

const DialogOverlay = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Overlay>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Overlay>
>(({ className, style, ...props }, ref) => (
  <DialogPrimitive.Overlay
    ref={ref}
    className={cn(
      // A modal must cover the app shell (public drawer z-1000, its navbar
      // z-1001) — a dialog opened FROM those is meaningless underneath them.
      // But it sits BELOW the popover layer (z-1400): a Select / dropdown /
      // popover opened from INSIDE the dialog is portaled to <body> as a
      // sibling and must render on top of the dialog it belongs to (otherwise
      // e.g. a language list clips behind the settings dialog). Keep dialog and
      // alert-dialog on the same value.
      "fixed inset-0 z-1300 bg-overlay data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
      className
    )}
    style={style}
    {...props}
  />
))
DialogOverlay.displayName = DialogPrimitive.Overlay.displayName

/**
 * Width is a CSS variable, not a prop: set `--width-dialog` on the element.
 *
 *     <DialogContent className="[--width-dialog:940px]">
 *
 * The card renders at `min(--width-dialog, 100vw - 2rem)`, so raising the token
 * widens it and the viewport margin is kept for you. A Tailwind `max-w-*`
 * instead does nothing — the width is declared, and a maximum above a declared
 * width is inert. Ignored when `fullscreen`.
 *
 * Proportional cards: set `--aspect-dialog` (width / height) and the card keeps
 * that ratio at every size — the width shrinks to `(100dvh - 2rem) * ratio` when
 * the window is short, so the height never overflows. Pure CSS, no measuring:
 *
 *     <DialogContent className="[--width-dialog:1024px] [--aspect-dialog:1.28]">
 */
interface DialogContentProps
  extends React.ComponentPropsWithoutRef<typeof DialogPrimitive.Content> {
  /**
   * Stretch the content to fill the viewport (`100dvw × 100dvh`) and drop
   * the centred-card chrome (no `max-w`, no `rounded`, no `border`, no
   * default padding). Use for full-screen pickers, galleries, onboarding.
   */
  fullscreen?: boolean
  /**
   * Close affordance shown in the top-right corner.
   * - `undefined` (default): renders the built-in `X` button.
   * - `false`: no close button — use this when the surrounding UI provides
   *   its own close trigger (or the dialog has no dismiss).
   * - `ReactNode`: replaces the built-in button. Wrap your node in
   *   `DialogClose` so it dismisses the dialog.
   */
  closeButton?: React.ReactNode | false
}

const DialogContent = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Content>,
  DialogContentProps
>(({ className, children, fullscreen = false, closeButton, ...props }, ref) => (
  <DialogPortal>
    <DialogOverlay />
    <DialogPrimitive.Content
      ref={ref}
      aria-describedby={undefined}
      className={cn(
        // The content auto-focuses on open; suppress the focus outline on the
        // panel itself (a stray ring around the whole modal looks broken).
        // Inner controls keep their own focus-visible rings.
        "fixed z-1300 bg-background duration-200 focus:outline-none focus-visible:outline-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
        fullscreen
          // `grid-rows-[minmax(0,1fr)]` is load-bearing: a grid row defaults to
          // `min-height:auto`, so it grows past `h-[100dvh]` to fit its content.
          // A child sizing itself with `h-full` then measures that overgrown
          // row, its own `min-h-0`/`overflow-y-auto` never receive a bound, and
          // a long list (e.g. the locale picker) runs off-screen unscrollable.
          ? "left-0 top-0 grid grid-rows-[minmax(0,1fr)] h-[var(--app-height,100dvh)] w-screen max-w-none gap-0 border-0 p-0 pt-[var(--safe-top,0px)] pb-[var(--safe-bottom,0px)] shadow-none data-[state=closed]:zoom-out-[0.98] data-[state=open]:zoom-in-[0.98]"
          // Rounded on ALL sizes — the radius used to be `sm:`-gated, which left
          // phone dialogs with hard square corners. Centered, soft-cornered card.
          // Width by MEASUREMENT, not breakpoint: `min()` keeps the card off
          // both edges at any viewport. A `sm:` gate reads the window, so a
          // narrow desktop pane lost its margins and rendered as a sheet with
          // its rounding cropped.
          //
          // The size is `--width-dialog` (32rem by default) rather than a
          // literal, so a consumer can widen the card WITHOUT restating the
          // viewport clamp: `className="[--width-dialog:940px]"`. It used to be
          // hard-coded, which made the width unoverridable in practice — a
          // `max-width` beside a declared `width` is inert, so callers that
          // needed a wider dialog silently got 32rem.
          //
          // `grid-cols-[minmax(0,1fr)]` is the same fix as the fullscreen
          // branch's rows, on the other axis: a grid column also defaults to
          // `min-width:auto`, so one unbreakable child — a long description, a
          // path, a token — refuses to shrink and pushes the card past the
          // width declared right here. The clamp reads as inert when that
          // happens, and the overflow lands on whichever child is widest
          // rather than on the one at fault.
          //
          // HEIGHT is capped for the same reason width is clamped. The card is
          // `fixed` and centred by `-translate-y-1/2`, so content taller than
          // the viewport grows the box and then centres it on its own overflow:
          // BOTH ends leave the screen, and because nothing clips, nothing
          // scrolls. The cap is only a ceiling — a card that must scroll adds
          // `overflow-y-auto`, and one laying out its own regions overrides
          // `max-h` as before.
          : "left-1/2 top-1/2 grid max-h-[calc(var(--app-height,100dvh)-2rem-var(--safe-top,0px)-var(--safe-bottom,0px))] grid-cols-[minmax(0,1fr)] [aspect-ratio:var(--aspect-dialog,auto)] w-[min(var(--width-dialog),calc(100vw-2rem),calc((100dvh-2rem)*var(--aspect-dialog,1000)))] -translate-x-1/2 -translate-y-1/2 gap-4 rounded-[var(--radius-dialog)] border p-6 shadow-lg data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
        className
      )}
      {...props}
    >
      {children}
      {closeButton === undefined ? (
        <DialogPrimitive.Close className="absolute right-4 top-4 cursor-pointer rounded-sm opacity-70 transition-opacity hover:opacity-100 focus:outline-none focus:ring-1 focus:ring-ring disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
          <Cross2Icon className="h-4 w-4" />
          <span className="sr-only">Close</span>
        </DialogPrimitive.Close>
      ) : closeButton === false ? null : (
        closeButton
      )}
    </DialogPrimitive.Content>
  </DialogPortal>
))
DialogContent.displayName = DialogPrimitive.Content.displayName

const DialogHeader = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      // Start-aligned at every width: the `sm:` gate centred the title in a
      // narrow pane only, so one dialog read as two different components.
      "flex flex-col space-y-1.5 text-start",
      className
    )}
    {...props}
  />
)
DialogHeader.displayName = "DialogHeader"

const DialogFooter = ({
  className,
  ...props
}: React.HTMLAttributes<HTMLDivElement>) => (
  <div
    className={cn(
      // One row, buttons sized to their labels. The `sm:`-gated stack read the
      // window, so a narrow pane got two full-bleed buttons — Cancel as loud as
      // Confirm. `flex-wrap` handles a long label by measurement instead.
      "flex flex-wrap items-center justify-end gap-2",
      className
    )}
    {...props}
  />
)
DialogFooter.displayName = "DialogFooter"

const DialogTitle = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Title>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Title>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Title
    ref={ref}
    className={cn(
      "text-lg font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
DialogTitle.displayName = DialogPrimitive.Title.displayName

const DialogDescription = React.forwardRef<
  React.ElementRef<typeof DialogPrimitive.Description>,
  React.ComponentPropsWithoutRef<typeof DialogPrimitive.Description>
>(({ className, ...props }, ref) => (
  <DialogPrimitive.Description
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
DialogDescription.displayName = DialogPrimitive.Description.displayName

export {
  Dialog,
  DialogPortal,
  DialogOverlay,
  DialogTrigger,
  DialogClose,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
}
