'use client';

import { Fragment, type ReactNode } from 'react';
import { cn } from '@djangocfg/ui-core/lib';

import { useTreeContext } from '../context/TreeContext';
import { appearanceToStyle } from '../data/appearance';
import type { FlatRow, TreeRowRenderProps, TreeRowSlot } from '../types';
import { TreeRow } from './TreeRow';
import { TreeEmpty } from './TreeEmpty';

export interface TreeContentProps<T> {
  /** Custom row renderer; falls back to <TreeRow />. */
  children?: TreeRowSlot<T>;
  className?: string;
  /** Override aria-label for the container. */
  ariaLabel?: string;
  /**
   * Container ARIA role. Defaults to `'tree'` for standalone composition
   * use. `<TreeRoot>` passes `'group'` because its own outer element
   * already carries `role="tree"` + `aria-activedescendant`.
   */
  role?: 'tree' | 'group' | 'presentation';
}

/** DOM id for a tree row — referenced by `aria-activedescendant`. */
export const treeRowDomId = (id: string) => `tree-row-${id}`;

export function TreeContent<T>({
  children,
  className,
  ariaLabel,
  role = 'tree',
}: TreeContentProps<T>) {
  const { flatRows, labels, selected, focused, matchingIds, appearance, selectionMode } =
    useTreeContext<T>();

  if (flatRows.length === 0) {
    return <TreeEmpty>{labels.empty}</TreeEmpty>;
  }

  const isTree = role === 'tree';

  return (
    <div
      role={role}
      aria-label={isTree ? (ariaLabel ?? labels.ariaLabel) : undefined}
      aria-multiselectable={
        isTree && selectionMode === 'multiple' ? true : undefined
      }
      className={cn('relative flex flex-col py-1', className)}
      style={appearanceToStyle(appearance)}
    >
      {flatRows.map((row: FlatRow<T>) => {
        const slot: TreeRowRenderProps<T> = {
          node: row.node,
          level: row.level,
          isSelected: selected.has(row.node.id),
          isExpanded: row.isExpanded,
          isFocused: focused === row.node.id,
          isFolder: row.isFolder,
          isLoading: row.isLoading,
          isMatchingSearch: matchingIds.has(row.node.id),
        };
        const node: ReactNode = children ? children(slot) : <TreeRow row={row} />;
        return <Fragment key={row.node.id}>{node}</Fragment>;
      })}
    </div>
  );
}
