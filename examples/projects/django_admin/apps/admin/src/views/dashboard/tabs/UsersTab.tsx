/**
 * UsersTab Component
 *
 * User statistics and activity tab
 *
 * Features:
 * - User statistics chart
 * - Recent user activity
 * - User metrics
 */

'use client';

import React from 'react';
import type { UserStatistics, ActivityEntry } from '@/contexts/dashboard';

// Dashboard components
import { RecentActivityList } from '../components/RecentActivityList';

// Chart components
import { UserStatisticsChart } from '../components/UserStatisticsChart';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface UsersTabProps {
  userStatistics?: UserStatistics;
  isLoadingUserStatistics?: boolean;
  recentActivity?: ActivityEntry[];
  isLoadingRecentActivity?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────

export function UsersTab({
  userStatistics,
  isLoadingUserStatistics,
  recentActivity,
  isLoadingRecentActivity,
}: UsersTabProps) {
  return (
    <div className="space-y-6">
      {/* User Statistics Chart - Full Width */}
      <UserStatisticsChart
        statistics={userStatistics}
        isLoading={isLoadingUserStatistics}
      />

      {/* Recent User Activity */}
      <RecentActivityList
        activities={recentActivity}
        isLoading={isLoadingRecentActivity}
        maxItems={20}
      />
    </div>
  );
}
