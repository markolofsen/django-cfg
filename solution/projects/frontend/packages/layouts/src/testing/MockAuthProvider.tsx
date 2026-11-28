'use client';

import React, { useMemo, useState } from 'react';

import {
  AuthContext,
  type AuthContextType,
  type UserProfile,
} from '@djangocfg/api/auth';

// Storybook-only auth provider. Reproduces the AuthContext shape with
// fixed in-memory values so components that call `useAuth()` (Profile,
// PrivateLayout, etc.) can render without hitting the real auth API.

export interface MockAuthProviderProps {
  children: React.ReactNode;
  user?: UserProfile | null;
  isLoading?: boolean;
  /** Override `isAuthenticated`. Defaults to `!!user`. */
  isAuthenticated?: boolean;
  /** Override `isAdminUser`. Defaults to `false`. */
  isAdminUser?: boolean;
  /** Override resolved auth routes (e.g. `defaultCallback`, the private landing page). */
  routes?: Partial<{ auth: string; defaultCallback: string; defaultAuthCallback: string }>;
}

const noopAsync = async () => {};

export function buildMockUser(overrides: Partial<UserProfile> = {}): UserProfile {
  return {
    id: 1,
    email: 'jane.cooper@example.com',
    username: 'jane.cooper',
    first_name: 'Jane',
    last_name: 'Cooper',
    full_name: 'Jane Cooper',
    is_active: true,
    is_staff: false,
    is_superuser: false,
    date_joined: '2025-01-15T10:00:00Z',
    last_login: '2026-05-20T14:30:00Z',
    initials: 'JC',
    display_username: 'jane.cooper',
    company: null,
    phone: null,
    position: null,
    unanswered_messages_count: 0,
    avatar: null,
    ...overrides,
  } as UserProfile;
}

export const MockAuthProvider: React.FC<MockAuthProviderProps> = ({
  children,
  user: initialUser = buildMockUser(),
  isLoading = false,
  isAuthenticated,
  isAdminUser = false,
  routes,
}) => {
  const [user, setUser] = useState<UserProfile | null>(initialUser);

  const value = useMemo<AuthContextType>(() => ({
    user,
    isLoading,
    status: isLoading ? 'resolving' : (isAuthenticated ?? Boolean(user)) ? 'authenticated' : 'anonymous',
    isHydrated: true,
    isAuthenticated: isAuthenticated ?? Boolean(user),
    isAdminUser,
    routes: { auth: '/auth', defaultCallback: '/', defaultAuthCallback: '/auth', ...routes },

    loadCurrentProfile: noopAsync,
    checkAuthAndRedirect: noopAsync,

    getToken: () => 'mock-access-token',
    getRefreshToken: () => 'mock-refresh-token',

    getSavedEmail: () => user?.email ?? null,
    saveEmail: () => {},
    clearSavedEmail: () => {},

    requestOTP: async () => ({ success: true, message: 'mock' }),
    verifyOTP: async () => ({ success: true, message: 'mock', user: user ?? undefined }),
    login: async () => ({ success: true, message: 'mock', user: user ?? undefined }),
    refreshToken: async () => ({ success: true, message: 'mock' }),
    logout: () => {},

    saveRedirectUrl: () => {},
    getRedirectUrl: () => '/dashboard',
    clearRedirectUrl: () => {},
    hasRedirectUrl: () => false,

    // Edits update local state so the form reflects the change in
    // Storybook just like a real backend round-trip would.
    updateProfile: async (data) => {
      const next = { ...(user ?? buildMockUser()), ...data } as UserProfile;
      setUser(next);
      return next;
    },
    uploadAvatar: async () => user ?? buildMockUser(),
  }), [user, isLoading, isAuthenticated, isAdminUser, routes]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
