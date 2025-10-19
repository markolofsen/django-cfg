/**
 * Mobile Menu User Card Component
 *
 * Displays user information and action buttons in mobile menu
 * - Authenticated: shows user info with dashboard, profile, and logout
 * - Guest: shows welcome message with sign in button
 */

'use client';

import React from 'react';
import { Crown, LogOut, Settings, User } from 'lucide-react';
import { Button, ButtonLink, Card, CardContent } from '@djangocfg/ui/components';
import { ThemeToggle } from '@djangocfg/ui/theme';

interface MobileMenuUserCardProps {
  isAuthenticated: boolean;
  user?: {
    email?: string;
    avatar?: string;
  } | null;
  dashboardPath?: string;
  profilePath: string;
  authPath: string;
  onLogout: () => void;
  onNavigate: () => void;
}

export function MobileMenuUserCard({
  isAuthenticated,
  user,
  dashboardPath,
  profilePath,
  authPath,
  onLogout,
  onNavigate,
}: MobileMenuUserCardProps) {
  if (isAuthenticated) {
    return (
      <Card className="border-primary/20 shadow-lg !bg-accent/50">
        <CardContent className="p-4">
          {/* User Info Header */}
          <div className="flex items-center gap-3 mb-4 p-3 rounded-sm border border-border bg-accent/70">
            <div className="w-10 h-10 rounded-full flex items-center justify-center bg-primary flex-shrink-0 overflow-hidden relative">
              {user?.avatar ? (
                <img
                  src={user.avatar}
                  alt={user?.email || 'User'}
                  className="w-10 h-10 rounded-full object-cover"
                />
              ) : (
                <User className="w-5 h-5 text-primary-foreground" />
              )}
              {/* Active indicator */}
              <div className="absolute -bottom-0.5 -right-0.5 size-3 rounded-full bg-green-500 border-2 border-background" />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                Signed in as
              </p>
              <p className="text-sm font-semibold truncate text-foreground">
                {user?.email}
              </p>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="space-y-3">
            {/* Dashboard link */}
            {dashboardPath && (
              <ButtonLink
                href={dashboardPath}
                variant="default"
                size="sm"
                className="w-full h-9"
                onClick={onNavigate}
              >
                <Crown className="w-4 h-4 mr-2" />
                Dashboard
              </ButtonLink>
            )}

            {/* Quick Actions - Icons only */}
            <div className="flex items-center justify-center gap-2 pt-3 mt-1 border-t border-border/30">
              {/* Profile Settings */}
              <ButtonLink
                href={profilePath}
                variant="ghost"
                size="icon"
                className="h-9 w-9"
                onClick={onNavigate}
                aria-label="Profile Settings"
              >
                <Settings className="h-5 w-5" />
              </ButtonLink>

              {/* Theme Toggle */}
              <ThemeToggle />

              {/* Sign Out */}
              <Button
                onClick={onLogout}
                variant="ghost"
                size="icon"
                className="h-9 w-9 text-destructive hover:bg-destructive/10 hover:text-destructive"
                aria-label="Sign Out"
              >
                <LogOut className="h-5 w-5" />
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Guest Card
  return (
    <Card className="border-border !bg-accent/50">
      <CardContent className="p-4">
        <div className="text-center space-y-4">
          <div className="w-12 h-12 rounded-full flex items-center justify-center mx-auto bg-muted">
            <User className="w-6 h-6 text-muted-foreground" />
          </div>
          <div>
            <p className="text-sm font-medium mb-1 text-foreground">Welcome!</p>
            <p className="text-xs text-muted-foreground">
              Sign in to access your dashboard
            </p>
          </div>
          <ButtonLink
            href={authPath}
            variant="default"
            size="default"
            className="w-full"
            onClick={onNavigate}
          >
            <User className="w-5 h-5 mr-2" />
            Sign In
          </ButtonLink>

          {/* Theme toggle */}
          <div className="flex justify-center pt-2 border-t border-border/30">
            <ThemeToggle />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
