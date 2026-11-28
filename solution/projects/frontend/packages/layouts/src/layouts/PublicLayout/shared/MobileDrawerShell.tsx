/**
 * MobileDrawerShell — shared drawer body used by every navbar variant.
 *
 * Variants differ only in `panelClassName` (rounded/flush, shadow, border) and
 * optional outer container class.
 */

'use client';

import { ArrowRight } from 'lucide-react';
import React, { useMemo } from 'react';

import { useAuth } from '@djangocfg/api/auth';
import { useAppT } from '@djangocfg/i18n';
import { Button, Link } from '@djangocfg/ui-core/components';
import { useBodyScrollLock, useIsTabletOrBelow } from '@djangocfg/ui-core/hooks';
import { cn } from '@djangocfg/ui-core/lib';

import { usePathnameWithoutLocale } from '../../../hooks';
import { UserMenu } from '../components/UserMenu';
import { usePublicLayoutOptional } from '../context';
import { useMobileNavPanel } from '../hooks';
import { NavControls } from '../primitives/NavControls';

import type { NavigationItem, UserMenuConfig } from '../../types';

export interface MobileDrawerShellProps {
  isOpen?: boolean;
  onClose?: () => void;
  navigation?: NavigationItem[];
  userMenu?: UserMenuConfig;
  /** Wrapper around the panel — controls horizontal padding / max width. */
  outerClassName?: string;
  /** Panel surface (bg, border, rounding, shadow). */
  panelClassName?: string;
  /** Optional theme/locale controls shown as a row inside the drawer footer. */
  controls?: {
    showThemeSwitcher?: boolean;
    showLocaleSwitcher?: boolean;
  };
}

// Module-level so the "no navigation" case keeps one identity: a fresh `[]` per
// render would make `mobileNavigation`'s memo recompute on every render.
const NO_NAVIGATION: NavigationItem[] = [];

