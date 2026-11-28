/**
 * Sidebar Nav Item — icon, label, optional badge. Active state is a surface
 * plus `aria-current`; weight never changes, so labels do not jump.
 */

'use client';

import React, { memo } from 'react';

import {
  Link,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
} from '@djangocfg/ui-core/components';
import { cn } from '@djangocfg/ui-core/lib';

import { LucideIcon } from '../../../components';
import { usePrivateLayoutContext } from '../context';
import { useSettingsSectionState } from '../../SettingsLayout/hooks/useSettingsSectionState';
import { isSettingsItem } from '../sidebarItems';
import type { SidebarItem, SidebarLinkItem, SidebarSettingsItem } from '../types';

interface SidebarNavItemProps {
  item: SidebarItem;
  hideItemIcons?: boolean;
}

const ITEM_CLASS = cn(
  'rounded-(--sidebar-item-radius) border-0 font-normal shadow-none transition-colors duration-150',
  'text-sidebar-foreground/90 hover:bg-sidebar-accent/70 hover:text-sidebar-foreground',
  'data-[active=true]:bg-sidebar-accent data-[active=true]:font-normal data-[active=true]:text-sidebar-foreground',
  '[&>svg]:text-sidebar-foreground/80 [&>svg]:opacity-100 hover:[&>svg]:text-sidebar-foreground',
  'data-[active=true]:[&>svg]:text-sidebar-foreground',
);

function ItemContent({ item, hideItemIcons }: SidebarNavItemProps) {
  return (
    <>
      {!hideItemIcons && item.icon ? <LucideIcon icon={item.icon} /> : null}
      <span>{item.label}</span>
      {item.badge ? (
        <SidebarMenuBadge
          className={cn(item.badgeVariant === 'pill' && 'rounded-md bg-primary/15 px-1.5 font-medium text-primary')}
        >
          {item.badge}
        </SidebarMenuBadge>
      ) : null}
    </>
  );
}

/**
 * A row that opens Settings on a section. Not rendered while the dialog does not list the section (no dead door),
 * active while the dialog shows it. The dialog owns the URL, so a row never writes the address itself.
 */
function SidebarSettingsNavItem({ item, hideItemIcons }: { item: SidebarSettingsItem; hideItemIcons?: boolean }) {
  const { geometry } = usePrivateLayoutContext();
  const { registered, active, open } = useSettingsSectionState(item.settingsSection);
  if (!registered) return null;

  return (
    <SidebarMenuItem>
      <SidebarMenuButton
        isActive={active}
        onClick={open}
        aria-haspopup="dialog"
        aria-current={active ? 'true' : undefined}
        className={cn(ITEM_CLASS, geometry.item, hideItemIcons && geometry.indent)}
      >
        <ItemContent item={item} hideItemIcons={hideItemIcons} />
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}

function SidebarLinkNavItem({ item, hideItemIcons }: { item: SidebarLinkItem; hideItemIcons?: boolean }) {
  const { isActive, geometry } = usePrivateLayoutContext();
  const active = isActive(item.href);

  return (
    <SidebarMenuItem>
      <SidebarMenuButton
        asChild
        isActive={active}
        className={cn(ITEM_CLASS, geometry.item, hideItemIcons && geometry.indent)}
      >
        <Link href={item.href} aria-current={active ? 'page' : undefined}>
          <ItemContent item={item} hideItemIcons={hideItemIcons} />
        </Link>
      </SidebarMenuButton>
    </SidebarMenuItem>
  );
}

function SidebarNavItemRaw({ item, hideItemIcons }: SidebarNavItemProps) {
  return isSettingsItem(item) ? (
    <SidebarSettingsNavItem item={item} hideItemIcons={hideItemIcons} />
  ) : (
    <SidebarLinkNavItem item={item} hideItemIcons={hideItemIcons} />
  );
}

const itemEqual = (a: SidebarItem, b: SidebarItem) =>
  a.href === b.href &&
  a.settingsSection === b.settingsSection &&
  a.label === b.label &&
  a.icon === b.icon &&
  a.badge === b.badge &&
  a.badgeVariant === b.badgeVariant;

export const SidebarNavItem = memo(
  SidebarNavItemRaw,
  (prev, next) => prev.hideItemIcons === next.hideItemIcons && itemEqual(prev.item, next.item),
);
