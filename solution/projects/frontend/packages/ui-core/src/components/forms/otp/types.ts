// Reserved for future use
// import type { OTPInputProps as BaseOTPInputProps } from 'input-otp'

/**
 * OTP Input validation modes
 */
export type OTPValidationMode = 'numeric' | 'alphanumeric' | 'alpha' | 'custom'

/**
 * OTP Input paste behavior
 */
export type OTPPasteBehavior = 'clean' | 'strict' | 'lenient'

/**
 * Custom validator function
 */
export type OTPValidator = (value: string) => boolean

/**
 * Props for the smart OTP component
 */
export interface SmartOTPProps {
  /**
   * Number of OTP slots
   * @default 6
   */
  length?: number

  /**
   * Current OTP value
   */
  value?: string

  /**
   * Callback when value changes
   */
  onChange?: (value: string) => void

  /**
   * Callback when OTP is complete
   */
  onComplete?: (value: string) => void

  /**
   * Validation mode
   * @default 'numeric'
   */
  validationMode?: OTPValidationMode

  /**
   * Custom validator function (used when validationMode is 'custom')
   */
  customValidator?: OTPValidator

  /**
   * Paste behavior
   * - clean: Remove all non-valid characters
   * - strict: Only accept paste if all characters are valid
   * - lenient: Accept paste and keep valid characters only
   * @default 'clean'
   */
  pasteBehavior?: OTPPasteBehavior

  /**
   * Auto-submit when complete
   * @default false
   */
  autoSubmit?: boolean

  /**
   * Disabled state
   */
  disabled?: boolean

  /**
   * Show separator between slots
   * @default false
   */
  showSeparator?: boolean

  /**
   * Separator position (0-based index, appears after this index)
   */
  separatorIndex?: number

  /**
   * Custom class name for container
   */
  containerClassName?: string

  /**
   * Custom class name for slots
   */
  slotClassName?: string

  /**
   * Custom class name for separator
   */
  separatorClassName?: string

  /**
   * Auto-focus first slot on mount
   * @default true
   */
  autoFocus?: boolean

  /**
   * Slot size variant. When omitted, auto-detects: 'default' on mobile, 'lg' on desktop.
   */
  size?: 'sm' | 'default' | 'lg'

  /**
   * Error state
   */
  error?: boolean

  /**
   * Success state
   */
  success?: boolean
}

/**
 * Return type for useSmartOTP hook
 */
export interface UseSmartOTPReturn {
  value: string
  handleChange: (newValue: string) => void
  handleComplete: (completedValue: string) => void
  isComplete: boolean
  isValid: boolean
  clear: () => void
}
