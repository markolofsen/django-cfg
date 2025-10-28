/**
 * Publish Test Dialog
 *
 * Dialog for testing message publishing to Centrifugo channels
 */

'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  Button,
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
  Input,
  Switch,
  Textarea,
} from '@djangocfg/ui';
import { useEventListener, useToast } from '@djangocfg/ui';
import { Send, RefreshCw } from 'lucide-react';
import { CENTRIFUGO_EVENTS, type PublishTestDialogPayload } from '../../events';
import { useCentrifugoTestingContext, useCentrifugoMonitoringContext } from '@/contexts/centrifugo';
import { PublishTestRequestRequestSchema } from '@/api/generated/cfg/_utils/schemas/PublishTestRequestRequest.schema';
import { APIError } from '@/api/BaseClient';
import { z } from 'zod';

// Extended schema for form with message as string
const PublishTestFormSchema = z.object({
  channel: z.string().min(1, 'Channel is required'),
  message: z.string().min(1, 'Message is required'),
  wait_for_ack: z.boolean().optional(),
  ack_timeout: z.number().int().min(1).max(60).optional(),
});

type PublishTestFormData = z.infer<typeof PublishTestFormSchema>;

export const PublishTestDialog: React.FC = () => {
  const [open, setOpen] = React.useState(false);
  const { publishTest } = useCentrifugoTestingContext();
  const { refreshPublishes, refreshOverview } = useCentrifugoMonitoringContext();
  const { toast } = useToast();

  const form = useForm<PublishTestFormData>({
    resolver: zodResolver(PublishTestFormSchema),
    defaultValues: {
      channel: '',
      message: '{"type": "test", "content": "Hello from admin"}',
      wait_for_ack: false,
      ack_timeout: 5,
    },
  });

  // Listen for dialog open event
  useEventListener(
    CENTRIFUGO_EVENTS.OPEN_PUBLISH_TEST_DIALOG,
    (event: { payload?: PublishTestDialogPayload }) => {
      if (event.payload?.channel) {
        form.setValue('channel', event.payload.channel);
      }
      if (event.payload?.message) {
        form.setValue('message', JSON.stringify(event.payload.message, null, 2));
      }
      setOpen(true);
    }
  );

  const handleClose = () => {
    setOpen(false);
    form.reset();
  };

  const handleSubmit = async (data: PublishTestFormData) => {
    try {
      // Parse message as JSON or wrap as object
      let parsedMessage: Record<string, any> = { message: data.message };
      try {
        const parsed = JSON.parse(data.message);
        parsedMessage = typeof parsed === 'object' && parsed !== null ? parsed : { message: parsed };
      } catch {
        // Use wrapped string if not valid JSON
      }

      await publishTest({
        channel: data.channel,
        data: parsedMessage,
        wait_for_ack: data.wait_for_ack,
        ack_timeout: data.ack_timeout,
      });

      toast({
        title: 'Message Published',
        description: `Successfully published to channel "${data.channel}"`,
      });

      // Refresh data
      await refreshPublishes();
      await refreshOverview();

      handleClose();
    } catch (error) {
      let title = 'Publishing Failed';
      let description = 'Failed to publish message';

      if (error instanceof APIError) {
        // Handle specific HTTP errors
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
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>Publish Test Message</DialogTitle>
          <DialogDescription>
            Publish a test message to a Centrifugo channel via the wrapper
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="channel"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Channel *</FormLabel>
                  <FormControl>
                    <Input placeholder="test:channel" {...field} />
                  </FormControl>
                  <FormDescription>
                    Target channel name (e.g., "test:channel")
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="message"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Message *</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder='{"type": "test", "content": "Hello"}'
                      rows={6}
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    JSON object or string (will be auto-wrapped if needed)
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="grid grid-cols-2 gap-4">
              <FormField
                control={form.control}
                name="wait_for_ack"
                render={({ field }) => (
                  <FormItem className="flex flex-row items-center justify-between rounded-lg border p-3">
                    <div className="space-y-0.5">
                      <FormLabel>Wait for ACK</FormLabel>
                      <FormDescription className="text-xs">
                        Track client acknowledgments
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

              <FormField
                control={form.control}
                name="ack_timeout"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>ACK Timeout (seconds)</FormLabel>
                    <FormControl>
                      <Input
                        type="number"
                        min="1"
                        max="60"
                        {...field}
                        onChange={(e) => field.onChange(parseInt(e.target.value) || 5)}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />
            </div>

            <DialogFooter>
              <Button type="button" variant="outline" onClick={handleClose}>
                Cancel
              </Button>
              <Button type="submit" disabled={form.formState.isSubmitting}>
                {form.formState.isSubmitting ? (
                  <>
                    <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                    Publishing...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4 mr-2" />
                    Publish
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
