"use client"

import { cva, type VariantProps } from 'class-variance-authority';
import * as React from 'react';

import { cn } from '../../../lib/utils';
import { Button } from '../../forms/button';
import { CONTROL_SIZE, type FieldControlSize } from '../control-size';
import { Input } from '../../forms/input';
import { Textarea } from '../../forms/textarea';

function InputGroup({
  className,
  inputSize = "default",
  ...props
}: React.ComponentProps<"div"> & {
  /** Height from the shared control ladder — the same name as `Input`'s `inputSize`. */
  inputSize?: FieldControlSize
}) {
  return (
    <div
      data-slot="input-group"
      role="group"
      className={cn(
        // `border-border` and `bg-input`, the same pair `Input` resolves to. The
        // group had `border-input`, which in the light theme is the *fill*
        // token (97% L) rather than the edge one (86%) — so its border was
        // nearly invisible next to a plain field's, and a focused money input
        // showed a crisp inner rectangle inside a ghost of an outer one.
        "group/input-group border-border bg-input shadow-xs relative flex w-full items-center rounded-[var(--radius)] border outline-none transition-[color,background-color,border-color,box-shadow]",
        // Height comes from the shared control ladder, the same map `Input` and
        // `SelectTrigger` read, so a grouped input is never a row shorter or
        // taller than a bare one beside it. A wrapper that changes a control's
        // height cannot be dropped into an existing row.
        CONTROL_SIZE[inputSize].height,
        "has-[>textarea]:h-auto",

        // Variants based on alignment.
        //
        // Each side gets its inset from EITHER the addon or the control, never
        // both and never neither. With an addon the addon supplies the edge
        // gap and the control only needs to clear it (pl-2); with no addon the
        // control has to stand in for it (pl-3, matching `Input`'s own px-3).
        //
        // The `not-has-` half is load-bearing: `bare` strips the control's
        // padding, so a group without an addon on a side used to leave its text
        // flush against the border — visible on any addon-less group, and on a
        // MoneyField with `showSymbol={false}`.
        "has-[>[data-align=inline-start]]:[&>input]:pl-2",
        "not-has-[>[data-align=inline-start]]:[&>input]:pl-3",
        "has-[>[data-align=inline-end]]:[&>input]:pr-2",
        "not-has-[>[data-align=inline-end]]:[&>input]:pr-3",
        "has-[>[data-align=block-start]]:h-auto has-[>[data-align=block-start]]:flex-col has-[>[data-align=block-start]]:[&>input]:pb-3",
        "has-[>[data-align=block-end]]:h-auto has-[>[data-align=block-end]]:flex-col has-[>[data-align=block-end]]:[&>input]:pt-3",

        // Focus state. Border AND ring, the same pair `Input` uses on its own
        // — the group is standing in for a field's edge, so it has to draw the
        // whole treatment. Ring alone left the group's border its resting grey
        // while the control inside lit up, which reads as two nested fields.
        "has-[[data-slot=input-group-control]:focus-visible]:border-ring has-[[data-slot=input-group-control]:focus-visible]:ring-ring has-[[data-slot=input-group-control]:focus-visible]:ring-1",

        // Error state.
        "has-[[data-slot][aria-invalid=true]]:ring-destructive/20 has-[[data-slot][aria-invalid=true]]:border-destructive dark:has-[[data-slot][aria-invalid=true]]:ring-destructive/40",

        className
      )}
      {...props}
    />
  )
}

