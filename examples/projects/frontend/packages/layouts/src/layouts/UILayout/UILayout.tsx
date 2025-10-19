/**
 * UILayout
 * Modern, config-driven layout for UI component documentation
 */

'use client';

import React, { ReactNode } from 'react';
import { useCopy, Sticky } from '@djangocfg/ui';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { MobileOverlay } from './components/MobileOverlay';
import { generateAIContext } from './config';
import { useShowcase } from './context';
import type { ComponentCategory } from './config';

export interface UILayoutProps {
  children: ReactNode;
  title?: string;
  description?: string;
  categories: ComponentCategory[];
  currentCategory?: string;
  onCategoryChange?: (categoryId: string) => void;
  logo?: ReactNode;
  projectName?: string;
}

/**
 * UILayout - Main layout component for UI documentation
 *
 * Features:
 * - Config-driven: All component data comes from centralized config
 * - "Copy for AI": One-click export of all documentation
 * - Responsive: Mobile-first design with sidebar
 * - Type-safe: Full TypeScript support
 *
 * @example
 * ```tsx
 * <UILayout
 *   title="UI Components"
 *   categories={CATEGORIES}
 *   currentCategory={category}
 *   onCategoryChange={setCategory}
 * >
 *   <CategoryRenderer categoryId={category} />
 * </UILayout>
 * ```
 */
export function UILayout({
  children,
  title = "UI Component Library",
  description,
  categories,
  currentCategory,
  onCategoryChange,
  logo,
  projectName = "Django CFG UI",
}: UILayoutProps) {
  const { isSidebarOpen, toggleSidebar, closeSidebar } = useShowcase();
  const { copyToClipboard } = useCopy();

  const handleCategoryChange = (categoryId: string) => {
    onCategoryChange?.(categoryId);
    closeSidebar();
  };

  const handleCopyForAI = () => {
    const aiContext = generateAIContext();
    copyToClipboard(aiContext);
  };

  return (
    <div className="flex bg-background">
      {/* Mobile Overlay - outside flex container for proper z-index stacking */}
      <MobileOverlay
        isOpen={isSidebarOpen}
        onClose={closeSidebar}
      />

      {/* Sidebar with Sticky - parent must be scrollable for react-sticky-box */}
      <div className="h-full sticky top-0">
        <Sidebar
          categories={categories}
          currentCategory={currentCategory}
          onCategoryChange={handleCategoryChange}
          isOpen={isSidebarOpen}
          projectName={projectName}
          logo={logo}
        />
      </div>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header with Copy for AI button */}
        <Header
          title={title}
          projectName={projectName}
          logo={logo}
          isSidebarOpen={isSidebarOpen}
          onToggleSidebar={toggleSidebar}
          onCopyForAI={handleCopyForAI}
        />

        {/* Content Area */}
        <div className="flex-1">
          <div className="container max-w-7xl mx-auto p-6">
            {description && (
              <p className="text-sm text-muted-foreground mb-6">
                {description}
              </p>
            )}
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}

// Legacy export for backward compatibility
export { UILayout as ComponentShowcaseLayout };
export type { UILayoutProps as ComponentShowcaseLayoutProps };
