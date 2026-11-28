import { createElement, isValidElement, type ReactNode } from 'react';

import { cn } from '../../../lib';
import { DropdownMenuShortcut } from '../dropdown-menu';
import type { MenuRowBase } from './types';

/**
 * Resolve the `icon` field to a node. `icon` may be:
 *  - a ready React element (`<Foo />`)
 *  - a component *type*: a plain function component OR a
 *    `forwardRef`/`memo` object (lucide-react icons are forwardRef
 *    objects, so a bare `typeof === 'function'` check misses them).
 */
function renderIcon(icon: MenuRowBase['icon']): ReactNode {
  if (!icon) return null;
  if (isValidElement(icon)) return icon;

  const isFunctionComponent = typeof icon === 'function';
  const isObjectComponent =
    typeof icon === 'object' && icon !== null && '$$typeof' in icon;

  if (isFunctionComponent || isObjectComponent) {
    return createElement(
      icon as React.ComponentType<{ className?: string }>,
      { className: 'size-4 shrink-0' },
    );
  }
  return icon as ReactNode;
}

export interface MenuRowProps {
  icon?: MenuRowBase['icon'];
  label: ReactNode;
  description?: ReactNode;
  shortcut?: string;
  showDescription?: boolean;
}

/**
 * Inner layout shared by every menu row kind: leading icon, label with
 * an optional muted description line, trailing shortcut. Sits inside the
 * Radix `Item` / `SubTrigger` / `CheckboxItem` wrappers.
 */
export function MenuRow({
  icon,
  label,
  description,
  shortcut,
  showDescription = true,
}: MenuRowProps) {
  const iconNode = renderIcon(icon);

  return (
    <>
      {iconNode}
      <span className="flex min-w-0 flex-1 flex-col">
        <span className="truncate">{label}</span>
        {showDescription && description ? (
          <span className="truncate text-xs text-muted-foreground">
            {description}
          </span>
        ) : null}
      </span>
      {shortcut ? <DropdownMenuShortcut>{shortcut}</DropdownMenuShortcut> : null}
    </>
  );
}

/** Row layout for radio/checkbox rows — the Radix wrapper reserves the
 *  indicator column (`pl-8`) so the icon is placed inside the flex flow
 *  after that reserved space rather than as a leading element. */
export function MenuIndicatorRow({
  icon,
  label,
  description,
  shortcut,
  showDescription = true,
}: MenuRowProps) {
  const iconNode = renderIcon(icon);

  return (
    <span className={cn('flex min-w-0 flex-1 items-center gap-2')}>
      {iconNode}
      <span className="flex min-w-0 flex-1 flex-col">
        <span className="truncate">{label}</span>
        {showDescription && description ? (
          <span className="truncate text-xs text-muted-foreground">
            {description}
          </span>
        ) : null}
      </span>
      {shortcut ? <DropdownMenuShortcut>{shortcut}</DropdownMenuShortcut> : null}
    </span>
  );
}
