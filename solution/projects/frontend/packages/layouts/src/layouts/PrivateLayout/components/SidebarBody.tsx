/**
 * The sidebar's content: brand header, scrollable nav, account footer.
 * Rendered by the docked sidebar, the peek panel and the mobile drawer alike.
 */

'use client';

import React, { useMemo } from 'react';

import { usePrivateLayoutContext } from '../context';
import { SIDEBAR_SPACING } from '../geometry';
import { cn } from '@djangocfg/ui-core/lib';
import { sidebarItemKey } from '../sidebarItems';
import { PrivateSidebarAccount } from './PrivateSidebarAccount';
import { SidebarBrand } from './SidebarBrand';
import { SidebarNavGroup } from './SidebarNavGroup';
import { SidebarSlots } from './SidebarSlots';
import { SidebarViews } from './SidebarViews';

export function SidebarBody() {
  const { sidebar, header, isMobile, accountInBar } = usePrivateLayoutContext();

  const views = sidebar?.views;
  // The last pick survives a reload (a viewer's own habit, not app state).
  const [picked, setPicked] = React.useState<string | undefined>(() => {
    try {
      return typeof window === 'undefined' ? undefined : (window.localStorage.getItem('sidebar-view') ?? undefined);
    } catch {
      return undefined;
    }
  });
  const activeId = sidebar?.activeView ?? picked ?? views?.[0]?.id;
  const activeView = views?.find((v) => v.id === activeId) ?? views?.[0];
  const pick = (id: string) => {
    setPicked(id);
    try {
      window.localStorage.setItem('sidebar-view', id);
    } catch {
      // Private mode: the pick lasts for the session.
    }
    sidebar?.onViewChange?.(id);
  };
  const shown = useMemo(() => [...(sidebar?.groups ?? []), ...(activeView?.groups ?? [])], [sidebar?.groups, activeView]);

  const groups = useMemo(
    () =>
      shown.map((group) =>
        // A group of launchers for sections nobody registered renders nothing itself (see SidebarNavGroup).
        group.dynamic && group.items.length === 0 ? null : (
          <SidebarNavGroup
            key={group.label || `__flat_${group.items.map(sidebarItemKey).join('|')}`}
            group={group}
          />
        ),
      ),
    [shown],
  );

  // Three zones: pinned header, the ONLY scroller (nav), pinned footer. The header gets a border once the nav scrolls.
  const [scrolled, setScrolled] = React.useState(false);
  const onScroll = React.useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const next = e.currentTarget.scrollTop > 0;
    setScrolled((prev) => (prev === next ? prev : next));
  }, []);

  return (
    <>
      <SidebarBrand bordered={scrolled} />
      <div
        data-sidebar="content"
        onScroll={onScroll}
        className={cn(
          'flex min-h-0 flex-1 flex-col overflow-y-auto overflow-x-hidden overscroll-contain',
          SIDEBAR_SPACING[isMobile ? 'mobile' : 'desktop'].body,
        )}
      >
        {views && views.length > 0 && activeView ? <SidebarViews views={views} active={activeView.id} onChange={pick} /> : null}
        {activeView?.menuStart}
        <SidebarSlots />
        {groups}
      </div>
      {/* On a phone the account lives in the top bar when it shows the avatar; no second entry point here. */}
      {isMobile && accountInBar ? null : <PrivateSidebarAccount header={header} />}
    </>
  );
}
