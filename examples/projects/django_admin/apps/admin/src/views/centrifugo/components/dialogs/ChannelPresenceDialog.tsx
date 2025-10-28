/**
 * Channel Presence Dialog
 *
 * Dialog for viewing channel presence (subscribed clients)
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
import { Users, RefreshCw } from 'lucide-react';
import { useCentrifugoAdminApiContext } from '@/contexts/centrifugo';
import { CENTRIFUGO_EVENTS, type ChannelPresenceDialogPayload } from '../../events';
import { APIError } from '@/api/BaseClient';

export const ChannelPresenceDialog: React.FC = () => {
  const [open, setOpen] = React.useState(false);
  const [channel, setChannel] = React.useState('');
  const [presence, setPresence] = React.useState<any>(null);
  const [loading, setLoading] = React.useState(false);

  const { getPresence } = useCentrifugoAdminApiContext();
  const { toast } = useToast();

  // Listen for dialog open event
  useEventListener(
    CENTRIFUGO_EVENTS.OPEN_CHANNEL_PRESENCE_DIALOG,
    async (event: { payload: ChannelPresenceDialogPayload }) => {
      setChannel(event.payload.channel);
      setOpen(true);
      await loadPresence(event.payload.channel);
    }
  );

  const loadPresence = async (channelName: string) => {
    setLoading(true);
    setPresence(null);
    try {
      const result = await getPresence({ channel: channelName });
      setPresence(result);
    } catch (error) {
      let title = 'Failed to Load Presence';
      let description = 'Failed to load channel presence';

      if (error instanceof APIError) {
        if (error.isPermissionError) {
          title = 'Permission Denied';
          description = error.errorMessage || 'You do not have permission to view channel presence';
        } else if (error.isAuthError) {
          title = 'Authentication Required';
          description = 'Please log in to view channel presence';
        } else if (error.isNotFoundError) {
          title = 'Channel Not Found';
          description = `Channel "${channelName}" not found`;
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
    setPresence(null);
  };

  const handleRefresh = () => {
    if (channel) {
      loadPresence(channel);
    }
  };

  const clientCount = presence?.presence ? Object.keys(presence.presence).length : 0;

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
      <DialogContent className="max-w-5xl max-h-[90vh]">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Channel Presence: {channel}
            {presence && (
              <Badge variant="secondary">
                {clientCount} {clientCount === 1 ? 'client' : 'clients'}
              </Badge>
            )}
          </DialogTitle>
          <DialogDescription>
            View currently subscribed clients for this channel
          </DialogDescription>
        </DialogHeader>

        <ScrollArea className="h-[60vh] w-full">
          {loading ? (
            <div className="space-y-3">
              <Skeleton className="h-[80px] w-full" />
              <Skeleton className="h-[80px] w-full" />
              <Skeleton className="h-[80px] w-full" />
            </div>
          ) : presence?.presence && Object.keys(presence.presence).length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[250px]">Client ID</TableHead>
                  <TableHead className="w-[150px]">User</TableHead>
                  <TableHead>Connection Info</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {Object.entries(presence.presence).map(([clientId, info]: [string, any]) => (
                  <TableRow key={clientId}>
                    <TableCell className="font-mono text-xs align-top">
                      <code className="text-xs bg-muted px-2 py-1 rounded">
                        {clientId}
                      </code>
                    </TableCell>
                    <TableCell className="align-top">
                      <Badge variant="outline">
                        {info.user || 'Anonymous'}
                      </Badge>
                    </TableCell>
                    <TableCell className="text-xs align-top">
                      {info.conn_info ? (
                        <pre className="text-xs bg-muted p-3 rounded-md overflow-x-auto max-w-xl">
                          {JSON.stringify(info.conn_info, null, 2)}
                        </pre>
                      ) : (
                        <span className="text-muted-foreground">No connection info</span>
                      )}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <Users className="h-12 w-12 text-muted-foreground mb-3" />
              <p className="text-muted-foreground">
                No clients currently subscribed to this channel
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
