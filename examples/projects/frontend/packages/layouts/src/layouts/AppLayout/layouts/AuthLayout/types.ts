import React from 'react';

// Auth Context Types - Multi-channel support
export interface AuthContextType {
  // Form state
  identifier: string; // Email or phone number
  channel: 'email' | 'phone';
  otp: string;
  isLoading: boolean;
  acceptedTerms: boolean;

  // Auth state
  step: 'identifier' | 'otp';
  error: string;

  // Support configuration
  supportUrl?: string;
  termsUrl?: string;
  privacyUrl?: string;
  sourceUrl: string;
  enablePhoneAuth?: boolean;

  // Form handlers
  setIdentifier: (identifier: string) => void;
  setChannel: (channel: 'email' | 'phone') => void;
  setOtp: (otp: string) => void;
  setAcceptedTerms: (accepted: boolean) => void;
  setError: (error: string) => void;
  clearError: () => void;

  // Auth handlers
  handleIdentifierSubmit: (e: React.FormEvent) => Promise<void>;
  handleOTPSubmit: (e: React.FormEvent) => Promise<void>;
  handleResendOTP: () => Promise<void>;
  handleBackToIdentifier: () => void;
  forceOTPStep: () => void;

  // Utility methods
  detectChannelFromIdentifier: (identifier: string) => 'email' | 'phone' | null;
  validateIdentifier: (identifier: string, channel?: 'email' | 'phone') => boolean;
}

// Unified Auth Props - used by both AuthProvider and AuthLayout
export interface AuthProps {
  children?: React.ReactNode;
  sourceUrl?: string;
  supportUrl?: string;
  termsUrl?: string;
  privacyUrl?: string;
  className?: string;
  enablePhoneAuth?: boolean; // Controls whether phone authentication is available
  onIdentifierSuccess?: (identifier: string, channel: 'email' | 'phone') => void;
  onOTPSuccess?: () => void;
  onError?: (message: string) => void;
}

// Auth Help Types
export interface AuthHelpProps {
  className?: string;
  variant?: 'default' | 'compact';
}
