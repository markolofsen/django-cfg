import React, { createContext, useContext } from 'react';

import { useAuthForm } from '../../../../auth/hooks';

import type { AuthContextType, AuthProps } from './types';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<AuthProps> = ({
  children,
  sourceUrl: sourceUrlProp,
  supportUrl,
  termsUrl,
  privacyUrl,
  enablePhoneAuth = false, // Default to true for backward compatibility
  onIdentifierSuccess,
  onOTPSuccess,
  onError,
}) => {
  const sourceUrl = sourceUrlProp || (typeof window !== 'undefined' ? window.location.origin : '');

  // Use the auth form hook with required sourceUrl
  const authForm = useAuthForm({
    onIdentifierSuccess,
    onOTPSuccess,
    onError,
    sourceUrl,
  });

  const value: AuthContextType = {
    // Form state from auth form hook
    ...authForm,

    // UI-specific configuration
    sourceUrl,
    supportUrl,
    termsUrl,
    privacyUrl,
    enablePhoneAuth,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuthContext = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuthContext must be used within an AuthProvider');
  }
  return context;
};
