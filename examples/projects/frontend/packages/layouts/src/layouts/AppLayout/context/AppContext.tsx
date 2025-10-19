/**
 * App Context
 *
 * Unified context for entire application layout system
 * Provides centralized access to configuration, state, and utilities
 */

'use client';

import React, { createContext, useContext, useState, ReactNode, useMemo } from 'react';
import { useRouter } from 'next/router';
import type { AppLayoutConfig, LayoutMode, RouteDetectors } from '../types';

// ═══════════════════════════════════════════════════════════════════════════
// Context Types
// ═══════════════════════════════════════════════════════════════════════════

interface AppContextValue {
  // Configuration
  config: AppLayoutConfig;

  // Route detection
  routes: RouteDetectors;
  currentPath: string;
  layoutMode: LayoutMode;

  // Mobile menu state
  mobileMenuOpen: boolean;
  openMobileMenu: () => void;
  closeMobileMenu: () => void;
  toggleMobileMenu: () => void;

  // User menu state (desktop dropdown)
  userMenuOpen: boolean;
  openUserMenu: () => void;
  closeUserMenu: () => void;
  toggleUserMenu: () => void;

  // Sidebar state (dashboard)
  sidebarCollapsed: boolean;
  collapseSidebar: () => void;
  expandSidebar: () => void;
  toggleSidebar: () => void;
}

// ═══════════════════════════════════════════════════════════════════════════
// Context Creation
// ═══════════════════════════════════════════════════════════════════════════

const AppContext = createContext<AppContextValue | null>(null);

// ═══════════════════════════════════════════════════════════════════════════
// Provider Component
// ═══════════════════════════════════════════════════════════════════════════

export interface AppContextProviderProps {
  children: ReactNode;
  config: AppLayoutConfig;
}

/**
 * AppContext Provider
 *
 * Provides unified application context to all child components
 * Manages layout state and exposes configuration
 */
export function AppContextProvider({ children, config }: AppContextProviderProps) {
  const router = useRouter();

  // UI state
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  // Determine current layout mode
  const layoutMode = useMemo((): LayoutMode => {
    const { isAuthRoute, isPrivateRoute } = config.routes.detectors;

    if (isAuthRoute(router.pathname)) return 'auth';
    if (isPrivateRoute(router.pathname)) return 'private';
    return 'public';
  }, [router.pathname, config.routes.detectors]);

  // Mobile menu handlers
  const openMobileMenu = () => setMobileMenuOpen(true);
  const closeMobileMenu = () => setMobileMenuOpen(false);
  const toggleMobileMenu = () => setMobileMenuOpen(prev => !prev);

  // User menu handlers
  const openUserMenu = () => setUserMenuOpen(true);
  const closeUserMenu = () => setUserMenuOpen(false);
  const toggleUserMenu = () => setUserMenuOpen(prev => !prev);

  // Sidebar handlers
  const collapseSidebar = () => setSidebarCollapsed(true);
  const expandSidebar = () => setSidebarCollapsed(false);
  const toggleSidebar = () => setSidebarCollapsed(prev => !prev);

  const value: AppContextValue = {
    config,
    routes: config.routes.detectors,
    currentPath: router.pathname,
    layoutMode,
    mobileMenuOpen,
    openMobileMenu,
    closeMobileMenu,
    toggleMobileMenu,
    userMenuOpen,
    openUserMenu,
    closeUserMenu,
    toggleUserMenu,
    sidebarCollapsed,
    collapseSidebar,
    expandSidebar,
    toggleSidebar,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
}

// ═══════════════════════════════════════════════════════════════════════════
// Hook
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Hook to access AppContext
 *
 * @throws {Error} If used outside AppContextProvider
 *
 * @example
 * ```tsx
 * const { config, layoutMode, toggleMobileMenu } = useAppContext();
 * ```
 */
export function useAppContext(): AppContextValue {
  const context = useContext(AppContext);

  if (!context) {
    throw new Error(
      'useAppContext must be used within AppContextProvider. ' +
      'Make sure your component is wrapped with <AppLayout>.'
    );
  }

  return context;
}
