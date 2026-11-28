import { cva, type VariantProps } from 'class-variance-authority';
import * as React from 'react';

import { cn } from '../../../lib/utils';

const badgeVariants = cva(
  "inline-flex items-center rounded-(--badge-radius) border px-(--badge-px) py-(--badge-py) text-(length:--badge-font-size) font-(weight:--badge-weight) transition-colors focus:outline-none focus:ring-1 focus:ring-ring",
  {
    variants: {
      variant: {
        default:
          "border-transparent bg-primary text-primary-foreground shadow hover:bg-primary/80",
        secondary:
          "border-transparent bg-secondary text-secondary-foreground hover:bg-secondary/80",
        destructive:
          "border-transparent bg-destructive text-destructive-foreground shadow hover:bg-destructive/80",
        outline: "text-foreground",
        gray: "border-transparent bg-(--tag-gray-bg) text-(--tag-gray-fg)",
        brown: "border-transparent bg-(--tag-brown-bg) text-(--tag-brown-fg)",
        orange: "border-transparent bg-(--tag-orange-bg) text-(--tag-orange-fg)",
        yellow: "border-transparent bg-(--tag-yellow-bg) text-(--tag-yellow-fg)",
        green: "border-transparent bg-(--tag-green-bg) text-(--tag-green-fg)",
        blue: "border-transparent bg-(--tag-blue-bg) text-(--tag-blue-fg)",
        purple: "border-transparent bg-(--tag-purple-bg) text-(--tag-purple-fg)",
        pink: "border-transparent bg-(--tag-pink-bg) text-(--tag-pink-fg)",
        red: "border-transparent bg-(--tag-red-bg) text-(--tag-red-fg)",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
