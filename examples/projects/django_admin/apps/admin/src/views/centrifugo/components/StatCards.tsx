/**
 * Statistics Cards Component
 *
 * Displays overview statistics in card format
 */

'use client';

import React, { useMemo } from 'react';
import { Card, CardContent, Skeleton } from '@djangocfg/ui';
import { Send, CheckCircle, Clock, XCircle } from 'lucide-react';
import { useCentrifugoMonitoringContext } from '@/contexts/centrifugo';

export const StatCards: React.FC = () => {
  const { overview, isLoadingOverview } = useCentrifugoMonitoringContext();

  const stats = useMemo(() => {
    if (!overview) {
      return {
        total: 0,
        successful: 0,
        failed: 0,
        timeout: 0,
        successRate: 0,
        avgDuration: 0,
      };
    }

    const { total, successful, failed, timeout, success_rate, avg_duration_ms } = overview;
    const successRate = Math.round(success_rate || 0);
    const avgDuration = avg_duration_ms || 0;

    return {
      total,
      successful,
      failed: failed + timeout,
      timeout,
      successRate,
      avgDuration: Math.round(avgDuration),
    };
  }, [overview]);

  // Loading state
  if (isLoadingOverview) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <Skeleton className="h-20 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {/* Total Publishes */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <Send className="h-8 w-8 text-purple-500" />
            <span className="text-xs text-muted-foreground">Today</span>
          </div>
          <h3 className="text-2xl font-bold mb-1">{stats.total.toLocaleString()}</h3>
          <p className="text-sm text-muted-foreground">Total Publishes</p>
        </CardContent>
      </Card>

      {/* Success Rate */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <CheckCircle className="h-8 w-8 text-green-500" />
            <span className="text-xs text-muted-foreground">Rate</span>
          </div>
          <h3 className="text-2xl font-bold mb-1">
            {stats.successRate}
            <span className="text-lg text-muted-foreground">%</span>
          </h3>
          <p className="text-sm text-muted-foreground">Success Rate</p>
        </CardContent>
      </Card>

      {/* Average Duration */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <Clock className="h-8 w-8 text-yellow-500" />
            <span className="text-xs text-muted-foreground">Average</span>
          </div>
          <h3 className="text-2xl font-bold mb-1">
            {stats.avgDuration}
            <span className="text-lg text-muted-foreground">ms</span>
          </h3>
          <p className="text-sm text-muted-foreground">Avg Duration</p>
        </CardContent>
      </Card>

      {/* Failed/Timeout */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between mb-4">
            <XCircle className="h-8 w-8 text-red-500" />
            <span className="text-xs text-muted-foreground">Issues</span>
          </div>
          <h3 className="text-2xl font-bold mb-1">{stats.failed.toLocaleString()}</h3>
          <p className="text-sm text-muted-foreground">Failed/Timeout</p>
        </CardContent>
      </Card>
    </div>
  );
};
