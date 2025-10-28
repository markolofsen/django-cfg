/**
 * Dashboard Statistics Context
 *
 * Manages dashboard statistics data with SWR hooks
 *
 * Features:
 * - Statistics cards
 * - User statistics
 * - Application statistics
 *
 * Usage:
 * ```tsx
 * import { DashboardStatisticsProvider, useDashboardStatisticsContext } from '@/contexts/dashboard';
 *
 * function App() {
 *   return (
 *     <DashboardStatisticsProvider>
 *       <StatsView />
 *     </DashboardStatisticsProvider>
 *   );
 * }
 *
 * function StatsView() {
 *   const { cards, isLoadingCards, refreshCards } = useDashboardStatisticsContext();
 *
 *   return <StatsGrid cards={cards} />;
 * }
 * ```
 */

'use client';

import React, { createContext, useContext, type ReactNode } from 'react';
import { api } from '@/api/BaseClient';
import {
  useDashboardApiStatisticsCardsList,
  useDashboardApiStatisticsUsersRetrieve,
  useDashboardApiStatisticsAppsList,
} from '@/api/generated/cfg/_utils/hooks/cfg__dashboard__dashboard_statistics';

// Import types from schemas
import type { StatCard } from '@/api/generated/cfg/_utils/schemas/StatCard.schema';
import type { UserStatistics } from '@/api/generated/cfg/_utils/schemas/UserStatistics.schema';
import type { AppStatistics } from '@/api/generated/cfg/_utils/schemas/AppStatistics.schema';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface DashboardStatisticsContextValue {
  // Statistics cards
  cards?: StatCard[];
  isLoadingCards: boolean;
  cardsError: Error | undefined;
  refreshCards: () => Promise<void>;

  // User statistics
  users?: UserStatistics;
  isLoadingUsers: boolean;
  usersError: Error | undefined;
  refreshUsers: () => Promise<void>;

  // Application statistics
  apps?: AppStatistics[];
  isLoadingApps: boolean;
  appsError: Error | undefined;
  refreshApps: () => Promise<void>;

  // Refresh all
  refreshAll: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const DashboardStatisticsContext = createContext<DashboardStatisticsContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function DashboardStatisticsProvider({ children }: { children: ReactNode }) {
  // Statistics cards
  const {
    data: cards,
    error: cardsError,
    isLoading: isLoadingCards,
    mutate: mutateCards,
  } = useDashboardApiStatisticsCardsList(api);

  // User statistics
  const {
    data: users,
    error: usersError,
    isLoading: isLoadingUsers,
    mutate: mutateUsers,
  } = useDashboardApiStatisticsUsersRetrieve(api);

  // Application statistics
  const {
    data: apps,
    error: appsError,
    isLoading: isLoadingApps,
    mutate: mutateApps,
  } = useDashboardApiStatisticsAppsList(api);

  // Refresh functions
  const refreshCards = async () => {
    await mutateCards();
  };

  const refreshUsers = async () => {
    await mutateUsers();
  };

  const refreshApps = async () => {
    await mutateApps();
  };

  const refreshAll = async () => {
    await Promise.all([
      mutateCards(),
      mutateUsers(),
      mutateApps(),
    ]);
  };

  const value: DashboardStatisticsContextValue = {
    cards,
    isLoadingCards,
    cardsError,
    refreshCards,

    users,
    isLoadingUsers,
    usersError,
    refreshUsers,

    apps,
    isLoadingApps,
    appsError,
    refreshApps,

    refreshAll,
  };

  return (
    <DashboardStatisticsContext.Provider value={value}>
      {children}
    </DashboardStatisticsContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useDashboardStatisticsContext(): DashboardStatisticsContextValue {
  const context = useContext(DashboardStatisticsContext);
  if (!context) {
    throw new Error('useDashboardStatisticsContext must be used within DashboardStatisticsProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types
// ─────────────────────────────────────────────────────────────────────────

export type {
  StatCard,
  UserStatistics,
  AppStatistics,
};
