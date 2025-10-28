/**
 * QuickActionsPanel Component
 *
 * Grid of quick action buttons for common dashboard tasks
 *
 * Features:
 * - Responsive grid layout (2-4 columns)
 * - Color-coded buttons
 * - Icons for each action
 * - Hover effects
 * - Link navigation support
 */

'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@djangocfg/ui';
import { Button, Skeleton, Badge } from '@djangocfg/ui';
import { ExternalLink, Zap } from 'lucide-react';
import type { QuickAction } from '@/contexts/dashboard';

// ─────────────────────────────────────────────────────────────────────────
// Types
// ─────────────────────────────────────────────────────────────────────────

export interface QuickActionsPanelProps {
  actions?: QuickAction[];
  isLoading?: boolean;
}

// ─────────────────────────────────────────────────────────────────────────
// Helpers
// ─────────────────────────────────────────────────────────────────────────

const getButtonVariant = (
  color?: 'primary' | 'success' | 'warning' | 'danger' | 'secondary'
): 'default' | 'destructive' | 'outline' | 'secondary' | 'ghost' | 'link' => {
  switch (color) {
    case 'danger':
      return 'destructive';
    case 'secondary':
      return 'secondary';
    case 'primary':
    case 'success':
    case 'warning':
    default:
      return 'default';
  }
};

// Icon mapping for Material Icons (fallback to Lucide)
const getIcon = (iconName: string) => {
  // Fallback icon
  return <Zap className="h-5 w-5" />;
};

// ─────────────────────────────────────────────────────────────────────────
// Loading Skeleton
// ─────────────────────────────────────────────────────────────────────────

function QuickActionSkeleton() {
  return (
    <div className="flex flex-col gap-3 p-4 border rounded-lg">
      <Skeleton className="h-10 w-10 rounded" />
      <Skeleton className="h-5 w-3/4" />
      <Skeleton className="h-4 w-full" />
    </div>
  );
}

function QuickActionsPanelSkeleton() {
  return (
    <Card>
      <CardHeader>
        <Skeleton className="h-6 w-32 mb-2" />
        <Skeleton className="h-4 w-48" />
      </CardHeader>
      <CardContent>
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2">
          {Array.from({ length: 4 }).map((_, i) => (
            <QuickActionSkeleton key={i} />
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

// ─────────────────────────────────────────────────────────────────────────
// Component
// ─────────────────────────────────────────────────────────────────────────

export function QuickActionsPanel({ actions, isLoading }: QuickActionsPanelProps) {
  // Loading state
  if (isLoading) {
    return <QuickActionsPanelSkeleton />;
  }

  // FIXME: API returns single QuickAction object, but we expect array
  // Temporary workaround: treat single object as array with one item
  const actionsArray = actions ? (Array.isArray(actions) ? actions : [actions]) : [];

  return (
    <Card>
      <CardHeader>
        <CardTitle>Quick Actions</CardTitle>
        <CardDescription>Common tasks and shortcuts</CardDescription>
      </CardHeader>
      <CardContent>
        {actionsArray.length === 0 ? (
          <div className="text-center py-8 text-muted-foreground">
            <Zap className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p className="text-sm">No quick actions available</p>
          </div>
        ) : (
          <div className="grid gap-4 grid-cols-1 sm:grid-cols-2">
            {actionsArray.map((action, index) => {
              // Get background and text colors based on action.color
              const getColorClasses = (color?: 'primary' | 'success' | 'warning' | 'danger' | 'secondary') => {
                switch (color) {
                  case 'success':
                    return { bg: 'bg-green-500/10', text: 'text-green-600', border: 'hover:border-green-500' };
                  case 'warning':
                    return { bg: 'bg-yellow-500/10', text: 'text-yellow-600', border: 'hover:border-yellow-500' };
                  case 'danger':
                    return { bg: 'bg-red-500/10', text: 'text-red-600', border: 'hover:border-red-500' };
                  case 'secondary':
                    return { bg: 'bg-gray-500/10', text: 'text-gray-600', border: 'hover:border-gray-500' };
                  case 'primary':
                  default:
                    return { bg: 'bg-primary/10', text: 'text-primary', border: 'hover:border-primary' };
                }
              };

              const colorClasses = getColorClasses(action.color);

              return (
                <a
                  key={index}
                  href={action.link}
                  className="group block"
                  target={action.link.startsWith('http') ? '_blank' : undefined}
                  rel={action.link.startsWith('http') ? 'noopener noreferrer' : undefined}
                >
                  <div className={`flex flex-col gap-3 p-4 border rounded-lg ${colorClasses.border} hover:shadow-md transition-all duration-200`}>
                    <div className="flex items-start justify-between">
                      <div className={`h-10 w-10 rounded-md ${colorClasses.bg} flex items-center justify-center ${colorClasses.text}`}>
                        {getIcon(action.icon)}
                      </div>
                      {action.link.startsWith('http') && (
                        <ExternalLink className="h-4 w-4 text-muted-foreground opacity-0 group-hover:opacity-100 transition-opacity" />
                      )}
                    </div>

                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <h3 className="font-semibold text-sm">{action.title}</h3>
                        {action.category && (
                          <Badge variant="secondary" className="text-xs">
                            {action.category}
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">
                        {action.description}
                      </p>
                    </div>
                  </div>
                </a>
              );
            })}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
