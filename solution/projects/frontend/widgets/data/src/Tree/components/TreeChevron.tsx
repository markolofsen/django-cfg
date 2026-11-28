'use client';

import { ChevronDown, ChevronRight } from 'lucide-react';
import { memo } from 'react';
import { cn } from '@djangocfg/ui-core/lib';

import { useTreeContext } from '../context/TreeContext';

export interface TreeChevronProps {
  isExpanded: boolean;
  isFolder: boolean;
  className?: string;
}

/**
 * TreeChevron — expand/collapse chevron for a tree row.
 *
 * Memoised: re-renders only when `isExpanded`, `isFolder` or `className`
 * change. Reads appearance from context.
 */
function TreeChevronRaw({ isExpanded, isFolder, className }: TreeChevronProps) {
  const { appearance } = useTreeContext();
  const size = { width: 'var(--tree-icon-size)', height: 'var(--tree-icon-size)' };

  if (!isFolder) {
    return (
      <span
        aria-hidden
        style={size}
        className={cn('inline-block shrink-0', className)}
      />
    );
  }
  const Icon = isExpanded ? ChevronDown : ChevronRight;
  return (
    <Icon
      aria-hidden
      strokeWidth={appearance.iconStrokeWidth}
      style={size}
      className={cn(
        'shrink-0 text-muted-foreground/70 transition-transform',
        className,
      )}
    />
  );
}

export const TreeChevron = memo(TreeChevronRaw);
