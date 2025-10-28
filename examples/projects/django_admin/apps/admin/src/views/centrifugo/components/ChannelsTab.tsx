/**
 * Channels Tab Component
 *
 * Displays channel statistics
 */

'use client';

import React from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Button,
  Skeleton,
} from '@djangocfg/ui';
import { RefreshCw, History, Users } from 'lucide-react';
import { useCentrifugoMonitoringContext } from '@/contexts/centrifugo';
import { emitOpenChannelHistoryDialog, emitOpenChannelPresenceDialog } from '../events';

export const ChannelsTab: React.FC = () => {
  const { timeline, isLoadingTimeline, refreshTimeline } = useCentrifugoMonitoringContext();

  const channelList = timeline?.channels || [];

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Channel Statistics</CardTitle>
          <Button onClick={() => refreshTimeline()} variant="outline" size="sm" disabled={isLoadingTimeline}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {isLoadingTimeline ? (
          <Skeleton className="h-[400px] w-full" />
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Channel</TableHead>
                  <TableHead>Total Publishes</TableHead>
                  <TableHead>Success Rate</TableHead>
                  <TableHead>Avg Duration</TableHead>
                  <TableHead>Avg ACKs</TableHead>
                  <TableHead>Last Activity</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {channelList.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center py-8 text-muted-foreground">
                      No channel data available
                    </TableCell>
                  </TableRow>
                ) : (
                  channelList.map((channel: any) => {
                    const successRate = channel.total > 0
                      ? Math.round((channel.successful / channel.total) * 100)
                      : 0;

                    return (
                      <TableRow key={channel.channel}>
                        <TableCell className="font-medium">{channel.channel}</TableCell>
                        <TableCell>{channel.total.toLocaleString()}</TableCell>
                        <TableCell>{successRate}%</TableCell>
                        <TableCell>{Math.round(channel.avg_duration_ms)}ms</TableCell>
                        <TableCell>{channel.avg_acks?.toFixed(1) || '0.0'}</TableCell>
                        <TableCell>
                          {channel.last_activity_at
                            ? new Date(channel.last_activity_at).toLocaleString()
                            : 'N/A'}
                        </TableCell>
                        <TableCell className="text-right space-x-2">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => emitOpenChannelHistoryDialog({ channel: channel.channel })}
                          >
                            <History className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => emitOpenChannelPresenceDialog({ channel: channel.channel })}
                          >
                            <Users className="h-4 w-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    );
                  })
                )}
              </TableBody>
            </Table>

            <div className="mt-4 text-sm text-muted-foreground">
              Showing statistics for the last 24 hours
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};
