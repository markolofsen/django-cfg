'use client';

import { File, Folder, FolderOpen } from 'lucide-react';
import { memo } from 'react';
import { cn } from '@djangocfg/ui-core/lib';

import { useTreeContext } from '../context/TreeContext';

export interface TreeIconProps {
  isFolder: boolean;
  isExpanded: boolean;
  className?: string;
}

/**
 * TreeIcon — file/folder icon for a tree row.
 *
 * Memoised: re-renders only when `isFolder`, `isExpanded` or `className`
 * change. Reads appearance from context — context updates will still
 * trigger re-render as expected.
 */
function TreeIconRaw({ isFolder, isExpanded, className }: TreeIconProps) {
  const { appearance } = useTreeContext();
  const Icon = isFolder ? (isExpanded ? FolderOpen : Folder) : File;
  return (
    <Icon
      aria-hidden
      strokeWidth={appearance.iconStrokeWidth}
      style={{ width: 'var(--tree-icon-size)', height: 'var(--tree-icon-size)' }}
      className={cn(
        'shrink-0',
        isFolder ? 'text-foreground/70' : 'text-muted-foreground/80',
        className,
      )}
    />
  );
}

export const TreeIcon = memo(TreeIconRaw);
