import { cva, type VariantProps } from "class-variance-authority"
import * as React from "react"
import { Slot } from "@radix-ui/react-slot"

import { cn } from "../../../lib/utils"

const statusVariants = cva(
  "inline-flex w-fit shrink-0 items-center gap-1.5 overflow-hidden whitespace-nowrap rounded-full border px-2.5 py-1 font-medium text-xs transition-colors",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-muted text-muted-foreground **:data-[slot=status-indicator]:bg-muted-foreground",
        success:
          "border-success-border bg-success-background text-success **:data-[slot=status-indicator]:bg-success",
        error:
          "border-destructive/20 bg-destructive/10 text-destructive **:data-[slot=status-indicator]:bg-destructive",
        warning:
          "border-warning-border bg-warning-background text-warning **:data-[slot=status-indicator]:bg-warning",
        info: "border-info-border bg-info-background text-info **:data-[slot=status-indicator]:bg-info",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  },
)

interface StatusProps
  extends VariantProps<typeof statusVariants>,
    React.ComponentProps<"div"> {
  asChild?: boolean
}

function Status(props: StatusProps) {
  const { className, variant = "default", asChild, ...rootProps } = props

  const RootPrimitive = asChild ? Slot : "div"

  return (
    <RootPrimitive
      data-slot="status"
      data-variant={variant}
      {...rootProps}
      className={cn(statusVariants({ variant }), className)}
    />
  )
}

function StatusIndicator(props: React.ComponentProps<"div">) {
  const { className, ...indicatorProps } = props

  return (
    <div
      data-slot="status-indicator"
      {...indicatorProps}
      className={cn(
        "relative flex size-2 shrink-0 rounded-full",
        "before:absolute before:inset-0 before:animate-ping before:rounded-full before:bg-inherit",
        "after:absolute after:inset-[2px] after:rounded-full after:bg-inherit",
        className,
      )}
    />
  )
}

function StatusLabel(props: React.ComponentProps<"div">) {
  const { className, ...labelProps } = props

  return (
    <div
      data-slot="status-label"
      {...labelProps}
      className={cn("leading-none", className)}
    />
  )
}

export { Status, StatusIndicator, StatusLabel, statusVariants }
export type { StatusProps }
