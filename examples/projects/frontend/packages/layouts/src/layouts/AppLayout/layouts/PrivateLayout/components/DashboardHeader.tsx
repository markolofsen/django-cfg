/**
 * Dashboard Header
 *
 * Header for private/dashboard layout
 * Refactored from _old/DashboardLayout - uses context only!
 */

'use client';

import { Bell, LogIn, LogOut, User } from 'lucide-react';
import React from 'react';

import {
  Avatar,
  AvatarFallback,
  AvatarImage,
  Badge,
  Button,
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
  Separator,
  SidebarTrigger,
} from '@djangocfg/ui';
import { ThemeToggle } from '@djangocfg/ui/theme';
import { useAuthDialog } from '../../../../../snippets';
import { useAppContext } from '../../../context';
import { useAuth } from '../../../../../auth';
import { useNavigation } from '../../../hooks';

/**
 * Dashboard Header Component
 *
 * Features:
 * - Sidebar trigger (mobile)
 * - Page title
 * - Custom header actions
 * - Notifications button with badge
 * - Theme toggle
 * - User dropdown with avatar, profile, logout
 * - Login button for guests
 *
 * All data from context!
 */
export function DashboardHeader() {
  const { config } = useAppContext();
  const { user } = useAuth();
  const { getPageTitle } = useNavigation();
  const { openAuthDialog } = useAuthDialog();
  const { logout } = useAuth();

  const { privateLayout } = config;
  const pageTitle = getPageTitle();

  // Notification handler - TODO: implement notification system
  const handleNotificationClick = () => {
    console.log('Notifications clicked');
  };

  const handleLogin = () => {
    openAuthDialog();
  };

  return (
    <header className="sticky top-0 py-2 z-10 h-16 flex items-center justify-between px-4 shrink-0 bg-background border-b border-border">
      {/* Left side */}
      <div className="flex items-center gap-4">
        <SidebarTrigger className="-ml-1" />
        <Separator orientation="vertical" className="mr-2 h-4" />

        {pageTitle && (
          <h1 className="text-lg font-semibold text-foreground">{pageTitle}</h1>
        )}
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* Custom header actions */}
        {privateLayout.headerActions}

        {/* Notifications */}
        <Button
          variant="ghost"
          size="icon"
          className="relative"
          onClick={handleNotificationClick}
        >
          <Bell className="h-5 w-5" />
          {/* TODO: implement notification count from context */}
        </Button>

        {/* Theme Toggle */}
        <ThemeToggle />

        {/* User menu or Login button */}
        {user ? (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="ghost" className="flex items-center gap-2 p-2">
                <Avatar className="h-8 w-8">
                  <AvatarImage
                    src={user.avatar || ''}
                    alt={user.display_username || user.email || ''}
                  />
                  <AvatarFallback className="bg-primary/10 text-primary">
                    {user.display_username?.charAt(0)?.toUpperCase() || 'U'}
                  </AvatarFallback>
                </Avatar>
                <span className="hidden md:block text-sm font-medium">
                  {user.display_username}
                </span>
              </Button>
            </DropdownMenuTrigger>

            <DropdownMenuContent align="end" className="w-48">
              <DropdownMenuLabel className="p-0 font-normal">
                <div className="flex items-center gap-2 px-1 py-1.5 text-left text-sm">
                  <Avatar className="h-8 w-8">
                    <AvatarImage
                      src={user.avatar || ''}
                      alt={user.display_username || user.email || ''}
                    />
                    <AvatarFallback className="bg-primary/10 text-primary">
                      {user.display_username?.charAt(0)?.toUpperCase() || 'U'}
                    </AvatarFallback>
                  </Avatar>
                  <div className="grid flex-1 text-left text-sm leading-tight">
                    <span className="truncate font-semibold">
                      {user.display_username || user.full_name || user.email}
                    </span>
                    <span className="truncate text-xs text-muted-foreground">
                      {user.email}
                    </span>
                  </div>
                </div>
              </DropdownMenuLabel>

              <DropdownMenuSeparator />

              <DropdownMenuItem asChild>
                <a
                  href={privateLayout.profileHref}
                  className="flex items-center gap-2"
                >
                  <User className="h-4 w-4" />
                  Profile
                </a>
              </DropdownMenuItem>

              <DropdownMenuSeparator />

              <DropdownMenuItem onClick={logout}>
                <LogOut className="mr-2 h-4 w-4" />
                Logout
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        ) : (
          <Button onClick={handleLogin} size="sm" className="gap-2">
            <LogIn className="h-4 w-4" />
            <span className="hidden sm:inline">Sign In</span>
          </Button>
        )}
      </div>
    </header>
  );
}
