'use client';

import React, { memo } from 'react';

import { OTPInput } from '@djangocfg/ui-core/components';

import { AUTH } from '../../constants';

export interface AuthOTPInputProps {
  value: string;
  onChange: (value: string) => void;
  onComplete?: (value: string) => void;
  disabled?: boolean;
  autoFocus?: boolean;
  size?: 'sm' | 'default' | 'lg';
  length?: number;
}

/**
 * AuthOTPInput - Reusable OTP input with consistent styling.
 *
 * Used in: OTPStep (email, 4 digits).
 *
 * Memoised: re-renders only when value, disabled, autoFocus, size or length
 * change. `onChange` and `onComplete` are compared by reference — callers
 * should stabilise them with useCallback.
 */
function AuthOTPInputRaw({
  value,
  onChange,
  onComplete,
  disabled = false,
  autoFocus = true,
  size,
  length = AUTH.TOTP_LENGTH,
}: AuthOTPInputProps) {
  return (
    <div className="auth-otp-container">
      <OTPInput
        length={length}
        validationMode="numeric"
        pasteBehavior="clean"
        value={value}
        onChange={onChange}
        onComplete={onComplete}
        disabled={disabled}
        autoFocus={autoFocus}
        size={size}
      />
    </div>
  );
}

export const AuthOTPInput = memo(AuthOTPInputRaw);
