/**
 * Public Layout
 *
 * Simple layout for public pages (home, docs, contact, legal pages)
 * Import and use directly with props - no complex configs needed!
 *
 * Features:
 * - Responsive navigation with mobile drawer
 * - User menu integration
 * - No footer (add your own custom footer component)
 *
 * @example
 * ```tsx
 * import { PublicLayout, PublicNavbar } from '@djangocfg/layouts';
 *
 * <PublicLayout
 *   navbar={
 *     <PublicNavbar
 *       config={{
 *         brand: <YourNavbarBrand />,
 *         navigation: [
 *           { label: 'Home', href: '/' },
 *           { label: 'Docs', href: '/docs' },
 *         ],
 *       }}
 *     />
 *   }
 * >
 *   {children}
 * </PublicLayout>
 * ```
 * Pass `brand` on `PublicNavbar` (`ReactNode` or string).
 */

'use client';

import { usePathname } from 'next/navigation';
import { ReactNode, useCallback, useEffect, useMemo, useState } from 'react';

import { cn } from '@djangocfg/ui-core/lib';

import { PublicLayoutProvider, usePublicLayoutOptional } from './context';
import type { PublicNavbarSurface } from './navbarTypes';

export interface PublicLayoutProps {
  children: ReactNode;

  /**
   * Slots (advanced).
   *
   * Slots-only API: this layout does not render any default navbar/drawer/footer.
   * Pass `navbar`, `mobileDrawer`, `footer` explicitly (or keep them empty).
   */
  navbar?: ReactNode;
  footer?: ReactNode;
  /**
   * When `auto` (default), `<main>` gets a small top offset from `PublicNavigation` surface
   * (`floating` vs `flush`). Set `none` if the page controls spacing itself.
   */
  contentTopSpacing?: 'auto' | 'none';
  /**
   * When `auto` (default), `<main>` gets bottom padding before the footer so the last block of
   * page content is not flush against the footer edge. Set `none` if the page/footer slot handles it.
   * `compact` uses a smaller gap than `auto`.
   */
  contentBottomSpacing?: 'auto' | 'none' | 'compact';
}

function PublicMain({
  children,
  contentTopSpacing,
  contentBottomSpacing,
}: {
  children: ReactNode;
  contentTopSpacing: 'auto' | 'none';
  contentBottomSpacing: 'auto' | 'none' | 'compact';
}) {
  const ctx = usePublicLayoutOptional();
  const variant = ctx?.navbarSurface?.variant;

  const topClass =
    contentTopSpacing === 'none'
      ? undefined
      : !variant
        ? 'pt-4 sm:pt-5'
        : variant === 'floating'
          ? 'pt-2 sm:pt-3 lg:pt-4'
          : 'pt-1 sm:pt-2 lg:pt-3';

  const bottomClass =
    contentBottomSpacing === 'none'
      ? undefined
      : contentBottomSpacing === 'compact'
        ? 'pb-4 sm:pb-6 lg:pb-8'
        : 'pb-8 sm:pb-10 lg:pb-12';

  return (
    <main className={cn('flex-1', topClass, bottomClass)}>
      {children}
    </main>
  );
}

export function PublicLayout({
  children,
  navbar,
  footer,
  contentTopSpacing = 'auto',
  contentBottomSpacing = 'auto',
}: PublicLayoutProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [navbarSurface, setNavbarSurfaceState] = useState<PublicNavbarSurface | null>(null);
  const pathname = usePathname();

  const setNavbarSurface = useCallback((surface: PublicNavbarSurface | null) => {
    setNavbarSurfaceState(surface);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [pathname]);

  const contextValue = useMemo(
    () => ({
      mobileMenuOpen,
      toggleMobileMenu: () => setMobileMenuOpen((prev) => !prev),
      closeMobileMenu: () => setMobileMenuOpen(false),
      navbarSurface,
      setNavbarSurface,
    }),
    [mobileMenuOpen, navbarSurface, setNavbarSurface],
  );

  return (
    <PublicLayoutProvider value={contextValue}>
      <div className="min-h-screen flex flex-col">
        {navbar ?? null}

        <PublicMain
          contentTopSpacing={contentTopSpacing}
          contentBottomSpacing={contentBottomSpacing}
        >
          {children}
        </PublicMain>

        {footer ?? null}
      </div>
    </PublicLayoutProvider>
  );
}

