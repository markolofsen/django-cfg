/**
 * PrivateLayout Context
 *
 * What the sidebar parts share: config, the active-route check, brand
 * identity and the row geometry for the current form factor.
 */

'use client';

import { useLandingRoute } from './hooks/useLandingRoute';
import { useProjectName } from '../../shared/ProjectContext';
import React, { createContext, useContext, useMemo } from 'react';

import { NAV_GEOMETRY } from './geometry';
import type { NavGeometry } from './geometry';
import { isLinkItem } from './sidebarItems';
import type { HeaderConfig, SidebarConfig, SidebarLinkItem } from './types';

export interface PrivateLayoutContextValue {
  sidebar: SidebarConfig | undefined;
  header: HeaderConfig | undefined;
  pathname: string;
  isMobile: boolean;
  /** The top bar carries the account avatar, so the phone drawer drops its footer account (one entry point). */
  accountInBar: boolean;
  geometry: NavGeometry;
  /** The route rows; Settings launchers have no route and take no part in the active-route check. */
  allItems: SidebarLinkItem[];
  isActive: (href: string) => boolean;
  homeHref: string;
  brandTitle: string;
  brandMonogram: string;
}

const PrivateLayoutContext = createContext<PrivateLayoutContextValue | null>(null);

export function usePrivateLayoutContext(): PrivateLayoutContextValue {
  const ctx = useContext(PrivateLayoutContext);
  if (!ctx) {
    throw new Error('usePrivateLayoutContext must be used within a PrivateLayoutProvider');
  }
  return ctx;
}

interface PrivateLayoutProviderProps {
  children: React.ReactNode;
  sidebar: SidebarConfig | undefined;
  header: HeaderConfig | undefined;
  pathname: string;
  isMobile: boolean;
  accountInBar?: boolean;
}

export function PrivateLayoutProvider({
  children,
  sidebar,
  header,
  pathname,
  isMobile,
  accountInBar = false,
}: PrivateLayoutProviderProps) {
  // header.href > sidebar.homeHref > the private landing route AppLayout/BaseApp configures (`auth.routes.defaultCallback`,
  // resolved by the auth provider; `undefined` outside it) > '/'.
  const landing = useLandingRoute();
  const homeHref = header?.href || sidebar?.homeHref || landing || '/';
  // header.title > the project name from BaseApp > nothing (monogram only).
  const projectName = useProjectName();
  const brandTitle = header?.title?.trim() || projectName || '';
  const brandMonogram = (
    header?.brandLetter?.trim().charAt(0) ||
    brandTitle.charAt(0) ||
    'D'
  ).toUpperCase();

  const allItems = useMemo(
    () => [...(sidebar?.groups ?? []), ...(sidebar?.views?.flatMap((v) => v.groups) ?? [])].flatMap((g) => g.items).filter(isLinkItem),
    [sidebar?.groups, sidebar?.views],
  );

  // The most specific item wins: `/a` is not active on `/a/b` when `/a/b` is its own item.
  const isActive = React.useCallback(
    (href: string) => {
      const matches = pathname === href || pathname.startsWith(`${href}/`);
      if (!matches) return false;
      return !allItems.some(
        (other) =>
          other.href !== href &&
          other.href.startsWith(`${href}/`) &&
          (pathname === other.href || pathname.startsWith(`${other.href}/`)),
      );
    },
    [pathname, allItems],
  );

  const value = useMemo(
    () => ({
      sidebar,
      header,
      pathname,
      isMobile,
      accountInBar,
      geometry: isMobile ? NAV_GEOMETRY.mobile : NAV_GEOMETRY.desktop,
      allItems,
      isActive,
      homeHref,
      brandTitle,
      brandMonogram,
    }),
    [sidebar, header, pathname, isMobile, accountInBar, allItems, isActive, homeHref, brandTitle, brandMonogram],
  );

  return <PrivateLayoutContext.Provider value={value}>{children}</PrivateLayoutContext.Provider>;
}
