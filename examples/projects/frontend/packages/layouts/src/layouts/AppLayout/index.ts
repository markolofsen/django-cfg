/**
 * AppLayout - Unified Application Layout System
 *
 * Single self-sufficient component for all layout needs
 */

// Main component
export { AppLayout } from './AppLayout';

// Types
export type {
  AppLayoutConfig,
  PublicLayoutConfig,
  PrivateLayoutConfig,
  RouteConfig,
  RouteDetectors,
  LayoutMode,
  NavigationItem,
  NavigationSection,
  DashboardMenuItem,
  DashboardMenuGroup,
} from './types';

// Context and hooks
export { useAppContext, AppContextProvider } from './context';
export { useLayoutMode, useNavigation } from './hooks';

// Layouts (for custom usage if needed)
export { PublicLayout } from './layouts/PublicLayout';
export { PrivateLayout } from './layouts/PrivateLayout';
export { AuthLayout } from './layouts/AuthLayout';
