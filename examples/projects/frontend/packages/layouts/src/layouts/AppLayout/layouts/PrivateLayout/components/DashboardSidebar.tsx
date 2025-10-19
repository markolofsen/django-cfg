/**
 * Dashboard Sidebar
 *
 * Sidebar navigation for private/dashboard layout
 * Refactored from _old/DashboardLayout - uses context only!
 */

'use client';

import Link from 'next/link';
import React from 'react';

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuBadge,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarMenuSub,
  SidebarMenuSubButton,
  SidebarMenuSubItem,
  useSidebar,
} from '@djangocfg/ui/components';
import { useAppContext } from '../../../context';
import { useNavigation } from '../../../hooks';

/**
 * Dashboard Sidebar Component
 *
 * Features:
 * - Project logo and name (clickable to home)
 * - Menu groups with labels
 * - Menu items with icons, labels, badges
 * - Sub-menu items (nested navigation)
 * - Active state detection
 * - Optional footer content
 *
 * All data from context!
 */
export function DashboardSidebar() {
  const { config } = useAppContext();
  const { currentPath } = useNavigation();
  const { state, isMobile } = useSidebar();

  const { app, privateLayout } = config;

  const isActiveRoute = (path: string) => {
    // Only exact match - no prefix matching
    // This ensures /private/jobs ONLY matches /private/jobs
    // and NOT /private, /private/jobs/123, etc.
    return currentPath === path;
  };

  return (
    <Sidebar collapsible="icon">
      <SidebarHeader>
        <div
          className="flex items-center gap-3"
          style={state === "collapsed" ? {
            paddingLeft: '7px',
            paddingTop: '0.5rem',
            paddingBottom: '0.5rem',
            transition: 'padding 200ms ease-in-out'
          } : {
            padding: '0.5rem',
            transition: 'padding 200ms ease-in-out'
          }}
        >
          <Link href={privateLayout.homeHref}>
            <div className="flex items-center gap-3">
              {app.logoPath ? (
                <img
                  src={app.logoPath}
                  alt={app.name}
                  className={isMobile ? "h-10 w-10 flex-shrink-0" : "h-8 w-8 flex-shrink-0"}
                />
              ) : (
                <div className={isMobile ? "h-10 w-10 bg-primary rounded-sm flex items-center justify-center flex-shrink-0" : "h-8 w-8 bg-primary rounded-sm flex items-center justify-center flex-shrink-0"}>
                  <span className="text-primary-foreground font-bold text-sm">
                    {app.name.charAt(0).toUpperCase()}
                  </span>
                </div>
              )}
              {state !== "collapsed" && (
                <span className={isMobile ? "font-semibold text-foreground truncate text-base" : "font-semibold text-foreground truncate"} style={{ whiteSpace: 'nowrap' }}>
                  {app.name}
                </span>
              )}
            </div>
          </Link>
        </div>
      </SidebarHeader>

      <SidebarContent>
        {privateLayout.menuGroups.map((group) => (
          <SidebarGroup key={group.label}>
            <SidebarGroupLabel>{group.label}</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {group.items.map((item) => {
                  const isActive = isActiveRoute(item.path);
                  const Icon = item.icon;

                  return (
                    <SidebarMenuItem key={item.path}>
                      <SidebarMenuButton
                        asChild
                        isActive={isActive}
                        tooltip={item.label}
                        size={isMobile ? "lg" : "default"}
                      >
                        <Link href={item.path}>
                          <Icon className={isMobile ? "h-5 w-5" : "h-4 w-4"} />
                          <span className={isMobile ? "text-base" : ""}>{item.label}</span>
                          {item.badge && (
                            <SidebarMenuBadge>{item.badge}</SidebarMenuBadge>
                          )}
                        </Link>
                      </SidebarMenuButton>

                      {/* Submenu */}
                      {item.subItems && item.subItems.length > 0 && (
                        <SidebarMenuSub>
                          {item.subItems.map((subItem) => {
                            const isSubActive = isActiveRoute(subItem.path);
                            const SubIcon = subItem.icon;

                            return (
                              <SidebarMenuSubItem key={subItem.path}>
                                <SidebarMenuSubButton
                                  asChild
                                  isActive={isSubActive}
                                  size={isMobile ? "md" : "md"}
                                >
                                  <Link href={subItem.path}>
                                    <SubIcon className={isMobile ? "h-5 w-5" : "h-4 w-4"} />
                                    <span className={isMobile ? "text-base" : ""}>{subItem.label}</span>
                                  </Link>
                                </SidebarMenuSubButton>
                              </SidebarMenuSubItem>
                            );
                          })}
                        </SidebarMenuSub>
                      )}
                    </SidebarMenuItem>
                  );
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        ))}
      </SidebarContent>

      {/* TODO: implement footer content if needed */}
      {/* <SidebarFooter>Footer content here</SidebarFooter> */}
    </Sidebar>
  );
}
