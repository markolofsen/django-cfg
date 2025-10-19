/**
 * Message List Component
 * Displays messages in a ticket conversation with infinite scroll
 */

'use client';

import React, { useEffect, useRef, useCallback } from 'react';
import { ScrollArea, Skeleton, Avatar, AvatarFallback, AvatarImage, Card, CardContent, Button } from '@djangocfg/ui';
import { MessageSquare, Loader2, User, Headphones } from 'lucide-react';
import { useSupportLayoutContext } from '../context';
import { useInfiniteMessages } from '../hooks';
import { useAuth } from '../../../auth';
import { CfgSupportTypes } from '@djangocfg/api';

type Message = CfgSupportTypes.Message;

const formatTime = (date: string | null | undefined): string => {
  if (!date) return '';
  return new Date(date).toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
  });
};

const formatDate = (date: string | null | undefined): string => {
  if (!date) return '';
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

interface MessageBubbleProps {
  message: Message;
  isFromUser: boolean;
  currentUser: any;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isFromUser, currentUser }) => {
  const sender = message.sender;

  return (
    <div
      className={`flex gap-3 ${isFromUser ? 'justify-end' : 'justify-start'}
                 animate-in fade-in slide-in-from-bottom-2 duration-300`}
    >
      {/* Support Avatar (left side) */}
      {!isFromUser && (
        <Avatar className="h-8 w-8 shrink-0">
          {sender?.avatar ? (
            <AvatarImage src={sender.avatar} alt={sender.display_username || 'Support'} />
          ) : (
            <AvatarFallback className="bg-primary text-primary-foreground">
              {sender?.is_staff ? (
                <Headphones className="h-4 w-4" />
              ) : (
                sender?.display_username?.charAt(0)?.toUpperCase() ||
                sender?.initials ||
                'S'
              )}
            </AvatarFallback>
          )}
        </Avatar>
      )}

      {/* Message Content */}
      <div className={`flex flex-col gap-1 flex-1 max-w-[80%] ${
        isFromUser ? 'items-end' : 'items-start'
      }`}>
        {/* Sender name (for support messages) */}
        {!isFromUser && sender && (
          <span className="text-xs text-muted-foreground px-1">
            {sender.display_username || sender.email || 'Support Team'}
            {sender.is_staff && ' (Staff)'}
          </span>
        )}

        {/* Message Bubble */}
        <Card
          className={`${
            isFromUser
              ? 'bg-primary text-primary-foreground'
              : 'bg-muted'
          } transition-all duration-200 hover:shadow-md`}
        >
          <CardContent className="p-3">
            <p className="text-sm whitespace-pre-wrap break-words">{message.text}</p>
          </CardContent>
        </Card>

        {/* Timestamp */}
        <span className="text-xs text-muted-foreground px-1">
          {formatTime(message.created_at)}
        </span>
      </div>

      {/* User Avatar (right side) */}
      {isFromUser && (
        <Avatar className="h-8 w-8 shrink-0">
          {currentUser?.avatar ? (
            <AvatarImage src={currentUser.avatar} alt={currentUser.display_username || currentUser.email || 'You'} />
          ) : (
            <AvatarFallback className="bg-primary/10 text-primary font-semibold">
              {currentUser?.display_username?.charAt(0)?.toUpperCase() ||
               currentUser?.email?.charAt(0)?.toUpperCase() ||
               currentUser?.initials ||
               <User className="h-4 w-4" />}
            </AvatarFallback>
          )}
        </Avatar>
      )}
    </div>
  );
};

