/**
 * NavbarShell — internal orchestrator shared by all public navbar variants.
 *
 * Handles the common layer each variant has to wire up anyway:
 *  - scroll behavior (hide on scroll, transparent → opaque)
 *  - desktop dropdown hover timers
 *  - viewport CSS vars (for the mobile drawer anchoring)
 *  - active-path detection
 *  - layout rows (default / brand-left / centered / split)
 *  - context registration (`setNavbarSurface`)
 *
 * Variants pass in their own chrome (outer positioning, shape, background) through
 * class-building render callbacks, then stay thin (just pick defaults, export types).
 */

'use client';

import React, {
  memo,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
} from 'react';

import { useAppT } from '@djangocfg/i18n';
import { useIsTabletOrBelow } from '@djangocfg/ui-core/hooks';
import { cn } from '@djangocfg/ui-core/lib';

import { usePathnameWithoutLocale } from '../../../hooks';
import { navItemsShallowEqual } from '../../../utils/navItemsShallowEqual';
import { LocaleSwitcher } from '../../_components/LocaleSwitcher';
import { useLayoutI18nOptional } from '../../../shared/LayoutI18nProvider';
import { usePublicLayoutOptional } from '../context';
import {
  useDropdownMenu,
  useNavbarScroll,
  useNavbarViewportVars,
} from '../hooks';
import type { NavigationItem } from '../../types';

import { NavActions } from '../primitives/NavActions';
import { NavBrand } from '../primitives/NavBrand';
import { NavControls } from '../primitives/NavControls';
import { NavDesktopItems } from '../primitives/NavDesktopItems';

import { NavbarRowDesktop, NavbarRowMobile } from './navbarRows';

import { heightClsDesktop, heightClsMobile, resolveInsetX } from './navbarShellStyles';
import type { NavbarShellProps } from './navbarShell.types';