export function MobileDrawerShell(props: MobileDrawerShellProps) {
  const context = usePublicLayoutOptional();
  const mobileMenuOpen = props.isOpen ?? context?.mobileMenuOpen ?? false;
  const closeMobileMenu = props.onClose ?? context?.closeMobileMenu ?? (() => {});
  const navigation = props.navigation ?? NO_NAVIGATION;
  const userMenu = props.userMenu;

  const { isAuthenticated, user, routes } = useAuth();
  const pathname = usePathnameWithoutLocale();
  const t = useAppT();
  const { mounted, visible } = useMobileNavPanel({
    isOpen: mobileMenuOpen,
    onClose: closeMobileMenu,
  });
  const isTabletOrBelow = useIsTabletOrBelow();
  useBodyScrollLock(mobileMenuOpen && isTabletOrBelow);

  const labels = useMemo(() => ({
    quickActions: 'Actions',
    signIn: t('layouts.profile.login'),
  }), [t]);

  const mobileNavigation = useMemo(() => {
    const hasHome = navigation.some((item) => item.href === '/');
    if (hasHome) return navigation;
    return [{ label: 'Home', href: '/' }, ...navigation];
  }, [navigation]);

  const isActivePath = (href: string) => {
    if (href === '/') return pathname === '/';
    return pathname === href || pathname.startsWith(`${href}/`);
  };

  if (!mounted) return null;

  const hasSessionUser = Boolean(isAuthenticated && user);
  const showSignInFooter = !hasSessionUser;
  const showThemeSwitcher = props.controls?.showThemeSwitcher === true;
  // Locale is deliberately NOT rendered here even when enabled: on mobile it
  // lives in the navbar beside the burger (see NavbarShell). The drawer footer
  // is the worst possible anchor for a locale list — it sits at the bottom
  // edge, so the list opened downward and spilled past the panel.
  const showControlsRow = showThemeSwitcher;

  return (
    <>
      {mobileMenuOpen && (
        <button
          type="button"
          aria-label={t('layouts.mobile.closeMenu')}
          className="fixed inset-0 z-[998] lg:hidden bg-black/35 transition-opacity duration-200"
          onClick={closeMobileMenu}
        />
      )}
      <div
        className={cn(
          // Horizontal padding mirrors the navbar outer wrapper so the drawer
          // panel aligns edge-to-edge with the navbar shell.
          'pointer-events-none fixed inset-x-0 z-1000 lg:hidden px-3 pb-3 sm:px-4 sm:pb-3 lg:px-6',
        )}
        style={{
          top: 'var(--public-navbar-mobile-drawer-top, 5rem)',
          bottom: 0,
        }}
      >
        <div
          className={cn(
            // Auto height: the panel hugs its content and only grows as tall as
            // it needs, capped by `max-height` below so it never exceeds the
            // screen (then the inner list scrolls). `h-full` would force it to
            // fill the whole navbar-bottom→screen-bottom region even with a few
            // links, leaving dead space.
            'mx-auto flex min-h-0 w-full flex-col overflow-hidden bg-background/72 backdrop-blur-[10px] dark:bg-card/80 transform-gpu will-change-transform transition-[transform,opacity] duration-[220ms] ease-out',
            props.panelClassName,
            props.outerClassName,
            visible
              ? 'pointer-events-auto opacity-100 translate-y-0 scale-100'
              : 'pointer-events-none opacity-0 -translate-y-2 scale-[0.985]',
          )}
          style={{
            maxHeight: 'min(var(--public-navbar-mobile-drawer-max-height, calc(100dvh - 5rem - 12px)), calc(100dvh - 12px))',
          }}
        >
          {/* `p-2` is the panel's inner gutter. Rows carry their own `px-3`, so
              a link's text sits at 20px from the panel edge while its hover /
              active pill still has room to breathe inside the rounded corners —
              at `px-4` the pill ran into them. */}
          <div className="flex-1 min-h-0 overflow-y-auto p-2 space-y-3">
            {hasSessionUser && (
              <div className="px-2">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
                  {labels.quickActions}
                </h3>
              </div>
            )}

            {hasSessionUser && (
              <UserMenu variant="mobile" groups={userMenu?.groups} authPath={userMenu?.authPath} i18n={userMenu?.i18n} />
            )}

            {/* No "MENU" heading: an open drawer IS the menu, so the label only
                cost a row of vertical space on the smallest screens.
                No `space-y` either — each row already carries its own height
                (`min-h-11`), so an extra gap on top of it read as drift rather
                than rhythm. Rows touch; their padding does the separating. */}
            <div>
              {mobileNavigation.map((item) => {
                  const childItems = item.items ?? [];
                  const hasChildNav = childItems.length > 0;
                  const anyChildActive = hasChildNav && childItems.some((sub) => isActivePath(sub.href));
                  const parentPageActive = hasChildNav
                    ? isActivePath(item.href) && !anyChildActive
                    : isActivePath(item.href);
                  const parentOnlySectionOpen = hasChildNav && anyChildActive;
                  return (
                    <div key={item.href}>
                      <Link
                        href={item.href}
                        onClick={closeMobileMenu}
                        title={item.label}
                        className={cn(
                          'flex min-h-11 min-w-0 max-w-full items-center rounded-control border-0 px-3 text-[15px] font-medium transition-colors ring-0 truncate',
                          'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/35',
                          parentPageActive
                            ? 'border-0 bg-accent font-semibold text-foreground shadow-sm dark:border dark:border-border dark:bg-muted dark:shadow-none'
                            : parentOnlySectionOpen
                              ? 'font-semibold text-foreground'
                              : 'text-foreground hover:bg-accent/60 hover:text-accent-foreground',
                        )}
                      >
                        {item.label}
                      </Link>
                      {hasChildNav && (
                        // Children stay expanded (a short scroll beats an extra
                        // tap). Every row is a 44px target, children included,
                        // with smaller type and no bold to keep the parents
                        // the louder line.
                        //
                        // The rule sits at `ml-[1.125rem]` — the centre of the
                        // parent's text inset (px-3 + half a character) — so the
                        // children hang off their parent instead of floating at
                        // an unrelated offset.
                        <div className="my-0.5 ml-[1.125rem] space-y-0 border-l border-border/50 pl-3">
                          {childItems.map((subItem) => {
                            const subActive = isActivePath(subItem.href);
                            return (
                              <Link
                                key={`${item.href}-${subItem.href}`}
                                href={subItem.href}
                                onClick={closeMobileMenu}
                                title={subItem.label}
                                className={cn(
                                  'flex min-h-11 min-w-0 max-w-full items-center rounded-control border-0 px-3 text-sm font-medium transition-colors ring-0 truncate',
                                  'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/35',
                                  subActive
                                    ? 'border-0 bg-accent font-semibold text-foreground shadow-sm dark:border dark:border-border dark:bg-muted/90 dark:shadow-none'
                                    : 'border-0 text-muted-foreground surface-hover hover:text-foreground',
                                )}
                              >
                                {subItem.label}
                              </Link>
                            );
                          })}
                        </div>
                      )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* One footer row, not three stacked bands. Controls are utilities and
              sit left at their natural width; Sign in is the single primary
              action and sits right, sized to its label — a full-bleed button
              here read as the loudest thing in the drawer while the language
              picker above it burned a whole row of its own. */}
          {/* `mx-2` insets the rule to the panel gutter so it reads as a divider
              between two zones of one panel, not a seam across it. */}
          {(showControlsRow || showSignInFooter) && (
            <div className="mx-2 shrink-0 border-t border-border/60 px-1 py-2.5 flex items-center justify-between gap-3">
              {showControlsRow ? (
                // Squared off to match the navbar controls and the Login button
                // beside it — `NavControls` itself stays pill-shaped for the
                // site footer, which has no such neighbours.
                <NavControls
                  className="[&>div]:rounded-[var(--radius-popover)] [&_button]:rounded-full"
                  showThemeSwitcher={showThemeSwitcher}
                  showLocaleSwitcher={false}
                  size="compact"
                />
              ) : (
                <span />
              )}

              {showSignInFooter && (
                <Link
                  href={userMenu?.authPath || routes.auth}
                  onClick={closeMobileMenu}
                  className="shrink-0"
                >
                  <Button className="rounded-full h-10 gap-1.5 px-5">
                    {labels.signIn}
                    <ArrowRight className="h-4 w-4 shrink-0" aria-hidden />
                  </Button>
                </Link>
              )}
            </div>
          )}
        </div>
      </div>
    </>
  );
}
