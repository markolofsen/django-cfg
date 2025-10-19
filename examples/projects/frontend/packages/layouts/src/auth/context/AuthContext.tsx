import { useRouter } from 'next/router';
import React, {
    createContext, ReactNode, useCallback, useContext, useEffect, useMemo, useRef, useState
} from 'react';

import { api, Enums } from '@djangocfg/api';
import { useAccountsContext, AccountsProvider } from '@djangocfg/api/cfg/contexts';
import { useLocalStorage } from '@djangocfg/ui/hooks';

import { authLogger } from '../../utils/logger';
import type { AuthConfig, AuthContextType, AuthProviderProps, UserProfile } from './types';

// Default routes
const defaultRoutes = {
  auth: '/auth',
  defaultCallback: '/dashboard',
  defaultAuthCallback: '/auth',
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Constants
const EMAIL_STORAGE_KEY = 'auth_email';
const PHONE_STORAGE_KEY = 'auth_phone';
const AUTH_REDIRECT_KEY = 'auth_redirect_url';

const hasValidTokens = (): boolean => {
  if (typeof window === 'undefined') return false;
  return api.isAuthenticated();
};

// Internal provider that uses AccountsContext
const AuthProviderInternal: React.FC<AuthProviderProps> = ({ children, config }) => {
  const accounts = useAccountsContext();
  const [isLoading, setIsLoading] = useState(true);
  const [initialized, setInitialized] = useState(false);
  const router = useRouter();

  // Use localStorage hooks for email, phone, and redirect
  const [storedEmail, setStoredEmail, clearStoredEmail] = useLocalStorage<string | null>(EMAIL_STORAGE_KEY, null);
  const [storedPhone, setStoredPhone, clearStoredPhone] = useLocalStorage<string | null>(PHONE_STORAGE_KEY, null);
  const [redirectUrl, setRedirectUrl, clearRedirectUrl] = useLocalStorage<string | null>(AUTH_REDIRECT_KEY, null);

  // Map AccountsContext profile to UserProfile
  const user = accounts.profile as UserProfile | null;

  // Use refs to avoid dependency issues
  const userRef = useRef(user);
  const configRef = useRef(config);

  // Update refs when values change
  useEffect(() => {
    userRef.current = user;
  }, [user]);

  useEffect(() => {
    configRef.current = config;
  }, [config]);

  // Note: API URL is configured in BaseClient, not at runtime

  // Common function to clear auth state
  const clearAuthState = useCallback((caller: string) => {
    authLogger.info('clearAuthState >> caller', caller);
    api.clearTokens();
    // Note: user is now managed by AccountsContext, will auto-update
    setInitialized(true);
    setIsLoading(false);
  }, []);

  // Global error handler for auth-related errors
  const handleGlobalAuthError = useCallback((error: any, context: string = 'API Request') => {
    // Simple error check - if response has error flag, it's an error
    if (error?.success === false) {
      authLogger.warn(`Error detected in ${context}, clearing tokens`);
      clearAuthState(`globalAuthError:${context}`);
      return true;
    }

    return false;
  }, [clearAuthState]);

  // Simple profile loading without retry - now uses AccountsContext
  const loadCurrentProfile = useCallback(async (): Promise<void> => {
    try {
      // Ensure API clients are properly initialized with current token
      if (!api.isAuthenticated()) {
        throw new Error('No valid authentication token');
      }

      // Refresh profile from AccountsContext
      const refreshedProfile = await accounts.refreshProfile();
      
      if (refreshedProfile) {
        setInitialized(true);
        authLogger.info('Profile loaded successfully:', refreshedProfile.id);
      } else {
        authLogger.warn('Profile refresh returned undefined');
        clearAuthState('loadCurrentProfile:noProfile');
      }
    } catch (error) {
      authLogger.error('Failed to load profile:', error);
      // Use global error handler first, fallback to clearing state
      if (!handleGlobalAuthError(error, 'loadCurrentProfile')) {
        clearAuthState('loadCurrentProfile:error');
      }
    }
  }, [clearAuthState, handleGlobalAuthError, accounts]);

  // Initialize auth state once
  useEffect(() => {
    if (initialized) return;

    const initializeAuth = async () => {
      authLogger.info('Initializing auth...');
      setIsLoading(true);

      // Debug token state
      const token = api.getToken();
      const refreshToken = api.getRefreshToken();
      authLogger.info('Token from API:', token ? `${token.substring(0, 20)}...` : 'null');
      authLogger.info('Refresh token from API:', refreshToken ? `${refreshToken.substring(0, 20)}...` : 'null');
      authLogger.info('localStorage keys:', Object.keys(localStorage).filter(k => k.includes('token') || k.includes('auth')));

      const hasTokens = hasValidTokens();
      authLogger.info('Has tokens:', hasTokens);

      if (hasTokens) {
        try {
          await loadCurrentProfile();
        } catch (error) {
          authLogger.error('Failed to load profile during initialization:', error);
          // If profile loading fails, clear auth state
          clearAuthState('initializeAuth:loadProfileFailed');
        }
      } else {
        setInitialized(true);
      }

      setIsLoading(false);
    };

    initializeAuth();
  }, [initialized, loadCurrentProfile, clearAuthState]);

  // Redirect logic - only for unauthenticated users on protected pages
  useEffect(() => {
    if (!initialized) return;

    const isAuthenticated = !!userRef.current && api.isAuthenticated();
    const authRoute = config?.routes?.auth || defaultRoutes.auth;
    const isAuthPage = router.pathname === authRoute;

    // Only redirect authenticated users away from auth page if they're not in a flow
    // This prevents interference with OTP verification flow
    if (isAuthenticated && isAuthPage && !router.query.flow) {
      const callbackUrl = config?.routes?.defaultCallback || defaultRoutes.defaultCallback;
      window.location.href = callbackUrl;
    }
  }, [initialized, router.pathname, config?.routes, router.query.flow]);

  const pushToDefaultCallbackUrl = useCallback(() => {
    const callbackUrl = config?.routes?.defaultCallback || defaultRoutes.defaultCallback;
    window.location.href = callbackUrl;
  }, [config?.routes]);

  const pushToDefaultAuthCallbackUrl = useCallback(() => {
    const authCallbackUrl = config?.routes?.defaultAuthCallback || defaultRoutes.defaultAuthCallback;
    window.location.href = authCallbackUrl;
  }, [config?.routes]);

  // Memoized checkAuthAndRedirect function
  const checkAuthAndRedirect = useCallback(async () => {
    try {
      setIsLoading(true);
      const isAuthenticated = api.isAuthenticated();

      if (isAuthenticated) {
        await loadCurrentProfile();
        if (userRef.current) {
          pushToDefaultCallbackUrl();
        }
      } else {
        pushToDefaultAuthCallbackUrl();
      }
    } catch (error) {
      authLogger.error('Failed to check authentication:', error);
      // Use global error handler first
      if (!handleGlobalAuthError(error, 'checkAuthAndRedirect')) {
        clearAuthState('checkAuthAndRedirect');
      }
      pushToDefaultAuthCallbackUrl();
    } finally {
      setIsLoading(false);
    }
  }, [loadCurrentProfile, clearAuthState, pushToDefaultCallbackUrl, pushToDefaultAuthCallbackUrl, handleGlobalAuthError]);

  // OTP methods - supports both email and phone - now uses AccountsContext
  const requestOTP = useCallback(
    async (identifier: string, channel?: 'email' | 'phone', sourceUrl?: string): Promise<{ success: boolean; message: string }> => {
      // Clear tokens before requesting OTP
      api.clearTokens();

      try {
        const channelValue = channel === 'phone' 
          ? Enums.OTPRequestRequestChannel.PHONE 
          : Enums.OTPRequestRequestChannel.EMAIL;
        const result = await accounts.requestOTP({
          identifier,
          channel: channelValue,
        });

        const channelName = channel === 'phone' ? 'phone number' : 'email address';
        return {
          success: true,
          message: result.message || `OTP code sent to your ${channelName}`,
        };
      } catch (error) {
        authLogger.error('Request OTP error:', error);
        return {
          success: false,
          message: 'Failed to send OTP',
        };
      }
    },
    [accounts],
  );

  const verifyOTP = useCallback(
    async (identifier: string, otpCode: string, channel?: 'email' | 'phone', sourceUrl?: string): Promise<{ success: boolean; message: string; user?: UserProfile }> => {
      try {
        const channelValue = channel === 'phone' 
          ? Enums.OTPVerifyRequestChannel.PHONE 
          : Enums.OTPVerifyRequestChannel.EMAIL;
        // AccountsContext automatically saves tokens and refreshes profile
        const result = await accounts.verifyOTP({
          identifier,
          otp: otpCode,
          channel: channelValue,
        });

        // Verify that we got valid tokens
        if (!result.access || !result.refresh) {
          authLogger.error('Verify OTP returned invalid response:', result);
          return {
            success: false,
            message: 'Invalid OTP verification response',
          };
        }

        // Save identifier based on channel and clear opposite channel
        if (channel === 'phone') {
          setStoredPhone(identifier);
          clearStoredEmail();
        } else if (identifier.includes('@')) {
          setStoredEmail(identifier);
          clearStoredPhone();
        }

        // Small delay to ensure profile state is updated
        await new Promise(resolve => setTimeout(resolve, 200));

        // Handle redirect logic here
        const defaultCallback = config?.routes?.defaultCallback || defaultRoutes.defaultCallback;

        if (redirectUrl && redirectUrl !== defaultCallback) {
          clearRedirectUrl();
          window.location.href = redirectUrl;
        } else {
          window.location.href = defaultCallback;
        }

        return {
          success: true,
          message: 'Login successful',
          user: result.user as UserProfile,
        };
      } catch (error) {
        authLogger.error('Verify OTP error:', error);
        return {
          success: false,
          message: 'Failed to verify OTP',
        };
      }
    },
    [setStoredEmail, setStoredPhone, clearStoredEmail, clearStoredPhone, redirectUrl, clearRedirectUrl, config?.routes?.defaultCallback, accounts],
  );

  const refreshToken = useCallback(async (): Promise<{ success: boolean; message: string }> => {
    try {
      const refreshTokenValue = api.getRefreshToken();
      if (!refreshTokenValue) {
        clearAuthState('refreshToken:noToken');
        return {
          success: false,
          message: 'No refresh token available',
        };
      }

      await accounts.refreshToken(refreshTokenValue);
      
      return {
        success: true,
        message: 'Token refreshed',
      };
    } catch (error) {
      authLogger.error('Refresh token error:', error);
      clearAuthState('refreshToken:error');
      return {
        success: false,
        message: 'Error refreshing token',
      };
    }
  }, [clearAuthState, accounts]);

  const clearRedirect = useCallback((): void => {
    clearRedirectUrl();
  }, [clearRedirectUrl]);

  // Save current URL for redirect after authentication
  const saveCurrentUrlForRedirect = useCallback((): void => {
    if (typeof window !== 'undefined') {
      const currentUrl = window.location.pathname + window.location.search;
      setRedirectUrl(currentUrl);
    }
  }, [setRedirectUrl]);

  const logout = useCallback(async (): Promise<void> => {
    // Use config.onConfirm if provided, otherwise use a simple confirm
    if (configRef.current?.onConfirm) {
      const { confirmed } = await configRef.current.onConfirm({
        title: 'Logout',
        description: 'Are you sure you want to logout?',
        confirmationButtonText: 'Logout',
        cancellationButtonText: 'Cancel',
        color: 'error',
      });
      if (confirmed) {
        accounts.logout(); // Clear tokens and profile
        setInitialized(true);
        setIsLoading(false);
        pushToDefaultAuthCallbackUrl();
      }
    } else {
      // Fallback to browser confirm
      const confirmed = window.confirm('Are you sure you want to logout?');
      if (confirmed) {
        accounts.logout(); // Clear tokens and profile
        setInitialized(true);
        setIsLoading(false);
        pushToDefaultAuthCallbackUrl();
      }
    }
  }, [accounts, pushToDefaultAuthCallbackUrl]);

  // Redirect URL methods
  const getSavedRedirectUrl = useCallback((): string | null => {
    if (typeof window !== 'undefined') {
      return sessionStorage.getItem(AUTH_REDIRECT_KEY);
    }
    return null;
  }, []);

  const saveRedirectUrl = useCallback((url: string): void => {
    if (typeof window !== 'undefined') {
      sessionStorage.setItem(AUTH_REDIRECT_KEY, url);
    }
  }, []);

  const clearSavedRedirectUrl = useCallback((): void => {
    if (typeof window !== 'undefined') {
      sessionStorage.removeItem(AUTH_REDIRECT_KEY);
    }
  }, []);

  const getFinalRedirectUrl = useCallback((): string => {
    const savedUrl = getSavedRedirectUrl();
    return savedUrl || (config?.routes?.defaultCallback || defaultRoutes.defaultCallback);
  }, [getSavedRedirectUrl, config?.routes?.defaultCallback]);

  const useAndClearRedirectUrl = useCallback((): string => {
    const finalUrl = getFinalRedirectUrl();
    clearSavedRedirectUrl();
    return finalUrl;
  }, [getFinalRedirectUrl, clearSavedRedirectUrl]);

  // Memoized context value
  const value = useMemo<AuthContextType>(
    () => ({
      user,
      isLoading,
      isAuthenticated: !!user && api.isAuthenticated(),
      loadCurrentProfile,
      checkAuthAndRedirect,
      getSavedEmail: () => storedEmail,
      saveEmail: setStoredEmail,
      clearSavedEmail: clearStoredEmail,
      getSavedPhone: () => storedPhone,
      savePhone: setStoredPhone,
      clearSavedPhone: clearStoredPhone,
      requestOTP,
      verifyOTP,
      refreshToken,
      logout,
      getSavedRedirectUrl,
      saveRedirectUrl,
      clearSavedRedirectUrl,
      getFinalRedirectUrl,
      useAndClearRedirectUrl,
      saveCurrentUrlForRedirect,
    }),
    [
      user, 
      isLoading, 
      loadCurrentProfile, 
      checkAuthAndRedirect, 
      storedEmail,
      setStoredEmail,
      clearStoredEmail,
      storedPhone,
      setStoredPhone,
      clearStoredPhone,
      requestOTP, 
      verifyOTP, 
      refreshToken, 
      logout, 
      getSavedRedirectUrl, 
      saveRedirectUrl, 
      clearSavedRedirectUrl, 
      getFinalRedirectUrl, 
      useAndClearRedirectUrl,
      saveCurrentUrlForRedirect,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Wrapper that provides AccountsContext
export const AuthProvider: React.FC<AuthProviderProps> = ({ children, config }) => {
  return (
    <AccountsProvider>
      <AuthProviderInternal config={config}>
        {children}
      </AuthProviderInternal>
    </AccountsProvider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext; 