function NavbarShellRaw(props: NavbarShellProps) {
  const context = usePublicLayoutOptional();

  const {
    variant,
    position,
    brand,
    brandHref = '/',
    navigation = [],
    userMenu,
    renderDesktopDropdown,
    desktopMaxPrimaryItems: desktopMaxPrimaryItemsProp,
    navLayout = 'default',
    navbarHeight = 'md',
    insetX,
    innerPadding,
    hideNavOnScroll = false,
    transparent = false,
    transparentThreshold = 40,
    outerClassName,
    shapeClassName,
    shapeForState,
  } = props;

  const desktopMaxPrimaryItems = desktopMaxPrimaryItemsProp
    ? Math.max(1, desktopMaxPrimaryItemsProp)
    : undefined;
  const mobileMenuOpen = props.mobileMenuOpen ?? context?.mobileMenuOpen ?? false;
  const toggleMobileMenu = props.onMobileMenuToggle ?? context?.toggleMobileMenu ?? (() => {});
  const closeMobileMenu = context?.closeMobileMenu ?? (() => {});

  const navOuterRef = useRef<HTMLDivElement | null>(null);

  const { hidden, scrolled } = useNavbarScroll({ hideNavOnScroll, transparent, transparentThreshold });
  const dropdown = useDropdownMenu();
  useNavbarViewportVars(navOuterRef, [position, variant, outerClassName, shapeClassName] as const);

  const isTabletOrBelow = useIsTabletOrBelow();
  const t = useAppT();
  const pathname = usePathnameWithoutLocale();
  // `LocaleSwitcher` throws without a provider, so the mobile flag is gated on
  // this being present — same contract `NavControls` applies internally.
  const i18n = useLayoutI18nOptional();

  // Close dropdowns when switching to mobile. Depends on `closeDropdown` alone,
  // not on `dropdown`: the object changes identity whenever a menu opens, and
  // depending on it would close the dropdown the moment it is opened.
  const { closeDropdown } = dropdown;
  useEffect(() => {
    if (isTabletOrBelow) closeDropdown();
  }, [isTabletOrBelow, closeDropdown]);

  // Sync navbar surface into context
  const setNavbarSurface = context?.setNavbarSurface;
  useLayoutEffect(() => {
    if (!setNavbarSurface) return;
    setNavbarSurface({ variant, position });
    return () => setNavbarSurface(null);
  }, [setNavbarSurface, variant, position]);

  const toggleMobileLabel = useMemo(() => t('layouts.navigation.toggleMobile'), [t]);

  const isActivePath = useMemo(() => (href: string) => {
    if (href === '/') return pathname === '/';
    return pathname === href || pathname.startsWith(`${href}/`);
  }, [pathname]);

  const isGroupActive = useMemo(() => (item: NavigationItem): boolean => {
    if (isActivePath(item.href)) return true;
    return item.items?.some((sub) => isActivePath(sub.href)) ?? false;
  }, [isActivePath]);

  // Filter lone link duplicating brand (keeps full list in drawer)
  const desktopNavItems = useMemo(
    () => navigation.filter((item) => item.items?.length || item.href !== brandHref),
    [navigation, brandHref],
  );

  const desktopItems = desktopNavItems;

  const outerCls = cn(
    outerClassName,
    'inset-x-0',
    // Stay above the mobile drawer backdrop (z-[998]) and drawer (z-[1000])
    // so the brand + close button remain visible and clickable.
    mobileMenuOpen ? 'z-[1001]' : 'z-50',
    // Slide timing tuned for a "settled" feel, not a slow drift: a short 220ms
    // with a gentle ease-out (decelerate into place) reads as the bar snapping
    // to attention on scroll-up, while `motion-reduce:transition-none` honours
    // the OS setting (the hook also refuses to set `hidden` under reduced
    // motion, so the bar simply stays put). `will-change` promotes it to its
    // own layer so the transform never repaints the page behind it.
    hideNavOnScroll &&
      'transition-transform duration-[220ms] ease-[cubic-bezier(0.22,1,0.36,1)] will-change-transform motion-reduce:transition-none',
    hideNavOnScroll && hidden && !mobileMenuOpen && '-translate-y-full',
  );

  const surfaceCls = shapeForState?.({ scrolled, transparent, menuOpen: mobileMenuOpen });

  const brandNode = (
    <div className="min-w-0 shrink-0 flex items-center">
      <NavBrand brand={brand} brandHref={brandHref} />
    </div>
  );

  const desktopNavNode = navLayout !== 'split' ? (
    <NavDesktopItems
      items={desktopItems}
      maxVisible={desktopMaxPrimaryItems}
      isActivePath={isActivePath}
      isGroupActive={isGroupActive}
      dropdown={dropdown}
      renderDesktopDropdown={renderDesktopDropdown}
    />
  ) : null;

  const showThemeSwitcher = props.controls?.showThemeSwitcher === true;
  const showLocaleSwitcher = props.controls?.showLocaleSwitcher === true;
  const hasControls = showThemeSwitcher || showLocaleSwitcher;
  const controlsNode = hasControls ? (
    <NavControls
      showThemeSwitcher={showThemeSwitcher}
      showLocaleSwitcher={showLocaleSwitcher}
    />
  ) : null;

  // Locale sits in the navbar beside the burger, reachable without opening the
  // menu. It stays the compact dropdown, NOT the fullscreen dialog: anchored at
  // the TOP of the screen it has all the room it needs to open downward, so the
  // overflow that plagued the drawer footer cannot happen here — and a modal is
  // far too heavy a response to a mistap on a small target.
  //
  // Rendered directly rather than through `NavControls`: that wrapper hardcodes
  // an outlined, tinted pill for the site footer, and overriding it from the
  // outside produced exactly the mismatch this pairing must avoid — an outlined
  // flag next to a ghost burger. Here both are ghost squircles of equal size.
  const mobileLocaleNode = showLocaleSwitcher && i18n ? (
    // Capture-phase close: the navbar (z-1001) stays clickable above an open
    // drawer, so without this the drawer would sit open behind the menu.
    <div
      onClickCapture={() => {
        if (mobileMenuOpen) closeMobileMenu();
      }}
    >
      <LocaleSwitcher
        variant="dropdown"
        buttonVariant="ghost"
        size="icon"
        showTriggerLabel={false}
        className="h-11 w-11 rounded-full"
      />
    </div>
  ) : null;

  const actionsNode = props.renderActions ? (
    props.renderActions({
      userMenu,
      mobileMenuOpen,
      toggleMobileMenu,
      toggleMobileLabel,
      navLayout,
      controls: controlsNode,
    })
  ) : (
    <NavActions
      userMenu={userMenu}
      mobileMenuOpen={mobileMenuOpen}
      onMobileMenuToggle={toggleMobileMenu}
      toggleMobileLabel={toggleMobileLabel}
      forceShowMobileTrigger={navLayout === 'split'}
      actions={props.actions}
      leadingSlot={props.actionsLeadingSlot}
      trailingSlot={props.actionsTrailingSlot}
      controlsSlot={controlsNode}
      mobileLeadingSlot={mobileLocaleNode}
    />
  );

  const innerPaddingCls = innerPadding ?? cn('w-full', resolveInsetX(insetX));

  return (
    <div ref={navOuterRef} className={outerCls}>
      <nav className={cn(shapeClassName, surfaceCls)}>
        <div className={innerPaddingCls}>
          {/* Two rows, one config. Exactly one is visible at any width — see
              the note in `navbarRows.tsx` for why this is CSS and not a
              media-query hook. */}
          <NavbarRowDesktop
            brand={brandNode}
            actions={actionsNode}
            desktopNav={desktopNavNode}
            navLayout={navLayout}
            heightClassName={heightClsDesktop[navbarHeight]}
          />
          <NavbarRowMobile
            brand={brandNode}
            actions={actionsNode}
            heightClassName={heightClsMobile[navbarHeight]}
          />
        </div>
      </nav>
    </div>
  );
}

