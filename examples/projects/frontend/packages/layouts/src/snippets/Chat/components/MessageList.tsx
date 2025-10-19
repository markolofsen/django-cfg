/**
 * Message List Component
 * Displays chat messages with markdown support and sources
 */

'use client';

import React, { useEffect, useRef } from 'react';
import { Card, CardContent, Avatar, AvatarImage, AvatarFallback, Badge, ScrollArea } from '@djangocfg/ui';
import { Bot, User, ExternalLink, Loader2 } from 'lucide-react';
import { Enums } from '@djangocfg/api/cfg/generated';
import { useAuth } from '../../../auth';
import type { MessageListProps } from '../types';

// ─────────────────────────────────────────────────────────────────────────
// Message List Component
// ─────────────────────────────────────────────────────────────────────────

export const MessageList: React.FC<MessageListProps> = ({
  messages,
  isLoading = false,
  showSources = true,
  showTimestamps = false,
  autoScroll = true,
  className = '',
}) => {
  const scrollRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      const scrollContainer = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
    }
  }, [messages, isLoading, autoScroll]);

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <ScrollArea className={`h-full bg-muted/50 ${className}`} ref={scrollRef}>
      <div className="space-y-4 p-4">
        {messages.length === 0 && !isLoading ? (
          <div className="flex flex-col items-center justify-center h-full text-center py-12">
            <Bot className="h-12 w-12 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold text-foreground mb-2">
              Start a Conversation
            </h3>
            <p className="text-sm text-muted-foreground max-w-md">
              Ask me anything about the documentation, features, or get help with your project.
            </p>
          </div>
        ) : (
          messages.map((message, index) => {
            const isUser = message.role === Enums.ChatMessageRole.USER;
            const isAssistant = message.role === Enums.ChatMessageRole.ASSISTANT;
            
            return (
            <div
              key={message.id}
              className={`flex gap-3 ${isUser ? 'justify-end' : 'justify-start'}
                         animate-in fade-in slide-in-from-bottom-2 duration-300`}
              style={{ animationDelay: `${index * 50}ms` }}
            >
              {/* Avatar */}
              {isAssistant && (
                <Avatar className="h-8 w-8 shrink-0">
                  <div className="flex h-full w-full items-center justify-center bg-primary text-primary-foreground">
                    <Bot className="h-5 w-5" />
                  </div>
                </Avatar>
              )}

              {/* Message Content */}
              <div
                className={`flex flex-col gap-2 flex-1 max-w-[80%] ${
                  isUser ? 'items-end' : 'items-start'
                }`}
              >
                {/* Message Bubble */}
                <Card
                  className={`${
                    isUser
                      ? 'bg-primary text-primary-foreground'
                      : 'bg-muted'
                  } transition-all duration-200 hover:shadow-md`}
                >
                  <CardContent className="p-3">
                    <div className="text-sm whitespace-pre-wrap break-words">
                      {message.content}
                    </div>
                  </CardContent>
                </Card>

                {/* Timestamp */}
                {showTimestamps && message.created_at && (
                  <span className="text-xs text-muted-foreground px-1">
                    {formatTimestamp(message.created_at)}
                  </span>
                )}

                {/* Sources */}
                {showSources &&
                  isAssistant &&
                  message.sources &&
                  message.sources.length > 0 && (
                    <div className="flex flex-wrap gap-2 px-1 animate-in fade-in slide-in-from-left-2 duration-300 delay-100">
                      {message.sources.map((source, idx) => (
                        <Badge
                          key={idx}
                          variant="secondary"
                          className="text-xs flex items-center gap-1 cursor-pointer 
                                   hover:bg-secondary/80 hover:scale-105 active:scale-95 
                                   transition-all duration-200 animate-in fade-in zoom-in-95"
                          style={{ animationDelay: `${(idx + 1) * 100}ms` }}
                        >
                          {source.document_title || `Source ${idx + 1}`}
                          <ExternalLink className="h-3 w-3" />
                        </Badge>
                      ))}
                    </div>
                  )}
              </div>

              {/* User Avatar */}
              {isUser && (
                <Avatar className="h-8 w-8 shrink-0">
                  {user?.avatar && <AvatarImage src={user.avatar} alt={user.display_username || user.email || 'User'} />}
                  <AvatarFallback className="bg-primary/10 text-primary font-semibold">
                    {user?.display_username?.charAt(0)?.toUpperCase() || 
                     user?.email?.charAt(0)?.toUpperCase() || 
                     <User className="h-5 w-5" />}
                  </AvatarFallback>
                </Avatar>
              )}
            </div>
            );
          })
        )}

        {/* Loading Indicator */}
        {isLoading && (
          <div className="flex gap-3 justify-start animate-in fade-in slide-in-from-bottom-2 duration-300">
            <Avatar className="h-8 w-8 shrink-0 animate-pulse">
              <div className="flex h-full w-full items-center justify-center bg-primary text-primary-foreground">
                <Bot className="h-5 w-5 animate-bounce" />
              </div>
            </Avatar>
            <Card className="bg-muted animate-pulse">
              <CardContent className="p-3">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span className="animate-pulse">Thinking...</span>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </ScrollArea>
  );
};

