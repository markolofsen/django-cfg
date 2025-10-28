/**
 * Recent Publishes Tab Component
 *
 * Displays recent publishes with filtering and pagination
 */

'use client';

import React, { useState, useMemo } from 'react';
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
  Badge,
  Button,
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
  Skeleton,
} from '@djangocfg/ui';
import { RefreshCw } from 'lucide-react';
import { useCentrifugoMonitoringContext } from '@/contexts/centrifugo';

export const PublishesTab: React.FC = () => {
  const { publishes, isLoadingPublishes, refreshPublishes } = useCentrifugoMonitoringContext();
  const [channelFilter, setChannelFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [offset, setOffset] = useState(0);
  const pageSize = 50;

  const uniqueChannels = useMemo(() => {
    if (!publishes?.publishes) return [];
    const channels = new Set(publishes.publishes.map((p: any) => p.channel));
    return Array.from(channels);
  }, [publishes]);

  const handleRefresh = () => {
    refreshPublishes({
      channel: channelFilter !== 'all' ? channelFilter : undefined,
      status: statusFilter !== 'all' ? statusFilter : undefined,
      offset,
      count: pageSize,
    });
  };

  const handlePrevPage = () => {
    const newOffset = Math.max(0, offset - pageSize);
    setOffset(newOffset);
    refreshPublishes({
      channel: channelFilter !== 'all' ? channelFilter : undefined,
      status: statusFilter !== 'all' ? statusFilter : undefined,
      offset: newOffset,
      count: pageSize,
    });
  };

  const handleNextPage = () => {
    const newOffset = offset + pageSize;
    setOffset(newOffset);
    refreshPublishes({
      channel: channelFilter !== 'all' ? channelFilter : undefined,
      status: statusFilter !== 'all' ? statusFilter : undefined,
      offset: newOffset,
      count: pageSize,
    });
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'success':
        return <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">Success</Badge>;
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>;
      case 'timeout':
        return <Badge variant="secondary">Timeout</Badge>;
      default:
        return <Badge>{status}</Badge>;
    }
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Recent Publishes</CardTitle>
          <Button onClick={handleRefresh} variant="outline" size="sm" disabled={isLoadingPublishes}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {/* Filters */}
        <div className="flex flex-wrap gap-4 mb-4">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium mb-2">Filter by Channel</label>
            <Select value={channelFilter} onValueChange={setChannelFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All Channels" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Channels</SelectItem>
                {uniqueChannels.map((channel: any) => (
                  <SelectItem key={channel} value={channel}>
                    {channel}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium mb-2">Filter by Status</label>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger>
                <SelectValue placeholder="All Statuses" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Statuses</SelectItem>
                <SelectItem value="success">Success</SelectItem>
                <SelectItem value="failed">Failed</SelectItem>
                <SelectItem value="timeout">Timeout</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex items-end">
            <Button onClick={handleRefresh}>Apply Filters</Button>
          </div>
        </div>

        {/* Table */}
        {isLoadingPublishes ? (
          <Skeleton className="h-[400px] w-full" />
        ) : (
          <>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Timestamp</TableHead>
                  <TableHead>Message ID</TableHead>
                  <TableHead>Channel</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>ACKs</TableHead>
                  <TableHead>Duration</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {publishes?.publishes?.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center py-8 text-muted-foreground">
                      No publishes found
                    </TableCell>
                  </TableRow>
                ) : (
                  publishes?.publishes?.map((publish: any) => (
                    <TableRow key={publish.id}>
                      <TableCell>
                        {new Date(publish.created_at).toLocaleString()}
                      </TableCell>
                      <TableCell className="font-mono text-xs">
                        {publish.message_id?.substring(0, 8)}...
                      </TableCell>
                      <TableCell>{publish.channel}</TableCell>
                      <TableCell>{getStatusBadge(publish.status)}</TableCell>
                      <TableCell>{publish.acks_received || 0}</TableCell>
                      <TableCell>{publish.duration_ms}ms</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>

            {/* Pagination */}
            <div className="flex justify-between items-center mt-4">
              <div className="text-sm text-muted-foreground">
                Showing {publishes?.count || 0} of {publishes?.total_available || 0} publishes
              </div>
              <div className="flex gap-2">
                <Button onClick={handlePrevPage} variant="outline" size="sm" disabled={offset === 0}>
                  Previous
                </Button>
                <Button
                  onClick={handleNextPage}
                  variant="outline"
                  size="sm"
                  disabled={!publishes?.has_more}
                >
                  Next
                </Button>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
};