export const MessageList: React.FC = () => {
  const { selectedTicket } = useSupportLayoutContext();
  const { user } = useAuth();

  const {
    messages,
    isLoading,
    isLoadingMore,
    hasMore,
    totalCount,
    loadMore,
  } = useInfiniteMessages(selectedTicket?.uuid || null);

  const scrollRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement>(null);
  const firstRender = useRef(true);

  // Set up intersection observer for infinite scroll at the top
  useEffect(() => {
    if (observerRef.current) {
      observerRef.current.disconnect();
    }

    observerRef.current = new IntersectionObserver(
      (entries) => {
        if (entries[0]?.isIntersecting && hasMore && !isLoadingMore) {
          loadMore();
        }
      },
      { threshold: 0.1 }
    );

    if (loadMoreRef.current) {
      observerRef.current.observe(loadMoreRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [hasMore, isLoadingMore, loadMore]);

  // Auto-scroll to bottom on first load and new messages
  useEffect(() => {
    if (firstRender.current && messages.length > 0) {
      // Scroll to bottom on first render
      const scrollContainer = scrollAreaRef.current?.querySelector('[data-radix-scroll-area-viewport]');
      if (scrollContainer) {
        scrollContainer.scrollTop = scrollContainer.scrollHeight;
      }
      firstRender.current = false;
    }
  }, [messages]);

  // Handle scroll position when loading older messages
  const handleLoadMore = useCallback(() => {
    const scrollContainer = scrollAreaRef.current?.querySelector('[data-radix-scroll-area-viewport]');
    const previousHeight = scrollContainer?.scrollHeight || 0;

    loadMore();

    // Restore scroll position after loading
    setTimeout(() => {
      if (scrollContainer) {
        const newHeight = scrollContainer.scrollHeight;
        scrollContainer.scrollTop = newHeight - previousHeight;
      }
    }, 100);
  }, [loadMore]);

  if (!selectedTicket) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center animate-in fade-in zoom-in-95 duration-300">
        <MessageSquare className="h-16 w-16 text-muted-foreground mb-4 animate-bounce" />
        <h3 className="text-lg font-semibold mb-2">No ticket selected</h3>
        <p className="text-sm text-muted-foreground max-w-sm">
          Select a ticket from the list to view the conversation
        </p>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="p-6 space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="flex gap-3 animate-pulse"
            style={{ animationDelay: `${i * 100}ms` }}
          >
            <Skeleton className="h-8 w-8 rounded-full" />
            <Skeleton className="h-16 flex-1 max-w-[70%]" />
          </div>
        ))}
      </div>
    );
  }

  if (!messages || messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center animate-in fade-in zoom-in-95 duration-300">
        <MessageSquare className="h-16 w-16 text-muted-foreground mb-4 animate-bounce" />
        <h3 className="text-lg font-semibold mb-2">No messages yet</h3>
        <p className="text-sm text-muted-foreground max-w-sm">
          Start the conversation by sending a message below
        </p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full bg-muted/50" ref={scrollAreaRef}>
      <div className="p-6 space-y-4" ref={scrollRef}>
        {/* Load more trigger at the top */}
        <div ref={loadMoreRef} className="h-2" />

        {/* Loading indicator at the top */}
        {isLoadingMore && (
          <div className="flex justify-center py-4">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">Loading older messages...</span>
            </div>
          </div>
        )}

        {/* Manual load button if needed */}
        {hasMore && !isLoadingMore && (
          <div className="flex justify-center pt-2 pb-4">
            <Button
              variant="outline"
              size="sm"
              onClick={handleLoadMore}
              className="text-xs"
            >
              Load older messages ({totalCount > 0 ? `${messages.length}/${totalCount}` : ''})
            </Button>
          </div>
        )}

        {/* Date separator for first message group */}
        {messages.length > 0 && (
          <div className="flex items-center gap-3 my-4">
            <div className="flex-1 h-px bg-border" />
            <span className="text-xs text-muted-foreground">
              {formatDate(messages[0]?.created_at)}
            </span>
            <div className="flex-1 h-px bg-border" />
          </div>
        )}

        {/* Messages */}
        {messages.map((message, index) => {
          // Check if message is from the current user
          // Convert IDs to strings for consistent comparison
          // Also check is_from_author flag when sender is the ticket creator
          const isFromUser =
            (message.sender?.id && user?.id && String(message.sender.id) === String(user.id)) ||
            (message.sender?.email && user?.email && message.sender.email === user.email) ||
            (message.is_from_author && selectedTicket?.user && user?.id &&
             String(selectedTicket.user) === String(user.id));

          // Show date separator if date changes
          const previousMessage = index > 0 ? messages[index - 1] : null;
          const showDateSeparator = previousMessage &&
            new Date(previousMessage.created_at || '').toDateString() !==
            new Date(message.created_at || '').toDateString();

          return (
            <React.Fragment key={message.uuid}>
              {showDateSeparator && (
                <div className="flex items-center gap-3 my-4">
                  <div className="flex-1 h-px bg-border" />
                  <span className="text-xs text-muted-foreground">
                    {formatDate(message.created_at)}
                  </span>
                  <div className="flex-1 h-px bg-border" />
                </div>
              )}
              <div style={{ animationDelay: `${Math.min(index, 10) * 50}ms` }}>
                <MessageBubble
                  message={message}
                  isFromUser={!!isFromUser}
                  currentUser={user}
                />
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </ScrollArea>
  );
};