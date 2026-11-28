/**
 * Public Layout exports
 *
 * Each navbar and footer is a self-contained variant — pick one and pass it
 * into `PublicLayout` via the `navbar` / `footer` slots.
 */

// Layout container
export { PublicLayout } from './PublicLayout';
export type { PublicLayoutProps } from './PublicLayout';

// Context
export { PublicLayoutProvider, usePublicLayout } from './context';

// Shared types
export type {
  PublicNavbarSurface,
  PublicNavbarVariant,
  PublicNavbarPosition,
  PublicNavbarShellConfig,
  PublicNavLayout,
  PublicNavbarHeight,
  PublicNavbarInsetX,
  PublicDesktopDropdownRenderer,
  PublicDesktopDropdownRenderProps,
} from './navbarTypes';

// Hook types (consumers occasionally want them)
export type { UseNavbarScrollOptions, UseNavbarScrollReturn } from './hooks/useNavbarScroll';
export type { UseDropdownMenuReturn } from './hooks/useDropdownMenu';

// Primitives (for users who want to build a custom navbar)
export {
  NavBrand,
  NavActions,
  NavActionItem,
  NavControls,
  NavDesktopItems,
} from './primitives';
export type {
  NavAction,
  NavControlsProps,
} from './primitives';

// Navbar variants
export * from './navbars';

// Footer variants
export * from './footers';
