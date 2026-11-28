'use client';

import { cn } from '../../../lib';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuTrigger,
} from '../dropdown-menu';
import { renderItems } from './render-items';
import type { MenuBuilderProps } from './types';

/**
 * MenuBuilder — declarative menu.
 *
 * Pass `items: MenuItem[]` and a trigger; it renders a fully accessible
 * menu through the existing Radix `DropdownMenu*` primitives (items,
 * submenus, radio groups, checkboxes, separators, section labels,
 * shortcuts, icons, descriptions).
 *
 * @example
 * <MenuBuilder items={menu} side="top" align="start">
 *   <Button variant="ghost" size="icon"><Plus /></Button>
 * </MenuBuilder>
 */
export function MenuBuilder({
  items,
  children,
  open,
  onOpenChange,
  defaultOpen,
  side,
  align = 'start',
  sideOffset,
  alignOffset,
  contentClassName,
  submenuClassName,
  showDescriptions = true,
}: MenuBuilderProps) {
  return (
    <DropdownMenu
      open={open}
      onOpenChange={onOpenChange}
      defaultOpen={defaultOpen}
    >
      {/* The trigger opens the menu on click; suppress its focus-visible ring
          so there's no stray outline around the avatar/button. */}
      <DropdownMenuTrigger asChild className="focus-visible:outline-none focus-visible:ring-0 focus-visible:ring-offset-0">
        {children}
      </DropdownMenuTrigger>
      <DropdownMenuContent
        side={side}
        align={align}
        sideOffset={sideOffset}
        alignOffset={alignOffset}
        // select-none: menu labels shouldn't be text-selectable (feels crisp).
        className={cn('min-w-56 max-w-xs select-none', contentClassName)}
      >
        {renderItems(items, { showDescriptions, submenuClassName })}
      </DropdownMenuContent>
    </DropdownMenu>
  );
}
