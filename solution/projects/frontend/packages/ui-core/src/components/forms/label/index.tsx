"use client"

import { cva, type VariantProps } from 'class-variance-authority';
import * as React from 'react';

import * as LabelPrimitive from '@radix-ui/react-label';

import { cn } from '../../../lib/utils';

// `select-none` is not cosmetic here.
//
// A label is text whose whole purpose is to be CLICKED, and a click that lands
// slightly off — or a click that drags a pixel — leaves the word highlighted in
// the selection colour. In a filter rail that reads as a selected FILTER rather
// than selected TEXT, so the control reports a state the user never set. The
// same shape appears in every checkbox list, radio group and switch row, which
// is why it belongs to the primitive and not to any one screen.
const labelVariants = cva(
  "select-none text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
)

const Label = React.forwardRef<
  React.ElementRef<typeof LabelPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof LabelPrimitive.Root> &
    VariantProps<typeof labelVariants>
>(({ className, ...props }, ref) => (
  <LabelPrimitive.Root
    ref={ref}
    className={cn(labelVariants(), className)}
    {...props}
  />
))
Label.displayName = LabelPrimitive.Root.displayName

export { Label }
