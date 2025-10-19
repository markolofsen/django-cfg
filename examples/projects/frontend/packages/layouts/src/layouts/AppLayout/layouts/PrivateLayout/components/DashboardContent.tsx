/**
 * Dashboard Content
 *
 * Main content wrapper for dashboard pages
 * Refactored from _old/DashboardLayout - uses context only!
 */

'use client';

import React from 'react';
import { cn } from '@djangocfg/ui/lib';
import { useAppContext } from '../../../context';

interface DashboardContentProps {
  children: React.ReactNode;
  className?: string;
}

const paddingVariants = {
  none: '',
  default: 'p-6',
  sm: 'p-4',
  md: 'p-6',
  lg: 'p-8',
};

/**
 * Dashboard Content Component
 *
 * Features:
 * - Configurable padding from context
 * - Full-width container
 * - Custom className support
 *
 * Padding controlled by config.privateLayout.contentPadding
 */
export function DashboardContent({
  children,
  className,
}: DashboardContentProps) {
  const { config } = useAppContext();
  const { privateLayout } = config;

  const padding =
    paddingVariants[
      privateLayout.contentPadding as keyof typeof paddingVariants
    ] || paddingVariants.default;

  return (
    <main
      className={cn(
        'w-full bg-background relative min-h-full',
        padding,
        className
      )}
    >
      {children}
    </main>
  );
}
