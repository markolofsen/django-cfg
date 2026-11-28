/**
 * Sidebar Nav Group — a labelled list, or an accordion when `collapsible`.
 * Groups are separated by air; only a `separated` group draws a rule.
 */

'use client';

import React, { memo, useCallback, useEffect, useMemo, useState } from 'react';
import { ChevronDown } from 'lucide-react';

import {
  Collapsible,
  CollapsibleContent,
  CollapsibleTrigger,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
} from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { LucideIcon } from '../../../components';
import { useSettingsDialogStore } from '../../SettingsLayout/store';
import { shallowEqualBy } from '../../../utils/shallowEqualBy';
import { usePrivateLayoutContext } from '../context';
import { isSettingsItem, isSidebarGroupVisible, sidebarItemKey, visibleSidebarItems } from '../sidebarItems';
import type { SidebarGroupConfig } from '../types';
import { SidebarNavItem } from './SidebarNavItem';

/**
 * Groups are told apart by air, not by rules: one gap between neighbours (8px, 6px in the phone drawer) and the same small padding inside, so every
 * block starts on the same rhythm. A hairline between plain groups doubled the gap and made the spacing look uneven; a group that wants a rule asks
 * for it with `separated`.
 */
const groupClassFor = (inset: string, insetRule: boolean) =>
  cn(`gap-0 ${inset} py-0.5`, insetRule ? '[&:not(:first-child)]:mt-1.5' : '[&:not(:first-child)]:mt-2');

/** A `separated` group draws its own, stronger divider (below), so it drops the hairline and takes more air. */
const separatedGroupClassFor = (inset: string) => `gap-0 ${inset} pb-1 pt-0`;

/** Full-width rule with room above and below; decorative, so the rail and the drawer read the same. */
function GroupDivider({ inset }: { inset: string }) {
  return (
    <div
      role="separator"
      aria-orientation="horizontal"
      data-sidebar="group-divider"
      className={cn(inset, 'mb-3 mt-3 h-(--sidebar-divider-h) shrink-0 bg-sidebar-border')}
    />
  );
}

function SidebarNavGroupRaw({ group }: { group: SidebarGroupConfig }) {
  const { isActive, geometry, isMobile } = usePrivateLayoutContext();

  const hasLabel = group.label.trim().length > 0;
  const isCollapsible = Boolean(group.collapsible) && hasLabel;
  const hideItemIcons = group.hideItemIcons ?? isCollapsible;

  const menuSections = useSettingsDialogStore((s) => s.sections);
  const dialogSection = useSettingsDialogStore((s) =>
    s.isOpen ? (s.activeSection ?? s.sections[0]?.id ?? null) : null,
  );
  const registered = useMemo(() => new Set(menuSections.map((s) => s.id)), [menuSections]);
  const items = useMemo(() => visibleSidebarItems(group.items, registered), [group.items, registered]);
  const visible = isSidebarGroupVisible(group, registered);

  const hasActiveChild = useMemo(
    () =>
      items.some((item) =>
        isSettingsItem(item) ? item.settingsSection === dialogSection : isActive(item.href),
      ),
    [items, isActive, dialogSection],
  );

  const [open, setOpen] = useState(isCollapsible ? Boolean(group.defaultOpen) || hasActiveChild : true);

  useEffect(() => {
    if (isCollapsible && hasActiveChild) setOpen(true);
  }, [isCollapsible, hasActiveChild]);

  const handleOpenChange = useCallback((value: boolean) => setOpen(value), []);

  const rows = items.map((item) => (
    <SidebarNavItem key={sidebarItemKey(item)} item={item} hideItemIcons={hideItemIcons} />
  ));
  if (!visible) return null;

  const groupClass = group.separated ? separatedGroupClassFor(geometry.inset) : groupClassFor(geometry.inset, isMobile);
  const divider = group.separated ? <GroupDivider inset={geometry.dividerInset} /> : null;

  if (isCollapsible) {
    return (
      <>
        {divider}
        <SidebarGroup className={groupClass}>
          <Collapsible open={open} onOpenChange={handleOpenChange} className="w-full">
            <CollapsibleTrigger asChild>
              <button
                type="button"
                aria-expanded={open}
                className={cn(
                  'flex w-full items-center rounded-lg font-normal text-sidebar-foreground',
                  'transition-colors duration-150 hover:bg-sidebar-accent/60',
                  'outline-none ring-sidebar-ring focus-visible:ring-2',
                  geometry.item,
                )}
              >
                {group.icon ? <LucideIcon icon={group.icon} className="shrink-0 text-sidebar-foreground/60" /> : null}
                <span className="flex-1 truncate text-left">{group.label}</span>
                <ChevronDown
                  aria-hidden
                  className={cn(
                    'size-4 shrink-0 text-sidebar-foreground/50 transition-transform duration-200',
                    open && 'rotate-180',
                  )}
                />
              </button>
            </CollapsibleTrigger>
            <CollapsibleContent className="overflow-hidden data-[state=closed]:animate-accordion-up data-[state=open]:animate-accordion-down">
              <SidebarGroupContent>
                <SidebarMenu className="mt-0.5 gap-(--sidebar-item-gap)">{rows}</SidebarMenu>
              </SidebarGroupContent>
            </CollapsibleContent>
          </Collapsible>
        </SidebarGroup>
      </>
    );
  }

  return (
    <>
      {divider}
      <SidebarGroup className={groupClass}>
        {hasLabel ? (
          <SidebarGroupLabel
            className={cn('font-medium normal-case tracking-normal text-sidebar-foreground/50', geometry.label)}
          >
            {group.label}
          </SidebarGroupLabel>
        ) : null}
        <SidebarGroupContent>
          <SidebarMenu className="gap-(--sidebar-item-gap)">{rows}</SidebarMenu>
        </SidebarGroupContent>
      </SidebarGroup>
    </>
  );
}

const groupEqual = (a: SidebarGroupConfig, b: SidebarGroupConfig) =>
  a.label === b.label &&
  a.collapsible === b.collapsible &&
  a.defaultOpen === b.defaultOpen &&
  a.icon === b.icon &&
  a.hideItemIcons === b.hideItemIcons &&
  a.separated === b.separated &&
  a.dynamic === b.dynamic &&
  shallowEqualBy(
    a.items,
    b.items,
    (x, y) =>
      x.href === y.href &&
      x.settingsSection === y.settingsSection &&
      x.label === y.label &&
      x.icon === y.icon &&
      x.badge === y.badge &&
      x.badgeVariant === y.badgeVariant,
  );

export const SidebarNavGroup = memo(SidebarNavGroupRaw, (prev, next) =>
  groupEqual(prev.group, next.group),
);
