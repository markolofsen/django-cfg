/**
 * Message Input Component
 * Input field for sending messages
 */

'use client';

import React, { useState } from 'react';
import { Button, Textarea, useToast } from '@djangocfg/ui';
import { Send } from 'lucide-react';
import { supportLogger } from '../../../utils/logger';
import { useSupportLayoutContext } from '../context';

export const MessageInput: React.FC = () => {
  const { selectedTicket, sendMessage } = useSupportLayoutContext();
  const { toast } = useToast();
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!message.trim() || !selectedTicket) return;

    setIsSending(true);
    try {
      await sendMessage(message.trim());
      setMessage('');
      toast({
        title: 'Success',
        description: 'Message sent successfully',
      });
    } catch (error) {
      supportLogger.error('Failed to send message:', error);
      toast({
        title: 'Error',
        description: 'Failed to send message',
        variant: 'destructive',
      });
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  if (!selectedTicket) {
    return null;
  }

  const canSendMessage = selectedTicket.status !== 'closed';

  return (
    <form onSubmit={handleSubmit} className="p-4 border-t bg-background/50 backdrop-blur-sm flex-shrink-0">
      <div className="flex gap-2">
        <Textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={
            canSendMessage
              ? 'Type your message... (Shift+Enter for new line)'
              : 'This ticket is closed'
          }
          className="min-h-[60px] max-h-[200px] transition-all duration-200 
                     focus:ring-2 focus:ring-primary/20"
          disabled={!canSendMessage || isSending}
        />
        <Button
          type="submit"
          size="icon"
          disabled={!message.trim() || !canSendMessage || isSending}
          className="shrink-0 transition-all duration-200 
                     hover:scale-110 active:scale-95 disabled:scale-100"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>
      {!canSendMessage && (
        <p className="text-xs text-muted-foreground mt-2 animate-in fade-in slide-in-from-top-1 duration-200">
          This ticket is closed. You cannot send new messages.
        </p>
      )}
    </form>
  );
};

