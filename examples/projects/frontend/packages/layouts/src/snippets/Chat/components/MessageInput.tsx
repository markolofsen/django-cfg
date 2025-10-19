/**
 * Message Input Component
 * Input field for sending chat messages
 */

'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { Button, Textarea } from '@djangocfg/ui';
import { Send, Loader2 } from 'lucide-react';
import { chatLogger } from '../../../utils/logger';
import type { MessageInputProps } from '../types';

// ─────────────────────────────────────────────────────────────────────────
// Message Input Component
// ─────────────────────────────────────────────────────────────────────────

export const MessageInput: React.FC<MessageInputProps> = ({
  onSend,
  isLoading = false,
  disabled = false,
  placeholder = 'Ask me anything...',
  className = '',
}) => {
  const [message, setMessage] = useState('');
  const [rows, setRows] = useState(1);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea based on content
  useEffect(() => {
    if (textareaRef.current) {
      const lineHeight = 24; // approximate line height
      const maxRows = 5;
      const minRows = 1;
      
      // If message is empty, reset to min height
      if (!message) {
        textareaRef.current.style.height = 'auto';
        setRows(minRows);
        return;
      }
      
      textareaRef.current.style.height = 'auto';
      const scrollHeight = textareaRef.current.scrollHeight;
      const newRows = Math.max(minRows, Math.min(maxRows, Math.floor(scrollHeight / lineHeight)));
      setRows(newRows);
    }
  }, [message]);

  const handleSubmit = useCallback(
    async (e?: React.FormEvent) => {
      e?.preventDefault();
      
      const trimmedMessage = message.trim();
      if (!trimmedMessage || isLoading || disabled) return;

      try {
        await onSend(trimmedMessage);
        setMessage('');
        setRows(1);
        
        // Reset textarea height
        if (textareaRef.current) {
          textareaRef.current.style.height = 'auto';
        }
      } catch (error) {
        chatLogger.error('Failed to send message from input:', error);
      }
    },
    [message, isLoading, disabled, onSend]
  );

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Send on Enter (without Shift)
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  const isDisabled = disabled || isLoading;
  const canSend = message.trim().length > 0 && !isDisabled;

  return (
    <form onSubmit={handleSubmit} className={`border-t p-4 ${className}`}>
      <div className="flex items-end gap-2">
        <Textarea
          ref={textareaRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={isDisabled}
          rows={rows}
          className="resize-none min-h-[40px] max-h-[120px] transition-all duration-200 
                     focus:ring-2 focus:ring-primary/20"
          style={{ resize: 'none' }}
        />
        
        <Button
          type="submit"
          size="icon"
          disabled={!canSend}
          className="shrink-0 h-10 w-10 transition-all duration-200 
                     hover:scale-110 active:scale-95 disabled:scale-100"
        >
          {isLoading ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Send className="h-4 w-4" />
          )}
        </Button>
      </div>
      
      <p className="text-xs text-muted-foreground mt-2">
        Press Enter to send, Shift+Enter for new line
      </p>
    </form>
  );
};

