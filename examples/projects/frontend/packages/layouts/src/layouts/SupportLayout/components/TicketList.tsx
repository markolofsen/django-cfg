/**
 * Ticket List Component
 * Displays a list of support tickets with infinite scroll
 */

'use client';

import React, { useEffect, useRef } from 'react';
import { ScrollArea, Skeleton, Button } from '@djangocfg/ui';
import { TicketCard } from './TicketCard';
import { useSupportLayoutContext } from '../context';
import { MessageSquare, Loader2 } from 'lucide-react';
import { useInfiniteTickets } from '../hooks';
import { SUPPORT_LAYOUT_EVENTS } from '../events';

export const TicketList: React.FC = () => {
  const { selectedTicket, selectTicket } = useSupportLayoutContext();
  const {
    tickets,
    isLoading,
    isLoadingMore,
    hasMore,
    loadMore,
    totalCount,
    refresh
  } = useInfiniteTickets();

  const scrollRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadMoreRef = useRef<HTMLDivElement>(null);

  // Listen for ticket creation events to refresh the list
  useEffect(() => {
    const handleTicketCreated = () => {
      // Refresh the tickets list when a new ticket is created
      refresh();
    };

    window.addEventListener(SUPPORT_LAYOUT_EVENTS.TICKET_CREATED, handleTicketCreated);

    return () => {
      window.removeEventListener(SUPPORT_LAYOUT_EVENTS.TICKET_CREATED, handleTicketCreated);
    };
  }, [refresh]);

  // Set up intersection observer for infinite scroll
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

  if (isLoading) {
    return (
      <div className="p-4 space-y-2">
        {[1, 2, 3, 4, 5].map((i) => (
          <Skeleton
            key={i}
            className="h-24 w-full animate-pulse"
            style={{ animationDelay: `${i * 100}ms` }}
          />
        ))}
      </div>
    );
  }

  if (!tickets || tickets.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-8 text-center animate-in fade-in zoom-in-95 duration-300">
        <MessageSquare className="h-16 w-16 text-muted-foreground mb-4 animate-bounce" />
        <h3 className="text-lg font-semibold mb-2">No tickets yet</h3>
        <p className="text-sm text-muted-foreground max-w-sm">
          Create your first support ticket to get help from our team
        </p>
      </div>
    );
  }

  return (
    <ScrollArea className="h-full" ref={scrollRef}>
      <div className="p-4 space-y-2">
        {tickets.map((ticket, index) => (
          <div
            key={ticket.uuid}
            className="animate-in fade-in slide-in-from-left-2 duration-300"
            style={{ animationDelay: `${Math.min(index, 10) * 50}ms` }}
          >
            <TicketCard
              ticket={ticket}
              isSelected={selectedTicket?.uuid === ticket.uuid}
              onClick={() => selectTicket(ticket)}
            />
          </div>
        ))}

        {/* Load more trigger */}
        <div ref={loadMoreRef} className="h-2" />

        {/* Loading indicator */}
        {isLoadingMore && (
          <div className="flex justify-center py-4">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span className="text-sm">Loading more tickets...</span>
            </div>
          </div>
        )}

        {/* Manual load button if needed */}
        {hasMore && !isLoadingMore && (
          <div className="flex justify-center pt-2 pb-4">
            <Button
              variant="outline"
              size="sm"
              onClick={loadMore}
              className="text-xs"
            >
              Load more ({totalCount > 0 ? `${tickets.length}/${totalCount}` : ''})
            </Button>
          </div>
        )}

        {/* End message */}
        {!hasMore && tickets.length > 0 && (
          <div className="text-center py-4 text-sm text-muted-foreground">
            All {totalCount} tickets loaded
          </div>
        )}
      </div>
    </ScrollArea>
  );
};

