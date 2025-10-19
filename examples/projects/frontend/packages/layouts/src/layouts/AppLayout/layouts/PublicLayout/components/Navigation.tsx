/**
 * Public Layout Navigation
 *
 * Full-featured navigation using @djangocfg/ui components
 * Refactored from _old/MainLayout - uses context only!
 */

'use client';

import React from 'react';
import Link from 'next/link';
import { Menu, ChevronDown } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuItem,
} from '@djangocfg/ui/components';
import { ThemeToggle } from '@djangocfg/ui/theme';
import { cn } from '@djangocfg/ui/lib';
import { useIsMobile } from '@djangocfg/ui/hooks';
import { useAppContext } from '../../../context';
import { useAuth } from '../../../../../auth';
import { useNavigation } from '../../../hooks';
import { DesktopUserMenu } from './DesktopUserMenu';
import { MobileMenu } from './MobileMenu';

/**
 * Navigation Component
 *
 * Features:
 * - Logo and branding
 * - NavigationMenu from @djangocfg/ui (Radix UI based)
 * - Theme toggle
 * - User menu (desktop)
 * - Mobile menu button
 *
 * All data from context - zero prop drilling!
 */
export function Navigation() {
  const { config, toggleMobileMenu } = useAppContext();
  const { user, isAuthenticated, logout } = useAuth();
  const { isActive } = useNavigation();
  const isMobile = useIsMobile();
  const [openDropdown, setOpenDropdown] = React.useState<string | null>(null);

  const { app, publicLayout } = config;

  return (
    <nav className="sticky top-0 w-full border-b backdrop-blur-xl z-10 bg-background/80 border-border/30">
      <div className="w-full px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Left side - Logo and Navigation Menu */}
          <div className="flex items-center gap-6">
            {/* Logo */}
            <Link
              href={publicLayout.navigation.homePath}
              className="flex items-center gap-3 group"
            >
              <img
                src={app.logoPath}
                alt={`${app.name} Logo`}
                className="h-8 w-auto object-contain transition-transform duration-300 group-hover:scale-105"
              />
              <span className="text-xl font-bold transition-colors duration-300 text-foreground group-hover:text-primary">
                {app.name}
              </span>
            </Link>

            {/* Desktop Navigation Menu */}
            {!isMobile && (
              <div className="flex items-center gap-1">
                {publicLayout.navigation.menuSections.map((section) => {
                  // Single item section - render as direct link
                  if (section.items.length === 1) {
                    const item = section.items[0];
                    if (!item) return null;

                    return (
                      <Link
                        key={section.title}
                        href={item.path}
                        className={cn(
                          'inline-flex h-9 items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground focus:outline-none disabled:pointer-events-none disabled:opacity-50',
                          isActive(item.path) && 'bg-accent text-accent-foreground'
                        )}
                      >
                        {item.label}
                      </Link>
                    );
                  }

                  // Multiple items - render as dropdown menu
                  return (
                    <div
                      key={section.title}
                      onMouseEnter={() => setOpenDropdown(section.title)}
                      onMouseLeave={() => setOpenDropdown(null)}
                    >
                      <DropdownMenu
                        open={openDropdown === section.title}
                        onOpenChange={(open) => setOpenDropdown(open ? section.title : null)}
                        modal={false}
                      >
                        <DropdownMenuTrigger
                          className={cn(
                            "inline-flex h-9 items-center justify-center gap-1 rounded-md px-4 py-2 text-sm font-medium transition-colors focus:bg-accent focus:text-accent-foreground focus:outline-none disabled:pointer-events-none disabled:opacity-50",
                            openDropdown === section.title ? "bg-accent text-accent-foreground" : "hover:bg-accent hover:text-accent-foreground"
                          )}
                        >
                          {section.title}
                          <ChevronDown className="h-3 w-3 transition-transform duration-200 group-data-[state=open]:rotate-180" />
                        </DropdownMenuTrigger>
                        <DropdownMenuContent
                          align="start"
                          sideOffset={0}
                          className="p-2"
                          style={{
                            minWidth: '250px',
                            backdropFilter: 'blur(24px)',
                            WebkitBackdropFilter: 'blur(24px)'
                          }}
                        >
                          {section.items.map((item) => (
                            <DropdownMenuItem key={item.path} asChild>
                              <Link
                                href={item.path}
                                className={cn(
                                  'cursor-pointer w-full hover:bg-accent hover:text-accent-foreground transition-colors text-base px-4 py-3 rounded-md',
                                  isActive(item.path) && 'bg-accent/50'
                                )}
                              >
                                {item.label}
                              </Link>
                            </DropdownMenuItem>
                          ))}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Right side - Theme Toggle & User Menu */}
          {!isMobile && (
          <div className="flex items-center gap-2">
            <ThemeToggle />
            <DesktopUserMenu />
          </div>
          )}

          {/* Mobile Menu Button - Only visible on mobile */}
          {isMobile && (
          <button
            onClick={toggleMobileMenu}
            className="p-3 rounded-sm border shadow-sm transition-all duration-200 bg-card/50 hover:bg-card border-border/50 hover:border-primary/50 text-foreground hover:text-primary"
            aria-label="Toggle mobile menu"
          >
            <Menu className="size-5" />
          </button>
          )}
        </div>
      </div>

      {/* Mobile Menu Drawer */}
      <MobileMenu />
    </nav>
  );
}
