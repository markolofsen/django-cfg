/**
 * Mobile Menu Drawer
 *
 * Full-screen slide-in menu for mobile devices
 * Refactored from _old/MainLayout - uses context only!
 */

'use client';

import React from 'react';
import { createPortal } from 'react-dom';
import Link from 'next/link';
import { X } from 'lucide-react';
import { useAppContext } from '../../../context';
import { useAuth } from '../../../../../auth';
import { useNavigation } from '../../../hooks';
import { MobileMenuUserCard } from './MobileMenuUserCard';

/**
 * Mobile Menu Component
 *
 * Features:
 * - Slide-in drawer from right
 * - User card with info (authenticated)
 * - Welcome card with sign in (guest)
 * - Navigation sections
 * - Theme toggle
 * - Backdrop overlay
 *
 * All data from context!
 */
export function MobileMenu() {
  const { config, mobileMenuOpen, closeMobileMenu } = useAppContext();
  const { user, isAuthenticated, logout } = useAuth();
  const { isActive } = useNavigation();

  const { app, publicLayout, routes } = config;

  // Track if we should render (stays true during close animation)
  const [shouldRender, setShouldRender] = React.useState(false);

  // Track animation state separately
  const [isOpen, setIsOpen] = React.useState(false);

  // Handle opening
  React.useEffect(() => {
    if (mobileMenuOpen) {
      setShouldRender(true);
      // Trigger animation after render
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          setIsOpen(true);
        });
      });
    } else {
      // Start close animation
      setIsOpen(false);
      // Wait for animation to finish before unmounting
      const timer = setTimeout(() => {
        setShouldRender(false);
      }, 300);
      return () => clearTimeout(timer);
    }
  }, [mobileMenuOpen]);

  const handleLogout = () => {
    logout();
    closeMobileMenu();
  };

  const handleClose = () => {
    closeMobileMenu();
  };

  const handleNavigate = () => {
    closeMobileMenu();
  };

  // Prepare menu sections before render
  const singleItemSections = React.useMemo(
    () => publicLayout.navigation.menuSections.filter(s => s.items.length === 1),
    [publicLayout.navigation.menuSections]
  );

  const multipleItemsSections = React.useMemo(
    () => publicLayout.navigation.menuSections.filter(s => s.items.length > 1),
    [publicLayout.navigation.menuSections]
  );

  if (!shouldRender) return null;

  // Portal to body to avoid z-index and positioning issues
  if (typeof window === 'undefined') return null;

  return createPortal(
    <>
      {/* Backdrop with fade animation */}
      <div
        className={`fixed inset-0 z-[150] bg-black/50 backdrop-blur-sm transition-opacity duration-300 ease-in-out lg:hidden ${
          isOpen ? 'opacity-100' : 'opacity-0'
        }`}
        onClick={handleClose}
        aria-hidden="true"
      />

      {/* Menu Content with slide animation */}
      <div
        className={`fixed top-0 right-0 bottom-0 w-80 z-[200] bg-popover border-l border-border shadow-2xl transition-transform duration-300 ease-in-out lg:hidden ${
          isOpen ? 'translate-x-0' : 'translate-x-full'
        }`}
        role="dialog"
        aria-modal="true"
        aria-label="Mobile navigation menu"
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-border/30">
            <div className="flex items-center gap-3">
              <img
                src={app.logoPath}
                alt={`${app.name} Logo`}
                className="h-8 w-auto object-contain"
              />
              <span className="text-lg font-bold text-foreground">
                {app.name}
              </span>
            </div>
            <button
              onClick={handleClose}
              className="p-2 rounded-sm transition-colors hover:bg-accent/50"
              aria-label="Close menu"
            >
              <X className="size-5" />
            </button>
          </div>

          {/* Scrollable Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {/* User Menu Card */}
            <MobileMenuUserCard
              isAuthenticated={isAuthenticated}
              user={user}
              dashboardPath={publicLayout.userMenu.dashboardPath}
              profilePath={publicLayout.userMenu.profilePath}
              authPath={routes.auth}
              onLogout={handleLogout}
              onNavigate={handleNavigate}
            />

            {/* Navigation Sections */}
            <div className="space-y-6">
              {/* Group all single-item sections into "Menu" */}
              {singleItemSections.length > 0 && (
                <div className="space-y-3">
                  <h3 className="px-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    Menu
                  </h3>
                  <div className="space-y-1">
                    {singleItemSections.map((section) => {
                      const item = section.items[0];
                      if (!item) return null;

                      return (
                        <Link
                          key={item.path}
                          href={item.path}
                          className={`block px-4 py-3 rounded-sm text-base font-medium transition-colors ${
                            isActive(item.path)
                              ? 'bg-accent text-accent-foreground'
                              : 'text-foreground hover:bg-accent hover:text-accent-foreground'
                          }`}
                          onClick={handleNavigate}
                        >
                          {item.label}
                        </Link>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Render multiple-items sections normally */}
              {multipleItemsSections.map((section) => (
                <div key={section.title} className="space-y-3">
                  <h3 className="px-2 text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                    {section.title}
                  </h3>
                  <div className="space-y-1">
                    {section.items.map((item) => (
                      <Link
                        key={item.path}
                        href={item.path}
                        className={`block px-4 py-3 rounded-sm text-base font-medium transition-colors ${
                          isActive(item.path)
                            ? 'bg-accent text-accent-foreground'
                            : 'text-foreground hover:bg-accent hover:text-accent-foreground'
                        }`}
                        onClick={handleNavigate}
                      >
                        {item.label}
                      </Link>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            {/* Bottom spacer */}
            <div style={{ height: '15vh' }}></div>
          </div>
        </div>
      </div>
    </>,
    document.body
  );
}
