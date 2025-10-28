/**
 * StatCardsGrid Component
 *
 * Displays dashboard statistics in a responsive grid of cards
 *
 * Features:
 * - 4-column responsive grid (mobile: 1, tablet: 2, desktop: 4)
 * - Color-coded icons
 * - Change indicators (positive/negative/neutral)
 * - Loading skeleton states
 */

'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@djangocfg/ui';
import { Badge, Skeleton } from '@djangocfg/ui';
import { ArrowUp, ArrowDown, Minus, TrendingUp, Users, Activity, DollarSign } from 'lucide-react';
import type { StatCard } from '@/contexts/dashboard';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface StatCardsGridProps {
  cards?: StatCard | StatCard[];
  isLoading?: boolean;
}

// Icon mapping (fallback if Material Icons not available)
const getIcon = (iconName: string) => {
  const iconMap: Record<string, React.ReactNode> = {
    trending_up: <TrendingUp className="h-4 w-4" />,
    people: <Users className="h-4 w-4" />,
    activity: <Activity className="h-4 w-4" />,
    attach_money: <DollarSign className="h-4 w-4" />,
  };

  return iconMap[iconName] || <Activity className="h-4 w-4" />;
};

// Change indicator icon
const getChangeIcon = (changeType?: 'positive' | 'negative' | 'neutral') => {
  switch (changeType) {
    case 'positive':
      return <ArrowUp className="h-3 w-3" />;
    case 'negative':
      return <ArrowDown className="h-3 w-3" />;
    case 'neutral':
    default:
      return <Minus className="h-3 w-3" />;
  }
};

// Change badge color
const getChangeBadgeVariant = (changeType?: 'positive' | 'negative' | 'neutral'): 'default' | 'secondary' | 'destructive' => {
  switch (changeType) {
    case 'positive':
      return 'default';
    case 'negative':
      return 'destructive';
    case 'neutral':
    default:
      return 'secondary';
  }
};

// ─────────────────────────────────────────────────────────────────────────
// Loading Skeleton
// ─────────────────────────────────────────────────────────────────────────

function StatCardSkeleton() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <Skeleton className="h-4 w-24" />
        <Skeleton className="h-4 w-4 rounded-full" />
      </CardHeader>
      <CardContent>
        <Skeleton className="h-8 w-20 mb-2" />
        <Skeleton className="h-3 w-full" />
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────

export function StatCardsGrid({ cards, isLoading }: StatCardsGridProps) {
  // Loading state
  if (isLoading) {
    return (
      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <StatCardSkeleton key={i} />
        ))}
      </div>
    );
  }

  // No data
  if (!cards) {
    return (
      <div className="text-center py-8 text-muted-foreground">
        No statistics available
      </div>
    );
  }

  // FIXME: API returns single StatCard object, but we expect array
  // Temporary workaround: treat single object as array with one item
  const cardsArray = Array.isArray(cards) ? cards : [cards];

  return (
    <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-4">
      {cardsArray.map((card, index) => (
        <Card key={index} style={card.color ? { borderLeftColor: card.color, borderLeftWidth: '4px' } : {}}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              {card.title}
            </CardTitle>
            <div
              className="text-muted-foreground"
              style={card.color ? { color: card.color } : {}}
            >
              {getIcon(card.icon)}
            </div>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{card.value}</div>
            <div className="flex items-center gap-2 mt-2">
              {card.change && (
                <Badge
                  variant={getChangeBadgeVariant(card.change_type)}
                  className="flex items-center gap-1 text-xs"
                >
                  {getChangeIcon(card.change_type)}
                  {card.change}
                </Badge>
              )}
              {card.description && (
                <p className="text-xs text-muted-foreground">
                  {card.description}
                </p>
              )}
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
