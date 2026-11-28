/**
 * The sidebar: docked on desktop, a peek panel while collapsed, a drawer on mobile.
 */

'use client';

import React from 'react';

import { Sidebar, useSidebar } from '@djangocfg/ui-core/components';

import { PrivateLayoutProvider } from '../context';
import { useSidebarKeyboard } from '../hooks';
import type { HeaderConfig, SidebarConfig } from '../types';
import { SidebarBody } from './SidebarBody';
import { SidebarPeek } from './SidebarPeek';
import { SidebarResizeHandle } from './SidebarResizeHandle';

interface PrivateSidebarProps {
  sidebar: SidebarConfig;
  header?: HeaderConfig;
  pathname?: string;
  variant?: 'sidebar' | 'inset';
  /** The top bar shows the account avatar (phone drawer then has no footer account). */
  accountInBar?: boolean;
}

export function PrivateSidebar({ sidebar, header, pathname = '', variant = 'sidebar', accountInBar = false }: PrivateSidebarProps) {
  const { state, isMobile, setOpenMobile } = useSidebar();
  const { setSidebarRef, handleSidebarKeyDown } = useSidebarKeyboard();

  React.useEffect(() => {
    if (isMobile) setOpenMobile(false);
  }, [pathname, isMobile, setOpenMobile]);

  return (
    <PrivateLayoutProvider sidebar={sidebar} header={header} pathname={pathname} isMobile={isMobile} accountInBar={accountInBar}>
      <Sidebar
        ref={setSidebarRef}
        collapsible="offcanvas"
        variant={variant}
        onKeyDown={handleSidebarKeyDown}
        // Collapsed: parked off-canvas. Inert keeps it out of tab order and the a11y tree.
        inert={state === 'collapsed' && !isMobile}
      >
        <SidebarBody />
        <SidebarResizeHandle />
      </Sidebar>
      <SidebarPeek />
    </PrivateLayoutProvider>
  );
}
