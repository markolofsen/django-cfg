'use client';

import { cn } from '@djangocfg/ui-core/lib';

import type { TreeMovePosition } from '../types';

export interface TreeDropIndicatorProps {
  position: TreeMovePosition;
  /** Indent in pixels — keeps the line aligned with the row's text. */
  indent: number;
  /** Render a "rejected" style (red wash) when the drop is forbidden. */
  invalid?: boolean;
}

/**
 * Visual hint for an in-progress drag-and-drop. Three modes:
 *
 *   - `before` / `after`  → a 2px horizontal line above / below the row
 *   - `inside`            → a translucent primary wash filling the row
 *
 * Indents the line by the row's depth so it visually aligns with the
 * target's content (rather than running edge-to-edge).
 *
 * Positioned absolutely — the parent `TreeRow` provides `position: relative`.
 */
export function TreeDropIndicator({
  position,
  indent,
  invalid = false,
}: TreeDropIndicatorProps) {
  if (position === 'inside') {
    return (
      <span
        aria-hidden
        data-tree-drop="inside"
        className={cn(
          'pointer-events-none absolute inset-0 rounded-sm ring-1',
          invalid
            ? 'bg-destructive/10 ring-destructive/40'
            : 'bg-primary/10 ring-primary/40',
        )}
      />
    );
  }

  const isBefore = position === 'before';
  return (
    <span
      aria-hidden
      data-tree-drop={position}
      style={{ paddingLeft: indent }}
      className={cn(
        'pointer-events-none absolute right-0 left-0 h-px',
        isBefore ? 'top-0' : 'bottom-0',
      )}
    >
      <span
        className={cn(
          'block h-0.5 rounded-full',
          invalid ? 'bg-destructive/70' : 'bg-primary',
        )}
      />
    </span>
  );
}
