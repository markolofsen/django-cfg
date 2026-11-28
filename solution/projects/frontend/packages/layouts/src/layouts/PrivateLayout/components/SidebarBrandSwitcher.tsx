/**
 * Sidebar Brand Switcher
 *
 * Dropdown for switching workspaces / accounts / projects.
 * Renders in the sidebar header area, replacing the static brand block.
 *
 */

'use client';

import React, { memo, useMemo } from 'react';
import { Check, ChevronsUpDown, Plus } from 'lucide-react';

import {
  Avatar,
  AvatarFallback,
  AvatarImage,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@djangocfg/ui-core/components';
import { Link } from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { usePeekPin } from '../hooks';
import { PrivateSidebarTrigger } from './PrivateSidebarTrigger';
import type { SidebarBrandSwitcherConfig, SidebarBrandSwitcherItem } from '../types';

interface SidebarBrandSwitcherProps {
  config: SidebarBrandSwitcherConfig;
  /** Show the sidebar collapse toggle inside the switcher row (desktop expanded only). */
  showCollapseTrigger?: boolean;
}

function SidebarBrandSwitcherRaw({ config, showCollapseTrigger }: SidebarBrandSwitcherProps) {
  const [open, setOpen] = React.useState(false);
  usePeekPin(open);

  const activeItem = useMemo(
    () => config.items.find((i) => i.active) ?? config.items[0] ?? null,
    [config.items],
  );

  const onOpenChange = React.useCallback((next: boolean) => {
    setOpen(next);
  }, []);

  if (!activeItem) return null;

  const activeMonogram = (
    activeItem.monogram?.charAt(0) ||
    activeItem.label.charAt(0) ||
    '?'
  ).toUpperCase();

  const activeAvatar = (
    <Avatar className="h-7 w-7 shrink-0 rounded-md">
      <AvatarImage src={activeItem.avatar} alt={activeItem.label} />
      <AvatarFallback className="rounded-md bg-sidebar-primary text-[11px] font-bold text-sidebar-primary-foreground">
        {activeMonogram}
      </AvatarFallback>
    </Avatar>
  );

  return (
    <div className="flex items-center gap-1">
      <DropdownMenu open={open} onOpenChange={onOpenChange}>
        <DropdownMenuTrigger asChild>
          <button
            type="button"
            className={cn(
              'group/switcher flex min-w-0 flex-1 items-center gap-2.5 rounded-lg px-2 py-2',
              'text-left transition-colors',
              'hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground',
              'outline-none ring-sidebar-ring focus-visible:ring-2',
            )}
            data-no-expand
          >
            {activeAvatar}
            <span className="flex min-w-0 flex-1 flex-col">
              <span className="truncate text-sm font-semibold leading-tight text-sidebar-foreground">
                {activeItem.label}
              </span>
              {activeItem.description ? (
                <span className="truncate text-xs leading-snug text-sidebar-foreground/55">
                  {activeItem.description}
                </span>
              ) : null}
            </span>
            <ChevronsUpDown
              className="h-4 w-4 shrink-0 text-sidebar-foreground/40 transition-colors group-hover/switcher:text-sidebar-foreground/70"
              aria-hidden
            />
          </button>
        </DropdownMenuTrigger>

        <DropdownMenuContent
          side="bottom"
          align="start"
          sideOffset={4}
          className="min-w-52 p-1.5"
        >
          {config.items.map((item) => (
            <SwitcherItem key={item.label} item={item} onClose={() => onOpenChange(false)} />
          ))}

          {config.addLabel ? (
            <>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onSelect={() => {
                  onOpenChange(false);
                  config.onAdd?.();
                }}
                className="flex items-center gap-2 rounded-md px-2 py-1.5 text-sm text-muted-foreground"
              >
                <Plus className="h-4 w-4 shrink-0" aria-hidden />
                <span className="truncate">{config.addLabel}</span>
              </DropdownMenuItem>
            </>
          ) : null}
        </DropdownMenuContent>
      </DropdownMenu>

      {showCollapseTrigger ? (
        <PrivateSidebarTrigger data-no-expand />
      ) : null}
    </div>
  );
}

interface SwitcherItemProps {
  item: SidebarBrandSwitcherItem;
  onClose: () => void;
}

function SwitcherItem({ item, onClose }: SwitcherItemProps) {
  const monogram = (
    item.monogram?.charAt(0) ||
    item.label.charAt(0) ||
    '?'
  ).toUpperCase();

  const handleSelect = React.useCallback(() => {
    onClose();
    item.onSelect?.();
  }, [item, onClose]);

  const inner = (
    <>
      <Avatar className="h-6 w-6 shrink-0 rounded-md">
        <AvatarImage src={item.avatar} alt={item.label} />
        <AvatarFallback className="rounded-md bg-sidebar-primary text-[10px] font-bold text-sidebar-primary-foreground">
          {monogram}
        </AvatarFallback>
      </Avatar>
      <span className="flex min-w-0 flex-1 flex-col">
        <span className="truncate text-sm font-medium">{item.label}</span>
        {item.description ? (
          <span className="truncate text-xs text-muted-foreground">{item.description}</span>
        ) : null}
      </span>
      {item.active ? (
        <Check className="h-4 w-4 shrink-0 text-primary" aria-hidden />
      ) : null}
    </>
  );

  if (item.href && !item.onSelect) {
    return (
      <DropdownMenuItem asChild>
        <Link
          href={item.href}
          onClick={onClose}
          className="flex items-center gap-2 rounded-md px-2 py-1.5"
        >
          {inner}
        </Link>
      </DropdownMenuItem>
    );
  }

  return (
    <DropdownMenuItem
      onSelect={handleSelect}
      className="flex items-center gap-2 rounded-md px-2 py-1.5"
    >
      {inner}
    </DropdownMenuItem>
  );
}

export const SidebarBrandSwitcher = memo(SidebarBrandSwitcherRaw);
