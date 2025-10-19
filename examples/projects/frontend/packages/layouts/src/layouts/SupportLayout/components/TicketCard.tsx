/**
 * Ticket Card Component
 * Card for displaying a single ticket
 */

'use client';

import React from 'react';
import { Badge, Card, CardContent, cn } from '@djangocfg/ui';
import { Clock, MessageSquare } from 'lucide-react';
import type { Ticket } from '@djangocfg/api/cfg/contexts';

interface TicketCardProps {
  ticket: Ticket;
  isSelected: boolean;
  onClick: () => void;
}

const getStatusBadgeVariant = (
  status: string
): 'default' | 'secondary' | 'destructive' | 'outline' => {
  switch (status) {
    case 'open':
      return 'default';
    case 'waiting_for_user':
      return 'secondary';
    case 'waiting_for_admin':
      return 'outline';
    case 'resolved':
      return 'outline';
    case 'closed':
      return 'secondary';
    default:
      return 'default';
  }
};

const formatRelativeTime = (date: string | null | undefined): string => {
  if (!date) return 'N/A';

  const now = new Date();
  const messageDate = new Date(date);
  const diffInSeconds = Math.floor((now.getTime() - messageDate.getTime()) / 1000);

  if (diffInSeconds < 60) return 'Just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)}d ago`;

  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
};

export const TicketCard: React.FC<TicketCardProps> = ({ ticket, isSelected, onClick }) => {
  return (
    <Card
      className={cn(
        'cursor-pointer transition-all duration-200 ease-out',
        'hover:bg-accent/50 hover:shadow-md hover:scale-[1.02]',
        'active:scale-[0.98]',
        isSelected && 'bg-accent border-primary shadow-sm'
      )}
      onClick={onClick}
    >
      <CardContent className="p-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="font-semibold text-sm line-clamp-2 flex-1">{ticket.subject}</h3>
          {(ticket.unanswered_messages_count || 0) > 0 && (
            <Badge 
              variant="destructive" 
              className="ml-2 shrink-0 animate-pulse"
            >
              {ticket.unanswered_messages_count}
            </Badge>
          )}
        </div>

        <div className="flex items-center justify-between text-xs text-muted-foreground">
          <div className="flex items-center gap-3">
            <Badge variant={getStatusBadgeVariant(ticket.status || 'open')} className="text-xs">
              {ticket.status || 'open'}
            </Badge>
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              <span>{formatRelativeTime(ticket.created_at)}</span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

