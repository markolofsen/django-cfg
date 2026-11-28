/**
 * Shared Layout Types - Central Export
 *
 * This is the main entry point for all layout types.
 * Types are organized by category and imported from their source modules.
 */

// ============================================================================
// Provider Configuration Types
// ============================================================================

// Local provider configs
export type {
  ThemeConfig,
  ThemeStylePresetId,
} from './providers.types';

// External provider configs (re-export for convenience)
export type { AnalyticsConfig } from '../../snippets/Analytics/types';
export type {
  ErrorBoundaryConfig,
  ErrorTrackingConfig,
  ValidationErrorConfig,
  CORSErrorConfig,
  NetworkErrorConfig,
} from '../../components/errors/types';

// ============================================================================
// UI Component Types
// ============================================================================

export type {
  NavigationItem,
  NavigationSection,
  FooterLink,
  FooterMenuSection,
  FooterSocialLinks,
  FooterConfig,
  UserMenuItem,
  UserMenuGroup,
  UserMenuLocaleConfig,
  UserMenuConfig,
} from './ui.types';

// ============================================================================
// Layout Types
// ============================================================================

export type {
  BaseLayoutProps,
  DevtoolsConfig,
  I18nLayoutConfig,
  LocaleSuggestionOptions,
  LayoutVisualVariant,
  LayoutVisualConfig,
  LayoutBoxedRadius,
  LayoutBoxedBackground,
} from './layout.types';
