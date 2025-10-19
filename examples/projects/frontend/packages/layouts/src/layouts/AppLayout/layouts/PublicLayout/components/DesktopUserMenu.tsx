/**
 * Desktop User Menu
 *
 * User dropdown menu for desktop navigation
 * Refactored from _old/MainLayout - uses context only!
 */

'use client';

import React from 'react';
import { useRouter } from 'next/router';
import { ChevronDown, LayoutDashboard, LogOut, User } from 'lucide-react';
import { ButtonLink } from '@djangocfg/ui/components';
import { useAppContext } from '../../../context';
import { useAuth } from '../../../../../auth';

/**
 * Desktop User Menu Component
 *
 * Features:
 * - Sign in button for guests
 * - Dashboard link for authenticated users (if not on dashboard)
 * - User dropdown with email and profile link
 * - Logout button
 *
 * All data from context!
 */
export function DesktopUserMenu() {
  const router = useRouter();
  const { config, userMenuOpen, toggleUserMenu, closeUserMenu } = useAppContext();
  const { user, isAuthenticated, logout } = useAuth();

  const { routes, publicLayout } = config;

  const handleLogout = () => {
    logout();
    closeUserMenu();
  };

  const isDashboard = publicLayout.userMenu.dashboardPath
    ? router.pathname.includes(publicLayout.userMenu.dashboardPath)
    : false;

  return (
    <div className="flex items-center gap-3">
      {/* Authenticated user */}
      {isAuthenticated ? (
        <div className="flex items-center gap-3">
          {/* Dashboard button (only if not on dashboard) */}
          {publicLayout.userMenu.dashboardPath && !isDashboard && (
            <ButtonLink
              href={publicLayout.userMenu.dashboardPath}
              variant="default"
              size="sm"
            >
              <LayoutDashboard className="size-4 mr-2" />
              Dashboard
            </ButtonLink>
          )}

          {/* User Dropdown */}
          <div className="relative">
            <button
              className="flex items-center gap-2 px-3 py-2 rounded-sm text-sm font-medium transition-colors text-foreground hover:text-primary hover:bg-accent/50"
              onClick={toggleUserMenu}
              aria-haspopup="true"
              aria-expanded={userMenuOpen}
            >
              <User className="size-4" />
              <span className="max-w-[120px] truncate">{user?.email}</span>
              <ChevronDown
                className={`size-4 transition-transform ${
                  userMenuOpen ? 'rotate-180' : ''
                }`}
              />
            </button>

            {userMenuOpen && (
              <>
                {/* Backdrop */}
                <div
                  className="fixed inset-0 z-[9995]"
                  onClick={closeUserMenu}
                  aria-hidden="true"
                />
                {/* Dropdown */}
                <div
                  className="absolute top-full right-0 mt-2 w-48 rounded-sm shadow-sm backdrop-blur-xl z-[9996] bg-popover border border-border"
                  role="menu"
                  aria-label="User menu"
                >
                  <div className="p-2">
                    {/* User info */}
                    <div className="px-3 py-2 text-sm mb-2 border-b border-border">
                      <div className="text-muted-foreground">Signed in as:</div>
                      <div className="font-medium truncate text-popover-foreground mt-1">
                        {user?.email}
                      </div>
                    </div>

                    {/* Profile link */}
                    <ButtonLink
                      href={publicLayout.userMenu.profilePath}
                      variant="ghost"
                      size="sm"
                      className="w-full justify-start"
                      onClick={closeUserMenu}
                    >
                      <User className="size-4 mr-2" />
                      Profile
                    </ButtonLink>

                    {/* Logout button */}
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-2 px-3 py-2 text-sm rounded-sm transition-colors text-destructive hover:bg-destructive/[0.1]"
                    >
                      <LogOut className="size-4" />
                      <span>Sign out</span>
                    </button>
                  </div>
                </div>
              </>
            )}
          </div>
        </div>
      ) : (
        /* Guest - Sign in button */
        <ButtonLink href={routes.auth} variant="default" size="sm" className="h-9 gap-1.5">
          <User className="w-4 h-4" />
          Sign In
        </ButtonLink>
      )}
    </div>
  );
}
