"use client"

import * as React from 'react';

import * as SwitchPrimitives from '@radix-ui/react-switch';

import { cn } from '../../../lib/utils';

const Switch = React.forwardRef<
  React.ElementRef<typeof SwitchPrimitives.Root>,
  React.ComponentPropsWithoutRef<typeof SwitchPrimitives.Root>
>(({ className, ...props }, ref) => (
  <SwitchPrimitives.Root
    className={cn(
      // Track: generous Cloudflare-style pill (44×24) with an inset thumb.
      // `select-none`: a drag starting on the pill must toggle or do nothing —
      // never paint a text selection across the row the switch sits in.
      "peer group relative inline-flex h-6 w-11 shrink-0 cursor-pointer select-none items-center rounded-full",
      "p-0.5 outline-none transition-colors duration-200 ease-out",
      // On/off surfaces — all on-token so every preset & theme follows along.
      "data-[state=unchecked]:bg-input data-[state=checked]:bg-primary",
      // Focus ring sits outside the pill with an offset gap (matches Cloudflare's selected state).
      "focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 focus-visible:ring-offset-background",
      "disabled:cursor-not-allowed disabled:opacity-50",
      className
    )}
    {...props}
    ref={ref}
  >
    <SwitchPrimitives.Thumb
      className={cn(
        "pointer-events-none block h-5 w-5 rounded-full bg-background shadow-md ring-0",
        "transition-transform duration-200 ease-out",
        "data-[state=unchecked]:translate-x-0 data-[state=checked]:translate-x-5",
        // Subtle press-in feel on active, like the CF thumb.
        "group-active:scale-95"
      )}
    />
  </SwitchPrimitives.Root>
))
Switch.displayName = SwitchPrimitives.Root.displayName

export { Switch }
