/**
 * Publish With Logging Dialog
 *
 * Dialog for publishing messages with database logging
 */

'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  Button,
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Input,
  Textarea,
  Switch,
} from '@djangocfg/ui/components';
import { useEventListener, useToast } from '@djangocfg/ui/hooks';
import { Database, RefreshCw } from 'lucide-react';
import { useCentrifugoTestingContext, useCentrifugoMonitoringContext } from '@/contexts/centrifugo';
import { CENTRIFUGO_EVENTS, type PublishTestDialogPayload, emitRefreshPublishes } from '../../events';
import { APIError } from '@/api/BaseClient';

// Extended schema with JSON parsing support
const PublishWithLoggingFormSchema = z.object({
  channel: z.string().min(1, 'Channel is required'),
  data: z.string().min(1, 'Message data is required'),
  wait_for_ack: z.boolean().optional(),
  ack_timeout: z.number().int().min(1).max(60).optional(),
});

type PublishWithLoggingFormData = z.infer<typeof PublishWithLoggingFormSchema>;

export const PublishWithLoggingDialog: React.FC = () => {
  const [open, setOpen] = React.useState(false);
  const { publishWithLogging } = useCentrifugoTestingContext();
  const { refreshPublishes, refreshOverview } = useCentrifugoMonitoringContext();
  const { toast } = useToast();

  const form = useForm<PublishWithLoggingFormData>({
    resolver: zodResolver(PublishWithLoggingFormSchema),
    defaultValues: {
      channel: '',
      data: '{}',
      wait_for_ack: true,
      ack_timeout: 5,
    },
  });

  // Listen for dialog open event
  useEventListener(
    CENTRIFUGO_EVENTS.OPEN_PUBLISH_WITH_LOGGING_DIALOG,
    (event: { payload?: PublishTestDialogPayload }) => {
      if (event.payload?.channel) {
        form.setValue('channel', event.payload.channel);
      }
      if (event.payload?.message) {
        form.setValue('data', JSON.stringify(event.payload.message, null, 2));
      }
      setOpen(true);
    }
  );

  const handleClose = () => {
    setOpen(false);
    form.reset();
  };

  const handleSubmit = async (data: PublishWithLoggingFormData) => {
    try {
      // Parse JSON data
      let parsedData: Record<string, any> = {};
      try {
        const parsed = JSON.parse(data.data);
        parsedData = typeof parsed === 'object' && parsed !== null ? parsed : { message: parsed };
      } catch (error) {
        // If JSON is invalid, wrap the string
        parsedData = { message: data.data };
      }

      await publishWithLogging({
        channel: data.channel.trim(),
        data: parsedData,
        wait_for_ack: data.wait_for_ack,
        ack_timeout: data.ack_timeout,
      });

      toast({
        title: 'Success',
        description: `Message published to ${data.channel} and saved to database`,
      });

      // Refresh publishes list
      emitRefreshPublishes();
      await refreshPublishes();
      await refreshOverview();

      handleClose();
    } catch (error) {
      let title = 'Publishing Failed';
      let description = 'Failed to publish message';

      if (error instanceof APIError) {
        if (error.isPermissionError) {
          title = 'Permission Denied';
          description = error.errorMessage || 'You do not have permission to publish messages';
        } else if (error.isAuthError) {
          title = 'Authentication Required';
          description = 'Please log in to publish messages';
        } else if (error.isValidationError) {
          title = 'Validation Error';
          description = error.errorMessage;
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
    }
  };

  return (
    <Dialog open={open} onOpenChange={(isOpen) => !isOpen && handleClose()}>
      <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>Publish with Database Logging</DialogTitle>
          <DialogDescription>Publish a message and save it to the database for tracking</DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            {/* Channel */}
            <FormField
              control={form.control}
              name="channel"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Channel *</FormLabel>
                  <FormControl>
                    <Input placeholder="e.g., user:123" {...field} />
                  </FormControl>
                  <FormDescription>
                    The channel to publish the message to
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Message Data */}
            <FormField
              control={form.control}
              name="data"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Message Data (JSON)</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder='{"type": "notification", "message": "Test"}'
                      rows={8}
                      className="font-mono text-sm"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    Enter JSON data or plain text (will be auto-wrapped)
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* ACK Options */}
            <div className="space-y-4">
              <h3 className="text-sm font-medium">ACK Options</h3>

              <FormField
                control={form.control}
                name="wait_for_ack"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                    <div className="space-y-0.5">
                      <FormLabel>Wait for ACK</FormLabel>
                      <FormDescription>
                        Track acknowledgment responses from subscribers
                      </FormDescription>
                    </div>
                    <FormControl>
                      <Switch
                        checked={field.value}
                        onCheckedChange={field.onChange}
                      />
                    </FormControl>
                  </FormItem>
                )}
              />

              {form.watch('wait_for_ack') && (
                <FormField
                  control={form.control}
                  name="ack_timeout"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>ACK Timeout (seconds)</FormLabel>
                      <FormControl>
                        <Input
                          type="number"
                          min={1}
                          max={60}
                          {...field}
                          onChange={(e) => field.onChange(parseInt(e.target.value) || 5)}
                        />
                      </FormControl>
                      <FormDescription>
                        Maximum time to wait for acknowledgments (1-60 seconds)
                      </FormDescription>
                      <FormMessage />
                    </FormItem>
                  )}
                />
              )}
            </div>

            <DialogFooter>
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                disabled={form.formState.isSubmitting}
              >
                {form.formState.isSubmitting ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Publishing...
                  </>
                ) : (
                  <>
                    <Database className="h-4 w-4 mr-2" />
                    Publish & Log
                  </>
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};
