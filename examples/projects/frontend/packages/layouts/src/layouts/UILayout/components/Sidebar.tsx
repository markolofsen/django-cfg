/**
 * Sidebar Component
 * Navigation sidebar for component categories
 */

'use client';

import React from 'react';
import { createPortal } from 'react-dom';
import { cn } from '@djangocfg/ui/lib';
import { useIsMobile } from '@djangocfg/ui';
import type { ComponentCategory } from '../types';

interface SidebarProps {
  categories: ComponentCategory[];
  currentCategory?: string;
  onCategoryChange?: (categoryId: string) => void;
  isOpen?: boolean;
  projectName?: string;
  logo?: React.ReactNode;
}

interface SidebarContentProps {
  categories: ComponentCategory[];
  currentCategory?: string;
  onCategoryChange?: (categoryId: string) => void;
  projectName?: string;
  logo?: React.ReactNode;
  isMobile: boolean;
}

/**
 * Sidebar Content Component
 * Extracted content for reuse in desktop and mobile versions
 */
function SidebarContent({
  categories,
  currentCategory,
  onCategoryChange,
  projectName,
  logo,
  isMobile,
}: SidebarContentProps) {
  return (
    <div className={cn("flex flex-col overflow-hidden", isMobile ? "h-full" : "h-screen")}>
      {/* Logo - Desktop only */}
      {!isMobile && (
        <div className="flex h-14 items-center border-b px-6 gap-2 flex-shrink-0">
          {logo}
          <span className="font-semibold text-sm">{projectName}</span>
        </div>
      )}

      {/* Navigation */}
      <div className="flex-1 overflow-y-auto scrollbar-thin">
        <div className="p-4">
          <nav>
            <div className="mb-4">
              <h3 className="mb-2 px-2 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
                Component Categories
              </h3>
            </div>

            <div className="space-y-1">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => onCategoryChange?.(category.id)}
                  className={cn(
                    "w-full flex items-center gap-3 px-3 py-2 rounded-md text-sm font-medium transition-colors",
                    currentCategory === category.id
                      ? "bg-primary text-primary-foreground"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  )}
                  title={category.description}
                >
                  <span className="flex-shrink-0">{category.icon}</span>
                  <span className="flex-1 text-left break-words">{category.label}</span>
                  {category.count && (
                    <span className={cn(
                      "text-xs px-2 py-0.5 rounded-full flex-shrink-0",
                      currentCategory === category.id
                        ? "bg-primary-foreground/20 text-primary-foreground"
                        : "bg-muted text-muted-foreground"
                    )}>
                      {category.count}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </nav>
        </div>
      </div>

      {/* Tailwind 4 Info Section */}
      <div className="border-t p-4 bg-muted/30">
        <div className="mb-3">
          <h4 className="text-xs font-semibold text-foreground uppercase tracking-wider mb-2">
            Tailwind CSS v4
          </h4>
          <p className="text-xs text-muted-foreground leading-relaxed mb-3">
            This UI library uses Tailwind CSS v4 with CSS-first configuration
          </p>
        </div>

        <div className="space-y-2 text-xs">
          <div className="flex items-start gap-2">
            <span className="text-primary mt-0.5">✓</span>
            <span className="text-muted-foreground">CSS-first @theme configuration</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-primary mt-0.5">✓</span>
            <span className="text-muted-foreground">10x faster build times</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-primary mt-0.5">✓</span>
            <span className="text-muted-foreground">Modern CSS features (color-mix, @property)</span>
          </div>
          <div className="flex items-start gap-2">
            <span className="text-primary mt-0.5">✓</span>
            <span className="text-muted-foreground">Responsive: px-4 sm:px-6 lg:px-8</span>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="border-t p-4">
        <p className="text-xs text-muted-foreground">
          Built with Radix UI + Tailwind CSS v4
        </p>
      </div>
    </div>
  );
}

export function Sidebar({
  categories,
  currentCategory,
  onCategoryChange,
  isOpen = false,
  projectName = 'Django CFG',
  logo,
}: SidebarProps) {
  const isMobile = useIsMobile();
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
  }, []);

  // Desktop sidebar - always visible, no portal
  if (!isMobile) {
    return (
      <aside className="w-64 border-r bg-background flex-shrink-0">
        <SidebarContent
          categories={categories}
          currentCategory={currentCategory}
          onCategoryChange={onCategoryChange}
          projectName={projectName}
          logo={logo}
          isMobile={false}
        />
      </aside>
    );
  }

  // Mobile sidebar - use portal when open
  if (!isOpen || !mounted) {
    return null;
  }

  if (typeof window === 'undefined') {
    return null;
  }

  return createPortal(
    <aside
      className={cn(
        "fixed inset-y-0 left-0 w-64 z-[200] bg-background border-r shadow-lg transition-transform duration-300",
        isOpen ? "translate-x-0" : "-translate-x-full"
      )}
    >
      <SidebarContent
        categories={categories}
        currentCategory={currentCategory}
        onCategoryChange={onCategoryChange}
        projectName={projectName}
        logo={logo}
        isMobile={true}
      />
    </aside>,
    document.body
  );
}
