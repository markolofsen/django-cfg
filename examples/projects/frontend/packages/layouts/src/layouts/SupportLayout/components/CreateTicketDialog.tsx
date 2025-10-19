/**
 * Create Ticket Dialog
 * Dialog for creating new support tickets
 */

'use client';

import React from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogDescription,
  Button,
  Form,
  FormField,
  FormItem,
  FormLabel,
  FormControl,
  FormMessage,
  Input,
  Textarea,
} from '@djangocfg/ui';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Loader2 } from 'lucide-react';
import { supportLogger } from '../../../utils/logger';
import { useSupportLayoutContext } from '../context';
import { useToast } from '@djangocfg/ui';
import type { TicketFormData } from '../types';

const createTicketSchema = z.object({
  subject: z.string().min(1, 'Subject is required').max(200, 'Subject too long'),
  message: z.string().min(1, 'Message is required').max(5000, 'Message too long'),
});

export const CreateTicketDialog: React.FC = () => {
  const { uiState, createTicket, closeCreateDialog } = useSupportLayoutContext();
  const { toast } = useToast();
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const form = useForm<TicketFormData>({
    resolver: zodResolver(createTicketSchema),
    defaultValues: {
      subject: '',
      message: '',
    },
  });

  const onSubmit = async (data: TicketFormData) => {
    setIsSubmitting(true);
    try {
      await createTicket(data);
      form.reset();
      toast({
        title: 'Success',
        description: 'Support ticket created successfully',
      });
    } catch (error) {
      supportLogger.error('Failed to create ticket:', error);
      toast({
        title: 'Error',
        description: 'Failed to create ticket. Please try again.',
        variant: 'destructive',
      });
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleClose = () => {
    form.reset();
    closeCreateDialog();
  };

  return (
    <Dialog open={uiState.isCreateDialogOpen} onOpenChange={(open) => !open && handleClose()}>
      <DialogContent className="sm:max-w-[600px] animate-in fade-in slide-in-from-bottom-4 duration-300">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Plus className="h-5 w-5" />
            Create Support Ticket
          </DialogTitle>
          <DialogDescription>
            Describe your issue and we'll help you resolve it as quickly as possible.
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="subject"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Subject</FormLabel>
                  <FormControl>
                    <Input placeholder="Brief description of your issue..." {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="message"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Message</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Describe your issue in detail. Include any error messages, steps to reproduce, or relevant information..."
                      className="min-h-[120px]"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <div className="flex justify-end gap-3 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={handleClose}
                disabled={isSubmitting}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isSubmitting}>
                {isSubmitting ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Creating...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4 mr-2" />
                    Create Ticket
                  </>
                )}
              </Button>
            </div>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
};

