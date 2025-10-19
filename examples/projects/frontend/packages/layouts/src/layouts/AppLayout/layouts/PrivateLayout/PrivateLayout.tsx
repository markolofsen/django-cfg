/**
 * Private Layout
 *
 * Dashboard layout for authenticated pages
 * Refactored from _old/DashboardLayout - uses context only!
 */

'use client';

import React, { ReactNode, useEffect } from 'react';
import { SidebarInset, SidebarProvider } from '@djangocfg/ui/components';
import { useAuth } from '../../../../auth';
import { KnowledgeChat } from '../../../../snippets/Chat';
import { useAppContext } from '../../context';
import { DashboardContent, DashboardHeader, DashboardSidebar } from './components';

export interface PrivateLayoutProps {
  children: ReactNode;
}

/**
 * Private Layout Component
 *
 * Features:
 * - SidebarProvider for collapsible sidebar
 * - DashboardSidebar with navigation
 * - DashboardHeader with user menu, notifications, theme toggle
 * - DashboardContent with configurable padding
 * - KnowledgeChat (optional)
 * - Auth loading state
 * - Auth redirect for unauthenticated users
 *
 * All data from useAppContext() - no props!
 */
export function PrivateLayout({ children }: PrivateLayoutProps) {
  const { config } = useAppContext();
  const { isLoading, isAuthenticated } = useAuth();

  const { privateLayout, routes } = config;

  // Redirect unauthenticated users
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      const redirect = routes.detectors.getUnauthenticatedRedirect(
        window.location.pathname
      );
      if (redirect) {
        window.location.href = redirect;
      }
    }
  }, [isLoading, isAuthenticated, routes]);

  // Show loading state while checking auth
  if (isLoading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-4">
          <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
          <p className="text-sm text-muted-foreground">Loading...</p>
        </div>
      </div>
    );
  }

  // Don't render content if user is not authenticated
  if (!isAuthenticated) {
    return null;
  }

  return (
    <>
      <SidebarProvider defaultOpen={true}>
        {/* Sidebar */}
        <DashboardSidebar />

        {/* Main content area */}
        <SidebarInset className="flex flex-col">
          {/* Header */}
          <DashboardHeader />

          {/* Page content */}
          <div className="flex-1 overflow-y-auto">
            <DashboardContent>{children}</DashboardContent>
          </div>
        </SidebarInset>
      </SidebarProvider>

      {/* Chat positioned outside main layout for proper fixed positioning */}
      {privateLayout.showChat && <KnowledgeChat />}
    </>
  );
}