/**
 * Memoised navbar orchestrator. Re-renders only when any config prop changes
 * (variant, position, nav items, actions, slots, etc.). The heavy inner JSX
 * (brand, desktop nav, actions) is preserved across renders when props are
 * stable. Navigation items are compared via navItemsShallowEqual so that
 * reference churn from parent does not cause a re-render.
 */
export const NavbarShell = memo(NavbarShellRaw, (prev, next) => {
  return (
    prev.variant === next.variant &&
    prev.position === next.position &&
    prev.brand === next.brand &&
    prev.brandHref === next.brandHref &&
    prev.userMenu === next.userMenu &&
    prev.desktopMaxPrimaryItems === next.desktopMaxPrimaryItems &&
    prev.navLayout === next.navLayout &&
    prev.navbarHeight === next.navbarHeight &&
    prev.insetX === next.insetX &&
    prev.innerPadding === next.innerPadding &&
    prev.hideNavOnScroll === next.hideNavOnScroll &&
    prev.transparent === next.transparent &&
    prev.transparentThreshold === next.transparentThreshold &&
    prev.outerClassName === next.outerClassName &&
    prev.shapeClassName === next.shapeClassName &&
    prev.shapeForState === next.shapeForState &&
    prev.renderActions === next.renderActions &&
    prev.actions === next.actions &&
    prev.actionsLeadingSlot === next.actionsLeadingSlot &&
    prev.actionsTrailingSlot === next.actionsTrailingSlot &&
    prev.controls === next.controls &&
    prev.mobileMenuOpen === next.mobileMenuOpen &&
    prev.onMobileMenuToggle === next.onMobileMenuToggle &&
    navItemsShallowEqual(prev.navigation ?? [], next.navigation ?? [])
  );
});
