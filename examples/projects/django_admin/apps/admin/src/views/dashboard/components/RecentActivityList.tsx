/**
 * RecentActivityList Component
 *
 * Displays recent user activity in a timeline format
 *
 * Features:
 * - Timeline-style activity log
 * - Color-coded icons for different action types
 * - User names and timestamps
 * - Resource information
 * - Empty state handling
 * - Scrollable list with max height
 */

'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@djangocfg/ui';
import { Avatar, AvatarFallback, Skeleton, Badge } from '@djangocfg/ui';
import { FileEdit, FilePlus, Trash2, Activity } from 'lucide-react';
import moment from 'moment';
import type { ActivityEntry } from '@/contexts/dashboard';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface RecentActivityListProps {
  activities?: ActivityEntry[];
  isLoading?: boolean;
  maxItems?: number;
}

// ─────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────

const getActionIcon = (action: string) => {
  const iconMap: Record<string, React.ReactNode> = {
    created: <FilePlus className="h-4 w-4" />,
    updated: <FileEdit className="h-4 w-4" />,
    deleted: <Trash2 className="h-4 w-4" />,
  };

  return iconMap[action.toLowerCase()] || <Activity className="h-4 w-4" />;
};

const formatTimestamp = (timestamp: string): string => {
  try {
    return moment(timestamp).fromNow();
  } catch {
    return timestamp;
  }
};

const getUserInitials = (username: string): string => {
  const parts = username.split(' ');
  if (parts.length >= 2) {
    return `${parts[0][0]}${parts[1][0]}`.toUpperCase();
  }
  return username.substring(0, 2).toUpperCase();
};

// ─────────────────────────────────────────────────────────────────────────
// Loading Skeleton
// ─────────────────────────────────────────────────────────────────────────

function ActivityItemSkeleton() {
  return (
    <div className="flex gap-4">
      <Skeleton className="h-10 w-10 rounded-full" />
      <div className="flex-1 space-y-2">
        <Skeleton className="h-4 w-3/4" />
        <Skeleton className="h-3 w-1/2" />
      </div>
    </div>
  );
}

function RecentActivitySkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-32 mb-2" />
        <Skeleton className="h-4 w-48" />
      </CardHeader>
      <CardContent className="space-y-4">
        {Array.from({ length: 5 }).map((_, i) => (
          <ActivityItemSkeleton key={i} />
        ))}
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────

export function RecentActivityList({
  activities,
  isLoading,
  maxItems = 10,
}: RecentActivityListProps) {
  // Loading state
  if (isLoading) {
    return <RecentActivitySkeleton />;
  }

  // FIXME: API returns single ActivityEntry object, but we expect array
  // Temporary workaround: treat single object as array with one item
  const activitiesArray = activities
    ? Array.isArray(activities)
      ? activities
      : [activities]
    : [];

  // Limit items
  const displayedActivities = activitiesArray.slice(0, maxItems);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activity</CardTitle>
        <CardDescription>Latest actions across the system</CardDescription>
      </CardHeader>
      <CardContent>
        {displayedActivities.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p className="text-sm">No recent activity</p>
          </div>
        ) : (
          <div className="space-y-6 max-h-[400px] overflow-y-auto pr-2">
            {displayedActivities.map((activity) => (
              <div key={activity.id} className="flex gap-4">
                {/* Avatar with icon */}
                <div className="relative">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="text-xs">
                      {getUserInitials(activity.user)}
                    </AvatarFallback>
                  </Avatar>
                  <div
                    className="absolute -bottom-1 -right-1 h-5 w-5 rounded-full border-2 border-background flex items-center justify-center"
                    style={{ backgroundColor: activity.color }}
                  >
                    <div className="text-white">
                      {getActionIcon(activity.action)}
                    </div>
                  </div>
                </div>

                {/* Activity details */}
                <div className="flex-1 space-y-1">
                  <div className="flex items-start justify-between gap-2">
                    <p className="text-sm">
                      <span className="font-medium">{activity.user}</span>
                      {' '}
                      <span className="text-muted-foreground">{activity.action}</span>
                      {' '}
                      <span className="font-medium">{activity.resource}</span>
                    </p>
                    <span className="text-xs text-muted-foreground whitespace-nowrap">
                      {formatTimestamp(activity.timestamp)}
                    </span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary" className="text-xs">
                      {activity.action}
                    </Badge>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
