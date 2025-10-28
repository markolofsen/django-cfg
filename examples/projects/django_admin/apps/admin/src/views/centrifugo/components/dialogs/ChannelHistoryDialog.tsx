/**
 * Channel History Dialog
 *
 * Dialog for viewing channel message history
 */

'use client';

import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  Button,
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
  Skeleton,
  Badge,
  ScrollArea,
} from '@djangocfg/ui/components';
import { useEventListener, useToast } from '@djangocfg/ui/hooks';
import { History, RefreshCw } from 'lucide-react';
import { useCentrifugoAdminApiContext } from '@/contexts/centrifugo';
import { CENTRIFUGO_EVENTS, type ChannelHistoryDialogPayload } from '../../events';
import { APIError } from '@/api/BaseClient';

export const ChannelHistoryDialog: React.FC = () => {
  const [open, setOpen] = React.useState(false);
  const [channel, setChannel] = React.useState('');
  const [history, setHistory] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);

  const { getChannelHistory } = useCentrifugoAdminApiContext();
  const { toast } = useToast();

  // Listen for dialog open event
  useEventListener(
    CENTRIFUGO_EVENTS.OPEN_CHANNEL_HISTORY_DIALOG,
    async (event: { payload: ChannelHistoryDialogPayload }) => {
      setChannel(event.payload.channel);
      setOpen(true);
      await loadHistory(event.payload.channel);
    }
  );

  const loadHistory = async (channelName: string) => {
    setLoading(true);
    setHistory(null);
    try {
      const result = await getChannelHistory({ channel: channelName });
      setHistory(result);
    } catch (error) {
      let title = 'Failed to Load History';
      let description = 'Failed to load channel history';

      if (error instanceof APIError) {
        if (error.isPermissionError) {
          title = 'Permission Denied';
          description = error.errorMessage || 'You do not have permission to view channel history';
        } else if (error.isAuthError) {
          title = 'Authentication Required';
          description = 'Please log in to view channel history';
        } else if (error.isNotFoundError) {
          title = 'Channel Not Found';
          description = `Channel "${channelName}" not found or has no history`;
        } else if (error.isServerError) {
          title = 'Server Error';
          description = error.errorMessage || 'Internal server error occurred';
        } else {
          description = error.errorMessage;
        }
      } else if (error instanceof Error) {
        description = error.message;
      }

      toast({
        title,
        description,
        variant: 'destructive',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setOpen(false);
    setChannel('');
    setHistory(null);
  };

  const handleRefresh = () => {
    if (channel) {
      loadHistory(channel);
    }
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
      <DialogContent className="max-w-6xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <History className="h-5 w-5" />
            Channel History: {channel}
            {history?.publications && (
              <Badge variant="secondary">
                {history.publications.length} messages
              </Badge>
            )}
          </DialogTitle>
          <DialogDescription>
            View message history for this channel
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="h-[60vh] w-full">
          {loading ? (
            <div className="space-y-3">
              <Skeleton className="h-[100px] w-full" />
              <Skeleton className="h-[100px] w-full" />
              <Skeleton className="h-[100px] w-full" />
            </div>
          ) : history?.publications && history.publications.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[100px]">Offset</TableHead>
                  <TableHead>Data</TableHead>
                  <TableHead className="w-[200px]">Info</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {history.publications.map((pub: any, idx: number) => (
                  <TableRow key={idx}>
                    <TableCell className="font-mono text-xs align-top">
                      {pub.offset || 'N/A'}
                    </TableCell>
                    <TableCell className="align-top">
                      <pre className="text-xs bg-muted p-3 rounded-md overflow-x-auto max-w-2xl">
                        {JSON.stringify(pub.data, null, 2)}
                      </pre>
                    </TableCell>
                    <TableCell className="text-xs align-top">
                      {pub.info ? (
                        <div className="space-y-1">
                          <div className="flex items-center gap-1">
                            <span className="font-semibold">Client:</span>
                            <code className="text-xs bg-muted px-1 rounded">
                              {pub.info.client || 'N/A'}
                            </code>
                          </div>
                          <div className="flex items-center gap-1">
                            <span className="font-semibold">User:</span>
                            <code className="text-xs bg-muted px-1 rounded">
                              {pub.info.user || 'N/A'}
                            </code>
                          </div>
                        </div>
                      ) : (
                        <span className="text-muted-foreground">No info</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <History className="h-12 w-12 text-muted-foreground mb-3" />
              <p className="text-muted-foreground">
                No history available for this channel
              </p>
            </div>
          )}
        </ScrollArea>

        <DialogFooter>
          <Button
            variant="outline"
            onClick={handleRefresh}
            disabled={loading}
          >
            {loading ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Loading...
              </>
            ) : (
              <>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </>
            )}
          </Button>
          <Button variant="outline" onClick={handleClose}>
            Close
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
