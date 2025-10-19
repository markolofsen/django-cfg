/**
 * Public Layout
 *
 * Layout for public pages (landing, docs, etc.)
 * All data accessed through context - no prop drilling
 */

'use client';

import React, { ReactNode } from 'react';
import { Navigation } from './components/Navigation';
import { Footer } from './components/Footer';

export interface PublicLayoutProps {
  children: ReactNode;
}

/**
 * Public Layout Component
 *
 * Features:
 * - Top navigation bar
 * - User menu integration
 * - Footer with links
 * - Mobile responsive
 *
 * All data from useAppContext() and useAuth() - no props needed!
 */
export function PublicLayout({ children }: PublicLayoutProps) {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Navigation - gets data from context */}
      <Navigation />

      {/* Main Content */}
      <main className="flex-1">
        {children}
      </main>

      {/* Footer - gets data from context */}
      <Footer />
    </div>
  );
}
