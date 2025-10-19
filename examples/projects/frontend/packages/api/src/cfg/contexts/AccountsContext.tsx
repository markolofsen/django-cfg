/**
 * Accounts Context
 * 
 * Manages user authentication and profile operations using generated SWR hooks
 * 
 * Features:
 * - OTP-based authentication
 * - User profile management
 * - Avatar upload
 * - Profile updates
 */

"use client";

import { createContext, useContext, ReactNode } from 'react';
import { SWRConfig, useSWRConfig } from 'swr';
import { api } from '../BaseClient';
import {
  useAccountsProfileRetrieve,
  usePartialUpdateAccountsProfilePartialUpdate,
  useUpdateAccountsProfileUpdateUpdate,
  useCreateAccountsProfileAvatarCreate,
  useCreateAccountsOtpRequestCreate,
  useCreateAccountsOtpVerifyCreate,
  useCreateAccountsTokenRefreshCreate,
} from '../generated/_utils/hooks';
import type { API } from '../generated';
import type {
  User,
  UserProfileUpdateRequest,
  PatchedUserProfileUpdateRequest,
  OTPRequestRequest,
  OTPVerifyRequest,
  OTPRequestResponse,
  OTPVerifyResponse,
  TokenRefresh,
} from '../generated/_utils/schemas';

// Re-export schemas for external use
export { PatchedUserProfileUpdateRequestSchema } from '../generated/_utils/schemas/PatchedUserProfileUpdateRequest.schema';
export type { PatchedUserProfileUpdateRequest };

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface AccountsContextValue {
  // Current user profile
  profile?: User;
  isLoadingProfile: boolean;
  profileError: Error | null;

  // Profile operations
  updateProfile: (data: UserProfileUpdateRequest) => Promise<User>;
  partialUpdateProfile: (data: PatchedUserProfileUpdateRequest) => Promise<User>;
  uploadAvatar: (formData: FormData) => Promise<User>;
  refreshProfile: () => Promise<User | undefined>;

  // Authentication
  requestOTP: (data: OTPRequestRequest) => Promise<OTPRequestResponse>;
  verifyOTP: (data: OTPVerifyRequest) => Promise<OTPVerifyResponse>;
  refreshToken: (refresh: string) => Promise<TokenRefresh>;
  logout: () => void;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const AccountsContext = createContext<AccountsContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider Component
// ─────────────────────────────────────────────────────────────────────────

interface AccountsProviderProps {
  children: ReactNode;
}

export function AccountsProvider({ children }: AccountsProviderProps) {
  const { mutate } = useSWRConfig();
  
  // SWR config - disable auto-revalidation
  const swrConfig = {
    revalidateOnFocus: false,
    revalidateOnReconnect: false,
    revalidateIfStale: false,
  };

  // Get current user profile
  const {
    data: profile,
    error: profileError,
    isLoading: isLoadingProfile,
    mutate: mutateProfile,
  } = useAccountsProfileRetrieve(api as unknown as API);

  // Mutation hooks
  const updateMutation = useUpdateAccountsProfileUpdateUpdate();
  const partialUpdateMutation = usePartialUpdateAccountsProfilePartialUpdate();
  const avatarMutation = useCreateAccountsProfileAvatarCreate();
  const otpRequestMutation = useCreateAccountsOtpRequestCreate();
  const otpVerifyMutation = useCreateAccountsOtpVerifyCreate();
  const tokenRefreshMutation = useCreateAccountsTokenRefreshCreate();

  // Refresh profile
  const refreshProfile = async (): Promise<User | undefined> => {
    return await mutateProfile();
  };

  // Update profile (full)
  const updateProfile = async (data: UserProfileUpdateRequest): Promise<User> => {
    const result = await updateMutation(data, api as unknown as API);
    await refreshProfile();
    return result as User;
  };

  // Partial update profile
  const partialUpdateProfile = async (data: PatchedUserProfileUpdateRequest): Promise<User> => {
    const result = await partialUpdateMutation(data, api as unknown as API);
    await refreshProfile();
    return result as User;
  };

  // Upload avatar
  const uploadAvatar = async (formData: FormData): Promise<User> => {
    const result = await avatarMutation(formData, api as unknown as API);
    await refreshProfile();
    return result as User;
  };

  // Request OTP
  const requestOTP = async (data: OTPRequestRequest): Promise<OTPRequestResponse> => {
    const result = await otpRequestMutation(data, api as unknown as API);
    return result as OTPRequestResponse;
  };

  // Verify OTP
  const verifyOTP = async (data: OTPVerifyRequest): Promise<OTPVerifyResponse> => {
    const result = await otpVerifyMutation(data, api as unknown as API);
    
    // Automatically save tokens after successful verification
    if (result.access && result.refresh) {
      api.setToken(result.access, result.refresh);
      // Refresh profile to load user data with new token
      await refreshProfile();
    }
    
    return result as OTPVerifyResponse;
  };

  // Refresh token
  const refreshToken = async (refresh: string): Promise<TokenRefresh> => {
    const result = await tokenRefreshMutation({ refresh }, api as unknown as API);
    
    // Automatically save new access token
    if (result.access) {
      api.setToken(result.access, refresh);
    }
    
    return result as TokenRefresh;
  };

  // Logout - clear tokens and invalidate profile cache
  const logout = () => {
    api.clearTokens();
    // Invalidate profile cache to trigger re-fetch (which will fail and clear profile state)
    mutateProfile(undefined, false);
  };

  const value: AccountsContextValue = {
    profile,
    isLoadingProfile,
    profileError,
    updateProfile,
    partialUpdateProfile,
    uploadAvatar,
    refreshProfile,
    requestOTP,
    verifyOTP,
    refreshToken,
    logout,
  };

  return (
    <SWRConfig value={swrConfig}>
      <AccountsContext.Provider value={value}>
        {children}
      </AccountsContext.Provider>
    </SWRConfig>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useAccountsContext(): AccountsContextValue {
  const context = useContext(AccountsContext);
  if (!context) {
    throw new Error('useAccountsContext must be used within AccountsProvider');
  }
  return context;
}

