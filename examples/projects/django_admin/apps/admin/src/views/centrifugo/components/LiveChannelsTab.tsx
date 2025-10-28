/**
 * Live Channels Tab Component
 *
 * Displays live channels from Centrifugo server
 */

'use client';

import React, { useState } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  Button,
  Input,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Badge,
} from '@djangocfg/ui';
import { RefreshCw, Search } from 'lucide-react';
import { useCentrifugoAdminApiContext } from '@/contexts/centrifugo';

export const LiveChannelsTab: React.FC = () => {
  const { listChannels } = useCentrifugoAdminApiContext();
  const [channels, setChannels] = useState<any>(null);
  const [pattern, setPattern] = useState('');
  const [loading, setLoading] = useState(false);

  const handleLoadChannels = async () => {
    setLoading(true);
    try {
      const data = await listChannels(pattern ? { pattern } : undefined);
      setChannels(data);
    } catch (error) {
      console.error('Failed to load channels:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Live Channels</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* Search and Load */}
          <div className="flex gap-2">
            <Input
              placeholder="Channel pattern (e.g., user:*)"
              value={pattern}
              onChange={(e) => setPattern(e.target.value)}
              className="flex-1"
            />
            <Button onClick={handleLoadChannels} disabled={loading}>
              <Search className="h-4 w-4 mr-2" />
              Load Channels
            </Button>
          </div>

          {/* Results */}
          {channels && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <div className="text-sm text-muted-foreground">
                  Found {channels.channels?.length || 0} active channels
                </div>
                <Button onClick={handleLoadChannels} variant="outline" size="sm" disabled={loading}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  Refresh
                </Button>
              </div>

              {channels.channels && channels.channels.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Channel</TableHead>
                      <TableHead>Status</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {channels.channels.map((channel: string) => (
                      <TableRow key={channel}>
                        <TableCell className="font-medium">{channel}</TableCell>
                        <TableCell>
                          <Badge variant="default" className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                            Active
                          </Badge>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  No active channels found
                </div>
              )}
            </div>
          )}

          {!channels && (
            <div className="text-center py-8 text-muted-foreground">
              Click "Load Channels" to view active channels
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  );
};
