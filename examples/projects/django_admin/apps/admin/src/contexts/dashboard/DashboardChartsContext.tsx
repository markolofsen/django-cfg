/**
 * Dashboard Charts Context
 *
 * Manages dashboard charts and analytics data
 *
 * Features:
 * - User registration charts (7/30/90 days)
 * - User activity charts
 * - Activity tracker (GitHub-style 52 weeks)
 * - Recent users list
 *
 * Usage:
 * ```tsx
 * import { DashboardChartsProvider, useDashboardChartsContext } from '@/contexts/dashboard';
 *
 * function App() {
 *   return (
 *     <DashboardChartsProvider>
 *       <ChartsView />
 *     </DashboardChartsProvider>
 *   );
 * }
 *
 * function ChartsView() {
 *   const { registrationChart, activityTracker, recentUsers } = useDashboardChartsContext();
 *
 *   return (
 *     <div>
 *       <RegistrationChart data={registrationChart} />
 *       <ActivityTracker data={activityTracker} />
 *       <RecentUsersList users={recentUsers} />
 *     </div>
 *   );
 * }
 * ```
 */

'use client';

import React, { createContext, useContext, useState, type ReactNode } from 'react';
import { api } from '@/api/BaseClient';
import {
  useDashboardApiChartsRegistrationsRetrieve,
  useDashboardApiChartsActivityRetrieve,
  useDashboardApiChartsTrackerList,
  useDashboardApiChartsRecentUsersList,
} from '@/api/generated/cfg/_utils/hooks/cfg__dashboard__dashboard_charts';

import type { ChartData } from '@/api/generated/cfg/_utils/schemas/ChartData.schema';
import type { RecentUser } from '@/api/generated/cfg/_utils/schemas/RecentUser.schema';
import type { ActivityTrackerDay } from '@/api/generated/cfg/_utils/schemas/ActivityTrackerDay.schema';

// ─────────────────────────────────────────────────────────────────────────
// Context Type
// ─────────────────────────────────────────────────────────────────────────

export interface DashboardChartsContextValue {
  // User registration chart
  registrationChart?: ChartData;
  isLoadingRegistrationChart: boolean;
  registrationChartError: Error | undefined;
  registrationChartDays: number;
  setRegistrationChartDays: (days: number) => void;
  refreshRegistrationChart: () => Promise<void>;

  // User activity chart
  activityChart?: ChartData;
  isLoadingActivityChart: boolean;
  activityChartError: Error | undefined;
  activityChartDays: number;
  setActivityChartDays: (days: number) => void;
  refreshActivityChart: () => Promise<void>;

  // Activity tracker (GitHub-style)
  activityTracker?: ActivityTrackerDay[];
  isLoadingActivityTracker: boolean;
  activityTrackerError: Error | undefined;
  activityTrackerWeeks: number;
  setActivityTrackerWeeks: (weeks: number) => void;
  refreshActivityTracker: () => Promise<void>;

  // Recent users
  recentUsers?: RecentUser[];
  isLoadingRecentUsers: boolean;
  recentUsersError: Error | undefined;
  recentUsersLimit: number;
  setRecentUsersLimit: (limit: number) => void;
  refreshRecentUsers: () => Promise<void>;

  // Refresh all
  refreshAll: () => Promise<void>;
}

// ─────────────────────────────────────────────────────────────────────────
// Context
// ─────────────────────────────────────────────────────────────────────────

const DashboardChartsContext = createContext<DashboardChartsContextValue | undefined>(undefined);

// ─────────────────────────────────────────────────────────────────────────
// Provider
// ─────────────────────────────────────────────────────────────────────────

export function DashboardChartsProvider({ children }: { children: ReactNode }) {
  // State for configurable parameters
  const [registrationChartDays, setRegistrationChartDays] = useState(7);
  const [activityChartDays, setActivityChartDays] = useState(7);
  const [activityTrackerWeeks, setActivityTrackerWeeks] = useState(52);
  const [recentUsersLimit, setRecentUsersLimit] = useState(10);

  // User registration chart
  const {
    data: registrationChart,
    error: registrationChartError,
    isLoading: isLoadingRegistrationChart,
    mutate: mutateRegistrationChart,
  } = useDashboardApiChartsRegistrationsRetrieve({ days: registrationChartDays }, api);

  // User activity chart
  const {
    data: activityChart,
    error: activityChartError,
    isLoading: isLoadingActivityChart,
    mutate: mutateActivityChart,
  } = useDashboardApiChartsActivityRetrieve({ days: activityChartDays }, api);

  // Activity tracker
  const {
    data: activityTracker,
    error: activityTrackerError,
    isLoading: isLoadingActivityTracker,
    mutate: mutateActivityTracker,
  } = useDashboardApiChartsTrackerList({ weeks: activityTrackerWeeks }, api);

  // Recent users
  const {
    data: recentUsers,
    error: recentUsersError,
    isLoading: isLoadingRecentUsers,
    mutate: mutateRecentUsers,
  } = useDashboardApiChartsRecentUsersList({ limit: recentUsersLimit }, api);

  // Refresh functions
  const refreshRegistrationChart = async () => {
    await mutateRegistrationChart();
  };

  const refreshActivityChart = async () => {
    await mutateActivityChart();
  };

  const refreshActivityTracker = async () => {
    await mutateActivityTracker();
  };

  const refreshRecentUsers = async () => {
    await mutateRecentUsers();
  };

  const refreshAll = async () => {
    await Promise.all([
      mutateRegistrationChart(),
      mutateActivityChart(),
      mutateActivityTracker(),
      mutateRecentUsers(),
    ]);
  };

  const value: DashboardChartsContextValue = {
    registrationChart,
    isLoadingRegistrationChart,
    registrationChartError,
    registrationChartDays,
    setRegistrationChartDays,
    refreshRegistrationChart,

    activityChart,
    isLoadingActivityChart,
    activityChartError,
    activityChartDays,
    setActivityChartDays,
    refreshActivityChart,

    activityTracker,
    isLoadingActivityTracker,
    activityTrackerError,
    activityTrackerWeeks,
    setActivityTrackerWeeks,
    refreshActivityTracker,

    recentUsers,
    isLoadingRecentUsers,
    recentUsersError,
    recentUsersLimit,
    setRecentUsersLimit,
    refreshRecentUsers,

    refreshAll,
  };

  return (
    <DashboardChartsContext.Provider value={value}>
      {children}
    </DashboardChartsContext.Provider>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Hook
// ─────────────────────────────────────────────────────────────────────────

export function useDashboardChartsContext(): DashboardChartsContextValue {
  const context = useContext(DashboardChartsContext);
  if (!context) {
    throw new Error('useDashboardChartsContext must be used within DashboardChartsProvider');
  }
  return context;
}

// ─────────────────────────────────────────────────────────────────────────
// Re-export types
// ─────────────────────────────────────────────────────────────────────────

export type {
  ChartData,
  RecentUser,
  ActivityTrackerDay,
};
