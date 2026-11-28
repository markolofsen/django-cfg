"use client"

import { OTPInput, OTPInputContext, OTPInputProps as BaseOTPInputProps} from 'input-otp';
import * as React from 'react';

import { MinusIcon } from '@radix-ui/react-icons';

import { cn } from '../../../lib/utils';

type ChildrenBranch = Extract<BaseOTPInputProps, { render?: never }>;
type InputOTPProps = Omit<ChildrenBranch, 'className' | 'containerClassName'> & {
  className?: string;
  containerClassName?: string;
} & {
  children: React.ReactNode;
}
const InputOTP = React.forwardRef<
  React.ElementRef<typeof OTPInput>,
  InputOTPProps
>(({ className, containerClassName, children, ...props }, ref) => (
  <OTPInput
    ref={ref}
    containerClassName={cn(
      "flex items-center gap-2 has-[:disabled]:opacity-50",
      containerClassName
    )}
    className={cn("disabled:cursor-not-allowed", className)}
    {...props}
  >
    {children}
  </OTPInput>
))
InputOTP.displayName = "InputOTP"

const InputOTPGroup = React.forwardRef<
  React.ElementRef<"div">,
  React.ComponentPropsWithoutRef<"div">
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("flex items-center", className)} {...props} />
))
InputOTPGroup.displayName = "InputOTPGroup"

const InputOTPSlot = React.forwardRef<
  React.ElementRef<"div">,
  React.ComponentPropsWithoutRef<"div"> & { index: number }
>(({ index, className, ...props }, ref) => {
  const inputOTPContext = React.useContext(OTPInputContext)
  const slot = inputOTPContext.slots[index]
  if (!slot) return null
  const { char, hasFakeCaret, isActive } = slot

  return (
    <div
      ref={ref}
      className={cn(
        // Vercel-style slot: subtle near-black card, soft border, muted
        // digit colour, sharp focus ring. h/w come from `className`
        // (OTPInput sets either a fixed size or `flex-1 aspect-square`
        // for fluid layouts).
        "relative flex items-center justify-center rounded-md border border-border bg-card tabular-nums text-muted-foreground transition-colors",
        "hover:!border-foreground/40",
        // The library renders a single hidden <input> for the whole OTP, so
        // :focus-within fires on every slot at once. Visual focus must come
        // from the per-slot isActive flag instead. Use ! to win specificity
        // against the base `border-border`.
        isActive && "z-10 !border-foreground !text-foreground",
        className
      )}
      {...props}
    >
      {char}
      {hasFakeCaret && (
        <div className="pointer-events-none absolute inset-0 flex items-center justify-center">
          <div className="h-5 w-px animate-caret-blink bg-foreground duration-1000" />
        </div>
      )}
    </div>
  )
})
InputOTPSlot.displayName = "InputOTPSlot"

const InputOTPSeparator = React.forwardRef<
  React.ElementRef<"div">,
  React.ComponentPropsWithoutRef<"div">
>(({ ...props }, ref) => (
  <div ref={ref} role="separator" {...props}>
    <MinusIcon />
  </div>
))
InputOTPSeparator.displayName = "InputOTPSeparator"

export { InputOTP, InputOTPGroup, InputOTPSlot, InputOTPSeparator }
