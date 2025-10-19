import React from 'react';

import type { CfgUserProfileTypes } from '@djangocfg/api';

// User profile type
export type UserProfile = CfgUserProfileTypes.User;

// Auth configuration
export interface AuthConfig {
  apiUrl?: string;
  routes?: {
    auth?: string;
    defaultCallback?: string;
    defaultAuthCallback?: string;
  };
  onLogout?: () => void;
  onConfirm?: (options: {
    title: string;
    description: string;
    confirmationButtonText: string;
    cancellationButtonText: string;
    color: string;
  }) => Promise<{ confirmed: boolean }>;
}

// Auth context interface
export interface AuthContextType {
  user: UserProfile | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  loadCurrentProfile: () => Promise<void>;
  checkAuthAndRedirect: () => Promise<void>;

  // Email Methods
  getSavedEmail: () => string | null;
  saveEmail: (email: string) => void;
  clearSavedEmail: () => void;

  // Phone Methods
  getSavedPhone: () => string | null;
  savePhone: (phone: string) => void;
  clearSavedPhone: () => void;

  // OTP Methods - Multi-channel support
  requestOTP: (identifier: string, channel?: 'email' | 'phone', sourceUrl?: string) => Promise<{ success: boolean; message: string }>;
  verifyOTP: (identifier: string, otpCode: string, channel?: 'email' | 'phone', sourceUrl?: string) => Promise<{ success: boolean; message: string; user?: UserProfile }>;
  refreshToken: () => Promise<{ success: boolean; message: string }>;
  logout: () => Promise<void>;

  // Redirect Methods
  getSavedRedirectUrl: () => string | null;
  saveRedirectUrl: (url: string) => void;
  clearSavedRedirectUrl: () => void;
  getFinalRedirectUrl: () => string;
  useAndClearRedirectUrl: () => string;
  saveCurrentUrlForRedirect: () => void;
}

// Provider props
export interface AuthProviderProps {
  children: React.ReactNode;
  config?: AuthConfig;
} 