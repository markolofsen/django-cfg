/**
 * Send ACK Dialog
 *
 * Dialog for manually sending acknowledgments
 */

'use client';

import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
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
} from '@djangocfg/ui/components';
import { useEventListener, useToast } from '@djangocfg/ui/hooks';
import { CheckCircle, RefreshCw } from 'lucide-react';
import { useCentrifugoTestingContext } from '@/contexts/centrifugo';
import { CENTRIFUGO_EVENTS, type SendAckDialogPayload } from '../../events';
import { ManualAckRequestRequestSchema } from '@/api/generated/cfg/_utils/schemas/ManualAckRequestRequest.schema';
import type { ManualAckRequestRequest } from '@/api/generated/cfg/_utils/schemas/ManualAckRequestRequest.schema';
import { APIError } from '@/api/BaseClient';

type SendAckFormData = ManualAckRequestRequest;

export const SendAckDialog: React.FC = () => {
  const [open, setOpen] = React.useState(false);
  const { sendAck } = useCentrifugoTestingContext();
  const { toast } = useToast();

  const form = useForm<SendAckFormData>({
    resolver: zodResolver(ManualAckRequestRequestSchema),
    defaultValues: {
      message_id: '',
      client_id: '',
    },
  });

  // Listen for dialog open event
  useEventListener(
    CENTRIFUGO_EVENTS.OPEN_SEND_ACK_DIALOG,
    (event: { payload?: SendAckDialogPayload }) => {
      if (event.payload?.messageId) {
        form.setValue('message_id', event.payload.messageId);
      }
      if (event.payload?.channel) {
        form.setValue('client_id', event.payload.channel);
      }
      setOpen(true);
    }
  );

  const handleClose = () => {
    setOpen(false);
    form.reset();
  };

  const handleSubmit = async (data: SendAckFormData) => {
    try {
      await sendAck({
        message_id: data.message_id.trim(),
        client_id: data.client_id.trim(),
      });

      toast({
        title: 'Success',
        description: `ACK sent for message ${data.message_id}`,
      });

      handleClose();
    } catch (error) {
      let title = 'Failed to Send ACK';
      let description = 'Failed to send acknowledgment';

      if (error instanceof APIError) {
        if (error.isPermissionError) {
          title = 'Permission Denied';
          description = error.errorMessage || 'You do not have permission to send ACKs';
        } else if (error.isAuthError) {
          title = 'Authentication Required';
          description = 'Please log in to send ACKs';
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
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Send Manual ACK</DialogTitle>
          <DialogDescription>Manually send acknowledgment for a specific message</DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="message_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Message ID *</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Enter message ID"
                      className="font-mono"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    The unique identifier of the message to acknowledge
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="client_id"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Client ID *</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="e.g., client-123"
                      className="font-mono"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    The client ID that should acknowledge the message
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

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
                    Sending...
                  </>
                ) : (
                  <>
                    <CheckCircle className="h-4 w-4 mr-2" />
                    Send ACK
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
