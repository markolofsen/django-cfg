'use client'

import { useCallback, useEffect, useMemo, useState } from 'react';

import type {
  SmartOTPProps,
  UseSmartOTPReturn,
  OTPValidationMode,
  OTPPasteBehavior,
  OTPValidator,
} from './types'

/**
 * Validation patterns for different modes
 */
const VALIDATION_PATTERNS: Record<Exclude<OTPValidationMode, 'custom'>, RegExp> = {
  numeric: /^\d+$/,
  alphanumeric: /^[a-zA-Z0-9]+$/,
  alpha: /^[a-zA-Z]+$/,
}

/**
 * Clean input based on validation mode
 */
function cleanInput(
  input: string,
  validationMode: OTPValidationMode,
  customValidator?: OTPValidator
): string {
  if (!input) return ''

  // Remove all whitespace and convert to uppercase for consistency
  const cleaned = input.replace(/\s+/g, '').trim()

  if (validationMode === 'custom' && customValidator) {
    // For custom validation, filter character by character
    return cleaned
      .split('')
      .filter((char) => customValidator(char))
      .join('')
  }

  // For built-in modes, use regex patterns
  const pattern = VALIDATION_PATTERNS[validationMode as keyof typeof VALIDATION_PATTERNS]
  if (!pattern) return cleaned

  return cleaned
    .split('')
    .filter((char) => pattern.test(char))
    .join('')
}

/**
 * Validate entire value
 */
function validateValue(
  value: string,
  validationMode: OTPValidationMode,
  customValidator?: OTPValidator
): boolean {
  if (!value) return true // Empty is valid

  if (validationMode === 'custom' && customValidator) {
    return customValidator(value)
  }

  const pattern = VALIDATION_PATTERNS[validationMode as keyof typeof VALIDATION_PATTERNS]
  return pattern ? pattern.test(value) : true
}

/**
 * Process pasted content based on paste behavior
 */
function processPaste(
  pastedText: string,
  validationMode: OTPValidationMode,
  pasteBehavior: OTPPasteBehavior,
  length: number,
  customValidator?: OTPValidator
): string | null {
  const cleaned = cleanInput(pastedText, validationMode, customValidator)

  switch (pasteBehavior) {
    case 'strict':
      // Only accept if the cleaned version matches the original (no invalid chars)
      if (cleaned.length !== pastedText.replace(/\s+/g, '').length) {
        return null // Reject paste
      }
      return cleaned.slice(0, length)

    case 'lenient':
      // Accept and use only valid characters
      return cleaned.slice(0, length)

    case 'clean':
    default:
      // Clean and use valid characters
      return cleaned.slice(0, length)
  }
}

/**
 * Smart OTP Input Hook
 * Handles validation, paste behavior, and state management
 */
export function useSmartOTP({
  length = 6,
  value: controlledValue,
  onChange,
  onComplete,
  validationMode = 'numeric',
  customValidator,
  autoSubmit = false,
}: Pick<
  SmartOTPProps,
  | 'length'
  | 'value'
  | 'onChange'
  | 'onComplete'
  | 'validationMode'
  | 'customValidator'
  | 'autoSubmit'
>): UseSmartOTPReturn {
  const [internalValue, setInternalValue] = useState('')

  // Use controlled value if provided, otherwise use internal state
  const value = controlledValue !== undefined ? controlledValue : internalValue

  const isComplete = useMemo(() => value.length === length, [value, length])

  const isValid = useMemo(
    () => validateValue(value, validationMode, customValidator),
    [value, validationMode, customValidator]
  )

  /**
   * Handle value change with validation
   */
  const handleChange = useCallback(
    (newValue: string) => {
      // Clean the input
      const cleaned = cleanInput(newValue, validationMode, customValidator)

      // Limit to max length
      const limited = cleaned.slice(0, length)

      // Update state
      if (controlledValue === undefined) {
        setInternalValue(limited)
      }

      // Call onChange callback
      onChange?.(limited)
    },
    [validationMode, customValidator, length, onChange, controlledValue]
  )

  /**
   * Handle completion
   */
  const handleComplete = useCallback(
    (completedValue: string) => {
      if (completedValue.length === length && isValid) {
        onComplete?.(completedValue)
      }
    },
    [length, isValid, onComplete]
  )

  /**
   * Clear value
   */
  const clear = useCallback(() => {
    if (controlledValue === undefined) {
      setInternalValue('')
    }
    onChange?.('')
  }, [onChange, controlledValue])

  /**
   * Auto-submit when complete
   */
  useEffect(() => {
    if (autoSubmit && isComplete && isValid) {
      handleComplete(value)
    }
  }, [autoSubmit, isComplete, isValid, value, handleComplete])

  return {
    value,
    handleChange,
    handleComplete,
    isComplete,
    isValid,
    clear,
  }
}

/**
 * Create a paste handler for OTP input
 */
export function createPasteHandler(
  length: number,
  validationMode: OTPValidationMode,
  pasteBehavior: OTPPasteBehavior,
  onChange: (value: string) => void,
  customValidator?: OTPValidator
) {
  return (e: React.ClipboardEvent) => {
    e.preventDefault()
    const pastedText = e.clipboardData.getData('text')

    const processed = processPaste(
      pastedText,
      validationMode,
      pasteBehavior,
      length,
      customValidator
    )

    if (processed !== null) {
      onChange(processed)
    }
  }
}
