'use client'

import { MinusIcon } from 'lucide-react';
import * as React from 'react';

import { InputOTP, InputOTPGroup, InputOTPSlot } from '../input-otp';
import { cn } from '../../../lib';
import { useIsMobile } from '../../../hooks';

import { createPasteHandler, useSmartOTP } from './use-otp-input';

import type { SmartOTPProps } from './types'

/**
 * Size variants for OTP slots — fixed square dimensions (Vercel/Linear look).
 * The boxes never stretch to the container width: a code is a small, tidy
 * cluster of fixed cells, centered, not a row of full-width fields.
 */
const sizeVariants = {
  sm: 'h-10 w-10 text-base',
  default: 'h-12 w-12 text-lg',
  lg: 'h-14 w-14 text-xl',
}

/**
 * OTP Separator Component
 */
const InputOTPSeparator = React.forwardRef<
  HTMLDivElement,
  React.ComponentPropsWithoutRef<'div'>
>(({ className, ...props }, ref) => (
  <div ref={ref} role="separator" className={cn('flex items-center', className)} {...props}>
    <MinusIcon />
  </div>
))
InputOTPSeparator.displayName = 'InputOTPSeparator'

/**
 * Smart OTP Input Component
 *
 * Features:
 * - Automatic paste handling with cleaning
 * - Validation (numeric, alphanumeric, alpha, custom)
 * - Auto-submit on completion
 * - Customizable appearance
 * - Error/success states
 * - Optional separator
 *
 * @example
 * ```tsx
 * <OTPInput
 *   length={6}
 *   value={code}
 *   onChange={setCode}
 *   onComplete={(value) => console.log('Complete:', value)}
 * />
 * ```
 *
 * @example With custom validation
 * ```tsx
 * <OTPInput
 *   length={4}
 *   validationMode="custom"
 *   customValidator={(char) => /[A-F0-9]/i.test(char)}
 *   value={hexCode}
 *   onChange={setHexCode}
 * />
 * ```
 */
export const OTPInput = React.forwardRef<
  React.ComponentRef<typeof InputOTP>,
  SmartOTPProps
>(
  (
    {
      length = 6,
      value,
      onChange,
      onComplete,
      validationMode = 'numeric',
      customValidator,
      pasteBehavior = 'clean',
      autoSubmit = false,
      disabled = false,
      showSeparator = false,
      separatorIndex,
      containerClassName,
      slotClassName,
      separatorClassName,
      autoFocus = true,
      size,
      error = false,
      success = false,
      ...props
    },
    ref
  ) => {
    const isMobile = useIsMobile()
    // Vercel-tuned default — 48×48 even on desktop. Caller can still
    // pass size="lg" for marketing surfaces.
    const resolvedSize = size ?? (isMobile ? 'default' : 'default')

    const {
      value: otpValue,
      handleChange,
      handleComplete,
    } = useSmartOTP({
      length,
      value,
      onChange,
      onComplete,
      validationMode,
      customValidator,
      autoSubmit,
    })

    // Create paste handler
    const pasteHandler = React.useMemo(
      () =>
        createPasteHandler(
          length,
          validationMode,
          pasteBehavior,
          handleChange,
          customValidator
        ),
      [length, validationMode, pasteBehavior, handleChange, customValidator]
    )

    // Calculate separator position (default to middle)
    const separatorPosition = separatorIndex ?? Math.floor(length / 2)

    // Render slots
    const slots = React.useMemo(() => {
      const slotElements: React.ReactNode[] = []

      for (let i = 0; i < length; i++) {
        // Add separator if needed
        if (showSeparator && i === separatorPosition && i !== 0) {
          slotElements.push(
            <InputOTPSeparator
              key={`separator-${i}`}
              className={cn('mx-1', separatorClassName)}
            />
          )
        }

        // Add slot
        slotElements.push(
          <InputOTPSlot
            key={i}
            index={i}
            className={cn(
              sizeVariants[resolvedSize],
              error && 'border-destructive ring-destructive/20',
              success && 'border-success ring-success/20',
              slotClassName
            )}
          />
        )
      }

      return slotElements
    }, [length, showSeparator, separatorPosition, separatorClassName, resolvedSize, error, success, slotClassName])

    return (
      <InputOTP
        ref={ref}
        maxLength={length}
        value={otpValue}
        onChange={handleChange}
        onComplete={handleComplete}
        disabled={disabled}
        containerClassName={cn('gap-2', containerClassName)}
        autoFocus={autoFocus}
        onPaste={pasteHandler}
        {...props}
      >
        <InputOTPGroup className="gap-2">{slots}</InputOTPGroup>
      </InputOTP>
    )
  }
)

OTPInput.displayName = 'OTPInput'

/**
 * Re-export base components for advanced usage
 */
export { InputOTPGroup, InputOTPSlot } from '../input-otp'
export { InputOTPSeparator }

/**
 * Re-export types
 */
export type {
  SmartOTPProps as OTPInputProps,
  OTPValidationMode,
  OTPPasteBehavior,
  OTPValidator,
} from './types'

/**
 * Re-export hook for advanced usage
 */
export { useSmartOTP } from './use-otp-input'
