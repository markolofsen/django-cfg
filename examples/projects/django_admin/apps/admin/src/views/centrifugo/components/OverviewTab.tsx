/**
 * Overview Tab Component
 *
 * Displays timeline charts and ACK statistics
 */

'use client';

import React, { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle, Skeleton } from '@djangocfg/ui';
import { TrendingUp, PieChart, CheckCircle2 } from 'lucide-react';
import { useCentrifugoMonitoringContext } from '@/contexts/centrifugo';

export const OverviewTab: React.FC = () => {
  const { overview, timeline, isLoadingOverview, isLoadingTimeline } = useCentrifugoMonitoringContext();

  const ackStats = useMemo(() => {
    if (!overview) {
      return { totalAcks: 0, avgAcks: '0.0', ackRate: 0 };
    }

    // Note: total_acks_received not in the current API schema
    // Using avg_acks_received instead for now
    const avgAcksReceived = overview.avg_acks_received || 0;
    const total = overview.total || 0;
    const totalAcks = Math.round(avgAcksReceived * total);
    const avgAcks = avgAcksReceived.toFixed(1);
    const ackRate = total > 0 ? Math.round((avgAcksReceived / total) * 100) : 0;

    return { totalAcks, avgAcks, ackRate };
  }, [overview]);

  return (
    <div className="space-y-6">
      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Publish Timeline Chart Placeholder */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5 text-purple-500" />
              Publish Timeline (24h)
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingTimeline ? (
              <Skeleton className="h-[200px] w-full" />
            ) : (
              <div className="h-[200px] flex items-center justify-center text-muted-foreground">
                Chart visualization placeholder
                <br />
                <span className="text-xs mt-2">
                  {timeline?.channels?.length || 0} channels available
                </span>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Success/Failure Breakdown Placeholder */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PieChart className="h-5 w-5 text-purple-500" />
              Success/Failure Breakdown
            </CardTitle>
          </CardHeader>
          <CardContent>
            {isLoadingOverview ? (
              <Skeleton className="h-[200px] w-full" />
            ) : (
              <div className="h-[200px] flex items-center justify-center">
                <div className="text-center">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <div className="text-3xl font-bold text-green-600">
                        {overview?.successful || 0}
                      </div>
                      <div className="text-sm text-muted-foreground">Success</div>
                    </div>
                    <div>
                      <div className="text-3xl font-bold text-red-600">
                        {(overview?.failed || 0) + (overview?.timeout || 0)}
                      </div>
                      <div className="text-sm text-muted-foreground">Failed</div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* ACK Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-purple-500" />
            ACK Statistics
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoadingOverview ? (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {[...Array(3)].map((_, i) => (
                <Skeleton key={i} className="h-20 w-full" />
              ))}
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Card>
                <CardContent className="p-4">
                  <div className="text-sm text-muted-foreground mb-1">Total ACKs Received</div>
                  <div className="text-2xl font-bold">{ackStats.totalAcks.toLocaleString()}</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="text-sm text-muted-foreground mb-1">Avg ACKs per Publish</div>
                  <div className="text-2xl font-bold">{ackStats.avgAcks}</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4">
                  <div className="text-sm text-muted-foreground mb-1">ACK Tracking Rate</div>
                  <div className="text-2xl font-bold">{ackStats.ackRate}%</div>
                </CardContent>
              </Card>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
