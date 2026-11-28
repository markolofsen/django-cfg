'use client';

import React, { createContext, useContext } from 'react';

import type { PublicNavbarSurface } from './navbarTypes';

export interface PublicLayoutContextValue {
  mobileMenuOpen: boolean;
  toggleMobileMenu: () => void;
  closeMobileMenu: () => void;
  /** Filled by `<PublicNavigation />` — drives default `main` top spacing. */
  navbarSurface: PublicNavbarSurface | null;
  setNavbarSurface: (surface: PublicNavbarSurface | null) => void;
}

const PublicLayoutContext = createContext<PublicLayoutContextValue | null>(null);

export function PublicLayoutProvider({
  value,
  children,
}: {
  value: PublicLayoutContextValue;
  children: React.ReactNode;
}) {
  return <PublicLayoutContext.Provider value={value}>{children}</PublicLayoutContext.Provider>;
}

export function usePublicLayout() {
  const context = useContext(PublicLayoutContext);
  if (!context) {
    throw new Error('usePublicLayout must be used within PublicLayoutProvider');
  }
  return context;
}

export function usePublicLayoutOptional() {
  return useContext(PublicLayoutContext);
}

