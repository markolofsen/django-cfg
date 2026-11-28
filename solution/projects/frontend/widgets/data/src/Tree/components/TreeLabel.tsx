'use client';

import { memo } from 'react';
import { cn } from '@djangocfg/ui-core/lib';

export interface TreeLabelProps {
  children: React.ReactNode;
  isMatchingSearch?: boolean;
  className?: string;
}

/**
 * TreeLabel — truncated label for a tree row.
 *
 * Memoised: re-renders only when `children`, `isMatchingSearch` or
 * `className` change. `children` is compared by reference.
 */
function TreeLabelRaw({ children, isMatchingSearch, className }: TreeLabelProps) {
  return (
    <span
      // Colour is set inline via the semantic token rather than the
      // `text-foreground` Tailwind utility: that class isn't always
      // emitted into a consuming app's stylesheet (the bundler only
      // generates utilities it sees referenced in scanned source), so
      // relying on it left the label rendering as UA-default black on
      // a dark surface. `var(--foreground)` always resolves.
      style={{ fontSize: 'var(--tree-font-size)', color: 'var(--foreground)' }}
      className={cn(
        'truncate leading-tight tracking-[-0.005em]',
        isMatchingSearch && 'font-medium',
        className,
      )}
    >
      {children}
    </span>
  );
}

export const TreeLabel = memo(TreeLabelRaw);
