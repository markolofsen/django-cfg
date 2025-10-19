"use client"

import * as React from 'react';
import { TooltipProvider as RadixTooltipProvider } from '@radix-ui/react-tooltip';

interface SafeTooltipProviderProps {
  children: React.ReactNode;
  delayDuration?: number;
  skipDelayDuration?: number;
  disableHoverableContent?: boolean;
}

/**
 * SafeTooltipProvider - SSR-safe wrapper for Radix TooltipProvider
 * Only renders on client-side to avoid hydration mismatches
 */
export function SafeTooltipProvider({
  children,
  delayDuration = 700,
  skipDelayDuration = 300,
  disableHoverableContent,
}: SafeTooltipProviderProps) {
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    // During SSR, return children without TooltipProvider
    return <>{children}</>;
  }

  return (
    <RadixTooltipProvider
      delayDuration={delayDuration}
      skipDelayDuration={skipDelayDuration}
      disableHoverableContent={disableHoverableContent}
    >
      {children}
    </RadixTooltipProvider>
  );
}