const inputGroupAddonVariants = cva(
  "text-muted-foreground flex h-auto cursor-text select-none items-center justify-center gap-2 py-1.5 text-sm font-medium group-data-[disabled=true]/input-group:opacity-50 [&>kbd]:rounded-[calc(var(--radius)-5px)] [&>svg:not([class*='size-'])]:size-4",
  {
    variants: {
      align: {
        "inline-start":
          "order-first pl-3 has-[>button]:ml-[-0.45rem] has-[>kbd]:ml-[-0.35rem]",
        "inline-end":
          "order-last pr-3 has-[>button]:mr-[-0.4rem] has-[>kbd]:mr-[-0.35rem]",
        "block-start":
          "[.border-b]:pb-3 order-first w-full justify-start px-3 pt-3 group-has-[>input]/input-group:pt-2.5",
        "block-end":
          "[.border-t]:pt-3 order-last w-full justify-start px-3 pb-3 group-has-[>input]/input-group:pb-2.5",
      },
    },
    defaultVariants: {
      align: "inline-start",
    },
  }
)

function InputGroupAddon({
  className,
  align = "inline-start",
  ...props
}: React.ComponentProps<"div"> & VariantProps<typeof inputGroupAddonVariants>) {
  return (
    <div
      role="group"
      data-slot="input-group-addon"
      data-align={align}
      className={cn(inputGroupAddonVariants({ align }), className)}
      onClick={(e) => {
        if ((e.target as HTMLElement).closest("button")) {
          return
        }
        e.currentTarget.parentElement?.querySelector("input")?.focus()
      }}
      {...props}
    />
  )
}

const inputGroupButtonVariants = cva(
  "flex items-center gap-2 text-sm shadow-none",
  {
    variants: {
      size: {
        xs: "h-6 gap-1 rounded-[calc(var(--radius)-5px)] px-2 has-[>svg]:px-2 [&>svg:not([class*='size-'])]:size-3.5",
        sm: "h-8 gap-1.5 rounded-[var(--radius)] px-2.5 has-[>svg]:px-2.5",
        "icon-xs":
          "size-6 rounded-[calc(var(--radius)-5px)] p-0 has-[>svg]:p-0",
        "icon-sm": "size-8 p-0 has-[>svg]:p-0",
      },
    },
    defaultVariants: {
      size: "xs",
    },
  }
)

function InputGroupButton({
  className,
  type = "button",
  variant = "ghost",
  size = "xs",
  ...props
}: Omit<React.ComponentProps<typeof Button>, "size"> &
  VariantProps<typeof inputGroupButtonVariants>) {
  return (
    <Button
      type={type}
      data-size={size}
      variant={variant}
      className={cn(inputGroupButtonVariants({ size }), className)}
      {...props}
    />
  )
}

function InputGroupText({ className, ...props }: React.ComponentProps<"span">) {
  return (
    <span
      className={cn(
        "text-muted-foreground flex items-center gap-2 text-sm [&_svg:not([class*='size-'])]:size-4 [&_svg]:pointer-events-none",
        className
      )}
      {...props}
    />
  )
}

/**
 * Forwards its ref, unlike the other parts of this group.
 *
 * `Input` is a `forwardRef`, and a plain function wrapper around it swallows
 * the ref silently — no warning, no type error, just a null ref at the call
 * site. Anything wrapping this (see `InputAffix`) needs the node to focus or
 * measure it.
 */
const InputGroupInput = React.forwardRef<
  HTMLInputElement,
  React.ComponentProps<"input">
>(({ className, ...props }, ref) => {
  return (
    <Input
      ref={ref}
      bare
      data-slot="input-group-control"
      // `bare` omits the field chrome instead of overriding it. Cancelling it
      // from here needed `focus-visible:ring-0` to beat `focus-visible:ring-1`
      // at equal specificity — decided by stylesheet order, not by `cn()` — so
      // a focused money field drew a rectangle inside a rectangle whenever the
      // order went the other way.
      className={cn("flex-1", className)}
      {...props}
    />
  )
})
InputGroupInput.displayName = "InputGroupInput"

function InputGroupTextarea({
  className,
  ...props
}: React.ComponentProps<"textarea">) {
  return (
    <Textarea
      bare
      data-slot="input-group-control"
      className={cn("flex-1 resize-none", className)}
      {...props}
    />
  )
}

export {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupText,
  InputGroupInput,
  InputGroupTextarea,
}
