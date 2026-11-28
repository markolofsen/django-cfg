/**
 * Provider Configuration Types
 *
 * Configuration types for layout providers (theme, MCP chat)
 * Note: Analytics, PWA, Push, and Error types are defined in their respective modules
 */

export type { ThemeStylePresetId } from '@djangocfg/ui-core/styles/presets';

// ============================================================================
// Theme Configuration
// ============================================================================

export interface ThemeConfig {
  defaultTheme?: 'light' | 'dark' | 'system';
  storageKey?: string;
}

