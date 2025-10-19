/**
 * Session List Component
 * Drawer with list of chat sessions
 */

'use client';

import React, { useCallback, useRef, useEffect } from 'react';
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetDescription,
  Button,
  ScrollArea,
  Badge,
} from '@djangocfg/ui';
import { MessageSquare, Clock, Archive, Trash2, Loader2 } from 'lucide-react';
import { useKnowbaseSessionsContext } from '@djangocfg/api/cfg/contexts';
import { useInfiniteSessions } from '../hooks/useInfiniteSessions';
import type { SessionListProps } from '../types';

// ─────────────────────────────────────────────────────────────────────────
// Session List Component
// ─────────────────────────────────────────────────────────────────────────

export const SessionList: React.FC<SessionListProps> = ({
  isOpen,
  onClose,
  onSelectSession,
  className = '',
}) => {
  const { deleteSession, archiveSession } = useKnowbaseSessionsContext();
  const {
    sessions,
    isLoading,
    isLoadingMore,
    hasMore,
    loadMore,
  } = useInfiniteSessions();
  
  const scrollRef = useRef<HTMLDivElement>(null);

  // Handle scroll to load more
  const handleScroll = useCallback(() => {
    if (!scrollRef.current || isLoadingMore || !hasMore) return;

    const scrollContainer = scrollRef.current.querySelector('[data-radix-scroll-area-viewport]');
    if (!scrollContainer) return;

    const { scrollTop, scrollHeight, clientHeight } = scrollContainer;
    const scrollPercentage = (scrollTop + clientHeight) / scrollHeight;

    // Load more when scrolled 80% down
    if (scrollPercentage > 0.8) {
      loadMore();
    }
  }, [hasMore, isLoadingMore, loadMore]);

  // Attach scroll listener
  useEffect(() => {
    const scrollContainer = scrollRef.current?.querySelector('[data-radix-scroll-area-viewport]');
    if (!scrollContainer) return;

    scrollContainer.addEventListener('scroll', handleScroll);
    return () => scrollContainer.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
  };

  return (
    <Sheet open={isOpen} onOpenChange={onClose}>
      <SheetContent side="left" className={`w-[400px] sm:w-[540px] ${className}`}>
        <SheetHeader>
          <SheetTitle>Chat Sessions</SheetTitle>
          <SheetDescription>
            View and manage your chat history
          </SheetDescription>
        </SheetHeader>

        <ScrollArea className="h-[calc(100vh-120px)] mt-6" ref={scrollRef}>
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : !sessions || sessions.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <MessageSquare className="h-12 w-12 text-muted-foreground mb-4" />
              <h3 className="text-lg font-semibold text-foreground mb-2">
                No Sessions Yet
              </h3>
              <p className="text-sm text-muted-foreground max-w-md">
                Start a new conversation to create your first session.
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {sessions.map((session, index) => (
                <div
                  key={session.id}
                  className="group relative flex items-start gap-3 p-4 border rounded-sm 
                           hover:bg-muted/50 hover:border-primary/50 hover:shadow-md
                           transition-all duration-200 cursor-pointer
                           animate-in fade-in slide-in-from-left-2"
                  style={{ animationDelay: `${index * 50}ms` }}
                  onClick={() => {
                    onSelectSession(session.id);
                    onClose();
                  }}
                >
                  {/* Session Icon */}
                  <div className="shrink-0 mt-1">
                    <MessageSquare className="h-5 w-5 text-muted-foreground" />
                  </div>

                  {/* Session Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2 mb-1">
                      <h4 className="font-medium text-sm truncate">
                        {session.title || 'Untitled Session'}
                      </h4>
                      {session.is_active && (
                        <Badge variant="default" className="shrink-0 text-xs">
                          Active
                        </Badge>
                      )}
                    </div>

                    <div className="flex items-center gap-2 text-xs text-muted-foreground">
                      <Clock className="h-3 w-3" />
                      <span>{formatDate(session.created_at)}</span>
                    </div>
                  </div>

                  {/* Actions */}
                  <div className="shrink-0 flex items-center gap-1 opacity-0 group-hover:opacity-100 
                                transition-all duration-200 group-hover:translate-x-0 translate-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 hover:scale-110 active:scale-95 transition-transform duration-200"
                      onClick={(e) => {
                        e.stopPropagation();
                        archiveSession(session.id, {});
                      }}
                      title="Archive"
                    >
                      <Archive className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="h-8 w-8 p-0 text-destructive hover:text-destructive 
                               hover:scale-110 active:scale-95 transition-transform duration-200"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteSession(session.id);
                      }}
                      title="Delete"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
              
              {/* Loading more indicator */}
              {isLoadingMore && (
                <div className="flex items-center justify-center py-6">
                  <Loader2 className="h-5 w-5 animate-spin text-muted-foreground mr-2" />
                  <span className="text-sm text-muted-foreground">Loading more...</span>
                </div>
              )}
              
              {/* No more sessions indicator */}
              {!hasMore && sessions.length > 0 && (
                <div className="text-center py-4">
                  <span className="text-xs text-muted-foreground">No more sessions</span>
                </div>
              )}
            </div>
          )}
        </ScrollArea>
      </SheetContent>
    </Sheet>
  );
};

