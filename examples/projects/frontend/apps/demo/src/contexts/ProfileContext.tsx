import React, { createContext, useContext, ReactNode } from 'react';
import { profilesApi } from '@/api/BaseClient';
import {
  useProfilesProfilesMeRetrieve,
  useProfilesProfilesStatsRetrieve,
  usePartialUpdateProfilesProfilesMePartialUpdate
} from '../api/generated/profiles/_utils/hooks/profiles__api__profiles';
import type { API } from '../api/generated/profiles';
import type {
  UserProfile,
  UserProfileStats,
  PatchedUserProfileRequest
} from '../api/generated/profiles/profiles__api__profiles/models';

interface ProfileContextType {
  // Profile data
  profile: UserProfile | undefined;
  stats: UserProfileStats | undefined;
  isLoading: boolean;
  error: Error | null;

  // Actions
  updateProfile: (data: PatchedUserProfileRequest) => Promise<UserProfile>;
  refreshProfile: () => Promise<void>;
}

const ProfileContext = createContext<ProfileContextType | undefined>(undefined);

export function ProfileProvider({ children }: { children: ReactNode }) {
  // Get current user profile (SWR)
  const {
    data: profile,
    error: profileError,
    isLoading: profileLoading,
    mutate: mutateProfile
  } = useProfilesProfilesMeRetrieve(profilesApi as unknown as API);

  // Get profile statistics (SWR)
  const {
    data: stats,
    isLoading: statsLoading,
  } = useProfilesProfilesStatsRetrieve(profilesApi as unknown as API);

  // Update profile mutation (SWR)
  const updateProfileMutation = usePartialUpdateProfilesProfilesMePartialUpdate();

  const isLoading = profileLoading || statsLoading;
  const error = profileError as Error | null;

  const value: ProfileContextType = {
    profile,
    stats,
    isLoading,
    error,
    updateProfile: async (data: PatchedUserProfileRequest) => {
      return await updateProfileMutation(data, profilesApi as unknown as API);
    },
    refreshProfile: async () => {
      await mutateProfile();
    },
  };

  return (
    <ProfileContext.Provider value={value}>
      {children}
    </ProfileContext.Provider>
  );
}

export function useProfile() {
  const context = useContext(ProfileContext);
  if (context === undefined) {
    throw new Error('useProfile must be used within a ProfileProvider');
  }
  return context;
}
